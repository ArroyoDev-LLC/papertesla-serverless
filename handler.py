# -*- coding: utf-8 -*-

"""Paper Tesla API

Paper Tesla Serverless Api
"""


def handler(event, context):
    print("Lambda called!")
    print(event)
    print(context.__dict__)

    return {
        'status': 200,
        'message': "success!"
    }
