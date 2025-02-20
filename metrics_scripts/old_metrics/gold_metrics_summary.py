import json
import os
import sqlite3
from tqdm.auto import tqdm
from multiprocessing import Pool, TimeoutError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def classify_error(error_message):
    if "no such column" in error_message.lower():
        return "No such column"
    if "syntax error" in error_message.lower():
        return "Syntax error"
    if "no such table" in error_message.lower():
        return "No such table"
    if "query timed out" in error_message.lower():
        return "Query timed out"
    return "Other error"

def compare_queries(prediction_queries, gold_standard_queries, questions, db_base_path):
    exec_exact_matches = 0
    string_exact_matches = 0
    total = len(prediction_queries)
    db_scores = {}
    cosine_similarities = []

    error_counts = {}

    for i in tqdm(range(total), desc="Comparing queries"):
        gold_standard_query = gold_standard_queries[i]
        gold_standard_db_name = extract_db_name_from_query(gold_standard_query)
        gold_standard_query = strip_db_name_from_query(gold_standard_query)
        prediction_query = prediction_queries[i]

        if gold_standard_db_name not in db_scores:
            db_scores[gold_standard_db_name] = {
                "total": 0, "exec_exact_matches": 0, "string_exact_matches": 0, "cosine_similarities": []
            }

        try:
            db_path = os.path.join(db_base_path, gold_standard_db_name, f"{gold_standard_db_name}.sqlite")
            prediction_result, prediction_error = execute_query_with_timeout(db_path, prediction_query)
            gold_standard_result, gold_standard_error = execute_query_with_timeout(db_path, gold_standard_query)

            if prediction_error:
                error_type = classify_error(prediction_error)
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            else:
                # Check for exact execution match
                if prediction_result == gold_standard_result:
                    exec_exact_matches += 1
                    db_scores[gold_standard_db_name]["exec_exact_matches"] += 1

            if gold_standard_error:
                error_type = classify_error(gold_standard_error)
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

            # Check for exact string match
            if prediction_query == gold_standard_query:
                string_exact_matches += 1
                db_scores[gold_standard_db_name]["string_exact_matches"] += 1

            # Compute cosine similarity
            vectorizer = TfidfVectorizer().fit_transform([prediction_query, gold_standard_query])
            vectors = vectorizer.toarray()
            cosine_sim = cosine_similarity(vectors)[0, 1]
            cosine_similarities.append(cosine_sim)
            db_scores[gold_standard_db_name]["cosine_similarities"].append(cosine_sim)

        except sqlite3.Error as e:
            error_type = classify_error(str(e))
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        db_scores[gold_standard_db_name]["total"] += 1

    overall_score = {
        "total": total,
        "exec_exact_matches": exec_exact_matches,
        "string_exact_matches": string_exact_matches,
        "exec_accuracy": exec_exact_matches / total * 100 if total > 0 else 0,
        "string_accuracy": string_exact_matches / total * 100 if total > 0 else 0,
        "average_cosine_similarity": sum(cosine_similarities) / len(cosine_similarities) if cosine_similarities else 0
    }

    return overall_score, db_scores, error_counts

