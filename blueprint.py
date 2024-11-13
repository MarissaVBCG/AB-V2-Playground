#Adding function to select the list, when the format is Lists
from pyvirtualdisplay import Display
import os
import ast
import re
import platform
import shutil
from formula_loader import load_formulas
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
import pyperclip

logging.debug("Virtual display set up complete.")

# Import Selenium and other dependencies
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


# Utility function to generate user-specific file paths
def user_specific_file(filename):
    user_id = os.getenv('USER_ID', 'default_user')  # USER_ID is passed via environment variables
    user_dir = os.path.join(os.getcwd(), user_id)  # Create a folder for each user

    # Ensure the user-specific directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    return os.path.join(user_dir, filename)  # Return the file path within the user folder


#Read variables from variables.txt
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

#Define global file directory
file_path = user_specific_file('variables.txt')


parse_variables(file_path)

#Pull variable and save them to be used later on in the code
model_name = variables['model_name']
module_name = variables['module_name']      
line_items_input = variables['line_items']
format = variables['format']
# formula = variables['formula']
summary_mthd = variables['summary_mthd']
applies_to = variables['applies_to']
time_scale = variables['time_scale']
versions = variables['versions']

# Set up Chrome options
options = Options()
options.add_argument("--no-sandbox")  # Required for Docker
options.add_argument("--disable-dev-shm-usage")  # Mitigate memory issues
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-gpu")  # For compatibility
options.add_argument("--disable-software-rasterizer")  # Helps with Docker environments
options.add_argument("--log-level=3")  # Suppress logging

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

# Setup WebDriver with user-specific Chromedriver binary
service = Service(executable_path=user_chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)
actions = ActionChains(driver)


# HTML elements necessary for selenium to interact with Anaplan

#         CLASSNAMES
iframe_className = "ShellContent_iframe__rn6Ss" #necessary
child_frame_className = "_iframe_19ved_2" #Necessary

#Open the webdriver
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
#                   HARDCODED LOGIN ENDS
#==================================================================


# ==================================================================
#              Load cookies for login (user-specific)
# ==================================================================
# with open(user_specific_file("anaplan_cookies.pkl"), "rb") as file:
#     cookies = pickle.load(file)
#     for cookie in cookies:
#         driver.add_cookie(cookie)

# Refresh the page to apply cookies
# driver.refresh()

# time.sleep(5)
# ==================================================================


#Open the workspace
with open(user_specific_file("new_page_url.txt"), "r") as file:
    new_page_url = file.read().strip() 
driver.get(new_page_url)

time.sleep(10)

#Pyautogui and Selenium Navigation Functions

def modules_btn():
    timeout=60
    start_time = time.time()

    while True:
        try:
            location = pyautogui.locateCenterOnScreen('modules_btn.png', confidence=0.7)
            if location is not None:
                print(f"modules_btn.png found in {time.time() - start_time } seconds.")
                pyautogui.click(location)
                return location

        except pyautogui.ImageNotFoundException as e:
            print(f"Image not found {e} and {time.time() - start_time} seconds have passed")

        # Check if 60 secs have passed
        if time.time() - start_time > timeout:
            pyautogui.screenshot(user_specific_file('ss_error.png'))
            raise pyautogui.ImageNotFoundException(f"modules_btn.png not found within {timeout} seconds.")

        # Tries every other hald second
        time.sleep(0.5)


def select_module(child_frame_className,module_name,iframe_className): 
    iframe3 = WebDriverWait(driver, 5).until(
				EC.presence_of_element_located((By.CLASS_NAME, iframe_className))     
			)
    driver.switch_to.frame(iframe3)
    time.sleep(3)
    child_frame = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, child_frame_className))     
                )
    driver.switch_to.frame(child_frame)
    if isinstance(module_name,list): #if there is more than 1 module, select the first one
        module_name_xpath = f"//*[text()='{module_name[0]}']"
    else: #if only one, treat variable as a simple string
        module_name_xpath = f"//*[text()='{module_name}']"

    select_module = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, module_name_xpath))
        )
    select_module.click()
    time.sleep(3)

