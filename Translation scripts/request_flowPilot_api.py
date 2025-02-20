import requests
import json
from tqdm.auto import tqdm
from datetime import datetime


def request_question_on_data_source(question, dataSourceId, token):
    url = "https://flowpilot.res.ibm.com/api/text2sql"

    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    payload = {
        "messages": [{"content": question, "role": "user"}],
        "dataSourceId": dataSourceId,
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


def query_sql_on_data_source(sql, dataSourceId):
    url = "https://flowpilot.res.ibm.com/api/text2sql"

    headers = {"Authorization": f"Bearer {TOKEN}", "content-type": "application/json"}
    payload = {"sql": sql, "dataSourceId": dataSourceId}

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


def list_all_dataSources(token):
    url = "https://flowpilot.res.ibm.com/api/datasource"

    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    return response.json()


if __name__ == "__main__":
    startTime = datetime.now()

    print("read Token for FlowPilot API")
    f = open("./access/FlowPilot_TOKEN.txt", "r")
    TOKEN = f.readline()

    print("Request the list of public data source information in FlowPilot API")
    dataSources_info = list_all_dataSources(TOKEN)
    available_dataSource_ids = list(set([ds["id"] for ds in dataSources_info]))

    print("The number of unique dataSources is", len(available_dataSource_ids))

    # read the questions data
    with open("./data/questions_list.json") as file:
        questions_data = json.load(file)

    recorder = {}
    for i in tqdm(range(len(questions_data))):

        db_id = "spider_dev_" + questions_data[i]["db_id"]
        if db_id not in recorder.keys():
            recorder[db_id] = {}
        if db_id in available_dataSource_ids:
            
            if questions_data[i]["question"] in recorder[db_id].keys():
                questions_data[i]["query_by_flowpilot_api"] = recorder[db_id][questions_data[i]["question"]]
            else:
                flowpilot_query = request_question_on_data_source(
                    questions_data[i]["question"], db_id, TOKEN
                )["sql"]
                recorder[db_id][questions_data[i]["question"]] = flowpilot_query
                questions_data[i]["query_by_flowpilot_api"] = recorder[db_id][questions_data[i]["question"]]
                
    with open("./data/questions_list_flowpilot", "w") as file:
        json.dump(questions_data, file)

    print("Time:", datetime.now() - startTime)
