import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Read the SA model draft

# Read the model draft from a text file
with open("draft_model.txt", "r") as f:
    draft_model = f.read()

# Function to process the user input and generate a draft model
def process_draft_model(): 
    prompt = (
        "Description: You are an expert Anaplan Model Builder. Your role is to take the high-level model design provided by a Solutions Architect and create the necessary lists (dimensions) for the model in Anaplan. "
        "Only include explicit names for each list. Avoid using compound descriptions or general terms like 'Product Lines or Business Units'; instead, select clear and distinct names for each list. "
        "Focus only on creating the lists (dimensions) needed to support the model. "
        "If additional lists are necessary to ensure a fully functional model, include them directly, without explicitly stating that they are added or suggested. Do not suggest list with names 'Time', 'Users', 'Versions' or 'Currency' as they are reserved to system use"
        "Ensure alignment with the overall design from the Solutions Architect and include all necessary lists as if they were part of the original plan.\n\n"
        "IMPORTANT: The output should be plain text, without any special characters like asterisks (**), bullet points, or Markdown formatting. Only use plain text descriptions with no additional formatting.\n\n"
        
        "Goal: Create a list of the necessary lists (dimensions) for the model. Only provide lists, expanding as necessary to ensure the model is fully functional, but without explicitly stating that you are adding or suggesting anything additional.\n\n"
        
        f"Draft Model Provided:\n{draft_model}\n\n"
    )

    # Call GPT 
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a top-tier Anaplan Model Builder."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the output (draft model)
    lists_draft = response['choices'][0]['message']['content']

    # Save the draft model to a text file
    with open("lists_draft.txt", "w") as f: 
        f.write(lists_draft)

    print("Draft lists saved to lists_draft.txt")

# Call the function
process_draft_model()
