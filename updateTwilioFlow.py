import os
import boto3
import json
import base64
from twilio.rest import Client

env = os.environ['env']
commit_message = os.environ['commit_message']
if env == 'QA':
    # add your AWS QA secret name and region here
    secret_name = ""
    region_name = "eu-west-1"
elif env == 'PROD':
    # add your AWS Production secret name and region here
    secret_name = ""
    region_name = "us-east-1"

session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
)


get_secret_value_response = client.get_secret_value(SecretId=secret_name)

if 'SecretString' in get_secret_value_response:
    secret = get_secret_value_response['SecretString']
else:
    secret = base64.b64decode(get_secret_value_response['SecretBinary'])

secret_json = json.loads(secret)
# print(secret_json)
flow_json_file = "./flow-"+ env +".json"

for account_sid in secret_json.keys() :
    auth_token = secret_json.get(account_sid)
    client = Client(account_sid, auth_token)
    account = client.api.v2010.accounts(account_sid).fetch()
    print("Searching " + account.friendly_name)
    flows = client.studio.v2.flows.list(limit=50)
    for flow in flows:
        #this will update all flows with name having environment name (QA/PROD)
        if env in flow.friendly_name:
            print("Updating " + account_sid + "  " + account.friendly_name + "  " + flow.sid + "  " + flow.friendly_name)
            flow = client.studio.v2.flows(flow.sid) \
                .update(commit_message=commit_message, definition=json.load(open(flow_json_file)), status='published')
