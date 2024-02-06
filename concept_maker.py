import json
import csv
import requests
import stringcase
import xlrd


def addConcept(file_name,issaleable,datatype_uuid,isset,conceptClass):
    print(file_name)
    if file_name.endswith('.csv'):
        print("csv file")

        with open('data/'+file_name, newline="") as csvFile:
            data = list(csv.reader(csvFile))
            data_array = []

            for i in range(len(data)):
                data_array.append(data[i][0])
            print(data_array)
            print(len(data_array))
            insertData(data_array,issaleable,datatype_uuid,isset,conceptClass)

    if file_name.endswith('.xls'):
        print('excel file')
        with open('data/'+file_name, newline="") as csvFile:
            workbook = xlrd.open_workbook(file_name)
            worksheet = workbook.sheet_by_name('PDFTables.com')
            data_array = []
            for row_index in range(worksheet.nrows):
                row_data = worksheet.row_values(row_index)
                # print(row_data[0])
                data_array.append(row_data[0])
            print(len(data_array))
            insertData(data_array,issaleable,datatype_uuid,isset,conceptClass)


def insertData(data,issaleable,datatype_uuid,isset,conceptClass):
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
            "datatype": datatype_uuid,
            "set": isset,
            "conceptClass": conceptClass,

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
            with open("data/concepts_log.txt", "a") as file:
                file.write(json.dumps({file_data: uuid_value}) + ',' + '\n')
            # add saleable attribute
            if(issaleable):
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




def deleteConcepts():
    uuids=[]
    with open('data/concepts_log.txt') as logs:
        for l in logs:
            x=l.split('":')[1]
            y=x.split("}")[0].strip().replace('"', '')
            uuids.append(y)
        print(uuids)

        for uuid in uuids:
            url = "https://100.107.228.96/openmrs/ws/rest/v1/concept/"+uuid+"?purge=true"
            headers = {
                "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM="
            }
            
            try:
                response=requests.delete(url, headers=headers,verify=False,allow_redirects=True)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

                print("Concept deleted successfully!")
            except requests.exceptions.RequestException as e:
                    print("Error:", e)
                    return response.text


def addToConceptSet(concept_uuid,file_name):
    uuids=[]
    with open('data/'+file_name) as data:
        for l in data:
            x=l.split('":')[1]
            y=x.split("}")[0].strip().replace('"', '')
            uuids.append(y)
        print(uuids)

        url = "https://100.107.228.96/openmrs/ws/rest/v1/concept/"+concept_uuid
        headers = {
            "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM=",
            "Content-Type": "application/json;charset=UTF-8",
        }
        payload={
            "setMembers":uuids
        }


        try:
            response=requests.post(url, headers=headers, json=payload,verify=False,allow_redirects=True)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            print("Concept created successfully!")
            return response.json()
        except requests.exceptions.RequestException as e:
                print("Error:", e)
                return response.text


