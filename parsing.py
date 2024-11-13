import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Utility function to generate user-specific file paths
def user_specific_file(filename):
    """Generate a user-specific folder and file path based on the USER_ID."""
    user_id = os.getenv('USER_ID', 'default_user')  # USER_ID is passed via environment variables
    user_dir = os.path.join(os.getcwd(), user_id)  # Create a folder for each user

    # Ensure the user-specific directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    return os.path.join(user_dir, filename)  # Return the file path within the user folder

# Define the paths for user-specific files
user_input_file = user_specific_file('user_input.txt')  # User-specific user_input.txt
variables_file = user_specific_file('variables.txt')  # User-specific variables.txt
progress_file = user_specific_file('progress.txt')  # User-specific progress.txt

# Initialize the variables
model_name = ""
module_name = ""
line_items = ""
format = ""
formula = ""
summary_mthd = ""
applies_to = ""
list_aux = ""
time_scale = ""
versions = ""
time_dim = ""

def save_variables():
    with open(variables_file, 'w') as file:
        file.write(f'model_name = "{model_name}"\n')
        file.write(f'module_name = "{module_name}"\n')
        file.write(f'line_items = "{line_items}"\n')
        file.write(f'format = "{format}"\n')
        file.write(f'formula = "{formula}"\n')
        file.write(f'summary_mthd = "{summary_mthd}"\n')
        file.write(f'applies_to = "{applies_to}"\n')
        file.write(f'list_aux = "{list_aux}"\n')
        file.write(f'time_scale = "{time_scale}"\n')
        file.write(f'versions = "{versions}"\n')
        file.write(f'time_dim = "{time_dim}"\n')

