import openai
import os
import logging
from apilist import get_existing_lists
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import platform
import shutil

logging.basicConfig(level=logging.DEBUG)

from pyvirtualdisplay import Display
# Retrieve the user-specific display number from the environment variable
display_num = os.getenv('DISPLAY_NUM', ':99')

# Start Xvfb on the user-specific display
logging.debug("Setting up virtual display...")
disp = Display(visible=False, size=(1920,1080), backend="xvfb", use_xauth=True)
disp.start()

# Set the DISPLAY environment variable
os.environ['DISPLAY'] = disp.new_display_var
logging.debug(f"DISPLAY set to: {os.environ['DISPLAY']}")
print("DISPLAY environment variable:", os.environ["DISPLAY"])



# Proceed with the rest of your imports and script
import Xlib.display
import pyautogui._pyautogui_x11
pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])
import pyautogui

logging.debug("Virtual display set up complete.")

# Selenium Modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
import pickle
from selenium.webdriver.chrome.options import Options

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

# Use the saved key for encryption and decryption
encryption_key = os.environ.get('ENCRYPTION_KEY').encode()
cipher_suite = Fernet(encryption_key)

# Utility function to generate user-specific file paths
def user_specific_file(filename):
    """Generate a user-specific folder and file path based on the USER_ID."""
    user_id = os.getenv('USER_ID', 'default_user')  # USER_ID is passed via environment variables
    user_dir = os.path.join(os.getcwd(), user_id)  # Create a folder for each user

    # Ensure the user-specific directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    return os.path.join(user_dir, filename)

def selenium_part(): 
    # Set up Chrome options
    options = Options()
    options.add_argument("--no-sandbox")  # Required for Docker
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-dev-shm-usage")  # Mitigate memory issues
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")  # For compatibility
    options.add_argument("--disable-software-rasterizer")  # Helps with Docker environments
    options.add_argument("--log-level=3")  # Suppress logging
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Dynamically copy Chromedriver to user-specific folder
    if platform.system() == "Windows":
        chromedriver_name = "chromedriver.exe"
    else:
        chromedriver_name = "chromedriver"

    central_chromedriver_path = os.path.join(os.getcwd(), chromedriver_name)
    user_chromedriver_path = user_specific_file(chromedriver_name)
    if not os.path.exists(user_chromedriver_path):
        shutil.copy(central_chromedriver_path, user_chromedriver_path)

    # Setup WebDriver with user-specific Chromedriver binary
    service = Service(executable_path=user_chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    ############################################################

    ############ Open Page and goes to module ###################
    driver.maximize_window()

    # Navigate to the login page (or any page that requires login)
    driver.get("https://us1a.app.anaplan.com/auth/prelogin?service=https://us1a.app.anaplan.com/home")


    #==================================================================
    #                HARDCODED LOGIN FOR TESTING
    #==================================================================

    search = driver.find_element(By.ID, "email-prelogin")
    search.send_keys("jose.monge@vb-cg.com")
    search.send_keys(Keys.ENTER)

    time.sleep(5)

    password_input= WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
    password_input.send_keys("Anaplan24!")

    time.sleep(5)

    driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/form/button").click()

    time.sleep(10)
#==================================================================
#==================================================================




# #==================================================================
# #              Load cookies for login (user-specific)
# #==================================================================
#     with open(user_specific_file("anaplan_cookies.pkl"), "rb") as file:
#         cookies = pickle.load(file)
#         for cookie in cookies:
#             driver.add_cookie(cookie)
#     # Refresh the page to apply cookies
#     driver.refresh()

#     time.sleep(5)
# #==================================================================
   

    # Now navigate directly to the desired workspace URL (user-specific)
    logging.debug("Navigating to the workspace URL from new_page_url.txt.")
    with open(user_specific_file("new_page_url.txt"), "r") as file:
    # with open(("new_page_url.txt"), "r") as file: #For local version only

        new_page_url = file.read().strip()
    driver.get(new_page_url)

    time.sleep(5)

    module_click_xpath = "//html/body/div[1]/div/div/div[2]/article/div[1]/div/div[1]/div/div[1]/div/div/nav[1]/ul/li[3]/button"
    iframe_className = "ShellContent_iframe__rn6Ss"
    child_frame_className = "_iframe_19ved_2"

    # Wait for the iframe to appear
    logging.debug("Waiting for iframe to load.")
    iframe3 = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.CLASS_NAME, iframe_className))     
			)
    driver.switch_to.frame(iframe3)

    time.sleep(3)

    # Click on the modules element
    logging.debug("Attempting to click on the modules element.")
    modules_click = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, module_click_xpath))
    ).click()

    time.sleep(10)

def quit_driver():
    time.sleep(0.85)
    pyautogui.hotkey('ctrl', 'w')

    ############################################################    

def read_variables(file_path): #Read lists from variables file
    variables = {}

    with open(file_path, 'r') as file:
        for line in file:

            if not line or "=" not in line:
                continue

            name, value = line.split("=",1)
            name = name.strip()
            value = value.strip().strip('"')

            if ',' in value:
                value = [item.strip() for item in value.split(",")]
            else:
                value = value.strip()

            variables[name] = value
        return variables

def send_text_and_prompt(prompt): #Function that sends text and prompt to gpt
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error getting response from OpenAI: {e}")
        return None

