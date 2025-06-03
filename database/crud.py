import uuid
from typing import List, Optional, Dict, Any
from botocore.exceptions import ClientError

from database.dynamodb_client import get_users_table, get_resumes_table, get_metadata_table
from database.model import (
    UserCreate, UserInDB, ResumeCreate, ResumeUpdate, ResumeInDB, now_iso
)
from utils import auth


# --- User CRUD with DynamoDB ---
async def create_user(user_data: UserCreate) -> Optional[UserInDB]:
    users_table = get_users_table()

    # Check if username already exists using GSI
    existing_user_by_username = await get_user_by_username(user_data.username)
    if existing_user_by_username:
        raise ValueError(f"Username '{user_data.username}' already exists.")

    # Optionally, check for email existence if you have a GSI for email or accept slower scans for this check
    # For simplicity, we'll skip a direct email existence check here unless a GSI is on email.

    hashed_password = auth.get_password_hash(user_data.password)
    user_id = str(uuid.uuid4())
    timestamp = now_iso()

    user_item = UserInDB(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        disabled=False,
        created_at=timestamp,
        updated_at=timestamp
    )

    try:
        users_table.put_item(
            Item=user_item.model_dump(),
            ConditionExpression='attribute_not_exists(user_id)'  # Ensures this user_id is new
        )
        return user_item
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # This specific check might be redundant if user_id is always new UUID
            print(f"User item with user_id {user_id} already exists (race condition or UUID collision).")
        else:
            print(f"Error creating user in DynamoDB: {e}")
        return None


async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    users_table = get_users_table()
    try:
        response = users_table.get_item(Key={'user_id': user_id})
        item = response.get('Item')
        return UserInDB(**item) if item else None
    except ClientError as e:
        print(f"Error getting user by ID {user_id} from DynamoDB: {e}")
        return None


async def get_user_by_username(username: str) -> Optional[UserInDB]:
    users_table = get_users_table()
    try:
        response = users_table.query(
            IndexName='username-index',  # Use the GSI
            KeyConditionExpression='username = :username_val',
            ExpressionAttributeValues={':username_val': username}
        )
        items = response.get('Items')
        if items:
            return UserInDB(**items[0])  # Username should be unique
        return None
    except ClientError as e:
        print(f"Error getting user by username '{username}' from DynamoDB: {e}")
        return None


async def get_all_users_name_email() -> dict:
    users_table = get_users_table()
    try:
        response = users_table.scan(ProjectionExpression="user_id, full_name, email")
        items = response.get('Items', [])
        users = [
            {"user_id": item.get("user_id", ""), "name": item.get("full_name", ""), "email": item.get("email", "")}
            for item in items if item.get("email")
        ]
        total_count = response.get('Count', len(items))
        return {"count": total_count, "users": users}
    except ClientError as e:
        print(f"Error scanning users table: {e}")
        return {"count": 0, "users": []}


# --- Resume CRUD with DynamoDB ---
async def create_resume(user_id: str, resume_in: ResumeCreate) -> Optional[ResumeInDB]:
    resumes_table = get_resumes_table()
    resume_id = str(uuid.uuid4())
    timestamp = now_iso()

    # model_dump(by_alias=True) is important for fields with aliases
    resume_data_dict = resume_in.resume_data.model_dump(mode="json", by_alias=True)

    resume_item = ResumeInDB(
        user_id=user_id,
        resume_id=resume_id,
        title=resume_in.title,
        resume_data=resume_data_dict,  # Pydantic model_dump handles complex objects to dict
        created_at=timestamp,
        updated_at=timestamp
    )

    try:
        resumes_table.put_item(Item=resume_item.model_dump())
        return resume_item
    except ClientError as e:
        print(f"Error creating resume in DynamoDB: {e}")
        return None


async def get_resume_by_id(user_id: str, resume_id: str) -> Optional[ResumeInDB]:
    resumes_table = get_resumes_table()
    try:
        response = resumes_table.get_item(
            Key={'user_id': user_id, 'resume_id': resume_id}
        )
        item = response.get('Item')
        # When retrieving, ensure resume_data is parsed back into ResumeSchema if needed by logic,
        # Pydantic does this if the type hint is ResumeSchema in the model.
        return ResumeInDB(**item) if item else None
    except ClientError as e:
        print(f"Error getting resume by ID {resume_id} for user {user_id}: {e}")
        return None


