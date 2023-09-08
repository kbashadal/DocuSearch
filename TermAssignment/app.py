import json
import os
import boto3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, ClientError
import ast
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
login_manager = LoginManager()
login_manager.init_app(app)

# Create a boto3 session
session = boto3.Session(
    aws_access_key_id="ASIAXDJRUMVTM4ZGSKAR",
    aws_secret_access_key="qhtX6reSHtqULgpSqytlgpppStlZPYlqgKwPxSiF",
    aws_session_token="FwoGZXIvYXdzEPD//////////wEaDOtktVI1myF98dmPsyLAAdKugC5mp5dYD9dcakes49F6rkvYNb6hxMM/MWZScYDp1RAYNPynR1lnefrwObCgVyYEoDMbZtqso4Z0eQrG9kLIuTBeC1qV4UGxWR9bTxdGiRuToOd6CS0/zZ2MkZ0U/xA2wcmY5vdW5NudxJsIfSiKv8bfQiZAK0wsO98q8FDOXLKq61voo65g4jYcOceFG5HH2yzs2anuEs/RczjlvAPRLov6ZeVo2xmKE0nbF5iQ7KUSk37FZbGhfjjUXYfzSSi/7tyhBjItlns9DMNggG0mCEU5qP7h/gZ6GRH7R4fHekI0m15WRxoMGjvSdSP3u5hPpuA7"
)

# Create a DynamoDB resource
dynamodb = session.resource('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
INDEX_ID = '16408aca-a723-4940-9040-2bd34c2febd2'

# Define the table name
table_name = 'users'
table = dynamodb.Table(table_name)


class User:
    def __init__(self, username, password, active, authenticate):
        self.username = username
        self.password = password
        self.active = active
        self.authenticate = authenticate

    def get_id(self):
        return self.username

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticate


@login_manager.user_loader
def load_user(user_id):
    user_data = table.get_item(Key={'username': user_id})
    try:
        user_data['Item']['active'] = False
        user_data['Item']['authenticate'] = False
        if 'Item' in user_data:
            return User(user_id, user_data['Item']['password'], user_data['Item']['active'],
                        user_data['Item']['authenticate'])
        else:
            return None
    except:
        return None


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if not current_user.is_authenticated and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))


@app.route('/')
def index():
    # show_button = current_user.is_authenticated
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = {'username': username, 'password': password}
        table.put_item(Item=user_data)
        client = session.client('sns', region_name="us-east-1")
        response = client.subscribe(
            TopicArn='arn:aws:sns:us-east-1:488119756134:cloud5409project',
            Protocol='email',
            Endpoint=username,
            ReturnSubscriptionArn=True
        )
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = table.get_item(Key={'username': username})
        if 'Item' in user_data and password == user_data['Item']['password']:
            active = False
            authenticate = False
            user = User(username, password, active, authenticate)
            login_user(user)
            return redirect(url_for('home'))
            # next_page = request.args.get('next')
            # return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        s3 = session.resource('s3')
        file = request.files['file']
        username = current_user.username
        filename = secure_filename(file.filename)
        s3_file_path = f"{username}/{filename}"
        try:
            s3.Bucket('cloud5409projectbucket').put_object(
                Key=f'{current_user.username}/{file.filename}',
                Body=file
            )
        except NoCredentialsError:
            flash('S3 credentials not available')
            return redirect(url_for('home'))

        # Handle file upload logic here
        return redirect(url_for('home'))
    return render_template('upload.html')


@app.route('/view_files')
@login_required
def view_files():
    # Get a list of file names from the S3 bucket
    s3 = session.resource('s3')
    bucket = s3.Bucket("cloud5409projectbucket")
    file_names = []
    for obj in bucket.objects.filter(Prefix=f"{current_user.username}/"):
        file_names.append(obj.key.split('/')[-1])

    return render_template('view_files.html', file_names=file_names)


