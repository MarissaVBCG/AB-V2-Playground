import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Read the model draft from a text file
with open("draft_model.txt", "r") as f: 
    draft_model = f.read()

# Read the modules draft from a text file
with open("modules_draft.txt", "r") as f:
    modules_draft = f.read()

# Read the lists draft from a text file
with open("lists_draft.txt", "r") as f:
    lists_draft = f.read()

# Function to associate lists with modules
def process_associate_lists(): 
    # Define the prompt for GPT to suggest appropriate lists for each module
    prompt = (
        "Description: You are an expert Anaplan Model Builder. Your task is to analyze the model draft provided in `draft_model.txt`, "
        "the modules provided in the `modules_draft.txt` file, and suggest which lists (dimensions) should be applied to each module. "
        "Use strictly and exclusively only the lists provided in the `lists_draft.txt` file and associate them with the relevant modules based on best practices and logical functionality. "
        "Do not include list names such as 'Time', 'Users', 'Versions' or 'Currency' as they are reserved for system use. "
        "Any list not explicitly found in `lists_draft.txt` should be disregarded, even if it appears indirectly in the model draft or modules provided. "
        "If any list is not listed in `lists_draft.txt`, it should not appear in the output.\n\n"
        
        "Model Draft provided:\n"
        f"{draft_model}\n\n"

        "Modules Provided:\n"
        f"{modules_draft}\n\n"

        "Lists Provided (use only these exact names):\n"
        f"{lists_draft}\n\n"

        "IMPORTANT: The output should be plain text, without any special characters like asterisks (**), bullet points, or Markdown formatting. Only use plain text descriptions with no additional formatting.\n\n"
        
        "Goal: List each module followed by the names of the associated lists in the following format:\n"
        "Module Name\n- List Name\n- List Name (and so on)\n\n"
        "Provide as many lists as are appropriate for each module, ensuring only necessary lists from `lists_draft.txt` are included to align with the high-level design. Do not include any lists not present in `lists_draft.txt`."
    )

    # Call GPT 
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a top-tier Anaplan Model Builder."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the output (associations between modules and lists)
    associations_draft = response['choices'][0]['message']['content']

    # Save the associations to a text file
    with open("associations_draft.txt", "w") as f: 
        f.write(associations_draft)

    print("Associations between modules and lists saved to associations_draft.txt")

# Call the function
process_associate_lists()
