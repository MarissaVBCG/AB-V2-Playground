import json
import os


# Utility function to generate user-specific file paths
def user_specific_file(filename):
    user_id = os.getenv('USER_ID', 'default_user')  # USER_ID is passed via environment variables
    user_dir = os.path.join(os.getcwd(), user_id)  # Create a folder for each user

    # Ensure the user-specific directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    return os.path.join(user_dir, filename) 

def load_formulas(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The  '{file_path}' for json formumulas does not exist.")
        return None
    try:
        with open(file_path, 'r') as file:
            formulas = json.load(file)
        return formulas
    except json.JSONDecodeError as e:
        print(f"Error reading the JSson: {e}")
        return None




def main():

    json_file = user_specific_file('formulas.json')
    
    formulas = load_formulas(json_file)
    if formulas is None:
        return
    


if __name__ == "__main__":
    main()
