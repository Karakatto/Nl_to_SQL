import os
import sqlite3
import multiprocessing
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from tqdm import tqdm
import re
from collections import defaultdict

# Configuration
spider_path = './data/Spider-dev/databases'
gold_standard_file = './data/Spider-dev/gold.sql'
questions_file = './data_ibm/italian/google-translate/spider_google_translations.json'
predicted_folder = './predictions/Spider-dev/meta-llama/llama-3-8b-instruct/pre_perturbation_runs_ita_extra'
timeout_seconds = 10
model_id = "meta-llama/llama-3-8b-instruct"
language = "italian"
phase = "pre_perturbation"
perturbation = "consistency_baseline_runs"
log_base_dir = f'./logs/{model_id}/{language}/{phase}/{perturbation}'

# Ensure the logging base directory exists
os.makedirs(log_base_dir, exist_ok=True)

# Function to execute SQL with timeout
def worker(db_path, query, result_queue):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result_queue.put(cursor.fetchall())
        conn.close()
    except Exception as e:
        result_queue.put(e)

def execute_sql_with_timeout(db_path, query, timeout):
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=worker, args=(db_path, query, result_queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        return "Timeout"

    result = result_queue.get()
    if isinstance(result, Exception):
        raise result

    return result

# Function to calculate cosine similarity using TfidfVectorizer
def cosine_similarity_score(a, b):
    vectorizer = TfidfVectorizer().fit_transform([a, b])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0, 1]

# Load queries from SQL files
def load_queries(file_path):
    with open(file_path, 'r') as f:
        queries = f.readlines()
    return queries

# Function to categorize errors
def categorize_error(error):
    patterns = {
        "syntax_error": re.compile(r"syntax error", re.IGNORECASE),
        "no_such_table": re.compile(r"no such table", re.IGNORECASE),
        "no_such_column": re.compile(r"no such column", re.IGNORECASE),
        "misuse_of_aggregate": re.compile(r"misuse of aggregate", re.IGNORECASE),
        "timeout": re.compile(r"timeout", re.IGNORECASE),
        "ambiguous_column_name": re.compile(r"ambiguous column name", re.IGNORECASE),
        "no_such_function": re.compile(r"no such function", re.IGNORECASE),
        "incorrect_bindings": re.compile(r"Incorrect number of bindings", re.IGNORECASE),
    }
    
    for category, pattern in patterns.items():
        if pattern.search(error):
            return category
    return "other"

# Function to analyze errors
def analyze_errors(error_log):
    categorized_error_counts = defaultdict(int)
    specific_error_counts = defaultdict(int)

    for error in error_log:
        category = categorize_error(error)
        categorized_error_counts[category] += 1
        specific_error_counts[error] += 1

    return categorized_error_counts, specific_error_counts

# Function to write error counts to a file
def write_error_counts_to_file(categorized_errors, specific_errors, output_file):
    with open(output_file, 'w') as f:
        f.write("Categorized Error Counts:\n")
        for error_type, count in sorted(categorized_errors.items(), key=lambda item: item[1], reverse=True):
            f.write(f"{error_type}: {count}\n")
        
        f.write("\nSpecific Error Counts:\n")
        for error, count in sorted(specific_errors.items(), key=lambda item: item[1], reverse=True):
            f.write(f"{error}: {count}\n")

