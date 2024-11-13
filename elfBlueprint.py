import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Read the necessary drafts from text files
with open("draft_model.txt", "r") as f:
    sa_draft_model = f.read()

with open("associations_draft.txt", "r") as f:
    associations_draft = f.read()

with open("line_items_draft.txt", "r") as f:
    line_items_draft = f.read()

# Function to handle line item attributes using blueprint feature
def process_line_item_attributes(): 
    # Define the prompt for GPT to handle line item attributes based on the provided drafts
    prompt = (
        "Description: You are an expert Anaplan Model Builder. Your task is to suggest the appropriate attributes for line items in the model. "
        "The line item attributes that need to be customized are Format, Summary, Time Scale, and Versions (limited to 'All' or 'Not Applicable'). "
        "When providing format List please make sure that the suggested List is only one and enclosed in parentheses. \n\n"

        "Use the provided drafts (SA draft model, associations draft, and line items draft) to ensure that each line item is customized in alignment with the objectives and goals of the model. Stricly refer to only the modules names and lists found in `associations_draft.txt` and the line items found in `line_items_draft.txt`.\n\n"
        
        "Line Item Attributes to Consider:\n"
        "Format: Only use the following valid formats for each line item: Number, Text, Boolean, List (with one suggested List enclosed in parentheses), Date, Time Period, No Data.\n"
        "Summary: Aggregation methods are Sum, None, Formula, Average, Ratio, Min, Max, First non-blank, Last non-blank, Any, All. (do not explain None if selected).\n"
        "Time Scale: Not Applicable, Day, Month, Quarter, Year, at the module level and make sure all line items are the same for each module. \n"
        "Versions: Choose either 'All' or 'Not Applicable' at the module level and make sure all line items are the same for each module.\n\n"
        
        f"SA Draft Model:\n{sa_draft_model}\n\n"
        f"Associations Draft:\n{associations_draft}\n\n"
        f"Line Items Draft:\n{line_items_draft}\n\n"
        
        "Goal: Customize the line item attributes for each line item. Exclude any formulas."
        "IMPORTANT: The output should be plain text, without any special characters like asterisks (**), bullet points, or Markdown formatting. Only use plain text descriptions with no additional formatting.\n\n"

    )

    # Call GPT 
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a top-tier Anaplan Model Builder and Blueprint Architect."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the output (line item attributes)
    blueprint_draft = response['choices'][0]['message']['content']

    # Save the line item attributes to a text file
    with open("blueprint_draft.txt", "w") as f: 
        f.write(blueprint_draft)

    print("Line item attributes saved to blueprint_draft.txt")

# Call the function
process_line_item_attributes()
