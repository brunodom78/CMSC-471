import json
import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
}


def _resp(status, body):
    return {'statusCode': status, 'headers': HEADERS, 'body': json.dumps(body, default=str)}


def handler(event, context):
    print(json.dumps(event))

    table = dynamodb.Table(os.environ['JOB_TABLE'])
    method = event['httpMethod']
    params = event.get('pathParameters') or {}
    job_id = params.get('jobId')

    # DELETE /api/jobs/{jobId}/items/{index}
    if method == 'DELETE' and 'index' in params:
        try:
            index = int(params['index'])
        except (TypeError, ValueError):
            return _resp(400, {'error': 'index must be an integer'})

        try:
            result = table.update_item(
                Key={'jobId': job_id},
                UpdateExpression=f'REMOVE #i[{index}]',
                ExpressionAttributeNames={'#i': 'items'},
                ConditionExpression='attribute_exists(jobId)',
                ReturnValues='ALL_NEW',
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return _resp(404, {'jobId': job_id, 'status': 'NOT_FOUND'})
            raise

        return _resp(200, {
            'jobId': job_id,
            'removedIndex': index,
            'items': result.get('Attributes', {}).get('items', []),
        })

    # DELETE /api/jobs/{jobId}
    if method == 'DELETE':
        table.delete_item(Key={'jobId': job_id})
        return _resp(200, {'jobId': job_id, 'deleted': True})

    # GET /api/jobs/{jobId}
    item = table.get_item(Key={'jobId': job_id}).get('Item')
    if item is None:
        return _resp(404, {'jobId': job_id, 'status': 'NOT_FOUND'})
    return _resp(200, {
        'jobId': job_id,
        'status': item.get('status', 'UNKNOWN'),
        'message': item.get('message', ''),
        'items': item.get('items', []),
        'createdAt': item.get('createdAt'),
    })
