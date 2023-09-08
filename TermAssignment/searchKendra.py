import json
import os
import boto3
from flask import Flask, render_template, request, redirect, url_for,flash
from flask_login import LoginManager, login_user, login_required,current_user, logout_user
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, ClientError

def lambda_handler(event, context):
    session = boto3.Session(
        aws_access_key_id="ASIAXDJRUMVTM4ZGSKAR",
        aws_secret_access_key="qhtX6reSHtqULgpSqytlgpppStlZPYlqgKwPxSiF",
        aws_session_token="FwoGZXIvYXdzEPD//////////wEaDOtktVI1myF98dmPsyLAAdKugC5mp5dYD9dcakes49F6rkvYNb6hxMM/MWZScYDp1RAYNPynR1lnefrwObCgVyYEoDMbZtqso4Z0eQrG9kLIuTBeC1qV4UGxWR9bTxdGiRuToOd6CS0/zZ2MkZ0U/xA2wcmY5vdW5NudxJsIfSiKv8bfQiZAK0wsO98q8FDOXLKq61voo65g4jYcOceFG5HH2yzs2anuEs/RczjlvAPRLov6ZeVo2xmKE0nbF5iQ7KUSk37FZbGhfjjUXYfzSSi/7tyhBjItlns9DMNggG0mCEU5qP7h/gZ6GRH7R4fHekI0m15WRxoMGjvSdSP3u5hPpuA7"
    )
    query = event['query']
    kendra = session.client('kendra', region_name='us-east-1')
    INDEX_ID = '16408aca-a723-4940-9040-2bd34c2febd2'
    try:
        response = kendra.query(IndexId=INDEX_ID,QueryText=query)
        list_of_docs = []
        for result in response['ResultItems']:
            # str(result["DocumentId"].split("/", 3)[2:][1].split("/")[1])
            doc = {
                'link': str(result["DocumentId"]),
                'title': str(result['DocumentTitle']['Text'])
            }
            list_of_docs.append(doc)
        import pprint; pprint.pprint(list_of_docs)
    except ClientError as e:
        raise e
    # TODO implement
    return {
        'statusCode': 200,
        'body': f'{list_of_docs}'
    }
