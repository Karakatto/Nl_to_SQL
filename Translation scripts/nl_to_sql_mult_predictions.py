import json
import os
from tqdm.auto import tqdm
from datetime import datetime
from dotenv import load_dotenv
from genai.client import Client
from genai.credentials import Credentials
from genai.schema import DecodingMethod, TextGenerationParameters, TextGenerationReturnOptions
from utils import load_schema, extract_sql, load_json_from_file

def load_and_process_all(base_path, questions_file, output_file, model_id):
    questions = load_json_from_file(questions_file)
    schemas = {}
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    input_text_list = []

    for _, question in tqdm(enumerate(questions), total=len(questions), desc="questions"):
        db_name = question["db_id"]
        schema_path = os.path.join(base_path, "databases", db_name, "schema.sql")

        if db_name not in schemas and os.path.exists(schema_path):
            schemas[db_name] = load_schema(schema_path)

        if db_name in schemas:
            schema = schemas[db_name]

            input_text = (
                f"This is the schema of our database:\n"
                f"{schema}\n "
                f"\n"
                f"Task:\n"
                f"Please translate the question after [Question:] into a single valid SQL-query and output it after [Query:].\n"
                f"Add a semicolon at the end of the generated SQL-query."
                f"\n"
                f"[Question:] {question['question']}\n"
                f"[Query:] SELECT"
            )

            input_text_list.append(input_text)

    load_dotenv()
    client = Client(credentials=Credentials.from_env())

    # yields batch of results
    responses = client.text.generation.create(
        model_id=model_id,
        inputs=input_text_list,
        parameters=TextGenerationParameters(
            max_new_tokens=250,
            min_new_tokens=3,
            decoding_method=DecodingMethod.SAMPLE,
            temperature=0.7,
            top_k=50,
            top_p=1,
            return_options=TextGenerationReturnOptions(
                input_text=True,
            ),
        ),
    )

    with open(output_file, "w") as file:
        for response in responses:
            result = response.results[0]
            sql_query = extract_sql(result.generated_text)
            file.write(sql_query.strip() + "\n")

def process_all_perturbations(base_path, perturbed_dir, output_dir, model_id):
    os.makedirs(output_dir, exist_ok=True)

    for percentage in ["25", "50", "75", "100"]:
        questions_file = os.path.join(perturbed_dir, f'perturbation_{percentage}.json')
        output_file = os.path.join(output_dir, f'pred_punctuation_increase_{percentage}.sql')

        print(f"Processing {percentage}% punctuation changes...")
        load_and_process_all(base_path, questions_file, output_file, model_id)
        print(f"Completed {percentage}% punctuation changes.")

if __name__ == "__main__":
    startTime = datetime.now()

    model_id = "meta-llama/llama-3-8b-instruct"
    language = "italian"
    phase = "post-perturbation"
    base_path = "./data/Spider-dev"
    translator = "google_trans"
    perturbation = "punctuation_increase"
    phase = "post_perturbation"

    perturbed_dir = "./data_ibm/new perturbations italian/punctuation_increase"
    output_dir = f"./predictions/Spider-dev/{model_id}/{language}/{translator}/{perturbation}/{phase}"

    process_all_perturbations(base_path, perturbed_dir, output_dir, model_id)

    print("Time:", datetime.now() - startTime)
