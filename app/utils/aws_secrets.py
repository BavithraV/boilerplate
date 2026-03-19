import json

import boto3


def get_aws_secret(secret_name: str):

    session = boto3.Session()
    client = session.client("secretsmanager", region_name="us-west-2")

    response = client.get_secret_value(SecretId=secret_name)

    secret = json.loads(response["SecretString"])

    return secret