def process_files(predicted_file, log_dir):
    start_time = datetime.now()

    # Logging setup
    detailed_log = []
    error_log = []
    unprocessed_queries = []
    overall_metrics = {
        'Total Queries': 0,
        'Execution Exact Matches': 0,
        'String Exact Matches': 0,
        'Executable Queries': 0,
        'Executable Execution Matches': 0,
        'Execution Accuracy': 0.0,
        'String Accuracy': 0.0,
        'Average Cosine Similarity': 0.0,
        'Executable Execution Accuracy': 0.0,
    }
    database_metrics = {}
    error_counts = defaultdict(int)

    gold_standard_queries = load_queries(gold_standard_file)
    predicted_queries = load_queries(predicted_file)
    with open(questions_file, 'r') as f:
        questions = json.load(f)

    if len(gold_standard_queries) != len(predicted_queries):
        raise ValueError("The number of queries in the gold standard file does not match the number in the predicted file.")

    current_db_name = None
    conn = None

    for i, (gold_standard_query, predicted_query) in tqdm(enumerate(zip(gold_standard_queries, predicted_queries)), total=len(gold_standard_queries)):
        gold_standard_query, db_name = gold_standard_query.rsplit('\t', 1)
        predicted_query = predicted_query.strip()
        db_name = db_name.strip()
        question = questions[i]['question']

        if current_db_name != db_name:
            if conn:
                conn.close()
            db_path = os.path.join(spider_path, db_name, f"{db_name}.sqlite")
            if not os.path.isfile(db_path):
                error_log.append(f"Database file not found: {db_path}")
                unprocessed_queries.append((i, gold_standard_query, predicted_query, db_name, "Database file not found"))
                continue
            conn = sqlite3.connect(db_path)
            current_db_name = db_name

        if db_name not in database_metrics:
            database_metrics[db_name] = {
                'Total Queries': 0,
                'Execution Exact Matches': 0,
                'String Exact Matches': 0,
                'Average Cosine Similarity': 0.0,
            }

        gold_standard_result = None
        predicted_result = None
        gold_error = None
        pred_error = None

        try:
            gold_standard_result = execute_sql_with_timeout(db_path, gold_standard_query, timeout_seconds)
        except Exception as e:
            gold_error = str(e)
            error_counts[gold_error] = error_counts.get(gold_error, 0) + 1
            error_log.append(f"Error executing gold query {i} on database {db_name}: {gold_error}")

        try:
            predicted_result = execute_sql_with_timeout(db_path, predicted_query, timeout_seconds)
        except Exception as e:
            pred_error = str(e)
            error_counts[pred_error] = error_counts.get(pred_error, 0) + 1
            error_log.append(f"Error executing predicted query {i} on database {db_name}: {pred_error}")

        exact_execution_match = gold_standard_result == predicted_result
        exact_string_match = predicted_query == gold_standard_query
        cosine_sim = cosine_similarity_score(predicted_query, gold_standard_query)

        overall_metrics['Total Queries'] += 1
        if exact_execution_match:
            overall_metrics['Execution Exact Matches'] += 1
        if exact_string_match:
            overall_metrics['String Exact Matches'] += 1
        overall_metrics['Average Cosine Similarity'] += cosine_sim

        if gold_standard_result is not None and predicted_result is not None:
            overall_metrics['Executable Queries'] += 1
            if exact_execution_match:
                overall_metrics['Executable Execution Matches'] += 1

        db_metrics = database_metrics[db_name]
        db_metrics['Total Queries'] += 1
        if exact_execution_match:
            db_metrics['Execution Exact Matches'] += 1
        if exact_string_match:
            db_metrics['String Exact Matches'] += 1
        db_metrics['Average Cosine Similarity'] += cosine_sim

        detailed_log.append({
            'Question ID': i,
            'Question': question,
            'Database': db_name,
            'Gold standard query': gold_standard_query,
            'Predicted query': predicted_query,
            'Prediction result': predicted_result,
            'Gold standard result': gold_standard_result,
            'Exact execution match': exact_execution_match,
            'Cosine similarity': cosine_sim,
            'Exact string match': exact_string_match,
            'Gold error': gold_error,
            'Prediction error': pred_error,
        })

        if gold_error or pred_error:
            unprocessed_queries.append((i, gold_standard_query, predicted_query, db_name, gold_error or pred_error))

    if conn:
        conn.close()

    if overall_metrics['Total Queries'] > 0:
        overall_metrics['Execution Accuracy'] = round((overall_metrics['Execution Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['String Accuracy'] = round((overall_metrics['String Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['Average Cosine Similarity'] = round(overall_metrics['Average Cosine Similarity'] / overall_metrics['Total Queries'], 2)
        if overall_metrics['Executable Queries'] > 0:
            overall_metrics['Executable Execution Accuracy'] = round((overall_metrics['Executable Execution Matches'] / overall_metrics['Executable Queries']) * 100, 2)

    for db_name, db_metrics in database_metrics.items():
        if db_metrics['Total Queries'] > 0:
            db_metrics['Execution Accuracy'] = round((db_metrics['Execution Exact Matches'] / db_metrics['Total Queries']) * 100, 2)
            db_metrics['String Accuracy'] = round((db_metrics['String Exact Matches'] / db_metrics['Total Queries']) * 100, 2)
            db_metrics['Average Cosine Similarity'] = round(db_metrics['Average Cosine Similarity'] / db_metrics['Total Queries'], 2)

    # Write detailed log
    with open(os.path.join(log_dir, 'detailed_log.json'), 'w') as f:
        json.dump(detailed_log, f, indent=4)

    # Write error log
    with open(os.path.join(log_dir, 'error_log.json'), 'w') as f:
        json.dump(error_log, f, indent=4)

    # Write unprocessed queries log
    with open(os.path.join(log_dir, 'unprocessed_queries.json'), 'w') as f:
        json.dump(unprocessed_queries, f, indent=4)

    # Write overall metrics
    with open(os.path.join(log_dir, 'overall_metrics.json'), 'w') as f:
        json.dump(overall_metrics, f, indent=4)

    # Write database-specific metrics
    with open(os.path.join(log_dir, 'database_metrics.json'), 'w') as f:
        json.dump(database_metrics, f, indent=4)

    # Analyze and write error counts
    categorized_error_counts, specific_error_counts = analyze_errors(error_log)
    write_error_counts_to_file(categorized_error_counts, specific_error_counts, os.path.join(log_dir, 'error_counts.txt'))

    end_time = datetime.now()
    elapsed_time = end_time - start_time

    print("\nOverall Metrics:")
    print(f"Total Queries: {overall_metrics['Total Queries']}")
    print(f"Execution Exact Matches: {overall_metrics['Execution Exact Matches']}")
    print(f"String Exact Matches: {overall_metrics['String Exact Matches']}")
    print(f"Execution Accuracy: {overall_metrics['Execution Accuracy']:.2f}%")
    print(f"String Accuracy: {overall_metrics['String Accuracy']:.2f}%")
    print(f"Average Cosine Similarity: {overall_metrics['Average Cosine Similarity']:.2f}")
    print(f"Executable Queries: {overall_metrics['Executable Queries']}")
    print(f"Executable Execution Matches: {overall_metrics['Executable Execution Matches']}")
    print(f"Executable Execution Accuracy: {overall_metrics['Executable Execution Accuracy']:.2f}%")
    print(f"Time taken: {elapsed_time}")

    print("\nError Counts:")
    for error_type, count in sorted(categorized_error_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"{error_type}: {count}")

def main():
    for perturbation_file in os.listdir(predicted_folder):
        if perturbation_file.endswith('.sql'):
            perturbation_name = os.path.splitext(perturbation_file)[0]
            log_dir = os.path.join(log_base_dir, perturbation_name)
            os.makedirs(log_dir, exist_ok=True)
            predicted_file = os.path.join(predicted_folder, perturbation_file)
            process_files(predicted_file, log_dir)

if __name__ == '__main__':
    main()
