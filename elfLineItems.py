import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Read the user input from a text file
with open("default_user/user_input.txt", "r") as f: 
    user_input = f.read()

# Read the model draft from a text file
with open("draft_model.txt", "r") as f: 
    draft_model = f.read()

# Read the associations draft from a text file
with open("associations_draft.txt", "r") as f:
    associations_draft = f.read()

# Function to create line items for modules

def process_line_items_creation():
    # Define the prompt for GPT to suggest appropriate line items for each module
    prompt = (
        "Description: You are an expert Anaplan Model Builder. Your task is to analyze the model draft provided in `draft_model.txt`, what the user has requested specifically in 'user_input.txt', the modules and the respective lists (dimensions) in the `associations_draft.txt` file and suggest which line items should be created for each module. Stricly refer to only the modules names and lists found in `associations_draft.txt`"
        "Ensure the suggestions maintain alignment with the Solutions Architect’s design and what the user has requested.\n\n"

        "Model Draft provided:\n"
        f"{draft_model}\n\n"
    
        "User Input provided:\n"
        f"{user_input}\n\n" 

        "Modules and Lists(dimensions) Provided:\n"
        f"{associations_draft}\n\n"
    
        "IMPORTANT: The output should be plain text, without any special characters like asterisks (**), bullet points, or Markdown formatting. Only use plain text descriptions with no additional formatting.\n\n"

        "Goal: Suggest line items for each module to ensure the model is functional and aligned with the high-level design."
    )

    # Call GPT 
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a top-tier Anaplan Model Builder."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the output (creation of line items for each module)
    line_items_draft = response['choices'][0]['message']['content']

    # Save the associations to a text file
    with open("line_items_draft.txt", "w") as f: 
        f.write(line_items_draft)

    print("Suggested Line Items have been saved to line_items_draft.txt")

# Call the function
process_line_items_creation()
