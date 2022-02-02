import json
import os
import uuid
import logging
import requests
from src import decimalencoder

import boto3
from botocore.exceptions import ClientError
from src.serialize_json import from_dynamodb_to_json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])


def create_presigned_url_upload(key: str):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('put_object', Params={'Bucket': os.environ['IMAGES_BUCKET'],
                                                                          'Key': key})
        # response = s3_client.generate_presigned_url('put_object', Params={'Bucket': os.environ['IMAGES_BUCKET'],
        #                                                                   'Key': key}, ExpiresIn=120)
    except ClientError as e:
        logging.error(e)
        return None
    return response


def createBlob(event, context):
    if event.get('httpMethod') == "POST":
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
            "body": json.dumps(item)
        }
    else:
        id_uuid = event.get('pathParameters')['id']
        get_item = table.get_item(
            Key={
                'blob_id': id_uuid
            }
        )
        try:
            result = json.dumps(get_item['Item']['labels'],
                                cls=decimalencoder.DecimalEncoder)
        except KeyError:
            return {"statusCode": 404, "body": json.dumps("Not found")}

        response = {"statusCode": 200, "body": result}

    return response


def make_callback(event, context):
    action_db = event['Records'][0]['eventName']
    if action_db == "MODIFY":
        data = from_dynamodb_to_json(event['Records'][0]['dynamodb']['NewImage'])
        callback_url = data['callback_url']
        labels = data['labels']
        requests.post(callback_url, json={"labels": labels})
