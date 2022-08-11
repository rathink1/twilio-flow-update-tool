# twilio-flow-update-tool

This tool takes twilio subaccount id/auth token from AWS secret manager, 
logs into every twilio subaccount, 
scans the existing flows and 
updates the existing flow whose name contains the given environment name (QA/PROD), with a new flow json.

Before running this tool, make sure twilio subaccount id/auth token is stored in AWS secret manager.

Next you can hook up a jenkins python/shell-script job to this tool. Use this 

pip3 install twilio --upgrade
pip3 install boto3
python3 ./updateTwilioFlow.py
