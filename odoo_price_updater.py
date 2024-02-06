import csv
import json
import re
import xmlrpc.client as xc
from fastapi import FastAPI, Request
import requests
import stringcase


def updatePrice(file_name):
    url = "http://100.107.228.96:8069"
    db = "odoo"
    username = 'admin@kasaranihospital.co.ke'
    password = "admin123"

    common = xc.ServerProxy('{}/xmlrpc/2/common'.format(url))
    print(common.version())

    uid = common.authenticate(db, username, password, {})
    print(uid)
    models = xc.ServerProxy('{}/xmlrpc/2/object'.format(url))

    with open('data/'+file_name, newline="") as csvFile:
        data = list(csv.reader(csvFile))

        for i in range(len(data)):
            string_one = stringcase.lowercase(data[i][0]).title()
            string_two = stringcase.lowercase(data[i][1]).title()
            file_data=string_one+string_two
            clean_string = " ".join(file_data.split())

            print(file_data)
            product_data = models.execute_kw(db, uid, password,
                                             'product.template', 'search_read',
                                             [[['name', 'like', clean_string]]],
                                             {'fields': ['id'], 'limit': 1})
            print(product_data)
            product_tmpl_id = product_data[0].get('id')
            print(product_tmpl_id)
            print(data[i][2])

            result = models.execute_kw(db, uid, password, 'product.template', 'write', [[product_tmpl_id], {
                'list_price': data[i][2]
            }])
            print(result)


