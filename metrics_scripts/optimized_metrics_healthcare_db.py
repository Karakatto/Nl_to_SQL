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
db_path = './data_ibm/healthcare_db/hospital_management_2.db'  # Path to your single SQLite database
timeout_seconds = 10
model_id = "meta-llama/llama-3-8b-instruct"
language = "english"
predictions_dir = './predictions/healthcare/meta-llama/llama-3-8b-instruct/english'

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

def process_file(gold_standard_file, questions_file, predicted_file, log_dir):
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
        'Execution Accuracy': 0.0,
        'String Accuracy': 0.0,
        'Average Cosine Similarity': 0.0,
        'Executable Execution Accuracy': 0.0,
    }
    error_counts = defaultdict(int)

    gold_standard_queries = load_queries(gold_standard_file)
    predicted_queries = load_queries(predicted_file)
    with open(questions_file, 'r') as f:
        questions = json.load(f)

    if len(gold_standard_queries) != len(predicted_queries):
        raise ValueError("The number of queries in the gold standard file does not match the number in the predicted file.")

    conn = sqlite3.connect(db_path)

    for i, (gold_standard_query, predicted_query) in tqdm(enumerate(zip(gold_standard_queries, predicted_queries)), total=len(gold_standard_queries)):
        gold_standard_query = gold_standard_query.strip()
        predicted_query = predicted_query.strip()
        question = questions[i]['question']

        gold_standard_result = None
        predicted_result = None
        gold_error = None
        pred_error = None

        try:
            gold_standard_result = execute_sql_with_timeout(db_path, gold_standard_query, timeout_seconds)
        except Exception as e:
            gold_error = str(e)
            error_counts[gold_error] += 1
            error_log.append(f"Error executing gold query {i}: {gold_error}")

        try:
            predicted_result = execute_sql_with_timeout(db_path, predicted_query, timeout_seconds)
        except Exception as e:
            pred_error = str(e)
            error_counts[pred_error] += 1
            error_log.append(f"Error executing predicted query {i}: {pred_error}")

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

        detailed_log.append({
            'Question ID': i,
            'Question': question,
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
            unprocessed_queries.append((i, gold_standard_query, predicted_query, gold_error or pred_error))

    conn.close()

    if overall_metrics['Total Queries'] > 0:
        overall_metrics['Execution Accuracy'] = round((overall_metrics['Execution Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['String Accuracy'] = round((overall_metrics['String Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['Average Cosine Similarity'] = round(overall_metrics['Average Cosine Similarity'] / overall_metrics['Total Queries'], 2)
        if overall_metrics['Executable Queries'] > 0:
            overall_metrics['Executable Execution Accuracy'] = round((overall_metrics['Execution Exact Matches'] / overall_metrics['Executable Queries']) * 100, 2)

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
    print(f"Executable Execution Accuracy: {overall_metrics['Executable Execution Accuracy']:.2f}%")
    print(f"Time taken: {elapsed_time}")

    print("\nError Counts:")
    for error_type, count in sorted(categorized_error_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"{error_type}: {count}")

def main():
    question_levels = ["easy", "intermediate", "hard", "extrahard", "questions60_batch1"]
    
    for question_level in question_levels:
        predicted_folder = os.path.join(predictions_dir, question_level)
        for predicted_file in os.listdir(predicted_folder):
            if predicted_file.endswith(".sql"):
                predicted_file_path = os.path.join(predicted_folder, predicted_file)
                question_file_name = f"{question_level}_50_questions.json"  # Adjust based on actual question file names
                questions_file = f"./data_ibm/healthcare_db/{question_file_name}"
                gold_standard_file = f"./data_ibm/healthcare_db/gold_SQL_{question_level}.sql"
                log_dir = f'./logs/healthcare_db/{model_id}/{language}/{question_level}'
                
                os.makedirs(log_dir, exist_ok=True)
                process_file(
                    gold_standard_file=gold_standard_file,
                    questions_file=questions_file,
                    predicted_file=predicted_file_path,
                    log_dir=log_dir
                )

if __name__ == '__main__':
    main()
