"""
Simple test function to verify Vercel Python detection
"""
import json

def handler(req):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'message': 'Python serverless function is working!'})
    }

