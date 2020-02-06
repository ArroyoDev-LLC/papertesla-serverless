# -*- coding: utf-8 -*-

"""papertesla.data

Helpers for data
"""


import os

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

# Connection Info
TABLES = {
    'products': {
        'table_name': os.environ.get("DB_PRODUCTS"),
    },
    'orders': {
        'table_name': os.environ.get("DB_ORDERS"),
    },
}


class DynamoDB:
    """
    AWS Boto3 DynamoDB
    Handles transactions with database
    """

    def __init__(self, table: str):
        self.client = boto3.client('dynamodb')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = TABLES[table]
        self.hash = self.table.get('primary_key', 'id')
        self.db = self.dynamodb.Table(self.table['table_name'])

    def clean_item(self, item):
        """prepare item for database insertion"""
        clean = item.copy()
        for k, v in item.items():
            if type(v) is str and len(v) <= 0:
                clean.pop(k)
        return clean

    def add_item(self, item):
        """adds item to database"""
        item = self.clean_item(item)
        self.db.put_item(Item=item)
        return item

    def delete_item(self, itemId):
        """deletes item from database"""
        self.db.delete_item(Key={
            self.hash: itemId
        })
        return itemId

    def get_item(self, itemId):
        """retrieves an item from database"""
        try:
            resp = self.db.get_item(Key={
                self.hash: itemId
            })
            return resp.get('Item')
        except ClientError as e:
            print(e)
            return None

    def update_list(self, item, update, append=False, id_key='id', key=None, range_key=None, return_val=None):
        """updates item list attribute"""
        key_val = key or self.hash
        return_val = return_val or "NONE"
        item_id = item.get(id_key)
        up_attr, up_val = update
        up_val = up_val if type(up_val) is list else [up_val]
        update_expr = f":value"
        update_vals = {
            ":value": up_val
        }
        if append:
            update_expr = f"list_append(if_not_exists({up_attr}, :emptyList), :value)"
            update_vals[":emptyList"] = []
        update = {
            "Key": {
                key_val: item_id
            },
            "ReturnValues": return_val,
            "UpdateExpression": f"set {up_attr} = {update_expr}",
            "ExpressionAttributeValues": update_vals
        }
        if range_key:
            update["Key"][range_key[0]] = range_key[1]
        resp = self.db.update_item(**update)
        response = resp.get("Attributes", resp)
        return response

    def query(self, itemId, key=None, range_key=None, index=None, filters=None):
        """queries for item from database"""
        key_val = key or self.hash
        query = {
            "KeyConditionExpression": Key(key_val).eq(itemId),
        }
        if range_key:
            expr = query["KeyConditionExpression"]
            query["KeyConditionExpression"] = expr & Key(
                range_key[0]).eq(range_key[1])
        if index:
            query["IndexName"] = index
        if filters:
            filters = filters if type(filters) is list else [filters]
            init_f = filters[0]
            query["FilterExpression"] = Attr(init_f[0]).eq(init_f[1])
            for f in filters[1:]:
                query["FilterExpression"] = query["FilterExpression"] & Attr(
                    f[0]).eq(f[1])
        try:
            resp = self.db.query(**query)
            return resp.get('Items')
        except ClientError as e:
            print(e)
            return None

    def exists(self, itemId):
        """checks if an item exists in the database"""
        item = self.get_item(itemId)
        return False if item is None else item

    def scan(self, limit=20, next_token=None):
        """scans table with options"""
        if next_token:
            paginator = self.client.get_paginator('scan')
            resp = paginator.paginate(
                TableName=self.table['table_name'],
                PaginationConfig={
                    'MaxItems': limit,
                    'PageSize': limit,
                    'StartingToken': next_token
                }
            )
            return resp['Items']
        resp = self.db.scan(
            Limit=limit
        )
        return resp["Items"]

    def all(self):
        """list all items in the database table"""
        resp = self.db.scan()
        items = resp["Items"]
        return items
