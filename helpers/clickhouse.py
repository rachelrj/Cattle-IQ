import clickhouse_connect
import subprocess
import json
import boto3
from botocore.exceptions import ClientError
import certifi
import os
import time
from .error_email import send_error_email

def set_credentials():
    os.environ['SSL_CERT_FILE'] = certifi.where()

    secret_name = "clickhouse"
    region_name = "us-east-1"

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

    secret = json.loads(get_secret_value_response['SecretString'])
    host = secret['host']
    port = secret['port']
    username = secret['username']
    password = secret['password']
    secure = False

    client = clickhouse_connect.get_client(host=host, port=port, username=username, password=password, connect_timeout=30, secure=True)

    return client

def count_active_queries(client):
    active_queries = client.query("SELECT * FROM system.processes")

    rows = active_queries.result_rows
    number_of_rows = len(rows)
    print("Number of rows:", number_of_rows)

    return number_of_rows

def wait_for_available_slots(max_active_queries, client):
    while count_active_queries(client) >= max_active_queries:
        print("Waiting for available query slots...")
        time.sleep(5)

def identify_data_key(report_data):
    for key, value in report_data.items():
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            return key
    return None

def format_sql_value(value):
    if value is None:
        return "NULL"
    elif isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"  # Replace single quotes with two single quotes for SQL
    else:
        return str(value)

def format_record_for_sql(record):
    formatted_values = [format_sql_value(record[col]) for col in record_columns]
    return '(' + ', '.join(formatted_values) + ')'

batch_size = 1000

record_columns = [
'report_date',
'office_name',
'office_state',
'office_city',
'office_code',
'market_type',
'market_type_category',
'market_location_name',
'market_location_state',
'market_location_city',
'slug_id',
'slug_name',
'report_title',
'category',
'commodity',
'cattle_class',
'freight',
'price_unit',
'age',
'pregnancy_stage',
'head_count',
'avg_weight',
'avg_price',
'market_id',
'unique_hash',
'weight_range',
'insert_date',
'seller',
'buyer',
'breed'
]


def insert_batches(normalized_records, auction_name, date):
    try:
        records_to_add = []
        client = set_credentials()
        for record in normalized_records:
            records_to_add.append(record)
            if len(records_to_add) == batch_size:
                wait_for_available_slots(10, client)
                inserted_records = client.insert('transactions', records_to_add, column_names=record_columns)
                print(inserted_records)
                records_to_add.clear()
        if records_to_add:
            wait_for_available_slots(10, client)
            inserted_records = client.insert('transactions', records_to_add, column_names=record_columns)
            print(inserted_records)
            records_to_add.clear()
    except Exception as e:
        message = f"Failed to insert records for: {auction_name} on {date}"
        # send_error_email(message)
        print(message)
        print(e)
        
