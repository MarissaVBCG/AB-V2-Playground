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
        "Description: You are an expert Anaplan Model Builder. Your role is to take the high-level model design provided by a Solutions Architect and start building the model in Anaplan. "
        "Your task is to create only the modules based on the draft model provided. "
        "Do not include lists (dimensions), data flows, integrations, or any other components besides modules names"
        "If additional modules are necessary, include them directly without explicitly stating that they are suggestions. Ensure everything aligns with the draft model from the Solutions Architect.\n\n"
        "IMPORTANT: The output should be plain text, without any special characters like asterisks (**), bullet points, or Markdown formatting. Only use plain text descriptions with no additional formatting.\n\n"
        
        "Goal: Create a list of the modules. Only provide modules without any additional components like lists, integrations, or data flow.\n\n"
        
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
    modules_draft = response['choices'][0]['message']['content']

    # Save the draft model to a text file
    with open("modules_draft.txt", "w") as f: 
        f.write(modules_draft)

    print("Draft modules saved to modules_draft.txt")

# Call the function
process_draft_model()
