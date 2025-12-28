import json
import boto3
import os

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def handler(event, context):
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Query parameter is required'})
            }
        
        knowledge_base_id = os.environ.get('KNOWLEDGE_BASE_ID')
        bedrock_model_arn = os.environ.get('BEDROCK_MODEL_ARN')
        
        # System instructions for the AI assistant
        system_instruction = """You are an expert AWS Solutions Architect Professional (SAP-C02) exam preparation assistant. Your role is to:

1. Provide accurate, detailed information about the SAP-C02 exam based on the official exam guide
2. Help users understand exam domains, topics, and question formats
3. Explain AWS services and architectural patterns relevant to the exam
4. Offer study tips and best practices for exam preparation
5. Clarify complex concepts in a clear, educational manner
6. Always cite specific sections from the exam guide when available

Be concise but thorough. If a question is outside the scope of the SAP-C02 exam, politely redirect the user to exam-relevant topics."""
        
        # Query the knowledge base
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledge_base_id,
                    'modelArn': bedrock_model_arn,
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': f'{system_instruction}\n\nUser Question: $query$\n\nSearch Results: $search_results$\n\nProvide a helpful answer based on the search results:'
                        }
                    }
                }
            }
        )
        
        # Extract the generated response
        answer = response['output']['text']
        citations = []
        
        # Extract citations if available
        if 'citations' in response:
            for citation in response['citations']:
                if 'retrievedReferences' in citation:
                    for ref in citation['retrievedReferences']:
                        citations.append({
                            'content': ref.get('content', {}).get('text', ''),
                            'location': ref.get('location', {})
                        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'answer': answer,
                'citations': citations
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }