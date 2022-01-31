from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


def from_dynamodb_to_json(item):
    d = TypeDeserializer()
    return {k: d.deserialize(value=v) for k, v in item.items()}