def open_module_btn():
    timeout=60
    start_time = time.time()

    while True:
        try:
            location = pyautogui.locateCenterOnScreen('open_module_btn.png', confidence=0.7)
            if location is not None:
                print(f"open_module_btn.png found in {time.time() - start_time } seconds.")
                pyautogui.click(location)
                time.sleep(3)
                module_url = driver.current_url
                return module_url

        except pyautogui.ImageNotFoundException as e:
            print(f"Image not found {e} and {time.time() - start_time} seconds have passed")

        # Check if 60 secs have passed
        if time.time() - start_time > timeout:
            pyautogui.screenshot(user_specific_file('ss_error.png'))
            raise pyautogui.ImageNotFoundException(f"open_module_btn.png not found within {timeout} seconds.")

        # Tries every other hald second
        time.sleep(0.5)




def go_to_next_module(module_url): #Modifies previous module ULR but adding +1 to the URL and go to the next module
    last_url_number = re.search(r'/(\d+)$', module_url).group(1) #grabs last number of the module URL
    new_number = str(int(last_url_number) + 1)#it adds module_index and turns it into a string
    next_module_url = re.sub(r'(\d+)$', new_number, module_url) #saves into a new variable as a string
    driver.get(next_module_url) #Navigate to the next module, using its URL directly
    time.sleep(4)
    print(next_module_url) #Delete later, testing purposes only

def get_module_url(): #Captures current page URL
    return driver.current_url

def bp_btn():
    timeout=60
    start_time = time.time()

    while True:
        try:
            location = pyautogui.locateCenterOnScreen('bp_btn.png', confidence=0.7)
            if location is not None:
                print(f"bp_btn.png found in {time.time() - start_time } seconds.")
                pyautogui.click(location)
                return location

        except pyautogui.ImageNotFoundException as e:
            print(f"Image not found {e} and {time.time() - start_time} seconds have passed")

        # Check if 60 secs have passed
        if time.time() - start_time > timeout:
            pyautogui.screenshot(user_specific_file('ss_error.png'))
            raise pyautogui.ImageNotFoundException(f"bp_btn.png not found within {timeout} seconds.")

        # Tries every other hald second
        time.sleep(0.5)

def ok_button():
    timeout=60
    start_time = time.time()
    region = (1000, 600, 400, 400)
    time.sleep(0.7)


    while True:
        try:
            time.sleep(2)
            location = pyautogui.locateCenterOnScreen('ok.png', confidence=0.77, region=region)
            if location is not None:
                print(f"okformat_1.png found in {time.time() - start_time } seconds.")
                print(f"This is the location {location}")
                pyautogui.click(location)
                return location

        except pyautogui.ImageNotFoundException as e:
            print(f"Image not found {e} and {time.time() - start_time} seconds have passed")

        # Check if 60 secs have passed
        if time.time() - start_time > timeout:
            pyautogui.screenshot(user_specific_file('ss_error.png'))
            raise pyautogui.ImageNotFoundException(f"okformat_1.png not found within {timeout} seconds.")

        # Tries every other hald second
        time.sleep(0.5)

def click_on_cell():
    timeout=60
    start_time = time.time()

    while True:
        try:
            location = pyautogui.locateCenterOnScreen('number_cell.png', confidence=0.8)
            if location is not None:
                print(f"number_cell.png found in {time.time() - start_time } seconds.")
                pyautogui.click(location)
                return location

        except pyautogui.ImageNotFoundException as e:
            print(f"Image not found {e} and {time.time() - start_time} seconds have passed")

        # Check if 60 secs have passed
        if time.time() - start_time > timeout:
            pyautogui.screenshot(user_specific_file('ss_error.png'))
            raise pyautogui.ImageNotFoundException(f"number_cell.png not found within {timeout} seconds.")

        # Tries every other hald second
        time.sleep(0.5)