def check_and_add(it_exists, lists_to_add):
    # Normalize the response by stripping any punctuation or extra characters like periods.
    normalized_response = it_exists[1].strip().lower().rstrip('.')

    # If the response is "no", add the first element of it_exists to lists_to_add
    if normalized_response == "no":
        # Clean up the string to remove extra brackets and single quotes
        clean_value = it_exists[0].replace("[", "").replace("]", "").replace("'", "").strip()
        
        # Append the cleaned value to the list
        lists_to_add.append(clean_value)
        print(f"Added '{clean_value}' to lists_to_add.")  # Debugging output

    return lists_to_add

def add_lists(lists_to_add):
    # Insert log to track the detection process
    logging.debug("Looking for insert_list.png to add lists.")
    
    x,y = pyautogui.locateCenterOnScreen("insert_list.png", confidence=0.7)
    pyautogui.click(x,y)
    logging.debug("insert_list.png found, proceeding to click and add lists.")
    time.sleep(3)
    if isinstance(lists_to_add,list):
        for lists in lists_to_add:
            pyautogui.write(lists,interval=0.15)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
    else:
        pyautogui.write(lists_to_add,interval=0.15)
        time.sleep(1)
    x,y = pyautogui.locateCenterOnScreen('okformat_1.png', confidence=0.8)
    pyautogui.click(x,y)

def add_top_level(lists_to_add):
    time.sleep(0.3)
    x,y = pyautogui.locateCenterOnScreen('toplevel.png',confidence=0.8)
    pyautogui.click(x,(y+25))
    pyautogui.press('down')
    for new_lists in lists_to_add:
        time.sleep(0.2)
        pyautogui.write('All', interval=0.15)
        time.sleep(0.2)
        pyautogui.press('down')


def load_credentials_from_file():
    credentials_file = user_specific_file('credentials.enc')
    if os.path.exists(credentials_file):
        with open(credentials_file, 'rb') as f:
            encrypted_email, encrypted_password = f.read().split(b'\n')
            return encrypted_email, encrypted_password
    return None, None

def user_specific_file(filename):
    """Generate a user-specific folder and file path based on the user_id."""
    base_dir = os.getcwd()  # Get current working directory
    user_id = os.getenv('USER_ID', 'default_user')  # Get USER_ID from environment variables
    user_dir = os.path.join(os.getcwd(), user_id)  # Create a folder for each user

    # Ensure the user-specific directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    return os.path.join(user_dir, filename)  # Return the file path within the user folder

def decrypt_credentials(encrypted_email, encrypted_password):
    return cipher_suite.decrypt(encrypted_email).decode(), cipher_suite.decrypt(encrypted_password).decode()

def workspace_and_model():
    with open(user_specific_file("new_page_url.txt"), "r") as file:
    # with open(("new_page_url.txt"), "r") as file: #For local version

        new_page_url = file.read().strip()
    # Extract workspace_id
    workspace_id = new_page_url.split("workspaces/")[1].split("/")[0]
    #Extract model_id
    model_id = new_page_url.split("models/")[1].split("/")[0]
    return workspace_id, model_id

def main(): #Main program execution
    
    # encrypted_email, encrypted_password = load_credentials_from_file()
    # username, password = decrypt_credentials(encrypted_email, encrypted_password)
    username = "jose.monge@vb-cg.com"
    password = "Anaplan24!"
    workspace_id, model_id = workspace_and_model()
    file_path = user_specific_file('variables.txt')
    variables = read_variables(file_path)
    list_aux = variables.get('list_aux')
    existing_lists = get_existing_lists(username, password, workspace_id, model_id)
    print(f"The list in the module are: {existing_lists}")
    print(f"The list requested by the user are: {list_aux}")
   
    selenium_part() #logs in, gets to model, takes screenshot

    if isinstance(list_aux,list):
        lists_to_add = []
        for item in list_aux:
            
            prompt = f"Is the word '{item}' present in the table shown in this text {existing_lists}?, you will just reply with yes or no, only"
            print(f"Checking the list {item} with ChatGPT")
            print(f"Trying with this prompt: {prompt}")  
            chat_gpt_reponse = send_text_and_prompt(prompt)

            if chat_gpt_reponse:
                print(f"The list '{item}' exist in Model: {chat_gpt_reponse}\n")
                it_exists = [item, chat_gpt_reponse]
                print(f"Combination: {it_exists}")
                lists_to_add = check_and_add(it_exists, lists_to_add)
            else:
                print("Error: No response from OpenAI")
            
        print("Final lists_to_add:", lists_to_add)
    
    else:
        prompt = f"Is the word {list_aux} present in the table shown in this text {existing_lists}?, you will just reply with yes or no, only"
        print(f"Checking the list {list_aux} with ChatGPT")
        chat_gpt_reponse = send_text_and_prompt(prompt)
        if chat_gpt_reponse == "No":
            lists_to_add = list_aux
        else:
            lists_to_add = []
        
    print("Final lists_to_add:", lists_to_add)

    if len(lists_to_add) != 0:
        add_lists(lists_to_add)
        time.sleep(2)
        add_top_level(lists_to_add)
        time.sleep(5)
    else:
        pass
    quit_driver()
       


# Update user-specific progress.txt to 35%
with open(user_specific_file("progress.txt"), "w") as progress_file:
    progress_file.write("35")



if __name__ == "__main__":
    main()

# Stop virtual display at the end of the script
disp.stop()