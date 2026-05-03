import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')


def handler(event, context):
    print(json.dumps(event))

    job_id = event['jobId']
    items = event['items']

    dynamodb.Table(os.environ['JOB_TABLE']).update_item(
        Key={'jobId': job_id},
        UpdateExpression='SET #s = :s, #m = :m, #i = :i',
        ExpressionAttributeNames={
            '#s': 'status',
            '#m': 'message',
            '#i': 'items',
        },
        ExpressionAttributeValues={
            ':s': 'SUCCEEDED',
            ':m': f'Saved {len(items)} items',
            ':i': items,
        },
    )

    return {
        'jobId': job_id,
        'rowCount': len(items),
    }