def parse_formats(formats):
    if formats.startswith('List'):
        format_list = ''
        if '(' in formats and ')' in formats:
            start_index = formats.find('(') + 1
            end_index = formats.find(')', start_index)
            if end_index != -1:
                format_list = formats[start_index:end_index].strip()
        # Change the content of formats to List only,to be properly typed in the blueprint
        formats = 'List'
        return formats, format_list
    else:
        return formats, None

def give_format(format, module_index, ok_button, click_on_cell): #Applies format to each LI
    time.sleep(2)
    click_on_cell()
    time.sleep(4)
    for formats in format[module_index]:
        if formats != 'information needed':
            formats, format_list = parse_formats(formats)
            print(f"format: {formats}")
            print(f"list: {format_list}")
            pyautogui.write(formats, interval=0.20)
            enter_formatlist(format_list)
            ok_button()
            ok_button()
        time.sleep(0.7)    
        pyautogui.press('down')
        time.sleep(0.7)    

def enter_formatlist(format_list):
    if format_list != None: #This will only execulte when there is a list to be attached to the list format
        time.sleep(0.2)
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.write(format_list, interval=0.20)
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.2)
        print("\nList has been entered")

def go_to_next_atribute(format, module_index): #Goes to the top of the table and then to the right
    rows = 1
    while rows < len(format[module_index]):
        time.sleep(0.7)
        pyautogui.press('up')
        rows += 1
    time.sleep(0.7)
    pyautogui.press('right')    

def error_override():
    time.sleep(5)
    region = (1000, 600, 400, 400)
    time.sleep(0.7)

    for attempt in range(4):  # Tries to find the function 4 times
        try:
            location = pyautogui.locateCenterOnScreen('ok.png', confidence=0.9, region=region)
            if location is not None:
                print(f"ok button of error pop-up found.")
                print(f"This is the location {location}")
                pyautogui.click(location)
                break
            else:
                print(f"Attempt {attempt + 1}: no error found")
        except pyautogui.ImageNotFoundException:
            print(f"Attempt {attempt + 1}: ok button for error not found due to ImageNotFoundException.")
        time.sleep(0.4)
    # After 4 failed attempts, continue with the rest of the blueprint
    time.sleep(1)
    return

def enter_formula(formulas_dict, module_index, module_name):
    time.sleep(0.3)
    # Validate module_index is within modules qty range
    if module_index < 0 or module_index >= len(module_name):
        print(f"Error: module_index {module_index} is out of range.")
        return

    # Get the module name using the index
    module_name = module_name[module_index]
    print(f"Entering formulas for {module_name}")

    # Get the line items dictionary for the module
    line_items = formulas_dict[module_name]

    # Iterate over line items in the module
    for line_item, formula in line_items.items():
        print(f"This formula is: {formula} for the l.i. {line_item}")  # For testing purposes only
        if formula != 'information needed':
            print(formula)
            pyperclip.copy(formula)
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.15)
            error_override()
            pyautogui.press('down')
        else:
            pyautogui.press('down')



def enter_summary(summary_mthd, module_index): #Enter summary method for each LI
    for summaries in summary_mthd[module_index]:
        print(summaries) #Delete later, for testing purposes onlye
        if summaries != 'information needed':
            pyautogui.write(summaries, interval=0.15)
            pyautogui.press('enter')
            error_override()
        pyautogui.press('down')

def enter_lists(applies_to, module_index,ok_button): #Enter lists at the top of the grid, so lists apply to the module as a whole
    pyautogui.press('up')
    if len(applies_to[module_index])>1:
        joined_list = ", ".join(applies_to[module_index])
    else:
        joined_list = applies_to[module_index]
        joined_list = str(joined_list).strip("[]'")
    if joined_list != 'information needed':    
        pyautogui.write(joined_list, interval=0.15)
        pyautogui.press('enter')
        ok_button()
        error_override()
    pyautogui.press('right')

