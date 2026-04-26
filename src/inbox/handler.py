import json
import boto3
import os

s3 = boto3.client('s3')

BUCKET = os.environ["INBOX_BUCKET_NAME"]  # [] not ()

def handler(event, context):
    print(json.dumps(event))  # move to top so it always logs

    method = event['httpMethod']
    headers = {'Access-Control-Allow-Origin': "*"}  # fixed typo: Orgin -> Origin

    if method == "GET":
        response = s3.list_objects_v2(Bucket=BUCKET)
        files = [obj['Key'] for obj in response.get('Contents', [])]  # .get() not .get[]
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
        key = event['pathParameters']['key']  # fixed typo: pathParamaters -> pathParameters
        s3.delete_object(Bucket=BUCKET, Key=key)
        return {
            'statusCode': 200,
            'body': json.dumps({'deleted': key}),
            'headers': headers,
        }

    return {'statusCode': 405, 'body': json.dumps({'error': 'Method not allowed'}), 'headers': headers}