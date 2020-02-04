# -*- coding: utf-8 -*-

"""Paper Tesla API

Paper Tesla Serverless Api
"""


def handler(event, context):
    print(event)
    print(context.__dict__)

    field = event['field']
    args = event['args']

    return {
        'status': 200,
        'message': "success!"
    }
