import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the paths for "The Elves" outputs
draft_model_file = "draft_model.txt"
modules_draft_file = "modules_draft.txt"
associations_draft_file = "associations_draft.txt"
line_items_draft_file = "line_items_draft.txt"
blueprint_draft_file = "blueprint_draft.txt"
lists_draft_file = "lists_draft.txt"
formulas_draft_file = "formulas_draft.txt"
variables_file = "default_user/variables.txt"

def get_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_prompt():
    # Read outputs from "The Elves"
    draft_model = get_file_content(draft_model_file)
    modules_draft = get_file_content(modules_draft_file)
    associations_draft = get_file_content(associations_draft_file)
    line_items_draft = get_file_content(line_items_draft_file)
    blueprint_draft = get_file_content(blueprint_draft_file)
    lists_draft = get_file_content(lists_draft_file)
    formulas_draft = get_file_content(formulas_draft_file)
    
    # Combine them into a single prompt
    combined_prompt = (
        "You are an expert in Anaplan model building. Your task is to transform the outputs from the following files into variables "
        "that can be used in Python code. You need to generate the following variables: model_name, module_name, line_items, format, "
        "formula, summary_mthd, applies_to, list_aux, time_scale, versions, and time_dim.\n"
        "\nHere are the outputs of each file:\n\n"
        f"1. Draft Model Output:\n{draft_model}\n\n"
        f"2. Modules Draft Output:\n{modules_draft}\n\n"
        f"3. Line Items Draft Output: \n{line_items_draft}\n\n"
        f"4. Blueprint Draft Output:\n{blueprint_draft}\n\n"
        f"5. Associations Draft Output:\n{associations_draft}\n\n"
        f"6. Lists Draft Output:\n{lists_draft}\n\n"
        f"7. Formulas Draft Output: \n{formulas_draft}\n\n"
        "Your task is to extract the necessary information and generate variables using the following format:\n"
        "model_name = The name of the model. Enclose it in single quotes inside double quotes (e.g., `\"'Auto Builder Model'\"`).\n"
        "module_name = A list of module names. Enclose the entire list in double quotes and each module name in single quotes (e.g., `\"['El Rosario', 'Peche Cosme']\"`).\n"
        "line_items = A nested list of line items for each module. Each nested list should correspond to the modules. Enclose the entire list in double quotes and each line item in single quotes (e.g., `\"[['semita', 'budin', 'pichardin'], ['Queso', 'Chipilin']]\"`).\n"
        "format = A nested list of formats for each line item. Enclose the entire list in double quotes and each format in single quotes (e.g., `\"[['Boolean', 'Boolean'], ['Text']]\"`).\n"
        "formula = A nested list of formulas for each line item. Avoid escape characters like `\\` for both single and double quotes. "
        "The entire formula itself, as it is an element in the list, should be enclosed in single quotes **once**, without adding extra quotes. For example: `\"[[''Revenue Planning Module'.'Revenue by Product Line' + 'Revenue Planning Module'.'Revenue by Business Unit'', 'information needed']]\"`. Respect and keep the single or double quotes found in the formulas and treat them as standalone characters, same with the parentheses in the formulas. "
        "Avoid any backslashes under any circumstances.\n"
        "- Missing formulas or 'N/A' should be replaced with 'information needed'.\n"
        "summary_mthd = A nested list of summary methods. Enclose the entire list in double quotes and each method in single quotes (e.g., `\"[['Sum', 'None'], ['information needed']]\"`)."
        "applies_to = A nested list of lists that apply to each module. Enclose the entire list in double quotes and each element in single quotes, 'information needed' will be only assigned as a string when there is no mention of lists at all for a module (e.g., `\"[['Pan Dulce', 'Users'], ['Pupusas'], ['information needed']]\"`).\n"
        "list_aux = A flat list containing all lists used in the model. Enclose the list in double quotes and each element in single quotes (e.g., `\"['Pan Dulce', 'Users', 'Pupusas']\"`).\n"
        "time_scale = A nested list of time scales for each line item. Enclose the entire list in double quotes and each element in single quotes (e.g., `\"[['Month', 'Year']]\"`).\n"
        "versions = A nested list of versions for each line item. Enclose the entire list in double quotes and each version in single quotes (e.g., `\"[['All', 'Not Applicable']]\"`).\n"
        "time_dim = A list indicating whether Time is used as a dimension for each module. Enclose the list in double quotes and each element ('True' or 'False') in single quotes (e.g., `\"['True', 'False']\"`).\n\n"
        "Ensure that:\n"
        "- All elements, especially in `formula`, are represented without any escape characters, using quotes naturally as standalone characters.\n"
        "- Repeat each element explicitly in lists without using shorthand (e.g., `['None'] * 8`).\n"
        "- Replace missing elements or 'N/A' with 'information needed'.\n"
        "- Each variable is output on a single line, without any additional code formatting or symbols such as **, `python`, triple backticks, or markdown.\n"
    )
    
    return combined_prompt

def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error getting response from OpenAI: {e}")
        return None

def save_variables(variables_content):
    with open(variables_file, 'w') as file:
        file.write(variables_content)

def main():
    prompt = generate_prompt()
    chatgpt_response = get_chatgpt_response(prompt)

    if chatgpt_response:
        print("ChatGPT response received, saving variables...")
        save_variables(chatgpt_response)
        print("Variables saved successfully to variables.txt")
    else:
        print("Error: No response from OpenAI.")

if __name__ == "__main__":
    main()