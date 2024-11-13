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

# Function to process the user input and generate a draft model
def process_user_input(): 
    prompt = (
        "Description: You are an experienced Solutions Architect specializing in Anaplan model design. Your role is to provide high-level guidance for building foundational Anaplan models. "
        "Based on the user's input, offer a general model design without going into specific details. This design will serve as a starting point for more specialized and detailed development later.\n\n"
        "Goal: Provide a high-level overview of the model structure, covering key modules and dimensions, without focusing on line item specifics, formulas, or detailed configuration. The user will provide the model name and the types of modules they want, and your task is to offer a simplified structure that a model builder can expand on. Do not change the name of the model the user provided.\n\n"
        "IMPORTANT: The output should be plain text, without any special characters like asterisks (**), bullet points, or Markdown formatting. Only use plain text descriptions with no additional formatting.\n\n"
        "Model Design:\n"
        "Overview: Briefly describe the overall structure of the model, including the main modules (e.g., P&L, Opex, Capex). Focus on the big picture, explaining how the modules interact at a high level.\n\n" 
        "Key Components:\n"
        "Modules: Mention the key modules like P&L, Opex, Capex, etc. Provide a high-level explanation of their purpose and how they fit together. Avoid line item or formula specifics, focusing on the general structure.\n"
        "Lists (Dimensions): Describe the core dimensions needed (e.g., Cost Centers, Accounts), including any necessary hierarchies, but keep the focus on the general use of these lists rather than specific properties. Do not suggest list with names 'Time', 'Users', 'Versions' or 'Currency' as they are reserved to system use\n\n"
        "Data Flow and Integration:\n"
        "Data Flow: Provide a general explanation of how data will flow between modules. Keep this simple, mentioning any key connections between the modules without specifying technical details.\n\n"
        "Focus on creating a strong foundation that can later be expanded with more detailed and specialized instructions.\n\n"
        f"User's request: {user_input}\n\n"
    )  

    # Call GPT 
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a top-tier Solutions Architect and a Master Anaplaner."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the output (draft model)
    draft_model = response['choices'][0]['message']['content']

    # Save the draft model to a text file
    with open("draft_model.txt", "w") as f: 
        f.write(draft_model)

    print("Draft model saved to draft_model.txt")

# Call the function
process_user_input()
