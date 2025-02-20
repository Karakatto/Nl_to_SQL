import json
import re
from collections import defaultdict

# Path to the error log JSON file
error_log_file = './logs/meta-llama/llama-3-8b-instruct/english/pre_perturbation/error_counts.json'
# Path to the output text file
output_file = './logs/meta-llama/llama-3-8b-instruct/english/pre_perturbation/error_counts.txt'

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

def analyze_errors(error_log_file):
    with open(error_log_file, 'r') as f:
        error_log = json.load(f)

    categorized_error_counts = defaultdict(int)
    specific_error_counts = defaultdict(int)

    for error in error_log:
        category = categorize_error(error)
        categorized_error_counts[category] += 1
        specific_error_counts[error] += 1

    return categorized_error_counts, specific_error_counts

def write_error_counts_to_file(categorized_errors, specific_errors, output_file):
    with open(output_file, 'w') as f:
        f.write("Categorized Error Counts:\n")
        for error_type, count in sorted(categorized_errors.items(), key=lambda item: item[1], reverse=True):
            f.write(f"{error_type}: {count}\n")
        
        f.write("\nSpecific Error Counts:\n")
        for error, count in sorted(specific_errors.items(), key=lambda item: item[1], reverse=True):
            f.write(f"{error}: {count}\n")

def main():
    categorized_errors, specific_errors = analyze_errors(error_log_file)
    write_error_counts_to_file(categorized_errors, specific_errors, output_file)
    print(f"Error counts have been written to {output_file}")

if __name__ == "__main__":
    main()
