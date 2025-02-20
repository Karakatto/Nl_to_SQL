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

def print_results_to_file(file_path, tp, fp, fn, precision, recall, f1_score):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("Evaluation Metrics:\n")
        file.write(f"True Positives (TP): {tp}\n")
        file.write(f"False Positives (FP): {fp}\n")
        file.write(f"False Negatives (FN): {fn}\n")
        file.write(f"Precision: {precision:.2f}\n")
        file.write(f"Recall: {recall:.2f}\n")
        file.write(f"F1 Score: {f1_score:.2f}\n")

if __name__ == "__main__":
    prediction_file = "./predictions/Spider-dev/meta-llama/llama-3-8b-instruct/pred_250tok.sql"
    gold_standard_file = "./data/Spider-dev/gold.sql"
    questions_file = "./data/Spider-dev/questions.json"
    db_base_path = "./data/Spider-dev/databases"
    results_file = "./results/sql_performance_results_eng.txt"

    prediction_queries = load_queries(prediction_file)
    gold_standard_queries = load_queries(gold_standard_file)
    questions = load_questions(questions_file)

    print(f"Prediction queries: {len(prediction_queries)}")
    print(f"Gold standard queries: {len(gold_standard_queries)}")
    print(f"Questions: {len(questions)}")

    assert len(prediction_queries) == len(gold_standard_queries) == len(questions), "The number of queries and questions must be the same in all files."

    tp, fp, fn, precision, recall, f1_score = compare_queries(prediction_queries, gold_standard_queries, questions, db_base_path)

    print_results_to_file(results_file, tp, fp, fn, precision, recall, f1_score)

    print("\nEvaluation Metrics:")
    print(f"True Positives (TP): {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1_score:.2f}")
