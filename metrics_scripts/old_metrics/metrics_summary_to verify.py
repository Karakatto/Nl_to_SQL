import json
import os
import sqlite3
from tqdm.auto import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def load_queries(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def execute_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
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

def compute_cosine_similarity(query1, query2):
    vectorizer = TfidfVectorizer().fit_transform([query1, query2])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0, 1]

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

def process_query(i, prediction_query, gold_standard_query, db_base_path):
    gold_standard_db_name = extract_db_name_from_query(gold_standard_query)
    gold_standard_query = strip_db_name_from_query(gold_standard_query)

    db_scores = {
        gold_standard_db_name: {
            "total": 0, "exec_exact_matches": 0, "string_exact_matches": 0, "cosine_similarities": []
        }
    }
    error_counts = {}

    db_path = os.path.join(db_base_path, gold_standard_db_name, f"{gold_standard_db_name}.sqlite")
    try:
        logging.info(f"Executing prediction query {i} on {gold_standard_db_name}")
        prediction_result, prediction_error = execute_query(db_path, prediction_query)
        logging.info(f"Executing gold standard query {i} on {gold_standard_db_name}")
        gold_standard_result, gold_standard_error = execute_query(db_path, gold_standard_query)
    except Exception as e:
        logging.error(f"Error executing query {i}: {e}")
        return 0, 0, None, db_scores, {"Exception": str(e)}

    exec_exact_match = 0
    string_exact_match = 0
    cosine_sim = None

    if prediction_error:
        error_type = classify_error(prediction_error)
        error_counts[error_type] = error_counts.get(error_type, 0) + 1
    else:
        if prediction_result == gold_standard_result:
            exec_exact_match = 1
            db_scores[gold_standard_db_name]["exec_exact_matches"] += 1

    if gold_standard_error:
        error_type = classify_error(gold_standard_error)
        error_counts[error_type] = error_counts.get(error_type, 0) + 1

    if prediction_query == gold_standard_query:
        string_exact_match = 1
        db_scores[gold_standard_db_name]["string_exact_matches"] += 1

    cosine_sim = compute_cosine_similarity(prediction_query, gold_standard_query)
    db_scores[gold_standard_db_name]["cosine_similarities"].append(cosine_sim)

    db_scores[gold_standard_db_name]["total"] += 1

    return exec_exact_match, string_exact_match, cosine_sim, db_scores, error_counts

def compare_queries(prediction_queries, gold_standard_queries, db_base_path, chunk_size=10):
    total = len(prediction_queries)
    db_scores = {}
    cosine_similarities = []
    error_counts = {}
    exec_exact_matches = 0
    string_exact_matches = 0

    for start in range(0, total, chunk_size):
        end = min(start + chunk_size, total)
        chunk = [(start + i, prediction_queries[start + i], gold_standard_queries[start + i], db_base_path) for i in range(end - start)]

        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(process_query, *args): args[0] for args in chunk}

            for future in tqdm(as_completed(futures), total=len(chunk), desc=f"Comparing queries {start}-{end}"):
                query_index = futures[future]
                try:
                    exec_exact_match, string_exact_match, cosine_sim, db_score, error_count = future.result(timeout=30)
                    exec_exact_matches += exec_exact_match
                    string_exact_matches += string_exact_match
                    cosine_similarities.append(cosine_sim)

                    # Merge db_scores
                    for db_name, scores in db_score.items():
                        if db_name not in db_scores:
                            db_scores[db_name] = scores
                        else:
                            db_scores[db_name]["total"] += scores["total"]
                            db_scores[db_name]["exec_exact_matches"] += scores["exec_exact_matches"]
                            db_scores[db_name]["string_exact_matches"] += scores["string_exact_matches"]
                            db_scores[db_name]["cosine_similarities"].extend(scores["cosine_similarities"])

                    # Merge error_counts
                    for error_type, count in error_count.items():
                        if error_type not in error_counts:
                            error_counts[error_type] = count
                        else:
                            error_counts[error_type] += count

                except TimeoutError:
                    logging.error(f"Timeout error processing query {query_index}. Skipping.")
                    error_counts["Timeout error"] = error_counts.get("Timeout error", 0) + 1
                except Exception as e:
                    logging.error(f"Error processing query {query_index}: {e}")
                    error_counts["Exception"] = error_counts.get("Exception", 0) + 1

    overall_score = {
        "total": total,
        "exec_exact_matches": exec_exact_matches,
        "string_exact_matches": string_exact_matches,
        "exec_accuracy": exec_exact_matches / total * 100 if total > 0 else 0,
        "string_accuracy": string_exact_matches / total * 100 if total > 0 else 0,
        "average_cosine_similarity": sum(cs for cs in cosine_similarities if cs is not None) / len(cosine_similarities) if cosine_similarities else 0
    }

    return overall_score, db_scores, error_counts

def log_overall_metrics(total_exec_matches, total_string_matches, total_queries, db_scores, log_file, average_cosine_similarity, error_counts):
    overall_exec_accuracy = total_exec_matches / total_queries * 100 if total_queries > 0 else 0
    overall_string_accuracy = total_string_matches / total_queries * 100 if total_queries > 0 else 0
    with open(log_file, 'a', encoding='utf-8') as overall_file:
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
    
    prediction_file = "./predictions/Spider-dev/meta-llama/llama-3-8b-instruct/pred_250tok.sql"
    gold_standard_file = "./data/Spider-dev/gold.sql"
    questions_file = "./data/Spider-dev/questions.json"
    log_file = "./results/sql_performance_logs/english/meta-llama/llama-3-8b-instruct/pred_llama3_250tok_log3.txt"
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

    overall_score, db_scores, error_counts = compare_queries(prediction_queries, gold_standard_queries, db_base_path)

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
