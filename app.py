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

@app.route('/db_test')
def db_test():
    secret = get_secret()
    print(secret)
    return "DB Test Successful"

def get_db_connection():
    secret = get_secret()
    connection = pymysql.connect(host="terraform-20260102152553239000000002.chqywueo0dha.ap-south-1.rds.amazonaws.com",  # Replace with your RDS endpoint
                                 db="mydb",   # Replace with your database name
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
    secret = get_secret()
    app.run(debug=True, host='0.0.0.0')

    # print(secret)
    # print("Hello World")