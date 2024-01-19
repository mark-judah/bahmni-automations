import base64
import json
import subprocess
from fastapi import FastAPI, Request
import csv
import requests
import stringcase
import xlrd
from concept_set_maker import addConceptSet
from odoo_price_updater import updatePrice

app = FastAPI()

# send any api requests to https or nothing works


@app.post("/new-concept")
async def addConcept(request: Request):
    file_data = await request.json()
    file_name = file_data['file_name']
    print(file_name)
    if file_name.endswith('.csv'):
        print("csv file")

        with open(file_name, newline="") as csvFile:
            data = list(csv.reader(csvFile))
            data_array = []

            for i in range(len(data)):
                data_array.append(data[i][0])
            print(data_array)
            print(len(data_array))
            insertData(data_array)

    if file_name.endswith('.xls'):
        print('excel file')
        with open(file_name, newline="") as csvFile:
            workbook = xlrd.open_workbook(file_name)
            worksheet = workbook.sheet_by_name('PDFTables.com')
            data_array = []
            for row_index in range(worksheet.nrows):
                row_data = worksheet.row_values(row_index)
                # print(row_data[0])
                data_array.append(row_data[0])
            print(len(data_array))
            insertData(data_array)


def insertData(data):
    for i in range(len(data)):
        try:
            file_data = stringcase.lowercase(data[i]).title()
            print("###############"+file_data)
        except KeyError as e:
            print(f"KeyError: {e}")

        url = "https://100.107.228.96/openmrs/ws/rest/v1/concept"
        headers = {
            "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM=",
            "Content-Type": "application/json;charset=UTF-8",
        }
        api_data = {
            "names": [
                {
                    "name": file_data,
                    "locale": "en",
                    "localePreferred": True,
                    "conceptNameType": "FULLY_SPECIFIED"
                }
            ],
            "datatype": "8d4a5cca-c2cc-11de-8d13-0010c6dffd0f",
            "set": False,
            "conceptClass": "Services",

        }

        # content_length = len(json.dumps(data))
        # headers["Content-Length"] = str(content_length)
        try:
            response = requests.post(
                url, headers=headers, json=api_data, verify=False, allow_redirects=True)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            print("Concept created successfully!")
            print(response.json())

            parsed_data = response.json()

            # Extract the UUID from the parsed data
            uuid_value = parsed_data.get('uuid', None)
            print("UUID:", uuid_value)

            # save the uuid and concept name to a file
            with open("concepts_log.txt", "a") as file:
                file.write(json.dumps({file_data: uuid_value}) + ',' + '\n')
            # add saleable attribute
            addSaleable(uuid_value, headers)

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return response.text
    return "concepts created"


def addSaleable(uuid, headers):
    print("Adding saleable")
    url = "https://100.107.228.96/openmrs/ws/rest/v1/concept/"+uuid+"/attribute"

    saleable = {
        "attributeType": "f0f69334-f0cf-11ed-81e5-0242ac120006",
        "value": True
    }

    try:
        response = requests.post(
            url, headers=headers, json=saleable, verify=False, allow_redirects=True)
        response.raise_for_status()

        print("Attribute added successfully!")
        return response.json()

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return response.text


@app.post("/add-concept-set-members")
async def updateConcept(request: Request):
    data = await request.json()
    concept_uuid = data['concept_uuid']
    addConceptSet(concept_uuid)


@app.post("/update-item-odoo")
async def updateItem(request: Request):
    file_data = await request.json()
    file_name = file_data['file_name']
    updatePrice(file_name)
