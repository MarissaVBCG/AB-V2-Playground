import requests
import json

def get_existing_lists(username, password, workspace_id, model_id):
    
    # Function to retrieve lists from Anaplan API and return a list of names with 'Users' added by default.
    
    
    # Step 1: Obtain the Authentication Token
    auth_url = 'https://auth.anaplan.com/token/authenticate'

    # Make the POST request to get the auth token
    response = requests.post(auth_url, auth=(username, password))

    # Check if the request was successful
    if response.status_code == 201:  # Successful login
        auth_data = response.json()
        anaplan_auth_token = auth_data.get('tokenInfo', {}).get('tokenValue')
    else:
        print(f"Failed to authenticate. Status code: {response.status_code}")
        print("Response:", response.text)
        return None

    # Step 2: Use the AnaplanAuthToken to Retrieve Lists
    lists_url = f"https://api.anaplan.com/2/0/workspaces/{workspace_id}/models/{model_id}/lists"

    # Set up headers including the AnaplanAuthToken
    headers = {
        'Authorization': f'AnaplanAuthToken {anaplan_auth_token}',
        'Accept': 'application/json'
    }

    # Make the GET request to the Anaplan API
    response = requests.get(lists_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        lists = response.json()
        
        # Extract all "name" values from the "lists" section
        existing_lists = [item['name'] for item in lists['lists']]
        
        # Add 'Users' by default to the list
        existing_lists.append('Users')
        
        return existing_lists  # Return the list so it can be used by another script

    else:
        print(f"Failed to retrieve lists. Status code: {response.status_code}")
        print("Response:", response.text)
        return None
