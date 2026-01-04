from flask import Flask, jsonify, render_template, request
import pymysql
import json

app = Flask(__name__)

import boto3
from botocore.exceptions import ClientError


def get_secret():
    secret_name = "rds!db-ceaf6479-81a7-41e9-b5e5-a3c348c391f8" # Replace the Secret Name
    region_name = "ap-south-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# def get_db_config():
#     client = boto3.client('secretsmanager', region_name='ap-south-1')

#     response = client.get_secret_value(
#         SecretId='mysql-db-metadata'
#     )

#     db_config = json.loads(response['SecretString'])
#     return db_config

def get_parameter(name):
    ssm = boto3.client("ssm", region_name='ap-south-1')

    response = ssm.get_parameter(
        Name=name,
        WithDecryption=True
    )
    print(response)
    value = response["Parameter"]["Value"]
    return json.loads(value)

@app.route('/db_test')
def db_test():
    ssm = boto3.client("ssm", region_name='ap-south-1')
    response = ssm.get_parameter(
        Name="/db/mysql/db_name",
        WithDecryption=True
    )
    print(response)
    return "DB Test Successful"

def get_db_connection():
    secret = get_secret()
    db_config = get_db_config()
    connection = pymysql.connect(host="abc",  # Replace with your RDS endpoint
                                 db="abc",   # Replace with your database name
                                 user=secret["username"],      
                                 password=secret["password"],  
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

@app.route('/health')
def health():
    return "Up & Running"

@app.route('/create_table')
def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS example_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """
    cursor.execute(create_table_query)
    connection.commit()
    connection.close()
    return "Table created successfully"

@app.route('/insert_record', methods=['POST'])
def insert_record():
    name = request.json['name']
    connection = get_db_connection()
    cursor = connection.cursor()
    insert_query = "INSERT INTO example_table (name) VALUES (%s)"
    cursor.execute(insert_query, (name,))
    connection.commit()
    connection.close()
    return "Record inserted successfully"

@app.route('/data')
def data():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM example_table')
    result = cursor.fetchall()
    connection.close()
    return jsonify(result)

# UI route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0')

    # print(secret)
    # print("Hello World")