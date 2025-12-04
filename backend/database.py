import boto3
import os
from typing import Optional, List
from botocore.exceptions import ClientError
import uuid
from datetime import datetime, timezone


class DynamoDBClient:
    def __init__(self):
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'events')
        self.users_table_name = os.getenv('USERS_TABLE_NAME', 'users')
        self.registrations_table_name = os.getenv('REGISTRATIONS_TABLE_NAME', 'registrations')
        self.region = os.getenv('AWS_REGION', 'us-west-2')
        
        # Use local endpoint if specified (for local development)
        endpoint_url = os.getenv('DYNAMODB_ENDPOINT_URL')
        if endpoint_url:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name=self.region)
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        
        self.table = self.dynamodb.Table(self.table_name)
        self.users_table = self.dynamodb.Table(self.users_table_name)
        self.registrations_table = self.dynamodb.Table(self.registrations_table_name)

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

    # User management methods
    def create_user(self, user_data: dict) -> dict:
        """Create a new user with uniqueness check on userId"""
        try:
            self.users_table.put_item(
                Item=user_data,
                ConditionExpression='attribute_not_exists(userId)'
            )
            return user_data
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"User with userId '{user_data['userId']}' already exists")
            raise Exception(f"Failed to create user: {e.response['Error']['Message']}")

    def get_user(self, user_id: str) -> Optional[dict]:
        """Retrieve a user by userId"""
        try:
            response = self.users_table.get_item(Key={'userId': user_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Failed to get user: {e.response['Error']['Message']}")

    # Registration query methods
    def get_registration(self, user_id: str, event_id: str) -> Optional[dict]:
        """Retrieve a specific registration by userId and eventId"""
        try:
            response = self.registrations_table.get_item(
                Key={'userId': user_id, 'eventId': event_id}
            )
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Failed to get registration: {e.response['Error']['Message']}")

    def list_user_registrations(self, user_id: str) -> List[dict]:
        """List all registrations for a specific user"""
        try:
            response = self.registrations_table.query(
                KeyConditionExpression='userId = :userId',
                ExpressionAttributeValues={':userId': user_id}
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list user registrations: {e.response['Error']['Message']}")

    def list_event_registrations(self, event_id: str, status: Optional[str] = None) -> List[dict]:
        """List all registrations for a specific event, optionally filtered by status"""
        try:
            if status:
                response = self.registrations_table.query(
                    IndexName='EventRegistrationsIndex',
                    KeyConditionExpression='eventId = :eventId',
                    FilterExpression='#status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':eventId': event_id, ':status': status}
                )
            else:
                response = self.registrations_table.query(
                    IndexName='EventRegistrationsIndex',
                    KeyConditionExpression='eventId = :eventId',
                    ExpressionAttributeValues={':eventId': event_id}
                )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to list event registrations: {e.response['Error']['Message']}")

    def count_confirmed_registrations(self, event_id: str) -> int:
        """Count the number of confirmed registrations for an event"""
        try:
            response = self.registrations_table.query(
                IndexName='EventRegistrationsIndex',
                KeyConditionExpression='eventId = :eventId',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':eventId': event_id, ':status': 'confirmed'},
                Select='COUNT'
            )
            return response.get('Count', 0)
        except ClientError as e:
            raise Exception(f"Failed to count confirmed registrations: {e.response['Error']['Message']}")

    # Registration creation method
    def create_registration(self, registration_data: dict) -> dict:
        """Create a new registration with duplicate prevention and timestamp generation"""
        # Generate timestamp if not provided
        if 'registeredAt' not in registration_data:
            registration_data['registeredAt'] = datetime.now(timezone.utc).isoformat()
        
        try:
            self.registrations_table.put_item(
                Item=registration_data,
                ConditionExpression='attribute_not_exists(userId) AND attribute_not_exists(eventId)'
            )
            return registration_data
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"Registration already exists for user '{registration_data['userId']}' and event '{registration_data['eventId']}'")
            raise Exception(f"Failed to create registration: {e.response['Error']['Message']}")

    # Registration deletion and promotion methods
    def delete_registration(self, user_id: str, event_id: str) -> bool:
        """Delete a registration"""
        try:
            self.registrations_table.delete_item(
                Key={'userId': user_id, 'eventId': event_id}
            )
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete registration: {e.response['Error']['Message']}")

    def get_first_waitlisted_user(self, event_id: str) -> Optional[dict]:
        """Get the first waitlisted user for an event (ordered by registeredAt timestamp)"""
        try:
            response = self.registrations_table.query(
                IndexName='EventRegistrationsIndex',
                KeyConditionExpression='eventId = :eventId',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':eventId': event_id, ':status': 'waitlisted'},
                Limit=1
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            raise Exception(f"Failed to get first waitlisted user: {e.response['Error']['Message']}")

    def update_registration_status(self, user_id: str, event_id: str, status: str) -> dict:
        """Update the status of a registration"""
        try:
            response = self.registrations_table.update_item(
                Key={'userId': user_id, 'eventId': event_id},
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status},
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except ClientError as e:
            raise Exception(f"Failed to update registration status: {e.response['Error']['Message']}")


db_client = DynamoDBClient()
