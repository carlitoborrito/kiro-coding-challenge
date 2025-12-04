import boto3
import os
from typing import Optional, List
from botocore.exceptions import ClientError
import uuid


class DynamoDBClient:
    def __init__(self):
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'events')
        self.region = os.getenv('AWS_REGION', 'us-west-2')
        
        # Use local endpoint if specified (for local development)
        endpoint_url = os.getenv('DYNAMODB_ENDPOINT_URL')
        if endpoint_url:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name=self.region)
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        
        self.table = self.dynamodb.Table(self.table_name)

    def create_event(self, event_data: dict) -> dict:
        # Use provided eventId or generate new one
        event_id = event_data.get('eventId') or str(uuid.uuid4())
        item = {
            'eventId': event_id,
            **{k: v for k, v in event_data.items() if k != 'eventId'}
        }
        
        try:
            self.table.put_item(Item=item)
            return item
        except ClientError as e:
            raise Exception(f"Failed to create event: {e.response['Error']['Message']}")

    def get_event(self, event_id: str) -> Optional[dict]:
        try:
            response = self.table.get_item(Key={'eventId': event_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Failed to get event: {e.response['Error']['Message']}")

    def list_events(self, status_filter: Optional[str] = None) -> List[dict]:
        try:
            if status_filter:
                response = self.table.scan(
                    FilterExpression='#status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': status_filter}
                )
            else:
                response = self.table.scan()
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list events: {e.response['Error']['Message']}")

    def update_event(self, event_id: str, update_data: dict) -> Optional[dict]:
        if not update_data:
            return self.get_event(event_id)
        
        # Build update expression
        update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expr_attr_names = {f"#{k}": k for k in update_data.keys()}
        expr_attr_values = {f":{k}": v for k, v in update_data.items()}
        
        try:
            response = self.table.update_item(
                Key={'eventId': event_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                return None
            raise Exception(f"Failed to update event: {e.response['Error']['Message']}")

    def delete_event(self, event_id: str) -> bool:
        try:
            self.table.delete_item(Key={'eventId': event_id})
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete event: {e.response['Error']['Message']}")


db_client = DynamoDBClient()
