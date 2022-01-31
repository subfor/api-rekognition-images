import json
# import requests
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')


def rekognizeImage(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']
    rekognitionClient = boto3.client('rekognition', region_name='eu-west-1')
    response = rekognitionClient.detect_labels(Image={'S3Object': {'Bucket': bucket_name, 'Name': file_name}},
                                               MaxLabels=5)
    labels = [{"label": item['Name'],
               "confidence": item['Confidence'],
               "parents": [parent['Name'] for parent in item['Parents']]
               } for item in response['Labels']]

    table.update_item(
        Key={
            'blob_id': file_name,
        },
        UpdateExpression="set labels = :list",
        ExpressionAttributeValues={
            ':list': f"{labels}"
        },
        ReturnValues="UPDATED_NEW"
    )
    return None
    # table.update_item(
    #     Key={
    #         'blob_id': file_name,
    #     },
    #     UpdateExpression="set labels = :g",
    #     ExpressionAttributeValues={
    #         ':g': labels
    #     },
    #     ReturnValues="UPDATED_NEW"
    # )