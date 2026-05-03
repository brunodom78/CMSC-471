import json
import os
import boto3

s3 = boto3.client('s3')


def handler(event, context):
    print(json.dumps(event))

    job_id = event['jobId']
    filename = event['filename']
    bucket = os.environ['INBOX_BUCKET_NAME']

    # Verify the upload exists; head_object 404s cleanly if not.
    s3.head_object(Bucket=bucket, Key=filename)

    return {
        'jobId': job_id,
        'filename': filename,
        'bucket': bucket,
    }
