# -*- coding: utf-8 -*-

"""Paper Tesla Store

Paper Tesla Serverless Api Store Handler
"""

import uuid

import simplejson as json

from papertesla import data


def find_product(model, size):
    size_filter = ("size", size)
    products = data.DynamoDB('products')
    product = iter(products.query(
        model,
        key="model",
        index="model-index",
        filters=size_filter))
    return next(product, None)


def get_products(event, context):
    products = data.DynamoDB('products')
    resp = {
        'statusCode': 200,
        'body': json.dumps(products.all())
    }
    return resp


def create_order(event, context):
    req = json.loads(event.get('body'))
    order = req.get('order')

    options = order['options']
    opts_complete = options.copy()
    size = options.pop('size')

    product = find_product(order['model'], size)

    # grab prices for each selected addon
    addons = [k for k, v in options.items() if v]
    prices = [v for k, v in product['pricing'].items() if k in addons]
    # append base price
    prices.append(product['pricing']['base'])
    # add it all up
    total_price = sum(prices)

    # unverified order request
    order_obj = {
        'id': str(uuid.uuid4()),
        'email': 'example@example.com',
        'completed': False,
        'order': {
            'productId': product['id'],
            'options': opts_complete,
            'pricing': {
                'retail': total_price
            }
        }
    }

    # add it to table
    orders = data.DynamoDB('orders')
    orders.add_item(order_obj)

    # respond
    resp = {
        'statusCode': 200,
        'body': json.dumps(order_obj)
    }
    return resp
