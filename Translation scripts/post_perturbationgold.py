import json
import os

from tqdm.auto import tqdm

from datetime import datetime

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import DecodingMethod, LengthPenalty, ModerationHAP, ModerationHAPOutput, ModerationParameters
from genai.schema import TextGenerationParameters, TextGenerationReturnOptions
from genai.text.generation import CreateExecutionOptions

from utils import load_schema, extract_sql, load_json_from_file, load_all_schemas


def process_perturbations(databases_path, perturbation_folders, model_id):
    perturbations_list = sorted(
        [p for p in perturbation_folders if not p.startswith("Spider-dev") and not p.startswith("DB_")],
        key=str.casefold,
    )

    schemas = load_all_schemas(databases_path=databases_path)

    for perturbation in perturbations_list:

        print("perturbation:", perturbation)

        for phase in ["post"]:

            print("phase:", phase)

            input_text_list = []

            questions_file = os.path.join(base_path, "data", perturbation, f"questions_{phase}_perturbation.json")
            questions = load_json_from_file(questions_file)

            for question in questions:

                db_name = question["db_id"]

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
                else:
                    raise ValueError

            if len(input_text_list) > 0:
                load_dotenv()
                client = Client(credentials=Credentials.from_env())

                # yields batch of results
                responses = client.text.generation.create(
                    model_id=model_id,
                    inputs=input_text_list,
                    parameters=TextGenerationParameters(
                        max_new_tokens=25,
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

                output_directory = os.path.join(base_path, "predictions", perturbation, model_id, phase)
                os.makedirs(output_directory, exist_ok=True)
                output_file = os.path.join(output_directory, f"{phase}_pred.sql")

                with open(output_file, "w") as file:
                    for i, response in enumerate(responses):
                        result = response.results[0]
                        sql_query = extract_sql(result.generated_text)
                        file.write(sql_query.strip() + "\n")


if __name__ == "__main__":
    startTime = datetime.now()

    model_id = "meta-llama/llama-3-8b-instruct"

    base_path = "./"
    output_file = f"./predictions/Spider-dev/predictions/{model_id}/pred.sql"

    perturbation_folders = os.listdir(os.path.join(base_path, "data"))
    database_path = os.path.join(os.path.join(base_path, "data", "Spider-dev", "databases"))

    process_perturbations(database_path, perturbation_folders, model_id=model_id)

    print("Time:", datetime.now() - startTime)
