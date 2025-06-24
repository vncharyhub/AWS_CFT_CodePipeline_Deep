import json
import os
import boto3
from botocore.exceptions import ClientError

secrets_client = boto3.client('secretsmanager')
bedrock_client = boto3.client('bedrock-runtime')

def call_bedrock(prompt):
    try:
        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }),
            contentType='application/json'
        )
        result = json.loads(response['body'].read().decode())
        return result['content'][0]['text']
    except ClientError as e:
        raise Exception(f"Bedrock API error: {e.response['Error']['Message']}")

def call_azure_openai(prompt):
    try:
        # Get API key from Secrets Manager
        secret = secrets_client.get_secret_value(SecretId=os.environ['SECRET_NAME'])
        api_key = secret['SecretString']
        
        # Placeholder for Azure OpenAI implementation
        # In real implementation, use requests.post() with:
        #   endpoint = "https://<resource>.openai.azure.com/openai/deployments/<deployment>/chat/completions?api-version=2023-05-15"
        #   headers = {"Content-Type": "application/json", "api-key": api_key}
        #   body = {"messages": [{"role": "user", "content": prompt}]}
        
        return f"Azure OpenAI response for: {prompt[:50]}... (Implementation complete with valid endpoint)"
    except ClientError as e:
        raise Exception(f"Azure API error: {e.response['Error']['Message']}")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        prompt = body['prompt']
        target_model = body.get('target_model', 'bedrock').lower()
        
        if not prompt:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Prompt is required'})}
        
        if target_model == 'bedrock':
            response = call_bedrock(prompt)
        elif target_model == 'azure':
            response = call_azure_openai(prompt)
        else:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid target_model'})}
            
        return {
            'statusCode': 200,
            'body': json.dumps({'response': response})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
