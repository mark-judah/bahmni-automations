from fastapi import FastAPI, Request
from concept_maker import addConcept, addToConceptSet, deleteConcepts
from drugs import createDrugs, deleteDrugs
from non_saleable_item import createNonSaleableItems
from odoo_price_updater import updatePrice
from saleable_item import createSaleableItems

app = FastAPI()

# send any api requests to https or nothing works

@app.post("/new-concept")
async def addConcepts(request: Request):
    file_data = await request.json()
    file_name = file_data['file_name']
    issaleable=file_data['saleable']
    datatype_uuid=file_data['datatype_uuid']
    isset=file_data['set']
    conceptClass=file_data['conceptClass']
    addConcept(file_name,issaleable,datatype_uuid,isset,conceptClass)


@app.post("/add-concept-set-members")
async def addToConceptSets(request: Request):
    data = await request.json()
    concept_uuid = data['concept_uuid']
    file_name = data['file_name']

    addToConceptSet(concept_uuid,file_name)

@app.get("/delete-concepts")
async def deleteConcept():
    deleteConcepts()
    
@app.post("/create-non-saleable-item-odoo")
async def createNonSaleableItem(request: Request):
    file_data = await request.json()
    file_name = file_data['file_name']
    categ_id = file_data['categ_id']

    createNonSaleableItems(file_name,categ_id)

@app.post("/create-saleable-item-odoo")
async def createSaleableItem(request: Request):
    file_data = await request.json()
    file_name = file_data['file_name']
    categ_id = file_data['categ_id']

    createSaleableItems(file_name,categ_id)

@app.post("/update-item-odoo")
async def updateItem(request: Request):
    file_data = await request.json()
    file_name = file_data['file_name']
    updatePrice(file_name)

@app.post("/create-drug")
async def createDrug(request: Request):
    file_data = await request.json()
    file_name = file_data['file_name'] 
    dosage_form_uuid = file_data['dosage_form_uuid']

    createDrugs(file_name,dosage_form_uuid)

@app.get("/delete-drugs")
async def deleteDrug():
    deleteDrugs()