# @app.route('/search', methods=['GET', 'POST'])
# @login_required
# def search():
#     if request.method == 'POST':
#         query = request.form.get('query')
#         kendra = session.client('kendra', region_name='us-east-1')
#         # query = f'{current_user.username}/{query}'
#         if not query:
#             return render_template('search.html')
#
#         # Search for files in Kendra index
#         try:
#             response = kendra.query(
#                 IndexId=INDEX_ID,
#                 QueryText=query
#             )
#             list_of_docs = []
#             for result in response['ResultItems']:
#                 # str(result["DocumentId"].split("/", 3)[2:][1].split("/")[1])
#                 doc = {
#                     'link': str(result["DocumentId"]),
#                     'title': str(result['DocumentTitle']['Text'])
#                 }
#                 list_of_docs.append(doc)
#             # Render search results template with file URLs
#             return render_template('search_results.html', doc_list=list_of_docs)
#         except ClientError as e:
#             # Handle Kendra errors gracefully
#             return render_template('search.html', error=str(e))
#
#     return render_template('search.html')
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        client = session.client('lambda', region_name="us-east-1")
        username = request.args.get('username')
        query = request.form.get('query')
        payload = {'query': query}
        response = client.invoke(
            FunctionName='arn:aws:lambda:us-east-1:488119756134:function:uploadzip',
            Payload=json.dumps(payload)
        )
        payload = response['Payload'].read().decode('utf-8')
        parsed_response = json.loads(payload)
        print(parsed_response)
        if parsed_response:
            # Render search results template with file URLs
            list_of_docs = ast.literal_eval(parsed_response['body'])
            # list_of_docs = parsed_response['body']

            return render_template('search_results.html', doc_list=list_of_docs)
        # except ClientError as e:
        #     Handle Kendra errors gracefully
        # return render_template('search.html', error=str(e))

    return render_template('search.html')


@app.route('/download', methods=['GET'])
def download():
    # filename = request.args.get('filename')
    # print(filename)
    # bucket_name = filename.split('/')[2]
    # object_key = '/'.join(filename.split('/')[3:])
    # s3 = session.resource('s3')

    # Download the object to local file
    #     s3.Bucket(bucket_name).download_file(object_key, '/Users/sujahidbasha/Downloads/')
    # key = filename.split("/")[-2]
    # filename = filename.split("/", 3)[2:][1].split("/")[1].split('?')[0]
    # print(filename)
    # bucket_name='cloud5409projectbucket'
    #
    # s3 = boto3.client('s3')
    # local_folder = '/Users/sujahidbasha/Desktop/CloudComputin5409/project/downloads/'
    # print("key+'/'+filename",key+'/'+filename)
    # # s3.meta.client.download_file(bucket_name, key+'/'+filename, local_folder)
    # s3.download_file(bucket_name, key+'/'+filename, local_folder + filename)
    # client = boto3.client('lambda', region_name="us-east-1")

    ####working#########
    # client = session.client('lambda', region_name="us-east-1")
    # payload = {'name': 'Alice'}
    # response = client.invoke(
    #     FunctionName='arn:aws:lambda:us-east-1:488119756134:function:cloud5409project',
    #     Payload=json.dumps(payload)
    # )
    # print(response)

    ####to send email####
    # client = session.client('sns', region_name="us-east-1")
    filename = request.args.get('filename')
    #
    username = request.args.get('username')
    # to_email = username
    # subject = 'Subject: File Upload Success'
    # body = "File "+filename+" is uploaded"
    # response = client.publish(
    #     TopicArn='arn:aws:sns:us-east-1:488119756134:cloud5409project',
    #     Message=body,
    #     Subject=subject,
    #     MessageStructure='string',
    #     MessageAttributes={
    #         'email': {
    #             'DataType': 'String',
    #             'StringValue': to_email
    #         }
    #     }
    # )

    ###using api gateway####
    url = 'https://ozn1jgf7vc.execute-api.us-east-1.amazonaws.com/prod/triggermail'
    data = {'filename': filename, 'username': username}
    response = requests.post(url, json=data)
    return jsonify({'message': 'Email Sent successfully!'})


if __name__ == '__main__':
    app.run(debug=True)
