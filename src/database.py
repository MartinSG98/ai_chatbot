import boto3
from datetime import datetime
from typing import Optional

# Connect to DynamoDB using the broodmother profile
session = boto3.Session(profile_name="broodmother", region_name="eu-west-2")
dynamodb = session.resource("dynamodb")
table = dynamodb.Table("broodmother_chat_history")


def save_message(session_id: str, role: str, content: str, agent_name: Optional[str] = None):

    timestamp = datetime.utcnow().isoformat()
    
    item = {
        "session_id": session_id,
        "timestamp": timestamp,
        "role": role,
        "content": content,
    }
    
    if agent_name:
        item["agent_name"] = agent_name
    
    table.put_item(Item=item)
    return item


def get_chat_history(session_id: str):

    response = table.query(
        KeyConditionExpression="session_id = :sid",
        ExpressionAttributeValues={":sid": session_id},
        ScanIndexForward=True  # oldest first
    )
    return response.get("Items", [])


def delete_chat_history(session_id: str):

    # First get all items
    messages = get_chat_history(session_id)
    
    # Delete each one
    for msg in messages:
        table.delete_item(
            Key={
                "session_id": session_id,
                "timestamp": msg["timestamp"]
            }
        )
    
    return len(messages)