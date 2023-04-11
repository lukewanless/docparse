import openai
import os
import random
from docx2python import docx2python, utilities
import re
from enum import Enum 

class DocElements(Enum):
    EMAIL = "Email"
    PHONE_NUMBER = "Phone Number"
    ADDRESS = "Address"
    FULL_NAME = "Full Name"
    PARAGRAPH = "Paragraph"
    HEADING = "Heading"
    UNKNOWN = "Unknown"

# Function to get a completion from davinci 
def generate_text(prompt: str, max_tokens: int, ):
        openai.api_key = os.environ.get("OPENAI_KEY", "")
        completion = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, max_tokens=max_tokens, echo=False, stream=True
        )
        return completion 
        #assert isinstance(completion, dict)
        #text = random.choice(completion["choices"])["text"]
        #return text


# Function to classify a single text element  
def classify_text(text):
    # use the text run properties and length as well 
    if len(text.split()) > 5:
        return DocElements.PARAGRAPH
    else: 
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        phone_regex = r"\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}"
        address_regex = r"\d+\s[\w\s]+,\s[\w\s]+,\s[A-Z]{2}\s\d{5}"
        name_regex = r"\b[A-Z][a-z]+(?:\s[A-Z]\.)?\s[A-Z][a-z]+\b"

        email_match = re.search(email_regex, text)
        phone_match = re.search(phone_regex, text)
        address_match = re.search(address_regex, text)
        name_match = re.search(name_regex, text)
        
        if email_match:
            return DocElements.EMAIL
        elif phone_match:
            return DocElements.PHONE_NUMBER
        elif address_match:
            return DocElements.PHONE_NUMBER
        elif name_match:
            return DocElements.FULL_NAME
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

