# -*- coding: utf-8 -*-

"""Paper Tesla API

Paper Tesla Serverless Api
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
