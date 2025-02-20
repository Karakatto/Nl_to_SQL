import os
import json
import pandas as pd
import re

# Configuration
log_base_dir = './logs/healthcare_simple/english/post-perturbation/wildcard_changes'
summary_csv_file = './logs/healthcare_simple/english/post-perturbation/wildcard_changes/summary_metrics_case_changes.csv'
summary_text_file = './logs/healthcare_simple/english/post-perturbation/wildcard_changes/summary_metrics_case_changes.txt'

# Initialize list to hold metrics
metrics_list = []

# Traverse the directory and extract metrics
for subdir, _, files in os.walk(log_base_dir):
    if 'overall_metrics.json' in files:
        metrics_file_path = os.path.join(subdir, 'overall_metrics.json')
        with open(metrics_file_path, 'r') as f:
            metrics = json.load(f)
            metrics['run'] = os.path.basename(subdir)
            metrics_list.append(metrics)

# Convert the list of metrics to a DataFrame
df_metrics = pd.DataFrame(metrics_list)

# Function to extract numeric part of the run name for sorting
def extract_run_number(run_name):
    match = re.search(r'(\d+)$', run_name)
    return int(match.group(1)) if match else float('inf')

# Sort the DataFrame by the extracted run numbers
df_metrics['run_number'] = df_metrics['run'].apply(extract_run_number)
df_metrics = df_metrics.sort_values(by='run_number').drop(columns=['run_number'])

# Save the DataFrame to a CSV file
df_metrics.to_csv(summary_csv_file, index=False)

# Save the metrics to a text file
with open(summary_text_file, 'w') as f:
    for index, row in df_metrics.iterrows():
        f.write(f"Run: {row['run']}\n")
        for key, value in row.items():
            if key != 'run':
                f.write(f"{key}: {value}\n")
        f.write("\n")

print(f"Summary metrics saved to {summary_csv_file} and {summary_text_file}")
