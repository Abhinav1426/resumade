import boto3
from botocore.exceptions import ClientError
from core.config import settings
import time

# --- DynamoDB Client Initialization ---
import os
def get_dynamodb_resource():
    env = os.environ.get("ENV") or "local"
    if env == "local":
        print(f"Connecting to DynamoDB Local at {settings.DYNAMODB_ENDPOINT_URL}")
        return boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or 'fakeMyKeyId',
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or 'fakeSecretAccessKey'
        )
    else:
        print(f"Connecting to AWS DynamoDB in region {settings.AWS_REGION_NAME}")
        return boto3.resource('dynamodb', region_name=settings.AWS_REGION_NAME)

dynamodb_resource = get_dynamodb_resource()

# --- Table Creation Logic ---
def create_users_table_if_not_exists():
    table_name = settings.DYNAMODB_USERS_TABLE_NAME
    try:
        existing_table = dynamodb_resource.Table(table_name)
        existing_table.load() # Check if table exists
        print(f"Users table '{table_name}' already exists.")
        return existing_table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Users table '{table_name}' not found. Creating...")
            table = dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'username', 'AttributeType': 'S'} # For GSI
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'username-index',
                        'KeySchema': [
                            {'AttributeName': 'username', 'KeyType': 'HASH'}
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL' # Or 'KEYS_ONLY' or 'INCLUDE'
                        },
                        'ProvisionedThroughput': { # Ignored for On-Demand capacity
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                BillingMode='PAY_PER_REQUEST' # Or 'PROVISIONED' with ProvisionedThroughput for table
            )
            table.wait_until_exists()
            print(f"Users table '{table_name}' created successfully.")
            return table
        else:
            print(f"Error checking/creating users table: {e}")
            raise

def create_resumes_table_if_not_exists():
    table_name = settings.DYNAMODB_RESUMES_TABLE_NAME
    try:
        existing_table = dynamodb_resource.Table(table_name)
        existing_table.load()
        print(f"Resumes table '{table_name}' already exists.")
        return existing_table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Resumes table '{table_name}' not found. Creating...")
            table = dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'resume_id', 'KeyType': 'RANGE'} # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'resume_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            table.wait_until_exists()
            print(f"Resumes table '{table_name}' created successfully.")
            return table
        else:
            print(f"Error checking/creating resumes table: {e}")
            raise

# Initialize tables (call these at application startup if needed)
# users_table_dynamo = create_users_table_if_not_exists()
# resumes_table_dynamo = create_resumes_table_if_not_exists()

# You can get table objects directly when needed in CRUD
def get_users_table():
    return dynamodb_resource.Table(settings.DYNAMODB_USERS_TABLE_NAME)

def get_resumes_table():
    return dynamodb_resource.Table(settings.DYNAMODB_RESUMES_TABLE_NAME)

def get_metadata_table():
    return dynamodb_resource.Table(settings.DYNAMODB_METADATA_TABLE_NAME)