# def enter_timescale(time_scale, module_index,ok_button): #Enters timescame one by one
#     for timescales in time_scale[module_index]:
#         if timescales != 'information needed':
#             pyautogui.write(timescales, interval=0.15)
#             pyautogui.press('enter')
#             time.sleep(0.2)
#             ok_button()
#         elif timescales == 'information needed':     
#             pyautogui.press('down')

def enter_timescale(time_scale, module_index,ok_button): #Enters timescame one by one
    time.sleep(0.2)
    pyautogui.press('up')
    time.sleep(0.2)
    pyautogui.keyDown('shift')
    time.sleep(0.2)
    for timescales in time_scale[module_index]:
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.keyUp('shift')
    time.sleep(0.2)
    pyperclip.copy(time_scale[module_index][0])
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.15)
    ok_button()
    error_override()
    pyautogui.press('right')

    


def enter_timerange(time_range, module_index, ok_button): #Function to enter timerange ready, but not used yet
    for timeranges in time_range[module_index]:
        if timeranges != 'information needed':
            pyautogui.write(timeranges, interval=0.15)
            pyautogui.press('enter')
            ok_button()
            error_override()  
        pyautogui.press('down')

# def enter_version(versions, module_index, ok_button): #Versions typed in for each of the LI
#     for version in versions[module_index]:
#         if version != 'information needed':
#             pyautogui.write(version, interval=0.15)
#             pyautogui.press('enter')
#             ok_button()
#         elif version == 'information needed':     
#             pyautogui.press('down')


def enter_version(versions, module_index, ok_button): #Versions typed in for each of the LI
    time.sleep(0.2)
    pyautogui.press('up')
    time.sleep(0.2)
    pyautogui.keyDown('shift')
    time.sleep(0.2)
    for version in versions[module_index]:
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.keyUp('shift')
    time.sleep(0.2)
    pyperclip.copy(versions[module_index][0])
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.15)
    ok_button()
    error_override()
    pyautogui.press('right')

def write_progress(module_qty, percentage): #Function to write the percentage to the progress.txt
   
    if module_qty == 1: #If there is only one module 6.89 will be added after each attribute is done, adding up to the missing 41%
        percentage = percentage + 8 #percentage passed to this function will be 41% to begin, and adds up 6.89 with each atribute finnished
        with open(user_specific_file("progress.txt"), "w") as progress_file:
            progress_file.write(str(int(percentage)))  # Convert percentage to string before writing
    elif module_qty > 1: #if there is 1 more than module, then:
        progress_per_atr = 8/module_qty #the progress per atribute is divided by the amount of modules, so it adds up an the end
        percentage = percentage + progress_per_atr
        with open(user_specific_file("progress.txt"), "w") as progress_file:
            progress_file.write(str(int(percentage)))  # 
    print(percentage)       
    return int(percentage) #percentage is returned so the variable keeps record of its own previous value, and it can be modified according to the times the function is executed



#=====================================================================#
#                             Main program Sequence                   #
#=====================================================================#


json_file = user_specific_file('formulas.json') #paht for the Json file

# Step 1: Load the formulas from the JSON file
formulas = load_formulas(json_file)

