import csv
import json
import xmlrpc.client as xc
import requests
import stringcase
import re

# check if product exists in odoo

# if false, create concept and grab uuid

# create drug and pass name, concept uuid, dosage form and strength

# if product exists, add to existing drugs.csv


def createDrugs(file_name, dosage_form, dosage_form_uuid):

    url = "http://100.107.228.96:8069"
    db = "odoo"
    username = 'admin@kasaranihospital.co.ke'
    password = "admin123"

    common = xc.ServerProxy('{}/xmlrpc/2/common'.format(url))
    print(common.version())

    uid = common.authenticate(db, username, password, {})
    print(uid)
    models = xc.ServerProxy('{}/xmlrpc/2/object'.format(url))

    with open(file_name, newline="") as csvFile:
        data = list(csv.reader(csvFile))

        for i in range(len(data)):
            full_name = stringcase.lowercase(data[i][0]).title()
            lwc_dosage_form = stringcase.lowercase(dosage_form).title()
            # search_term=full_name.replace(lwc_dosage_form,'').replace(lwc_dosage_form+'s','')
            pattern = f"(?i){lwc_dosage_form}(.*)"
            term = re.sub(pattern, "", full_name)
            term2 = re.sub(r'[^a-zA-Z\s]', '', term)
            pattern2 = r"\b(MgMl|Mg|Ml|Mcg|Inj|G|Iu|McgMl|MgMg|Gm)\b"
            term3 = re.sub(pattern2, "", term2)+lwc_dosage_form
            term4 = term3.replace('/', ' & ')
            clean_term = " ".join(term4.split())

            print(clean_term)
            product_data = models.execute_kw(db, uid, password,
                                             'product.template', 'search_read',
                                             [[['name', 'ilike', clean_term.strip()]]],
                                             {'fields': ['id'], 'limit': 10})
            print(product_data)
            if (len(product_data) > 0):
                with open("existing_drugs.txt", "a") as file:
                    file.write(json.dumps(
                        {clean_term.strip(): product_data}) + ',' + '\n')
            else:
                # create concept and grab uuid
                createConcept(clean_term.strip(),
                              dosage_form_uuid, full_name.strip())


def createConcept(concept_name, dosage_form_uuid, drug_name):
    concept_uuid = conceptExists(concept_name)
    if (concept_uuid != None):
        print("concept exists: "+concept_uuid)
        createDrug(concept_uuid, drug_name, dosage_form_uuid)

    else:
        url = "https://100.107.228.96/openmrs/ws/rest/v1/concept"
        headers = {
            "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM=",
            "Content-Type": "application/json;charset=UTF-8",
        }
        api_data = {
            "names": [
                {
                    "name": concept_name,
                    "locale": "en",
                    "localePreferred": True,
                    "conceptNameType": "FULLY_SPECIFIED"
                }
            ],
            "datatype": "8d4a4c94-c2cc-11de-8d13-0010c6dffd0f",
            "set": False,
            "conceptClass": "Drug",
        }

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
                file.write(json.dumps({concept_name: uuid_value}) + ',' + '\n')

            createDrug(uuid_value, drug_name, dosage_form_uuid)

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return response.text
        return "concepts created"


def createDrug(concept_uuid, drug_name, dosage_form_uuid):
    url = "https://100.107.228.96/openmrs/ws/rest/v1/drug"
    headers = {
        "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM=",
        "Content-Type": "application/json;charset=UTF-8",
    }
    api_data = {
        "concept": concept_uuid,
        "combination": False,
        "name": drug_name,
        "minimumDailyDose": None,
        "maximumDailyDose": None,
        "dosageForm": dosage_form_uuid
    }

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
        with open("new_drugs.txt", "a") as file:
            file.write(json.dumps({drug_name: uuid_value}) + ',' + '\n')

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return response.text
    return "drugs created"


def deleteDrugs():
    uuids = []
    with open('new_drugs.txt') as logs:
        for l in logs:
            x = l.split('":')[1]
            y = x.split("}")[0].strip().replace('"', '')
            uuids.append(y)
        print(uuids)

        for uuid in uuids:
            url = "https://100.107.228.96/openmrs/ws/rest/v1/drug/"+uuid+"?purge=true"
            headers = {
                "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM="
            }

            try:
                response = requests.delete(
                    url, headers=headers, verify=False, allow_redirects=True)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

                print("Concept deleted successfully!")
            except requests.exceptions.RequestException as e:
                print("Error:", e)
                return response.text


def conceptExists(concept_name):
    url = "https://100.107.228.96/openmrs/ws/rest/v1/concept?q="+concept_name
    headers = {
        "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM=",
        "Content-Type": "application/json;charset=UTF-8",
    }

    try:
        response = requests.get(
            url, headers=headers, verify=False, allow_redirects=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        print(response.json())

        parsed_data = response.json()
        if (parsed_data.get('results', None) == []):
            return None
        else:
            # Extract the UUID from the parsed data
            uuid_value = parsed_data.get('results', None)[0].get('uuid', None)

            if (uuid_value != None):
                return uuid_value
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return response.text
