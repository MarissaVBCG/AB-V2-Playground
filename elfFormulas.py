import openai
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

with open("blueprint_draft.txt", "r") as f:
    blueprint_draft = f.read()

# Function to handle formula creation using the output of elfBlueprint.py
def generate_formulas(): 
    prompt = (
        "Description: You are an expert Anaplan Model Builder. Your task is to suggest the appropriate formulas for each line item in the model. "
        "If an explicit formula cannot be provided, please add 'N/A' instead without any explanation nor comment. Avoid using any invalid Anaplan functions such as 'RUNNINGSUM'. "
        "Do not add any explanations or comments for the formulas. "
        "Unlike Current Period, Previous Period is not an automatic selection in Anaplan’s time settings. Anaplan doesn’t have a built-in Time.'Previous Period' setting. \n\n"

        "Use the provided drafts (SA draft model, associations draft, line items draft, and blueprint draft) to ensure that each formula aligns with the model’s objectives and goals. Strictly refer to only the modules names and lists found in `associations_draft.txt` and the line items found in `line_items_draft.txt`. **Make sure that all modules, line items and lists that are referenced in the formulas are existing within those files.**\n\n"
        
        f"SA Draft Model:\n{sa_draft_model}\n\n"
        f"Associations Draft:\n{associations_draft}\n\n"
        f"Line Items Draft:\n{line_items_draft}\n\n"
        f"Blueprint Draft (Attributes):\n{blueprint_draft}\n\n"
        
        "Goal: Customize the formulas for each line item in a way that aligns with Anaplan’s syntax and best practices.\n"
        "IMPORTANT: Use only valid Anaplan functions. Reference the list of valid functions here: https://help.anaplan.com/all-functions-160769b0-de37-4f08-87a0-cc3aa55525a3 and do not invent new functions (e.g., avoid non-existent functions like `RUNNINGSUM`).\n\n"
        
        "In Anaplan, formula syntax follows specific rules to ensure clarity, accuracy, and performance. Here’s a breakdown of key syntax rules and best practices for writing formulas:\n\n"
        
        "1. **Basic Formula Structure**\n"
        "- **IF Statement**: Use the structure IF [condition] THEN [result if true] ELSE [result if false].\n"
        "- **Function Calls**: Use functions directly within line items (e.g., SUM, LOOKUP, CUMULATE).\n"
        "- **Reference**: Use 'Module Name'.'Line Item Name' to refer to line items in other modules.\n\n"

        "2. **Syntax Rules**\n"
        "- **Quotes for Line Item Names**: Enclose line item names in single quotes if they contain spaces or special characters. Example:\n"
        "  'Current Stock Levels' > 'Safety Stock Requirement'\n"
        "- **Parentheses**: Use parentheses to control the order of operations explicitly, especially in nested functions.\n"
        "- **Commas for Parameters**: Separate parameters within a function using commas. Example:\n"
        "  MOVINGSUM(Line Item, -2, 0, AVERAGE)\n"
        "- **Boolean Logic**: Structure Boolean expressions efficiently with AND, OR, NOT to optimize logical operations.\n\n"

        "3. **Optimization and Efficiency**\n"
        "- **Separate Calculations**: Break down complex formulas across multiple line items instead of nesting functions to improve readability and performance.\n"
        "- **Avoid Redundant Calculations**: Reference existing calculated line items rather than duplicating calculations.\n"
        "- **Aggregate Functions**: When using aggregation functions (SUM, LOOKUP), ensure proper context mapping to achieve accurate results and reduce unnecessary calculations.\n\n"

        "4. **Text Formatting**\n"
        "- **Case Sensitivity**: Functions are not case-sensitive, but line item names and list member names are.\n"
        "- **Whitespace**: Whitespace does not affect formulas but can be used to improve readability.\n\n"

        "5.**Error Handling**\n"
        "- **Handle Empty Cells**: Use functions like ISBLANK to manage potential empty cells and prevent errors.\n"
        "- **Data Type Consistency**: Ensure compatible data types are used in operations (e.g., numeric with numeric, Boolean with Boolean).\n\n"

        "Following these rules ensures formulas are clear, effective, and optimized for Anaplan’s calculation engine.\n"

        "IMPORTANT: **DO NOT USE** any additional code formatting or symbols such as **, `python`, triple backticks, or markdown. **Always** enclose module names and line item names in single quotes if they contain spaces or special characters. \n"
    )

    # Call GPT 
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a top-tier Anaplan Model Builder."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the formulas and save to a text file
    formulas_draft = response['choices'][0]['message']['content']

    with open("formulas_draft.txt", "w") as f: 
        f.write(formulas_draft)

    print("Formulas saved to formulas_draft.txt")

# Call the function
generate_formulas()