async def get_all_resumes_for_user(user_id: str) -> List[ResumeInDB]:
    resumes_table = get_resumes_table()
    try:
        response = resumes_table.query(
            IndexName='user_id-index',
            KeyConditionExpression='user_id = :uid_val',
            ExpressionAttributeValues={':uid_val': user_id},
            ScanIndexForward=False  # Optional: to sort by sort key (resume_id) descending
        )
        items = response.get('Items', [])
        return [ResumeInDB(**item) for item in items]
    except ClientError as e:
        print(f"Error getting all resumes for user {user_id}: {e}")
        return []


async def update_resume(
        user_id: str, resume_id: str, resume_update_data: ResumeUpdate
) -> Optional[ResumeInDB]:
    resumes_table = get_resumes_table()
    timestamp = now_iso()

    update_expression_parts = ["SET updated_at = :ts"]
    expression_attribute_values = {":ts": timestamp}
    expression_attribute_names = {}  # For attribute names that are reserved words

    if resume_update_data.title is not None:
        update_expression_parts.append("title = :t")
        expression_attribute_values[":t"] = resume_update_data.title

    if resume_update_data.resume_data is not None:
        # model_dump(by_alias=True) for nested data
        update_expression_parts.append("resume_data = :rd")
        expression_attribute_values[":rd"] = resume_update_data.resume_data.model_dump(by_alias=True)

    if len(update_expression_parts) == 1:  # Only updated_at, nothing to update from payload
        current_resume = await get_resume_by_id(user_id, resume_id)
        if current_resume:  # Just update the timestamp if no payload data
            resumes_table.update_item(
                Key={'user_id': user_id, 'resume_id': resume_id},
                UpdateExpression="SET updated_at = :ts",
                ExpressionAttributeValues={":ts": timestamp},
                ReturnValues="UPDATED_NEW"
            )
            current_resume.updated_at = timestamp  # Update in-memory object
            return current_resume
        return None

    update_expression = ", ".join(update_expression_parts)

    try:
        response = resumes_table.update_item(
            Key={'user_id': user_id, 'resume_id': resume_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names if expression_attribute_names else None,
            ReturnValues="ALL_NEW"  # Gets all attributes of the item after the update
        )
        updated_item = response.get('Attributes')
        return ResumeInDB(**updated_item) if updated_item else None
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':  # Example if you add conditions
            print(f"Update condition failed for resume {resume_id}")
        else:
            print(f"Error updating resume {resume_id} in DynamoDB: {e}")
        return None


async def delete_resume(user_id: str, resume_id: str) -> bool:
    resumes_table = get_resumes_table()
    try:
        resumes_table.delete_item(
            Key={'user_id': user_id, 'resume_id': resume_id},
            # ConditionExpression='attribute_exists(resume_id)' # Optional: ensure item exists
        )
        return True
    except ClientError as e:
        # if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        #     print(f"Resume {resume_id} not found for deletion or condition failed.")
        #     return False
        print(f"Error deleting resume {resume_id} from DynamoDB: {e}")
        return False


# Placeholder for user app metadata (could be part of User item or separate)
async def get_user_app_metadata(user_id: str) -> Optional[Dict[str, Any]]:
    user = await get_user_by_id(user_id=user_id)
    if user:
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "preferences": {"theme": "light", "notifications_ddb": True}  # Example
        }
    return None


async def get_and_update_metadata(env: str = None) -> dict:
    table = get_metadata_table()
    key = {"id": "prod_metadata"}  # Assuming single row with id 'prod_metadata'
    try:
        if env == "prod":
            # Atomically increment the visit count
            response = table.update_item(
                Key=key,
                UpdateExpression="SET prod_count = if_not_exists(prod_count, :zero) + :inc",
                ExpressionAttributeValues={":inc": 1, ":zero": 0},
                ReturnValues="ALL_NEW"
            )
            item = response.get("Attributes", {})
        else:
            response = table.get_item(Key=key)
            item = response.get("Item", {})
        return item
    except Exception as e:
        print(f"Error accessing metadata table: {e}")
        return {"error": str(e)}

