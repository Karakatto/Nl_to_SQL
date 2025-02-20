import json
from utils import *
import os
from tqdm.auto import tqdm
from datetime import datetime


def create_consolidated_list_questions(dataPath, perturbation_names, outputFile):

    consolidated_questions = []

    # loop on the list of perturbations
    for perturbation_name in perturbation_names:
        for question_type in ["pre", "post"]:
            questions_path = os.path.join(
                dataPath,
                perturbation_name,
                f"questions_{question_type}_perturbation.json",
            )
            questions = load_json_from_file(questions_path)

            for _, question in enumerate(questions):
                d = {}
                d["perturbation_type"] = perturbation_name
                d["question_type"] = question_type
                db_name = question["db_id"]
                d["db_id"] = db_name
                d["question"] = question["question"]
                d["gold_query"] = question["query"]

                # get the schema path different for the post perturbed question of DB perturbations
                if (question_type == "post") and (
                    perturbation_name
                    in [
                        "DB_schema_synonym",
                        "DB_DBcontent_equivalence",
                        "DB_schema_abbreviation",
                    ]
                ):
                    schema_number = db_name.split("_")[-1]
                    d["schema_path"] = os.path.join(
                        dataPath,
                        perturbation_name,
                        "database_post_perturbation",
                        db_name,
                        f"schema_{schema_number}.sql",
                    )
                else:
                    d["schema_path"] = os.path.join(
                        dataPath, "Spider-dev", "databases", db_name, "schema.sql"
                    )

                consolidated_questions.append(d)

    # get the non-perturbed questions
    questions_path = os.path.join(dataPath, "Spider-dev", "questions.json")
    questions = load_json_from_file(questions_path)

    for _, question in enumerate(questions):
        d = {}
        d["perturbation_type"] = "NO_perturbation"
        d["question_type"] = "pre"
        db_name = question["db_id"]
        d["db_id"] = db_name
        d["question"] = question["question"]
        d["gold_query"] = question["query"]
        d["schema_path"] = os.path.join(
            dataPath, "Spider-dev", "databases", db_name, "schema.sql"
        )
        consolidated_questions.append(d)

    with open(outputFile, "w") as file:
        json.dump(consolidated_questions, file)


if __name__ == "__main__":
    startTime = datetime.now()

    dataPath = "./data"
    perturbation_names = [
        "SQL_comparison",
        "NLQ_keyword_carrier",
        "SQL_DB_text",
        "NLQ_column_carrier",
        "SQL_DB_number",
        "DB_schema_abbreviation",
        "NLQ_multitype",
        "SQL_sort_order",
        "NLQ_others",
        "DB_schema_synonym",
        "SQL_NonDB_number",
        "NLQ_column_synonym",
        "NLQ_column_value",
        "NLQ_column_attribute",
        "NLQ_keyword_synonym",
        "DB_DBcontent_equivalence",
        "NLQ_value_synonym",
    ]
    outputFile = os.path.join(dataPath, "consolidated_list_of_questions.json")

    create_consolidated_list_questions(dataPath, perturbation_names, outputFile)

    print("Time:", datetime.now() - startTime)
