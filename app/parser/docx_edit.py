import openai
import os
import random
from docx2python import docx2python, utilities
import re
from enum import Enum 
from docx import Document
from docx.text.run import Run
from lxml import etree
import shutil
import xml.etree.ElementTree as ET
import tempfile
import zipfile

class DocElements(Enum):
    EMAIL = "Email Address"
    DATETIME = "Date or Time"
    PHONE_NUMBER = "Phone Number"
    ADDRESS = "Address"
    FULL_NAME = "Full Name"
    PARAGRAPH = "Paragraph"
    HEADING = "Heading"
    UNKNOWN = "Unknown"
    IMAGE = "Image"
    HYPERLINK= "Hyperlink"

# Function to get a completion from davinci 
def generate_text(prompt: str, max_tokens: int):
        openai.api_key = os.environ.get("OPENAI_KEY", "")
        completion = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=prompt, 
            max_tokens=max_tokens, 
            echo=False, 
            stream=True
        )
        return completion 


# Function to classify a single text element  
def classify_text(input_string):
    # Regular expressions for different types
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    location_address_regex = r'\d{1,5}\s[\w\s]+\b(?:Avenue|ave|Road|road|Street|street|Crescent|crescent|Drive|drive|Boulevard|boulevard|Lane|lane|Place|place)\b'
    phone_number_regex = r'(?:(?:Tel|Fax)\s*)?(\+\d{1,3}\s?)?(\(?\d{1,4}\)?\s?)*\d{1,4}[\s-]?\d{1,4}[\s-]?\d{1,9}' 
    full_name_regex = r'\b[A-Z][a-z]+(\s[A-Z][a-z]+)+\b'
    date_time_regex = r'(?:(?:(?:(?P<month>\d{1,2})[-/.](?P<day>\d{1,2})|(?P<day_text>\d{1,2})(?:th|st|nd|rd)?\s*(?P<month_text>Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?))(?:[-/.]?(?P<year>\d{2,4}))?)|(?:\b(?P<weekday>Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)\b))|(?:\b(?P<time>(?P<hour>\d{1,2})(?::|\.)(?P<minute>\d{2})(?::|\.)(?P<second>\d{2})\s?(?P<am_pm>[AP]M)?\b))'
    image_regex = '----media\/([a-zA-Z0-9_-]+)\.(jpg|jpeg|png|gif)----'
    hyperlink_regex = '<a href="([^"]+)">([^<]+)<\/a>'
    # Check for matches
    if re.match(image_regex, input_string):
        return DocElements.IMAGE 
    elif re.match(hyperlink_regex, input_string):
        return DocElements.HYPERLINK
    elif re.match(email_regex, input_string):
        return DocElements.EMAIL 
    elif re.match(date_time_regex, input_string):
        return DocElements.DATETIME
    elif re.match(location_address_regex, input_string):
        return DocElements.ADDRESS 
    elif re.match(phone_number_regex, input_string):
        return DocElements.PHONE_NUMBER 
    elif re.match(full_name_regex, input_string):
        return DocElements.FULL_NAME 
    elif len(input_string.split()) <= 10:
        return DocElements.HEADING
    elif len(input_string.split()) > 10:
        return DocElements.PARAGRAPH
    else:
        return DocElements.UNKNOWN 

# given a string to replace, classify it and generate new text 
def classify_and_regenerate(text):
    text_type = classify_text(text)
    prompt = f"The follwing text is a {text_type} from a document. Please return a string containing a fake replacement value. It should be of similar length and style to the following text: {text}"
    return generate_text(prompt=prompt, max_tokens=2*len(prompt.split())) 

# save the images as well in a directory specific to each file 
def get_document_text(path_in):
    with docx2python(path_in) as doc:
        doc_txt = doc.text.split('\n')
        return [txt for txt in doc_txt if txt != '']

# for doing a mass replacement use no arguments 
# this iterates over every text run and generates a replacement 
def generate_replacements(path_in):
    replacements = []
    doc = docx2python(path_in)
    document_text = get_document_text(path_in=path_in)
    for txt in document_text:
        old_text = txt 
        new_text = classify_and_regenerate(txt)
        replacements.append(tuple([old_text, new_text]))
    return replacements

# open python2docx xml, iterate through all text runs, classify and regenerate,
# then replace text and save to output path 
def replace_text(path_in, path_out, replacements=None):
    reader = docx2python(path_in).docx_reader
    for file in reader.content_files():
        root = file.root_element
        # if no replacements then we simply go 
        # through everything 
        if replacements is None:
            replacements = generate_replacements(path_in=path_in)
        # otherwise use specific replacements provided 
        for replacement in replacements:
            utilities.replace_root_text(root, replacement[0], replacement[1])
    reader.save(path_out)
    reader.close()


# unused but interesting so I decided to keep it.
def replace_hyperlink_text_in_docx(docx_path, old_text, new_text):
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    # Extract docx file into temporary directory
    with zipfile.ZipFile(docx_path, 'r') as docx:
        docx.extractall(temp_dir)

    # Parse document.xml
    tree = ET.parse(os.path.join(temp_dir, 'word', 'document.xml'))
    root = tree.getroot()

    # Define XML namespaces
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }

    # Find all hyperlink elements
    for hyperlink in root.findall('.//w:hyperlink', namespaces):
        # Find all text elements within this hyperlink
        for text_elem in hyperlink.findall('.//w:t', namespaces):
            # If the text matches the old text, replace it with the new text
            if text_elem.text == old_text:
                text_elem.text = new_text

    # Write back modified XML to document.xml
    tree.write(os.path.join(temp_dir, 'word', 'document.xml'))

    # Create a new docx file with modified content
    #new_docx_path = docx_path.replace('.docx', '_modified.docx')
    with zipfile.ZipFile(docx_path, 'w') as docx:
        for folder, _, files in os.walk(temp_dir):
            for file_name in files:
                absolute_path = os.path.join(folder, file_name)
                relative_path = os.path.relpath(absolute_path, temp_dir)
                docx.write(absolute_path, relative_path)

    # Clean up temporary directory
    shutil.rmtree(temp_dir)
