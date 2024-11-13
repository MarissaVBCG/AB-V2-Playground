from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pickle
import time
import os
import ast
from selenium.webdriver.common.keys import Keys
import shutil
import platform
import logging


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

# Proceed with the rest of your imports and script
import Xlib.display
import pyautogui._pyautogui_x11
pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])
import pyautogui

logging.debug("Virtual display set up complete.")

# Utility function to generate user-specific file paths
def user_specific_file(filename):
    user_id = os.getenv('USER_ID', 'default_user')  # USER_ID is passed via environment variables
    user_dir = os.path.join(os.getcwd(), user_id)  # Create a folder for each user

    # Ensure the user-specific directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    return os.path.join(user_dir, filename)  # Return the file path within the user folder

# Dictionary to store the variables after evaluation
variables = {}

# Function to parse the file and evaluate variables
def parse_variables(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            # Split each line at the '=' to get the variable name and value
            if '=' in line:
                var_name, var_value = line.split('=', 1)
                
                # Strip extra spaces and newlines
                var_name = var_name.strip()
                var_value = var_value.strip()
                
                # Remove any enclosing quotes from strings (like the model_name variable)
                if var_value.startswith('"') and var_value.endswith('"'):
                    var_value = var_value[1:-1]
                
                # Evaluate the value safely using ast.literal_eval
                try:
                    parsed_value = ast.literal_eval(var_value)
                except (ValueError, SyntaxError):
                    # In case of any failure to parse, keep it as a string
                    parsed_value = var_value
                
                # Store the evaluated variable in the dictionary
                variables[var_name] = parsed_value

file_path = user_specific_file('variables.txt')
parse_variables(file_path)
model_name = variables['model_name']
module_name = variables['module_name']      
line_items_input = variables['line_items']
 
print(f'Model name: {model_name}')
print(f'Module name: {module_name}')
print(f'Line items: {line_items_input}')

#---- Variables, Xpath, Class.Names, and ID's START------------------------
# ClassNames
iframe_classname = "ShellContent_iframe__rn6Ss"
# XPaths
model_xpath = f"//*[text()='{model_name}']"
arrow_button_xpath = '/html/body/div/div/div[2]/main/div/div[2]/div/div[2]/div[1]/section/div/header/h2/div/div/h3'
#---- Variables, Xpath, Class.Names, and ID's END------------------------

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")  # Required for Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # Mitigate memory issues
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-gpu")  # For compatibility
chrome_options.add_argument("--disable-software-rasterizer")  # Helps with Docker environments
chrome_options.add_argument("--log-level=3")  # Suppress logging

# Determine the appropriate chromedriver based on the OS
if platform.system() == "Windows":
    chromedriver_name = "chromedriver.exe"
else:
    chromedriver_name = "chromedriver"

# Path to the central Chromedriver binary (shared location)
central_chromedriver_path = os.path.join(os.getcwd(), chromedriver_name)

# Dynamically copy Chromedriver to user-specific folder if not already copied
user_chromedriver_path = user_specific_file(chromedriver_name)
if not os.path.exists(user_chromedriver_path):
    shutil.copy(central_chromedriver_path, user_chromedriver_path)

# Setup WebDriver
service = Service(executable_path=user_chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
actions = ActionChains(driver)

driver.get(
    "https://us1a.app.anaplan.com/auth/prelogin?service=https://us1a.app.anaplan.com/home"
)
driver.maximize_window()


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
# with open(user_specific_file("anaplan_cookies.pkl"), "rb") as file:
#     cookies = pickle.load(file)
#     for cookie in cookies:
#         driver.add_cookie(cookie)
# # Refresh the page to apply cookies
# driver.refresh()

# time.sleep(5)
# #==================================================================



# Now navigate directly to the desired workspace URL
workspace_url = "https://us1a.app.anaplan.com/home"
driver.get(workspace_url)

time.sleep(20)

iframe = WebDriverWait(driver, 20).until(
   EC.presence_of_element_located((By.CLASS_NAME, iframe_classname))
)
driver.switch_to.frame(iframe)

arrow = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, arrow_button_xpath,))
)
arrow.click()

model = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, model_xpath))
).click()
new_page_url = driver.current_url
print(f"The new page URL is: {new_page_url}")

with open(user_specific_file("new_page_url.txt"), "w") as file:
    file.write(new_page_url)

time.sleep(3)

#clicks on Modules button
def click_modules():
    time.sleep(12)    
    x,y = pyautogui.locateCenterOnScreen('modules_btn.png',confidence=0.8) 
    pyautogui.click(x,y)
    time.sleep(0.5)

def create_module(module_name,line_items_input,index):
    time.sleep(1)
    x,y = pyautogui.locateCenterOnScreen('insertmodule_btn.png',confidence=0.7)     #Clicks on Insert Module
    pyautogui.click(x,y)
    time.sleep(0.5)
    if isinstance(module_name,list):     #Types in module name from list element indicated by index if more than 1 module
        pyautogui.write(module_name[index],interval=0.15)
    else:#Writes the only name in the variable, as a whole, if only one module
        pyautogui.write(module_name,interval=0.15)
    time.sleep(0.5)
    x,y = pyautogui.locateCenterOnScreen('lineitemsbox.png',confidence=0.7)#Clicks on line items input field    
    pyautogui.click(x,y)
    time.sleep(0.5)
    #Writes line items
    if any(isinstance(i, list) for i in line_items_input): #The if above checks if it's a nested list, if it is then we have multiple modules, so we enter the line items of the module indicated by index
        for item in line_items_input[index]:
            pyautogui.write(item,interval=0.15)
            pyautogui.press('enter')
    else:#Otherwise it is a simple list, indication of a single module requested, so no need of index, the for will iterate though the values
         for item in line_items_input:
            pyautogui.write(item,interval=0.15)
            pyautogui.press('enter')
    time.sleep(2)
    x,y = pyautogui.locateCenterOnScreen('ok.png', confidence=0.8) #Click on OK
    pyautogui.click(x,y)

### MAAIN PROGRAM ######
click_modules()
if isinstance(module_name, list):
    quantity = (len(module_name)-1)
    index = 0
    while index <= quantity:
        print(module_name[index])
        create_module(module_name,line_items_input,index)
        click_modules()
        index += 1
        time.sleep(4)
else:   
    index = 0
    create_module(module_name,line_items_input,index)

if __name__ == "__main__":
    time.sleep(5)
driver.quit()
print("Your module has been created successfully!")
# Update user-specific progress.txt to 30%
with open(user_specific_file("progress.txt"), "w") as progress_file:
    progress_file.write("30")

# Stop virtual display at the end of the script
disp.stop()