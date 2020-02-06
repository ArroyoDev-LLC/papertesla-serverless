# -*- coding: utf-8 -*-

"""Paper Tesla Store

Paper Tesla Serverless Api Store Handler
"""

import json


def handler(event, context):
    print("Lambda called!")
    print(event)
    print(context.__dict__)
    resp = {
        'statusCode': 200,
        'body': json.dumps({
            "message": "Success!"
        })
    }

    return resp
