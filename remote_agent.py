import os
import openai
import json

with open('../../../key.txt', 'r') as f:
    secret_key = f.read().strip()

openai.api_key = secret_key

def query_remote_agent(prompt, logger):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ])
    response = response['choices'][0]['message']['content']
    logger.info(response)
    return json.loads(response)
