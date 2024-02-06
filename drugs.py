import csv
import json
import xmlrpc.client as xc
import requests
import stringcase
import re
from difflib import SequenceMatcher


def createDrugs(file_name, dosage_form_uuid):

    with open('data/'+file_name, newline="") as csvFile:
        data = list(csv.reader(csvFile))

        for i in range(len(data)):
            name_with_strength = stringcase.lowercase(
                data[i][0]+" "+data[i][1]).title()
            clean_name_with_strength = " ".join(
                name_with_strength.split()).strip()
            name_only = stringcase.lowercase(data[i][0]).title()
            clean_name_only = " ".join(name_only.split()).strip()

            drug_concept = drugConceptExtracter(clean_name_only)
            dosage_form = dosageFormExtracter(clean_name_only)
            dosage_form_uuid = getDosageFormUuid(dosage_form)
            drug_strength = stringcase.lowercase(data[i][1])
            clean_drug_strength = " ".join(drug_strength.split()).strip()

            product_data = odooDrugSearch(
                clean_name_with_strength, drug_concept, dosage_form, clean_drug_strength)
            print(product_data)
            if (product_data):
                with open("data/existing_drugs.txt", "a") as file:
                    file.write(json.dumps(
                        {clean_name_with_strength.strip(): product_data}) + ',' + '\n')

            else:
                # create concept and grab uuid
                createConcept(drug_concept.strip(),
                              dosage_form_uuid, clean_name_with_strength.strip())


def createConcept(concept_name, dosage_form_uuid, drug_name):
    counter = 0
    concept_uuid = conceptExists(concept_name, counter, '')
    if (concept_uuid != None):
        print("concept exists at: "+concept_uuid)
        print("creating drug: "+drug_name)

        createDrug(concept_uuid, drug_name.strip(), dosage_form_uuid)

    else:
        print("Concept doesn't exist, creating new concept")
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

            print(response.json())

            parsed_data = response.json()

            # Extract the UUID from the parsed data
            uuid_value = parsed_data.get('uuid', None)
            print("UUID:", uuid_value)

            # save the uuid and concept name to a file
            with open("data/concepts_log.txt", "a") as file:
                file.write(json.dumps({concept_name: uuid_value}) + ',' + '\n')

            createDrug(uuid_value, drug_name.strip(), dosage_form_uuid)

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

        print("Drug created successfully!")
        print(response.json())

        parsed_data = response.json()

        # Extract the UUID from the parsed data
        uuid_value = parsed_data.get('uuid', None)
        print("UUID:", uuid_value)

        # save the uuid and concept name to a file
        with open("data/new_drugs.txt", "a") as file:
            file.write(json.dumps({drug_name: uuid_value}) + ',' + '\n')

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return response.text
    return "drugs created"


def drugConceptExtracter(drug_string):

    filterWords = r"\b(Tablet|Syrup|Injection|Gel|Injectable|Suppository|Sup|Pfi|Solution|Dilution|Nebuliser|Lotion|Liquid|Susp|Suspension|Effervescent|Oral|Drop|Ointment|Cream|Powder|Flour|Granule|Capsule|Cap|Satchet|Sachet|Eye|Ear|Nose|Nasal|Vaginal|Oral|Rectal|Paste|For|Or|Transdermal|Patch|Implant|Sodf|Spray|Topical|Pellets|Pfol|Chewing Gum|Inhalation|Suppository|Infusion|Concentrate|Neonatal|X-pen|Usp|Ppf|Amp)\b"
    filterPlural = r"\b(Tablets|Syrups|Injections|Susps|Suspensions|Suppositories|Drops|Ointments|Creams|Powders|Granules|Capsules|Caps|Satchets|Sachets|Eyes|Ears)\b"
    filterUnits = r"\b(MgMl|Mg|Ml|Mcg|Inj|G|Iu|McgMl|MgMg|Gm|Mu|U|Micrograms|Hr|HoursMicrograms|Dose)\b"
    filterNumberedUnits = r"\b(\d+MgMl|\d+Mg|\d+Ml|\d+Mcg|\d+Inj|\d+G|\d+Iu|\d+McgMl|\d+MgMg|\d+Gm|\d+I.u)\b"
    filterNonText = r'[^a-zA-Z\s]'
    filterRomanNumerals = r"\b(I|Ii|Iii|Iv|V|Vi|Vii|Viii|Ix|X)\b"
    term = re.sub(filterWords, "", drug_string)
    term1 = re.sub(filterPlural, "", term)
    term2 = re.sub(filterUnits, "", term1)
    term3 = re.sub(filterNumberedUnits, "", term2)

    term4 = re.sub("\(.*?\)", "()", term3)
    term5 = term4.split('+')[0]
    # term4 removes any text after a plus sign, to grab the base concept from a combination
    term6 = re.sub(filterNonText, ' ', term5)
    term7 = re.sub(filterRomanNumerals, '', term6)
    clean_term = " ".join(term7.split())

    print(clean_term)
    return clean_term


