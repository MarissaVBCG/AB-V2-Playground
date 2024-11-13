import os

def run_script(script_name):
    os.system(f"python {script_name}")

def main():
    # Run all the required scripts in sequence
    run_script("elfSA.py")         # Process user_input.txt
    run_script("elfList.py")       # Generate lists
    run_script("elfModule.py")     # Create modules
    run_script("elfAppliesTo.py")  # Associate lists with modules
    run_script("elfLineItems.py")  # Creates line items
    run_script("elfBlueprint.py")  # Handle line item attributes
    run_script("elfFormulas.py")  # Creates and structures formulas
    
    # Run parsing.py after all the previous scripts
    run_script("elfParsing.py")    # Parsing 

    # Run JSON elf 
    run_script("elfJSON.py")

    #scripot to clean the json and remove all single quotes son Anaplan takes them 
    run_script("jsoncleaner.py")

if __name__ == "__main__":
    main()
