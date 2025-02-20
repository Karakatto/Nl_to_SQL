import os
import json
from tqdm.auto import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def load_queries(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def remove_db_name_from_gold_queries(gold_standard_queries):
    cleaned_gold_standard_queries = []
    for query in gold_standard_queries:
        query_parts = query.rsplit('\t', 1)
        if len(query_parts) == 2:
            cleaned_gold_standard_queries.append(query_parts[0].strip())
        else:
            cleaned_gold_standard_queries.append(query.strip())
    return cleaned_gold_standard_queries

def calculate_similarity(query1, query2):
    vectorizer = TfidfVectorizer().fit_transform([query1, query2])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0, 1]

def compare_queries(llama_queries, gold_standard_queries, questions, log_file):
    matches = 0
    partial_matches = 0

    with open(log_file, 'w', encoding='utf-8') as file:
        for i in tqdm(range(len(llama_queries)), desc="Comparing queries"):
            llama_query = llama_queries[i]
            gold_standard_query = gold_standard_queries[i]

            file.write(f"Query {i}:\n")
            file.write(f"Question: {questions[i]['question']}\n")
            file.write(f"Llama Query: {llama_query}\n")
            file.write(f"Gold Standard Query: {gold_standard_query}\n")

            if llama_query == gold_standard_query:
                file.write(f"{i}: EXACT MATCH\n\n")
                matches += 1
            else:
                similarity_score = calculate_similarity(llama_query, gold_standard_query)
                if similarity_score > 0.8:
                    file.write(f"{i}: PARTIAL MATCH ({similarity_score:.2f})\n\n")
                    partial_matches += 1
                else:
                    file.write(f"{i}: NO MATCH\n\n")

    total_queries = len(llama_queries)
    accuracy = matches / total_queries * 100
    partial_match_rate = partial_matches / total_queries * 100

    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f"\nTotal Queries: {total_queries}\n")
        file.write(f"Exact Matches: {matches}\n")
        file.write(f"Partial Matches: {partial_matches}\n")
        file.write(f"Accuracy: {accuracy:.2f}%\n")
        file.write(f"Partial Match Rate: {partial_match_rate:.2f}%\n")

    print(f"\nTotal Queries: {total_queries}")
    print(f"Exact Matches: {matches}")
    print(f"Partial Matches: {partial_matches}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Partial Match Rate: {partial_match_rate:.2f}%")

if __name__ == "__main__":
    llama_file = "./data_ibm/pred_normalized.sql"
    gold_standard_file = "./data_ibm/gold_normalized.sql"
    questions_file = "./data/Spider-dev/questions.json"
    log_file = "./results/llama-3-8b-instruct/sql_performance_logs/string_match_performance/query_string_comparison_log_detail.txt.txt"

    llama_queries = load_queries(llama_file)
    gold_standard_queries = load_queries(gold_standard_file)
    questions = load_questions(questions_file)

    gold_standard_queries = remove_db_name_from_gold_queries(gold_standard_queries)

    print(f"Llama queries: {len(llama_queries)}")
    print(f"Gold standard queries: {len(gold_standard_queries)}")
    print(f"Questions: {len(questions)}")

    assert len(llama_queries) == len(gold_standard_queries) == len(questions), "The number of queries and questions must be the same in all files."

    compare_queries(llama_queries, gold_standard_queries, questions, log_file)
