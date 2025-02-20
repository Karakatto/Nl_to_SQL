import json
import os
import time
from tqdm.auto import tqdm
from datetime import datetime
from dotenv import load_dotenv
import openai

def load_questions_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_sql(generated_text):
    # Ensure the SQL query starts with SELECT and remove the semicolon at the end if it exists
    generated_text = generated_text.strip()
    if not generated_text.lower().startswith("select"):
        generated_text = "SELECT " + generated_text
    return " ".join(generated_text.replace(';', '').split())

def save_sql_to_file(file_path, sql_queries):
    with open(file_path, 'w', encoding='utf-8') as file:
        for query in sql_queries:
            file.write(query + "\n")

def load_and_process_all(input_file, output_file):
    questions = load_questions_from_file(input_file)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    input_text_list = []

    for question in questions:
        input_text = (
            f"Translate the following English statement into an SQL query:\n"
            f"{question['question'].strip()}"
        )
        input_text_list.append(input_text)

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    sql_queries = []

    for i, input_text in enumerate(tqdm(input_text_list, desc="Processing questions")):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert SQL translator."},
                {"role": "user", "content": input_text}
            ],
            max_tokens=100,
            temperature=0.3,
            n=1,
            stop=None
        )
        generated_text = response.choices[0].message["content"].strip()
        sql_query = extract_sql(generated_text)
        sql_queries.append(sql_query)

        if i % 50 == 0:
            save_sql_to_file(output_file, sql_queries)

        # Handle rate limit
        if (i + 1) % 5 == 0:
            time.sleep(15)

    save_sql_to_file(output_file, sql_queries)

if __name__ == "__main__":
    startTime = datetime.now()

    input_file = "./data/Spider-dev/questions.json"
    output_file = "./data_ibm/gpt-4/pred.sql"

    load_and_process_all(input_file, output_file)

    print("Time:", datetime.now() - startTime)
