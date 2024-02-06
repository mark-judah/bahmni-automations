import csv
import json
import xmlrpc.client as xc
from fastapi import FastAPI, Request
import requests
import stringcase


def createNonSaleableItems(file_name,categ_id):
    url = 'http://100.107.228.96:8069'
    db = 'odoo'
    username = 'admin@kasaranihospital.co.ke'
    password = 'admin123'

    common = xc.ServerProxy('{}/xmlrpc/2/common'.format(url))
    print(common.version())

    uid = common.authenticate(db, username, password, {})
    print(uid)
    models = xc.ServerProxy('{}/xmlrpc/2/object'.format(url))

    with open('data/'+file_name, newline='') as csvFile:
        data = list(csv.reader(csvFile))
      
        for i in range(len(data)):
            file_data = stringcase.lowercase(data[i][0]).title()
            print(file_data)
            product_data = models.execute_kw(db, uid, password, 'product.template', 'create', [{
                'sale_ok': False,
                'purchase_ok': True,
                'company_id': '1',
                'uom_po_id': '1',
                'active': True,
                'categ_id': categ_id,
                'name': file_data.strip(),
                'rental': False,
                'type': 'product',
                'sale_line_warn': 'no-message',
                'track_service': 'manual',
                'invoice_policy': 'order',
                'expense_policy': 'no',
                'tracking': 'none',
                'sale_delay': '0',
                'mrp': '0',
                'to_weight': False,
                'available_in_pos': False,
                'purchase_method': 'receive',
                'purchase_line_warn': 'no-message'
            }])
            print(product_data)
            product_tmpl_id = product_data
            print(product_tmpl_id)
            print(data[i][1])

            result = models.execute_kw(db, uid, password, 'product.template', 'write', [[product_tmpl_id], {
                'list_price': 0.00
            }])
            print(result)
