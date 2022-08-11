# twilio-flow-update-tool

This tool takes twilio subaccount id/auth token from AWS secret manager, 
logs into every twilio subaccount, 
scans the existing flows and 
updates the flow whose name contains the given environment name (QA/PROD).

Before running this tool, make sure twilio subaccount id/auth token is stored in AWS secret manager.
