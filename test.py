from bs4 import BeautifulSoup
import json

# HTML string
html_string = '<img src="https://example.ru">'

# Parse the HTML string
soup = BeautifulSoup(html_string, 'html.parser')

# Extract the tag and its content
tag = soup.find()
tag_name = tag.name
children = [str(child) for child in tag.contents]

# Create a dictionary with the desired JSON-like structure
json_structure = {"tag": tag_name, "children": children}

# Convert the dictionary to JSON format
json_string = json.dumps(json_structure)

# Print the resulting JSON-like structure
print(json_string)