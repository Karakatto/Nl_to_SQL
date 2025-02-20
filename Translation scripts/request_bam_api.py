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

from utils import load_schema, extract_sql, load_json_from_file


def send_to_bam(consolidated_list_of_questions, model_id):

    input_text_list = []
    schemas = {}

    for _, question_info in tqdm(enumerate(consolidated_list_of_questions), total=len(consolidated_list_of_questions), desc="consolidated_list_of_questions"):

        db_name = question_info["db_id"]
        schema_path = question_info["schema_path"]
        question  = question_info["question"]

        if db_name not in schemas:
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
                f"[Question:] {question}\n"
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
            max_new_tokens=100,
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
    print("======= Responses obtained ==========")

    for i, response in tqdm(enumerate(responses)):
        result = response.results[0]
        sql_query = extract_sql(result.generated_text)

        # remove the "Task:Please" and "```sql" strings from the query
        sql_query = sql_query.split("Task:Please",1)[0].strip().split('```sql', 1)[0].strip().split("```## ",1)[0].strip().split("```",1)[0].strip().split("*/",1)[0].strip()
        consolidated_list_of_questions[i][f"query_by_{model_id}"] = sql_query

    return consolidated_list_of_questions

if __name__ == "__main__":
    startTime = datetime.now()

    model_id = "meta-llama/llama-2-13b-chat"

    with open('./data_ibm/questions_list_granite_meta_1.json') as file:
        consolidated_list_of_questions = json.load(file)

    questions_list = send_to_bam(consolidated_list_of_questions, model_id)

    with open('./data_ibm/questions_list_granite_meta_llama_2.json', "w") as file:
        json.dump(questions_list, file)

    print("Time:", datetime.now() - startTime)


# models to consider: 
# "meta-llama/llama-3-8b-instruct",
#                     "ibm/granite-20b-code-instruct"
#                     "ibm/granite-20b-sql-supply-chain" (flowpilot)
#                     "meta-llama/llama-3-70b-instruct"
#                     "meta-llama/llama-2-13b-chat"