######## APPLICABLE FOR 1st MODULE ONLY ##############
module_qty = len(module_name) #Calculates the amount of modules
percentage = 41
modules_btn() #Clicks on the Modules button
select_module(child_frame_className,module_name,iframe_className) #selects 1st module that was created
module_url = open_module_btn() #Clicks on Open button and saves 1st module URL in that variable
bp_btn()
module_index = 0 #Points to the first module
if line_items_input[module_index]:  #Checks if there are line items within that specific module
    give_format(format, module_index, ok_button, click_on_cell) #Gives format to all line items
    percentage = write_progress(module_qty, percentage)

    go_to_next_atribute(format, module_index) #Moves to the top of the grid, and to the next attribute
    enter_formula(formulas, module_index, module_name) #Types all formulas for all line items
    percentage = write_progress(module_qty, percentage)

    go_to_next_atribute(format, module_index) #Moves to the top of the grid, and to the next attribute
    enter_summary(summary_mthd, module_index) #Types all summary methods for all line items
    percentage = write_progress(module_qty, percentage)

    go_to_next_atribute(format, module_index) #Moves to the top of the grid, and to the next attribute
    enter_lists(applies_to, module_index,ok_button)
    percentage = write_progress(module_qty, percentage)

    enter_timescale(time_scale, module_index,ok_button)
    percentage = write_progress(module_qty, percentage)

    # go_to_next_atribute(format, module_index) #Moves to the top of the grid, and to the next attribute
    pyautogui.press('right') #This line skips Time Range for now
    enter_version(versions, module_index, ok_button)
else:
    pass    
percentage = write_progress(module_qty, percentage)


if module_qty == 1:  #if the amount of modules is just one, then it will write 100% to the progress bar after the BP for that module is done
    if percentage < 100:
        percentage = 100
        with open(user_specific_file("progress.txt"), "w") as progress_file:
            progress_file.write(str(int(percentage)))  # Convert percentage to string before writing
        print(percentage)
###########    The program ends here if there is only one single module   ######################################

############ 1st MODULE BP ENDS #################

################# MULTIPLE MODULES STARTS #########################################
#This section will run only if there is 2 or more modules
#Navigation among modules changes, and it uses the direct URL instead of Selenium, starting from the 2nd Module that was created

if isinstance(module_name,list): #This only runs if there is more than 1 module.
    module_index = 1 #Pointer used to go to the second module
    while module_index < module_qty: #Execution of this until it's gone to all modules saved in the array
        go_to_next_module(module_url) #Navigates to the next modules using its URL
        if line_items_input[module_index]: #Checks if there are line items within that specific module

            bp_btn() #Clicks on the blueprint button
            give_format(format, module_index, ok_button, click_on_cell) #Types in all formats
            percentage = write_progress(module_qty, percentage)

            go_to_next_atribute(format, module_index) #Goes to top of grid and next attribute
            enter_formula(formulas, module_index, module_name) #Types in all formulas
            percentage = write_progress(module_qty, percentage)

            go_to_next_atribute(format, module_index) #Goes to top of grid and next attribute
            enter_summary(summary_mthd, module_index) #Enter all summary methods
            percentage = write_progress(module_qty, percentage)

            go_to_next_atribute(format, module_index)#Goes to top of grid and next attribute
            enter_lists(applies_to, module_index,ok_button)
            percentage = write_progress(module_qty, percentage)

            enter_timescale(time_scale, module_index,ok_button)
            percentage = write_progress(module_qty, percentage)

            # go_to_next_atribute(format, module_index) #Moves to the top of the grid, and to the next attribute
            pyautogui.press('right') #This line skips Time Range for now
            enter_version(versions, module_index, ok_button)
        else:
            pass    
        percentage = write_progress(module_qty, percentage)

        module_url = get_module_url() #Onces it's done with the BP grid, get the current module URL 
        module_index += 1 #It points to the next module after the 1st while iteration, and blueprint while executes the same for the following module, until all modules' BP is done


time.sleep(10)
# 
print("Blueprint changes completed")	

if percentage < 100:
    percentage = 100
    with open(user_specific_file("progress.txt"), "w") as progress_file:
        progress_file.write(str(int(percentage)))  # Convert percentage to string before writing
    print(percentage)
    driver.quit()
################# MULTIPLE MODULES ENDS ##############################################

# Stop virtual display at the end of the script
disp.stop()