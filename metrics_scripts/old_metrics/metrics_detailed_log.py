import json
import os
import sqlite3
from tqdm.auto import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def load_queries(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def execute_query(conn, query):
    cursor = conn.cursor()
    results = []
    queries = query.split(';')
    for q in queries:
        q = q.strip()
        if q:
            try:
                cursor.execute(q)
                if cursor.description:  # Check if the query returns data
                    results.extend(cursor.fetchall())
            except sqlite3.Error as e:
                return [], str(e)
    return results, None

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

def compare_queries(llama_queries, gold_standard_queries, questions, db_base_path, log_file):
    exec_exact_matches = 0
    string_exact_matches = 0
    total = len(llama_queries)
    db_scores = {}

    with open(log_file, 'a', encoding='utf-8') as overall_file:
        for i in tqdm(range(total), desc="Comparing queries"):
            gold_standard_query = gold_standard_queries[i]
            gold_standard_db_name = extract_db_name_from_query(gold_standard_query)
            gold_standard_query = strip_db_name_from_query(gold_standard_query)
            llama_query = llama_queries[i]
            question = questions[i]['question']

            if gold_standard_db_name not in db_scores:
                db_scores[gold_standard_db_name] = {
                    "total": 0, "exec_exact_matches": 0, "string_exact_matches": 0
                }

            try:
                if gold_standard_db_name != "wta_1":
                    db_path = os.path.join(db_base_path, gold_standard_db_name, f"{gold_standard_db_name}.sqlite")
                    conn = sqlite3.connect(db_path, timeout=10)
                    llama_result, llama_error = execute_query(conn, llama_query)
                    gold_standard_result, gold_standard_error = execute_query(conn, gold_standard_query)
                    conn.close()

                    if llama_error:
                        overall_file.write(f"Error with Llama Query {i} on {gold_standard_db_name}:\n{llama_query}\nError: {llama_error}\n\n")
                    
                    if gold_standard_error:
                        overall_file.write(f"Error with Gold Standard Query {i} on {gold_standard_db_name}:\n{gold_standard_query}\nError: {gold_standard_error}\n\n")

                    if llama_result == gold_standard_result:
                        exec_exact_matches += 1
                        db_scores[gold_standard_db_name]["exec_exact_matches"] += 1
                        exec_match_status = "EXECUTION EXACT MATCH"
                    else:
                        exec_match_status = "EXECUTION NO MATCH"
                else:
                    exec_match_status = "SKIPPED EXECUTION"

                if llama_query == gold_standard_query:
                    string_exact_matches += 1
                    db_scores[gold_standard_db_name]["string_exact_matches"] += 1
                    string_match_status = "STRING EXACT MATCH"
                else:
                    string_match_status = "STRING NO MATCH"

            except sqlite3.Error as e:
                exec_match_status = "DATABASE ERROR"
                string_match_status = "DATABASE ERROR"
                print(f"Error with database {gold_standard_db_name}: {e}")

            db_scores[gold_standard_db_name]["total"] += 1
            log_entry = (
                f"Query {i} on {gold_standard_db_name}:\n"
                f"Question: {question}\n"
                f"Llama Query: {llama_query}\n"
                f"Llama Result: {llama_result}\n"
                f"Gold Standard Query: {gold_standard_query}\n"
                f"Gold Standard Result: {gold_standard_result}\n"
                f"{i}: {exec_match_status} | {string_match_status}\n\n"
            )
            overall_file.write(log_entry)

    overall_score = {
        "total": total,
        "exec_exact_matches": exec_exact_matches,
        "string_exact_matches": string_exact_matches,
        "exec_accuracy": exec_exact_matches / total * 100 if total > 0 else 0,
        "string_accuracy": string_exact_matches / total * 100 if total > 0 else 0,
    }

    return overall_score, db_scores

def log_overall_metrics(total_exec_matches, total_string_matches, total_queries, db_scores, log_file):
    overall_exec_accuracy = total_exec_matches / total_queries * 100 if total_queries > 0 else 0
    overall_string_accuracy = total_string_matches / total_queries * 100 if total_queries > 0 else 0
    with open(log_file, 'a', encoding='utf-8') as overall_file:
        overall_file.write("\nOverall Metrics:\n")
        overall_file.write(f"Total Queries: {total_queries}\n")
        overall_file.write(f"Execution Exact Matches: {total_exec_matches}\n")
        overall_file.write(f"String Exact Matches: {total_string_matches}\n")
        overall_file.write(f"Execution Accuracy: {overall_exec_accuracy:.2f}%\n")
        overall_file.write(f"String Accuracy: {overall_string_accuracy:.2f}%\n")

        for db_name, scores in db_scores.items():
            db_total = scores["total"]
            db_exec_exact_matches = scores["exec_exact_matches"]
            db_string_exact_matches = scores["string_exact_matches"]
            db_exec_accuracy = db_exec_exact_matches / db_total * 100 if db_total > 0 else 0
            db_string_accuracy = db_string_exact_matches / db_total * 100 if db_total > 0 else 0

            overall_file.write(f"\nDatabase: {db_name}\n")
            overall_file.write(f"Total Queries: {db_total}\n")
            overall_file.write(f"Execution Exact Matches: {db_exec_exact_matches}\n")
            overall_file.write(f"String Exact Matches: {db_string_exact_matches}\n")
            overall_file.write(f"Execution Accuracy: {db_exec_accuracy:.2f}%\n")
            overall_file.write(f"String Accuracy: {db_string_accuracy:.2f}%\n")

if __name__ == "__main__":
    llama_file = "./predictions_ita/meta-llama/llama-3-8b-instruct/pred_llama3_run2.sql"
    gold_standard_file = "./data/Spider-dev/gold.sql"
    questions_file = "./data/Spider-dev/questions.json"
    log_file = "./results/italian/gpt_to_llama/performance_logs_sql/pre_ita_llama3_run2.txt"
    db_base_path = "./data/Spider-dev/databases"

    # Ensure the directory for log files exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    llama_queries = load_queries(llama_file)
    gold_standard_queries = load_queries(gold_standard_file)
    questions = load_questions(questions_file)

    print(f"Llama queries: {len(llama_queries)}")
    print(f"Gold standard queries: {len(gold_standard_queries)}")
    print(f"Questions: {len(questions)}")

    assert len(llama_queries) == len(gold_standard_queries) == len(questions), "The number of queries and questions must be the same in all files."

    total_exec_matches = 0
    total_string_matches = 0
    total_queries = 0

    overall_score, db_scores = compare_queries(llama_queries, gold_standard_queries, questions, db_base_path, log_file)

    total_exec_matches += overall_score["exec_exact_matches"]
    total_string_matches += overall_score["string_exact_matches"]
    total_queries += overall_score["total"]

    log_overall_metrics(total_exec_matches, total_string_matches, total_queries, db_scores, log_file)

    overall_exec_accuracy = total_exec_matches / total_queries * 100 if total_queries > 0 else 0
    overall_string_accuracy = total_string_matches / total_queries * 100 if total_queries > 0 else 0

    print("\nOverall Metrics:")
    print(f"Total Queries: {total_queries}")
    print(f"Execution Exact Matches: {total_exec_matches}")
    print(f"String Exact Matches: {total_string_matches}")
    print(f"Execution Accuracy: {overall_exec_accuracy:.2f}%")
    print(f"String Accuracy: {overall_string_accuracy:.2f}%")
