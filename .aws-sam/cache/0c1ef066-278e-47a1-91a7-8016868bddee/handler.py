import json
import datetime
import os

def handler(event, context):
    print(json.dumps(event))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({
            "status": "ok",
            "service": "cmsc471-website",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "message": "Hello World",
            "region": os.environ.get("AWS_REGION", "us-east-1")
        })
    }