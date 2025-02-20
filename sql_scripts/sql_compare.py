def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def compare_queries(english_queries, italian_queries):
    differences = []
    for i, (eng_query, ita_query) in enumerate(zip(english_queries, italian_queries)):
        if eng_query.strip() != ita_query.strip():
            differences.append((i, eng_query, ita_query))
    return differences

def main():
    file_english_path = "./predictions/Spider-dev/meta-llama/llama-3-8b-instruct/pred_250tok.sql"  # Update this path
    file_italian_path = "./predictions/Spider-dev/meta-llama/llama-3-8b-instruct/italian/google_trans/pre_perturbation/pred_googletrans_ita.sql"  # Update this path
    log_file_path = "query_differences_log.txt"  # Log file to store differences

    english_queries = load_file(file_english_path)
    italian_queries = load_file(file_italian_path)

    len_english_queries = len(english_queries)
    len_italian_queries = len(italian_queries)

    print(f"Number of English queries: {len_english_queries}")
    print(f"Number of Italian queries: {len_italian_queries}")

    differences = compare_queries(english_queries, italian_queries)

    print(f"Number of differing queries: {len(differences)}")

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Number of English queries: {len_english_queries}\n")
        log_file.write(f"Number of Italian queries: {len_italian_queries}\n")
        log_file.write(f"Number of differing queries: {len(differences)}\n\n")

        for diff in differences:
            index, eng_query, ita_query = diff
            log_file.write(f"Difference at line {index + 1}:\n")
            log_file.write(f"English: {eng_query.strip()}\n")
            log_file.write(f"Italian: {ita_query.strip()}\n\n")
            
            # Also print to console for review
            print(f"\nDifference at line {index + 1}:")
            print(f"English: {eng_query.strip()}")
            print(f"Italian: {ita_query.strip()}")

if __name__ == "__main__":
    main()
