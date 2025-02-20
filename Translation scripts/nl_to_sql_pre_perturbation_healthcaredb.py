import json
import os
from tqdm.auto import tqdm
from datetime import datetime
from dotenv import load_dotenv
from genai.client import Client
from genai.credentials import Credentials
from genai.schema import DecodingMethod, TextGenerationParameters, TextGenerationReturnOptions
from utils import load_schema, extract_sql, load_json_from_file

def load_and_process_all(base_path, output_file, model_id):
    questions_path = os.path.join(base_path, "italian_healthcare.json")
    schema_path = os.path.join(base_path, "schema_ita.sql")
    questions = load_json_from_file(questions_path)
    schema = load_schema(schema_path)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    input_text_list = []

    for _, question in tqdm(enumerate(questions), total=len(questions), desc="questions"):
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

if __name__ == "__main__":
    startTime = datetime.now()

    model_id = "meta-llama/llama-3-8b-instruct"
    language = "italian"
    phase = "pre_perturbation"

    base_path = "./data_ibm/healthcare_db/simplified_db/italian/google-translate/italian_db/ita_schema_and_population"
    output_file = f"./predictions/healthcare/{model_id}/{language}/{phase}/pred_preperturbation_itaschema.sql"

    load_and_process_all(base_path, output_file, model_id=model_id)

    print("Time:", datetime.now() - startTime)
