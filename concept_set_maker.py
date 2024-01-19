import json
from fastapi import FastAPI, Request
import requests


def addConceptSet(concept_uuid):
    uuids=[]
    data=[]
    with open('concepts_log.txt') as logs:
        for l in logs:
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

