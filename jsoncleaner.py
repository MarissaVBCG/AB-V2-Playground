with open('default_user/formulas.json', 'r') as file:
    content = file.read()

# Remove all single quotes from the formulas
content_no_single_quotes = content.replace("'", "")

with open('default_user/formulas.json', 'w') as file:
    file.write(content_no_single_quotes)