def dosageFormExtracter(drug_string):
    dosageForms = [
        'Oral Suspension',
        'Ointment',
        'Cream',
        'Nasal Spray',
        'Gel',
        'Drops',
        'Suppository',
        'Transdermal Patch',
        'Aerosol',
        'Dental Cartridge',
        'Lotion',
        'Implant',
        'Chewing Gum',
        'Nasal Drop',
        'Solution',
        'Oral Liquid',
        'Pellets',
        'Concentrate',
        'Oral Powder',
        'Topical',
        'Ear Drop',
        'Powder',
        'Granules',
        'Oromucosal Solution',
        'Co-pack',
        'Pfi',
        'Pfol',
        'Jelly',
        'Liquid',
        'Suspension',
        'Test Strip',
        'Flour',
        'Diskettes',
        'Sodf',
        'Paste',
        'Spray',
        'Infusion',
        'Tablet',
        'Capsule',
        'Injection',
        'Inhaler',
        'Syrup',
        'Sachet'
    ]
    lowercase_dosage_forms = [word.lower() for word in dosageForms]

    match = ''
    words = drug_string.split()
    # search for words by splitting into group of 2 first
    groups = [words[i] + " " + words[i + 1] for i in range(len(words) - 1)]
    for word in groups:
        if word.replace('(', '').replace(')', '').lower() in lowercase_dosage_forms:
            match = word.replace('(', '').replace(')', '')
            break
        else:
            for word in words:
                # print("searching for"+word)
                if word.replace('(', '').replace(')', '').lower() in lowercase_dosage_forms:
                    match = word.replace('(', '').replace(')', '')
                    break

    print(drug_string+"======>"+match)
    return match


def getDosageFormUuid(dosage_form):
    dosage_plus_id = {}
    with open('data/inserted_dosage_forms.txt') as logs:
        for l in logs:
            a = l.split('":')[0]
            name = a.replace('{"', '').strip()

            b = l.split('":')[1]
            uuid = b.replace('"}', '').replace(
                '"', '').replace(',', '').strip()

            if (name == dosage_form):
                dosage_plus_id[name] = uuid
                print(dosage_plus_id)
                return uuid


def odooDrugSearch(full_string, drug_concept, dosage_form, strength):
    url = "http://100.107.228.96:8069"
    db = "odoo"
    username = 'admin@kasaranihospital.co.ke'
    password = "admin123"

    common = xc.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xc.ServerProxy('{}/xmlrpc/2/object'.format(url))
    search_match = []

    product_data = models.execute_kw(db, uid, password,
                                     'product.template', 'search_read',
                                     [[['name', 'ilike', drug_concept.strip()]]],
                                     {'fields': ['id', 'categ_id', 'name']})
    print(product_data)
    if (len(product_data) > 0):
        print(str(len(product_data))+" Probable match(es) found")
        # print(product_data)
        for i in range(len(product_data)):
            print(product_data[i]['name'])
            result_dosage_form = product_data[i]['categ_id'][1]
            drug_name = product_data[i]['name']
            print(strength.lower())
            if (dosage_form.lower() == result_dosage_form.lower() and strength.lower() in drug_name.lower()):
                result = full_string.replace(",", "").strip()
                result2 = " ".join(result.split())
                similarity_score = SequenceMatcher(
                    None, result2.lower(), drug_name.lower()).ratio()

                print("Match found at ==>"+drug_name)
                print(result2)
                print(similarity_score)
                if (similarity_score >= 0.7):
                    search_match.append(True)
                    if (len(search_match) > 0):
                        print(str(len(search_match))+"found")
                        # if the match contains a + while the search term doesn't
                        # then its a false positive due to a compound drug that
                        # contains the search term.
                        if ('+' in drug_name and '+' not in result2):
                            print("False positive in compound drug")
                            if (len(product_data) == 1):
                                return False

                        else:
                            return True

    else:
        product_data = models.execute_kw(db, uid, password,
                                         'product.template', 'search_read',
                                         [[['name', '=', full_string.strip()]]],
                                         {'fields': ['id', 'categ_id', 'name']})
        if (len(product_data) > 0):
            print('Exact match found')
            return True
        else:
            print("No match found")
            return False


def conceptExists(concept_name, counter, uuid_return_value=''):
    print('searching for concept: '+concept_name)
    url = "https://100.107.228.96/openmrs/ws/rest/v1/concept?q=" + concept_name
    headers = {
        "Authorization": "Basic c3VwZXJtYW46QWRtaW4xMjM=",
        "Content-Type": "application/json;charset=UTF-8",
    }

    try:
        response = requests.get(url, headers=headers,
                                verify=False, allow_redirects=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        parsed_data = response.json()
        print(parsed_data)
        if (parsed_data.get('results', None) == []):
            counter = counter + 1
            if (counter == 2):
                uuid_return_value = None
            else:

                words = concept_name.split(' ')
                words_less_one = len(words)-1
                print(
                    "concept not found: trying the first "+str(words_less_one) + " word(s) of the concept name only")
                search_term = concept_name.rsplit(' ', 1)[0]
                print(search_term)
                uuid_return_value = conceptExists(
                    search_term, counter, uuid_return_value)
        else:
            # Extract the UUID from the parsed data
            results = parsed_data.get('results', None)
            for i in range(len(results)):
                display_name = results[i].get('display')
                uuid_value = results[i].get('uuid')
                if (concept_name == display_name):
                    print("concept found at ==>" + concept_name)
                    uuid_return_value = uuid_value
                    return uuid_return_value

                else:
                    print("Similar concept found, but ignored")
                    return None

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return response.text


def deleteDrugs():
    uuids = []
    with open('data/new_drugs.txt') as logs:
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
