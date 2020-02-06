# -*- coding: utf-8 -*-

"""Paper Tesla Store

Paper Tesla Serverless Api Store Handler
"""

import simplejson as json

from papertesla import data


def get_products(event, context):
    products = data.DynamoDB('products')
    resp = {
        'statusCode': 200,
        'body': json.dumps(products.all())
    }
    return resp


def handler(event, context):
    print("Lambda called!\n")
    print(event)
    print("\n")
    print("Context:")
    print(context.__dict__)

    return None
