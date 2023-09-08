import boto3

session = boto3.Session(
    aws_access_key_id="ASIAXDJRUMVTPCRIXRWO",
    aws_secret_access_key="u3pL0H4PYlV0AOgwxWVihjgy8TeG1XCNNd1A+crn",
    aws_session_token="FwoGZXIvYXdzENH//////////wEaDMBNjjA/0lg+AXgdWCLAARBCDRMJ8QMd7yc2x6+2wVQQAI8wMWsUig+DDJx7T7xqZnWP4fuz7DO8gST4RbdffB/GabLNllTgruE28u5A6cZQurEmKCUGyvsXcuXjW9iPbSawjJ6UXm0M3UCrw+Qt4KG/qL8xTWeRBkuLEjcfxuRin61pYDLQlIhvb13YYLauxibuwefBsCtiFM0CNVi4KpPT2jOMmwb80kDiJ3+sMnsvXQLtTEgJ7LlOggAXEC5hzVYYi2p8itbgbI4MEV9+gyi/99WhBjIt0azv+nH4FDlBe8K1bNHLtq9fUvmdWZkzcJg2Vt8Ffi5qVpxZWaZIvrjDy8hu"
)


dynamodb = session.resource('dynamodb', region_name='us-east-1')

table = dynamodb.create_table(
    TableName='users',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        }
    ],
    BillingMode='PAY_PER_REQUEST'
)
