import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')


def rekognizeImage(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = event['Records'][0]['s3']['object']['key']
    rekognitionClient = boto3.client('rekognition', region_name=os.environ['REGION_NAME'])
    response = rekognitionClient.detect_labels(Image={'S3Object': {'Bucket': bucket_name, 'Name': file_name}},
                                               MaxLabels=5)
    labels = [{"label": item['Name'],
               "confidence": Decimal(item['Confidence']),
               "parents": [parent['Name'] for parent in item['Parents']]
               } for item in response['Labels']]

    table.update_item(
        Key={
            'blob_id': file_name,
        },
        UpdateExpression="set labels = :list",
        ExpressionAttributeValues={
            ':list': labels
        },
        ReturnValues="UPDATED_NEW"
    )
