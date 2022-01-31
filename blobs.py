import json
import os
import uuid
import logging
import requests

import boto3
from botocore.exceptions import ClientError
from serialize_json import from_dynamodb_to_json
dynamodb = boto3.resource('dynamodb')


def create_presigned_url_upload(key: str):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('put_object', Params={'Bucket': 'images-recognition234234zcz3',
                                                                          'Key': key}, ExpiresIn=120)
    except ClientError as e:
        logging.error(e)
        return None
    return response


def createBlob(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    blob_id = str(uuid.uuid1())
    upload_url = create_presigned_url_upload(blob_id)
    callback_url = json.loads(event['body'])['callback_url']
    item = {
        'blob_id': blob_id,
        'callback_url': callback_url,
        'upload_url': upload_url,
    }
    table.put_item(Item=item)
    response = {
        "statusCode": 201,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(item)
    }

    return response


def make_callback(event, context):
    action_db = event['Records'][0]['eventName']
    if action_db == "MODIFY":
        data = from_dynamodb_to_json(event['Records'][0]['dynamodb']['NewImage'])
        # d = from_dynamodb_to_json(data)
        callback_url = data['callback_url']
        labels = data['labels']
        requests.post(callback_url, json={"data": labels})

# def make_callback(event, context):
#     action_db = event['Records'][0]['eventName']
#     if action_db == "MODIFY":
#         data = event['Records'][0]['dynamodb']['NewImage']
#         d = data['labels']['L']
#         callback_url = data['callback_url']['S']
#         # labels = data['labels']['S']
#         requests.post(callback_url, json={"data": d})