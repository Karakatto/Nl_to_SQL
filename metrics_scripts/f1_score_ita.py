import json
import os
import sqlite3
from tqdm.auto import tqdm
from multiprocessing import Pool, TimeoutError

def load_queries(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def execute_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        results = []
        queries = query.split(';')
        for q in queries:
            q = q.strip()
            if q:
                cursor.execute(q)
                if cursor.description:  # Check if the query returns data
                    results.extend(cursor.fetchall())
        conn.close()
        return results, None
    except sqlite3.Error as e:
        return [], str(e)

def execute_query_with_timeout(db_path, query, timeout=10):
    with Pool(1) as pool:
        result = pool.apply_async(execute_query, (db_path, query))
        try:
            return result.get(timeout)
        except TimeoutError:
            pool.terminate()
            return [], "Query timed out"

def strip_db_name_from_query(query):
    try:
        return query.rsplit('\t', 1)[0]
    except IndexError:
        return query

def extract_db_name_from_query(query):
    try:
        return query.rsplit('\t', 1)[1]
    except IndexError:
        return None

def compare_queries(prediction_queries, gold_standard_queries, questions, db_base_path):
    tp = 0
    fp = 0
    fn = 0
    total = len(prediction_queries)

    for i in tqdm(range(total), desc="Comparing queries"):
        gold_standard_query = gold_standard_queries[i]
        gold_standard_db_name = extract_db_name_from_query(gold_standard_query)
        gold_standard_query = strip_db_name_from_query(gold_standard_query)
        prediction_query = prediction_queries[i]

        db_path = os.path.join(db_base_path, gold_standard_db_name, f"{gold_standard_db_name}.sqlite")

        prediction_result, prediction_error = execute_query_with_timeout(db_path, prediction_query)
        gold_standard_result, gold_standard_error = execute_query_with_timeout(db_path, gold_standard_query)

        if not prediction_error and prediction_result == gold_standard_result:
            tp += 1
        else:
            if prediction_error:
                fn += 1
            else:
                fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return tp, fp, fn, precision, recall, f1_score

def append_results_to_file(file_path, scenario, perturbation, file_name, tp, fp, fn, precision, recall, f1_score):
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"Scenario: {scenario}\n")
        file.write(f"Perturbation: {perturbation}\n")
        file.write(f"File: {file_name}\n")
        file.write("Evaluation Metrics:\n")
        file.write(f"True Positives (TP): {tp}\n")
        file.write(f"False Positives (FP): {fp}\n")
        file.write(f"False Negatives (FN): {fn}\n")
        file.write(f"Precision: {precision:.2f}\n")
        file.write(f"Recall: {recall:.2f}\n")
        file.write(f"F1 Score: {f1_score:.2f}\n")
        file.write("\n")

def process_directory(prediction_dir, scenario, perturbation, gold_standard_file, questions_file, db_base_path, results_file):
    gold_standard_queries = load_queries(gold_standard_file)
    questions = load_questions(questions_file)

    for root, _, files in os.walk(prediction_dir):
        for file in files:
            if file.endswith('.sql'):
                prediction_file = os.path.join(root, file)
                prediction_queries = load_queries(prediction_file)

                print(f"Processing file: {prediction_file}")
                print(f"Number of prediction queries: {len(prediction_queries)}")
                print(f"Number of gold standard queries: {len(gold_standard_queries)}")
                print(f"Number of questions: {len(questions)}")

                assert len(prediction_queries) == len(gold_standard_queries) == len(questions), \
                    f"The number of queries and questions must be the same in all files. " \
                    f"File: {prediction_file}, Prediction Queries: {len(prediction_queries)}, " \
                    f"Gold Standard Queries: {len(gold_standard_queries)}, Questions: {len(questions)}"

                tp, fp, fn, precision, recall, f1_score = compare_queries(prediction_queries, gold_standard_queries, questions, db_base_path)

                append_results_to_file(results_file, scenario, perturbation, file, tp, fp, fn, precision, recall, f1_score)

if __name__ == "__main__":
    gold_standard_file = "./data/Spider-dev/gold.sql"
    questions_file = "./data/Spider-dev/questions.json"
    db_base_path = "./data/Spider-dev/databases"
    results_file = "./results/sql_performance_results_ita.txt"

    # Ensure the results file is empty before starting
    open(results_file, 'w').close()

    # Paths for pre and post perturbation
    pre_perturbation_dir = "./predictions/Spider-dev/meta-llama/llama-3-8b-instruct/italian/google_trans/pre_perturbation"
    post_perturbation_dir = "./predictions/Spider-dev/meta-llama/llama-3-8b-instruct/italian/google_trans/post_perturbation/gpt-4.o"

    process_directory(pre_perturbation_dir, "pre_perturbation", "none", gold_standard_file, questions_file, db_base_path, results_file)
    process_directory(post_perturbation_dir, "post_perturbation", "gpt-4.o", gold_standard_file, questions_file, db_base_path, results_file)
