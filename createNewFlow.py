# run cmd for QA env : python3 createNewFlow.py -e QA -P nexus-qa -r eu-west-1 -s qa/subaccounts -C <newclientname> -m v3.5

import os
import boto3
import json
import base64
from twilio.rest import Client
import argparse

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("-e","--env")
parser.add_argument("-P","--awsprofile")
parser.add_argument("-r","--region")
parser.add_argument("-s","--secretname")
parser.add_argument("-C","--client")
parser.add_argument("-m","--commitmesg")
args = parser.parse_args()

env = args.env
if args.secretname is None :
    if env == 'QA':
        secret_name = "twilio/qa/subaccounts" # change accordingly
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

flow_json_file = "flow-"+ env +".json" # change to your file location

for account_sid in secret_json.keys() :
    auth_token = secret_json.get(account_sid)
    client = Client(account_sid, auth_token)
    account = client.api.v2010.accounts(account_sid).fetch()

    if account.friendly_name == args.client:
        flows = client.studio.v2.flows.list(limit=50)
        print("Found client : " + account.friendly_namen + " Listing flows : " + flows)

        if not flows or not any(env in flowname.friendly_name for flowname in flows) :
            print("Creating a new flow for client : " + account.friendly_name + " acc Id : " + account_sid)
            flow = client.studio.v2.flows.create(commit_message=commit_message, definition=json.load(open(flow_json_file)), friendly_name=flow_json_file,
                                                 status='draft')