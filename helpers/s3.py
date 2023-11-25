import boto3
import json

def create_directory_if_not_exists(s3_client, bucket_name, directory_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=directory_name, Delimiter='/')
    if 'Contents' not in response:
        s3_client.put_object(Bucket=bucket_name, Key=(directory_name + '/'))
        print(f"Created directory {directory_name} in bucket {bucket_name}")
    else:
        print(f"Directory {directory_name} already exists in bucket {bucket_name}")

def upload_file_to_directory(s3_client, bucket_name, directory_name, file_name, file_data):
    file_key = f"{directory_name}/{file_name}"
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_data)
    print(f"Uploaded file to s3://{bucket_name}/{file_key}")

def store_data(file_name, file_data, directory):
    bucket = "cattleiq"
    s3_client = boto3.client('s3')
    create_directory_if_not_exists(s3_client, bucket, directory)
    file_data_converted = Body=bytes(json.dumps(file_data).encode())
    upload_file_to_directory(s3_client, bucket, directory, file_name, file_data_converted)
