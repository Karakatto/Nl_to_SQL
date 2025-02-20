import os
import sqlite3
import multiprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from tqdm import tqdm

# Configuration
spider_path = './data/Spider-dev/databases'
gold_standard_file = './data/Spider-dev/gold.sql'
questions_file = './data/Spider-dev/questions.json'
predicted_folder = './predictions/Spider-dev/meta-llama/llama-3-8b-instruct/italian/pre_perturbation_runs'
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

def process_files(predicted_file, log_dir):
    # Create log directory for this perturbation if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    detailed_log = []
    error_log = []
    unprocessed_queries = []
    overall_metrics = {
        'Total Queries': 0,
        'Execution Exact Matches': 0,
        'String Exact Matches': 0,
        'Execution Accuracy': 0.0,
        'String Accuracy': 0.0,
        'Average Cosine Similarity': 0.0,
    }
    database_metrics = {}
    error_counts = {}

    gold_standard_queries = load_queries(gold_standard_file)
    predicted_queries = load_queries(predicted_file)
    with open(questions_file, 'r') as f:
        questions = json.load(f)

    if len(gold_standard_queries) != len(predicted_queries):
        raise ValueError("The number of queries in the gold standard file does not match the number in the predicted file.")

    for i, (gold_standard_query, predicted_query) in tqdm(enumerate(zip(gold_standard_queries, predicted_queries)), total=len(gold_standard_queries)):
        gold_standard_query, db_name = gold_standard_query.rsplit('\t', 1)
        predicted_query = predicted_query.strip()
        db_name = db_name.strip()
        db_path = os.path.join(spider_path, db_name, f"{db_name}.sqlite")
        question = questions[i]['question']

        if not os.path.isfile(db_path):
            error_log.append(f"Database file not found: {db_path}")
            unprocessed_queries.append((i, gold_standard_query, predicted_query, db_name, "Database file not found"))
            continue
        
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

        try:
            predicted_result = execute_sql_with_timeout(db_path, predicted_query, timeout_seconds)
        except Exception as e:
            pred_error = str(e)
            error_counts[pred_error] = error_counts.get(pred_error, 0) + 1

        exact_execution_match = gold_standard_result == predicted_result
        exact_string_match = predicted_query == gold_standard_query
        cosine_sim = cosine_similarity_score(predicted_query, gold_standard_query)

        overall_metrics['Total Queries'] += 1
        if exact_execution_match:
            overall_metrics['Execution Exact Matches'] += 1
        if exact_string_match:
            overall_metrics['String Exact Matches'] += 1
        overall_metrics['Average Cosine Similarity'] += cosine_sim

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

    if overall_metrics['Total Queries'] > 0:
        overall_metrics['Execution Accuracy'] = round((overall_metrics['Execution Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['String Accuracy'] = round((overall_metrics['String Exact Matches'] / overall_metrics['Total Queries']) * 100, 2)
        overall_metrics['Average Cosine Similarity'] = round(overall_metrics['Average Cosine Similarity'] / overall_metrics['Total Queries'], 2)

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

    # Write error counts
    with open(os.path.join(log_dir, 'error_counts.json'), 'w') as f:
        json.dump(error_counts, f, indent=4)

if __name__ == '__main__':
    for perturbation_file in os.listdir(predicted_folder):
        if perturbation_file.endswith('.sql'):
            perturbation_name = os.path.splitext(perturbation_file)[0]
            log_dir = os.path.join(log_base_dir, perturbation_name)
            predicted_file = os.path.join(predicted_folder, perturbation_file)
            process_files(predicted_file, log_dir)