def log_overall_metrics(total_exec_matches, total_string_matches, total_queries, db_scores, log_file, average_cosine_similarity, error_counts):
    overall_exec_accuracy = total_exec_matches / total_queries * 100 if total_queries > 0 else 0
    overall_string_accuracy = total_string_matches / total_queries * 100 if total_queries > 0 else 0
    with open(log_file, 'w', encoding='utf-8') as overall_file:
        overall_file.write("\nOverall Metrics:\n")
        overall_file.write(f"Total Queries: {total_queries}\n")
        overall_file.write(f"Execution Exact Matches: {total_exec_matches}\n")
        overall_file.write(f"String Exact Matches: {total_string_matches}\n")
        overall_file.write(f"Execution Accuracy: {overall_exec_accuracy:.2f}%\n")
        overall_file.write(f"String Accuracy: {overall_string_accuracy:.2f}%\n")
        overall_file.write(f"Average Cosine Similarity: {average_cosine_similarity:.2f}\n")

        for db_name, scores in db_scores.items():
            db_total = scores["total"]
            db_exec_exact_matches = scores["exec_exact_matches"]
            db_string_exact_matches = scores["string_exact_matches"]
            db_exec_accuracy = db_exec_exact_matches / db_total * 100 if db_total > 0 else 0
            db_string_accuracy = db_string_exact_matches / db_total * 100 if db_total > 0 else 0
            db_avg_cosine_similarity = sum(scores["cosine_similarities"]) / len(scores["cosine_similarities"]) if scores["cosine_similarities"] else 0

            overall_file.write(f"\nDatabase: {db_name}\n")
            overall_file.write(f"Total Queries: {db_total}\n")
            overall_file.write(f"Execution Exact Matches: {db_exec_exact_matches}\n")
            overall_file.write(f"String Exact Matches: {db_string_exact_matches}\n")
            overall_file.write(f"Execution Accuracy: {db_exec_accuracy:.2f}%\n")
            overall_file.write(f"String Accuracy: {db_string_accuracy:.2f}%\n")
            overall_file.write(f"Average Cosine Similarity: {db_avg_cosine_similarity:.2f}\n")

        overall_file.write("\nError Counts:\n")
        for error_type, count in error_counts.items():
            overall_file.write(f"{error_type}: {count}\n")

if __name__ == "__main__":

    model_id = "meta-llama/llama-3-8b-instruct"
    language = "italian"
    translator = "google_trans"
    phase = "post_perturbation"
    perturbator = "gpt-4.o"
    
    prediction_file = "./predictions/Spider-dev/meta-llama/llama-3-8b-instruct/italian/google_trans/resembling_wildcards/pred_statements_resembling_wildcards_75.sql"
    gold_standard_file = "./data/Spider-dev/gold.sql"
    questions_file = "./data_ibm/italian/google-translate/spider_google_translations.json"
    log_file = "./results/sql_performance_logs/italian/meta-llama/llama-3-8b-instruct/wildcards75.txt"
    db_base_path = "./data/Spider-dev/databases"

    # Ensure the directory for log files exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    prediction_queries = load_queries(prediction_file)
    gold_standard_queries = load_queries(gold_standard_file)
    questions = load_questions(questions_file)

    print(f"Prediction queries: {len(prediction_queries)}")
    print(f"Gold standard queries: {len(gold_standard_queries)}")
    print(f"Questions: {len(questions)}")

    assert len(prediction_queries) == len(gold_standard_queries) == len(questions), "The number of queries and questions must be the same in all files."

    total_exec_matches = 0
    total_string_matches = 0
    total_queries = 0

    overall_score, db_scores, error_counts = compare_queries(prediction_queries, gold_standard_queries, questions, db_base_path)

    total_exec_matches += overall_score["exec_exact_matches"]
    total_string_matches += overall_score["string_exact_matches"]
    total_queries += overall_score["total"]

    log_overall_metrics(total_exec_matches, total_string_matches, total_queries, db_scores, log_file, overall_score["average_cosine_similarity"], error_counts)

    overall_exec_accuracy = total_exec_matches / total_queries * 100 if total_queries > 0 else 0
    overall_string_accuracy = total_string_matches / total_queries * 100 if total_queries > 0 else 0

    print("\nOverall Metrics:")
    print(f"Total Queries: {total_queries}")
    print(f"Execution Exact Matches: {total_exec_matches}")
    print(f"String Exact Matches: {total_string_matches}")
    print(f"Execution Accuracy: {overall_exec_accuracy:.2f}%")
    print(f"String Accuracy: {overall_string_accuracy:.2f}%")
    print(f"Average Cosine Similarity: {overall_score['average_cosine_similarity']:.2f}")

    print("\nError Counts:")
    for error_type, count in error_counts.items():
        print(f"{error_type}: {count}")