def get_user_prompt_from_file(file_path):
    with open(file_path, 'r') as file:
        user_prompt = file.read()
    combined_prompt = (
        "1. Below this prompt you will receive a natural language prompt from the user, you will transform the user's prompt into variables compatible with python code, the variables are the following: model_name, module_name, line_items, format, formula, summary_mthd, applies_to, time_scale, and versions. Take in consideration all these variables will be used in python code, so make their formatting compatible with python code.\n"
        "2. summary_mthd means summary method, the applies_to might be referred to as 'list', 'lists', or 'apply the lists' by the user.\n "
        "3. The variable model_name will always contain one value only, meaning this is not a list variable"
        "4. The variable module_name can either contain one single value or more. When it has a single value your output for this variable has the following formatting: module_name = 'name of the module', when the user specifies more than one value, then you will save this as a python list variable like this module_name = ['module A','module B'] (When there is one more than modulue, this will be treated as an especial case that will affect the rest of the variables, but will be discussed in step number 11 \n"
        "5. The line_items variable might be referred as line items by the users. This variable may contain one or more values, you save this as a list variable, even if only one line item is specified, for example one called element1, then the variable should be line_items = ['element1'], if more than one line item is specified, for example element1 and element2, then line_items = ['element1, element2']. \n"
        "6. The format variable will be a list variable, and it will contain the same amount of elements as there are line items, for example, for line_items = 'lement1, element2', the user might specify that the format for the first line item is Number, and the format for the second one is Text, then format = ['Number', 'Text'], however the user might not want to add format to all the line items, for line_items = 'element1, element2'assert, the user might say 'the format for the second line items is Text', in this case you will keep the format variable dimensions even with line_items, so it will be format = ['information needed', 'Text'], as the user only specified format for the second line item. Everytime a user does not specify information for one of the line items, you will populate that position with 'information needed' \n"
        "7. For formula variable, this will be a list variable which has to have the same amount of element as line_items variable. The user might specify the formulas for all the line items, or not. For example, if for line_items = 'element1, element2', the user says 'the formula (or value, sometimes formula might be referred as value) for the first element is 1+1, and for the second one 2+2', then formula = ['1+1','2+2']. If the users misses a formula for one of the line items, for example 'the formula for the second element is 2+2', them formula = ['information needed', '2+2'], always keeping the same amount of elements, as there are line items.\n"
        "8. The summary_mthd much like the format variable will be a list variable and it must have as many elements as there are line items. So, in the same way as the format variable, if there are 3 line items for example line_items = 'element1, element2, element3', and the user specifies the three of them as 'Sum for the first line item, Formula for the second one, and All for the third one', then summary_mthd = ['Sum', 'Formula', 'All] if there is still 3 line items, but the users says 'the summary method for the first is All', then summary_mthd = ['All', 'information needed', 'information needed'], keeping the dimensionality even.\n"
        "9. For applies_to (which the user might refer as lists) there will be an exception: dimensionality should not be kept as far as the amount of line items goes. If the user does not mention no lists at all, for a given module, then the variable will be applies_to = 'information needed', so it's a simple string saved in the variable, no matter how many line items there are. The same applies in case the user does specify lists for example: 'I want to add the lists Users and Organization to my module', then the variable will be saved as a list like this, applies_to = ['Users', 'Organization'], just like that no matter how many line items there are, there is no need to add 'information needed' for this list variable elements. 'information needed' will be only assigned as a string when the user does not mention no lists at all.\n"
        "10. For the variable list_aux, the information will come from applies_to, this will take the values from applies_to and save them a simple, not a nested string, and will also remove repeated values, for example if 'applies_to = [['Organization', 'Users'], ['information needed'], ['Products', 'Geography', 'Countries','Users','Organization']]' then you will take those values and save them just once in list_aux, making sure there are no duplicates, do not include 'information needed', but include everything else, so in this case based on that applies_to, list_aux will look like this list_aux = ['Organization','Users','Products','Geography','Countries]. Carefully review all the values of applies_to, one by one, and do not miss a single one when composing list_aux, review individually every single element of the nested list applies_to, at least 3 times."
        "11. For time_scale and versions, please apply the same principles from numeral 6,7,8, the same principles to formatting format, formula and summary_mthd. Where dimensionality should be kept accordingly to the amount of line items. \n"
        "12. For time_dim, this variable will contain one value per module, that value can only either be True or False. It's dimensionality (amount of items within the list variable) should be the same as the modules, hence if there is one module, then just one value, two module, then two values. The variable default value will be True for all modules.The True or False value will depend on wether the user specifies using Time as a module dimension, if the user doesn't specify that, then the value should be True, or if the user says they DO want to use Time as a dimension for a module, then its value will be True as well. The value will be false only when the user says they want to remove time as a dimension. The user might say in the prompt: 'There will be 2 modules, module A and Module B, I want to use time as a dimension for module B'. In this case, we have two modules, and Time as a dimension is only specified for Module B, so the variable will look like this time_dim = ['True','True']. We have two values, True corresponding to module A, as the user did not mention time as a dimension, and True for module B, since the user said he wanted to use Time as a dimension. Here's another example: 'There will be 2 modules, module A and Module B, I want to remove time as a dimension for module B'. In this last example, the variable will look like time_dim = ['True','False'], the value is only false when the user explicitly says to remove Time as a dimension.  \n"
        "13. Special case: when there is two modules or more, for example: module_name = ['module A','module B'], then the rest of the variables will be affected and will turn into nested variables. Each sublist within them will correspond to one of the modules. A good example is 'I want to use the model called Auto Builder 3, and I want to create 2 modules, one called Module A and another called Module B. Module A will have 3 line items: bread, meat, eggs. The format for the first one is Number, and for the third one is Text. The formula will be 1+1 for the first one, and 2+2 for the second one. The summary method will be Sum for the first two, the list added will be Organization and Users. The time scale will be Day for all line items. Now for Module B, there will be 2 line items: hand, feet. The format will be Number for both of them, the formula will be 1+1 and 2+3. The time scale will be Day and Month. The version for the second one will be All' In this scenario your output will be: \n"
        "model_name = 'Auto Builder 3'"
        "module_name = ['module A', 'module B']"
        "line_items = [['bread', 'meat', 'eggs'],['hand','feet']]"
        "format = [['Number', 'information needed', 'Text'],['Number', 'Number']]"
        "formula = [['1+1', '2+2', 'information needed'],['1+1', '2+3']]"
        "summary_mthd = [['Sum','Sum','information needed'], ['information needed','information needed','information needed']]"
        "applies_to = [['Organization','Users'], ['information needed']]"
        "list_aux = ['Organization','Users']"
        "time_scale = [['Day', 'Day', 'Day'], ['Day', 'Month']]"
        "versions = [['information needed', 'information needed', 'information needed'],['information needed', 'All']]"
        "time_dim = ['True','True']\n" 
        "14. You will only return the variables and their content in your response, nothing else, always making sure there is the same amount of opening brackets as closing brackets for each variable. Use one line per variable, no multiple lines" 

     + user_prompt
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

def parse_response(response):
    global model_name, module_name, line_items, format, formula, summary_mthd, applies_to, list_aux, time_scale, versions, time_dim

    def extract_field(pattern, response, field_name):
        match = re.search(pattern, response)
        if match:
            return match.group(1).strip()
        else:
            print(f"Warning: {field_name} not found in the response.")
            return "[information needed]"

    model_name = extract_field(r'model_name = (.+)', response, "model_name")
    module_name = extract_field(r'module_name = (.+)', response, "module_name")
    line_items = extract_field(r'line_items = (.+)', response, "line_items")
    format = extract_field(r'format = (.+)', response, "format")
    formula = extract_field(r'formula = (.+)', response, "formula")
    summary_mthd = extract_field(r'summary_mthd = (.+)', response, "summary_mthd")
    applies_to = extract_field(r'applies_to = (.+)', response, "applies_to")
    list_aux = extract_field(r'list_aux = (.+)', response, "list_aux")
    time_scale = extract_field(r'time_scale = (.+)', response, "time_scale")
    versions = extract_field(r'versions = (.+)', response, "versions")
    time_dim = extract_field(r'time_dim = (.+)', response, "time_dim")

    # Convert the line_items into a list
    line_items_list = [item.strip() for item in line_items.split(",")]

    # List of fields to be repeated if necessary
    fields_to_repeat = [format, formula, summary_mthd, time_scale, versions]

    # Ensure each field is repeated for each line item if it's a single value
    repeated_fields = []
    for field in fields_to_repeat:
        if len(field.split(",")) == 1:
            repeated_fields.append(", ".join([field] * len(line_items_list)))
        else:
            repeated_fields.append(field)

    # Assign repeated values back to the respective variables
    format, formula, summary_mthd, time_scale, versions = repeated_fields

    return model_name, module_name, line_items, format, formula, summary_mthd, applies_to, list_aux, time_scale, versions, time_dim

def main():
    user_prompt = get_user_prompt_from_file(user_input_file)
    chatgpt_response = get_chatgpt_response(user_prompt)

    if chatgpt_response:
        print("ChatGPT response:", chatgpt_response)
        
        # Parse the response to extract variables
        model_name, module_name, line_items, format, formula, summary_mthd, applies_to, list_aux,time_scale, versions, time_dim = parse_response(chatgpt_response)
        
        # Print the extracted variables
        print("\nExtracted Variables:")
        print("model_name: ", model_name)
        print("module_name: ", module_name)
        print("line_items: ", line_items)
        print("format: ", format)
        print("formula: ", formula)
        print("summary method: ", summary_mthd)
        print("Applies to: ", applies_to)
        print("Auxiliary list: ", list_aux)
        print("Time Scale: ", time_scale)
        print("Versions: ", versions)
        print("Time as dimension: ", time_dim)
        save_variables()
        print("Variables completed")  # Print statement
        with open("progress.txt", "w") as progress_file:
            progress_file.write("10")  # Update progress to 10%
        return "success"
    else:
        print("Error: No response from OpenAI.")
        return "error"

if __name__ == "__main__":
    main()
