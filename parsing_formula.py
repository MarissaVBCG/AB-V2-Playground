import openai
import json
import os
from dotenv import load_dotenv

# =====================================================
#       API key and file paths for users
# =====================================================

# Utility function to generate user-specific file paths
def user_specific_file(filename):
    user_id = os.getenv('USER_ID', 'default_user')  # USER_ID is passed via environment variables
    user_dir = os.path.join(os.getcwd(), user_id)  # Create a folder for each user

    # Ensure the user-specific directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    return os.path.join(user_dir, filename)  # Return the file path within the user folder

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')  

# =====================================================
#       Paths for the variables.txt and formulas.json
# ===================================================== 
INPUT_PROMPT_FILE = user_specific_file('variables.txt')
OUTPUT_JSON_FILE = user_specific_file('formulas.json')

## =====================================================
#                  Functions
# ====================================================== 

def read_input_prompt(file_path):
    try:
        with open(file_path, 'r') as file:
            prompt_content = file.read()
        return prompt_content
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit(1)

def construct_full_prompt(user_content):
    hardcoded_instructions = """
Please format the above information into the following JSON structure:

{
    "module1": {
        "line1": "MIN(Employee Data Module.'Start Date')",
        "line2": "Employee Data Module.'Position'"
    },
    "module2": {
        "line3": "SELECT Employee Data Module.'Position'",
        "line4": "COUNTIF(Employee Data Module.'Start Date', Timeframe, TRUE)",
        "line5": "IF Employee to Cohort Mapping THEN 1 ELSE 0",
        "line6": "MIN(Employee Data Module.'Start Date')"
    },
    "module3": {
        "line7": "Employee Data Module.'Position'"
    }
}

Ensure that:
- All strings are enclosed in double quotes.
- The JSON is properly formatted and valid.
- Single quotes inside the formulas remain intact.
- All line items are included, even those which formula is defined as 'information needed'
- The input you receive might have extra infor, but you will only use module_name, line_items and formula to parse out your response.
- Do not cut out names of line items when inputing formulas, if they have content within parenthesis (), add it when referrecing it in the formula
"""
    full_prompt = user_content + hardcoded_instructions
    return full_prompt

def get_chatgpt_response(full_prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0,  
            max_tokens=1000,  
            n=1,  
            stop=None  
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"An error occurred while communicating with OpenAI: {e}")
        exit(1)

def extract_json_from_response(response_text):
    try:
        start = response_text.index('{')
        end = response_text.rindex('}') + 1
        json_str = response_text[start:end]
        json_data = json.loads(json_str)
        return json_data
    except ValueError:
        print("Error: No JSON object found in the response.")
        print("Full response was:")
        print(response_text)
        exit(1)
    except json.JSONDecodeError as e:
        print("Error decoding JSON from the response:")
        print(e)
        print("Full response was:")
        print(response_text)
        exit(1)

def save_json_to_file(data, file_path):
    """Save the JSON data to a file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"JSON data successfully saved to '{file_path}'.")
    except IOError as e:
        print(f"Error saving JSON to file: {e}")
        exit(1)

def main():
    user_content = read_input_prompt(INPUT_PROMPT_FILE)
    
    full_prompt = construct_full_prompt(user_content)
    
    print("Sending prompt to ChatGPT...")
    response = get_chatgpt_response(full_prompt)
    
    print("\nChatGPT Response:")
    print(response)
    
    print("\nParsing JSON from the response...")
    json_data = extract_json_from_response(response)
    
    save_json_to_file(json_data, OUTPUT_JSON_FILE)
    
    
if __name__ == "__main__":
    main()
