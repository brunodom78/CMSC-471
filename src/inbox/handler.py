import json
import boto3
import os
from botocore.client import Config
from urllib.parse import unquote

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

BUCKET = os.environ["INBOX_BUCKET_NAME"]  # [] not ()

def handler(event, context):
    print(json.dumps(event))  # move to top so it always logs

    method = event['httpMethod']
    headers = {'Access-Control-Allow-Origin': "*"}  # fixed typo: Orgin -> Origin

    if method == "GET":
        response = s3.list_objects_v2(Bucket=BUCKET)
        # S3 list can occasionally return phantom entries that no longer exist
        # (HEAD/GET 404 but LIST still surfaces them). HEAD-filter to drop them.
        files = []
        for obj in response.get('Contents', []):
            try:
                s3.head_object(Bucket=BUCKET, Key=obj['Key'])
                files.append(obj['Key'])
            except s3.exceptions.ClientError:
                continue
        return {
            'statusCode': 200,
            'body': json.dumps(files),
            'headers': headers,
        }
    elif method == "POST":
        body = json.loads(event['body'])
        filename = body['filename']
        url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET,
                'Key': filename,
                'ContentType': 'image/png'
            },
            ExpiresIn=300
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'url': url, 'key': filename}),
            'headers': headers,
        }
    elif method == "DELETE":
        # API Gateway leaves path params URL-encoded; decode so keys with
        # spaces or unicode (e.g. "Screenshot ... PM.png") match the actual S3 key.
        key = unquote(event['pathParameters']['key'])
        s3.delete_object(Bucket=BUCKET, Key=key)
        return {
            'statusCode': 200,
            'body': json.dumps({'deleted': key}),
            'headers': headers,
        }

    return {'statusCode': 405, 'body': json.dumps({'error': 'Method not allowed'}), 'headers': headers}