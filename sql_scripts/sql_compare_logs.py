import re

def load_log_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_errors(log_content):
    pattern = re.compile(r'Error with Prediction Query (\d+) on (.+):\n(.+)\nError: (.+)')
    matches = pattern.findall(log_content)
    errors = [{"query_number": int(match[0]), "db_name": match[1], "prediction_query": match[2].strip(), "error_message": match[3].strip()} for match in matches]
    return errors

def compare_errors(english_errors, italian_errors):
    comparison = []
    english_error_dict = {(error["query_number"], error["db_name"]): error for error in english_errors}
    italian_error_dict = {(error["query_number"], error["db_name"]): error for error in italian_errors}

    all_keys = set(english_error_dict.keys()).union(set(italian_error_dict.keys()))

    for key in all_keys:
        eng_error = english_error_dict.get(key)
        ita_error = italian_error_dict.get(key)
        comparison.append({
            "query_number": key[0],
            "db_name": key[1],
            "english_error": eng_error,
            "italian_error": ita_error
        })
    
    return comparison

def main():
    english_log_path = "./results/sql_performance_logs/english/meta-llama/llama-3-8b-instruct/pred_llama3_250tok_log2.txt"
    italian_log_path = "./results/sql_performance_logs/italian/meta-llama/llama-3-8b-instruct/pre_pert/google_trans/pred_googletrans_250tok_log.txt"
    output_log_path = "./results/comparison_log.txt"

    english_log_content = load_log_file(english_log_path)
    italian_log_content = load_log_file(italian_log_path)

    english_errors = extract_errors(english_log_content)
    italian_errors = extract_errors(italian_log_content)

    comparison = compare_errors(english_errors, italian_errors)

    # Sort the comparison by query number
    comparison.sort(key=lambda x: x['query_number'])

    with open(output_log_path, 'w', encoding='utf-8') as log_file:
        for comp in comparison:
            log_file.write(f"Query {comp['query_number']} on {comp['db_name']}:\n")
            if comp["english_error"]:
                log_file.write(f"English Error:\n{comp['english_error']['prediction_query']}\nError: {comp['english_error']['error_message']}\n\n")
            else:
                log_file.write("English Error: None\n\n")
            
            if comp["italian_error"]:
                log_file.write(f"Italian Error:\n{comp['italian_error']['prediction_query']}\nError: {comp['italian_error']['error_message']}\n\n")
            else:
                log_file.write("Italian Error: None\n\n")
            
            log_file.write("\n\n")

    print(f"Comparison log written to {output_log_path}")

if __name__ == "__main__":
    main()
