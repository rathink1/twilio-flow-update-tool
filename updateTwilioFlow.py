# run QA : python3 updateChatbotScriptV2.py -e QA -m v2.3.32 -P nexus-qa -r eu-west-1 -s qa/subaccounts
import os
import boto3
import json
import base64
from twilio.rest import Client
import argparse

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("-e","--env")
parser.add_argument("-m","--commitmesg")
parser.add_argument("-P","--awsprofile")
parser.add_argument("-r","--region")
parser.add_argument("-s","--secretname")
args = parser.parse_args()

env = args.env
if args.secretname is None :
    if env == 'QA':
        secret_name = "twilio/qa/subaccounts"
    elif env == 'PROD':
        secret_name = "twilio/prod/subaccounts"
else :
    secret_name = args.secretname

session = boto3.session.Session(profile_name=args.awsprofile)
client = session.client(
    service_name='secretsmanager',
    region_name=args.region,
)
commit_message = args.commitmesg


get_secret_value_response = client.get_secret_value(SecretId=secret_name)

if 'SecretString' in get_secret_value_response:
    secret = get_secret_value_response['SecretString']
else:
    secret = base64.b64decode(get_secret_value_response['SecretBinary'])

secret_json = json.loads(secret)

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
