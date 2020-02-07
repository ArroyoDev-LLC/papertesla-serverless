# -*- coding: utf-8 -*-

"""Paper Tesla Store

Paper Tesla Serverless Api Store Handler
"""

# decompress zipped lambda requirements
try:
    import unzip_requirements  # noqa
except ImportError:
    pass

import uuid
from typing import Optional, Union

import simplejson as json

from papertesla import data


def http_response(data: dict, status_code: Union[str, int] = '200') -> dict:
    """return http response

    Args:
        data: object to return.
        status_code: HTTP status code.
            Defaults to '200'.
    """
    resp = {
        'statusCode': str(status_code),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'papertesla.com'
        },
        'body': json.dumps(data)
    }
    return resp


def find_product(model: str, size: str) -> Optional[dict]:
    """Find product item by model and size

    Args:
        model: model name
        size: model size

    Returns:
        product item
    """
    size_filter = ("size", size)
    products = data.DynamoDB('products')
    product = iter(products.query(
        model,
        key="model",
        index="model-index",
        filters=size_filter))
    return next(product, None)


def get_products(event: dict, context: dict) -> dict:
    """Fetch all products from database

    Args:
        event: lambda event
        context: lambda context

    Returns:
        http response object
    """
    products = data.DynamoDB('products')
    return http_response(products.all())


def create_order(event: dict, context: dict) -> dict:
    """Creates order item

    Args:
        event: lambda event
        context: lambda context

    Returns:
        http response object
    """
    req = json.loads(event.get('body', ''))
    order = req.get('order')

    options = order['options']
    opts_complete = options.copy()
    size = options.pop('size')

    product = find_product(order['model'], size)

    if not product:
        return http_response({
            'error': "product not found!"
        }, status_code=400)

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
    return http_response(order_obj)
