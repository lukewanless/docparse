import openai
import os
import random
from docx2python import docx2python, utilities
import re
from enum import Enum 
from typing import Dict
import io 
from PIL import Image
import shutil

class DocElements(Enum):
    EMAIL = "Email"
    PHONE_NUMBER = "Phone Number"
    ADDRESS = "Address"
    FULL_NAME = "Full Name"
    PARAGRAPH = "Paragraph"
    HEADING = "Heading"
    UNKNOWN = "Unknown"

# Function to get a completion from davinci 
def generate_text(prompt: str, max_tokens: int, ) -> str:
        openai.api_key = os.environ.get("OPENAI_KEY", "")
        completion = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, max_tokens=max_tokens, echo=False
        )
        assert isinstance(completion, dict)
        text = random.choice(completion["choices"])["text"]
        return text


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
    # create image directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(current_dir, "static", "images")
    images_path = os.path.join(images_dir, os.path.splitext(os.path.basename(path_in))[0])

    #delete all subdirectories to clean up after previous generation 
    for item in os.listdir(images_dir):
        if os.path.isdir(os.path.join(images_dir, item)):
            shutil.rmtree(os.path.join(images_dir, item))

    # make new images directory 
    os.mkdir(images_path)

    # save images and return all text in file
    with docx2python(path_in, images_path) as doc:
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

def get_image_names(path_in):
    doc = docx2python(path_in)
    return [name for name in doc.images.keys()]

def replace_images(path_in,path_out) -> None:
        """
        Replace images in the docx file with new images of the same size.
        :param replacements: A dictionary with the old image names as keys and new image paths as values
        """
        reader = docx2python(path_in).docx_reader
        # Pull existing images from the docx file
        existing_images = reader.pull_image_files()
        old_image_names = get_image_names(path_in)
        images_directory = 'parser/static/images/'+os.path.splitext(os.path.basename(path_in))[0]+'/'
 
        replacement_paths =[os.path.join(images_directory, f) for f in os.listdir(images_directory) if os.path.isfile(os.path.join(images_directory, f)) and 'replace' in f]

        # Iterate through the replacements
        replacements = dict(zip(old_image_names, replacement_paths))
        for old_image_name, new_image_path in replacements.items():
            # Check if the old image exists in the docx file
            if old_image_name in existing_images:
                # Load the old image and the new image using PIL
                old_image = Image.open(io.BytesIO(existing_images[old_image_name]))
                new_image = Image.open(new_image_path)

                # Check if the images have the same size
                #if old_image.size == new_image.size:
                    # Replace the old image with the new image in the docx file
                with open(new_image_path, "rb") as new_image_file:
                    new_image_data = new_image_file.read()
                for image in reader.files_of_type("image"):
                    if os.path.basename(image.Target) == old_image_name:
                        image.root_element.clear()
                        image.root_element.write(new_image_data)
                #else:
                    #print(f"Error: The new image {new_image_path} has a different size than the old image {old_image_name}.")
            else:
                print(f"Error: The old image {old_image_name} was not found in the docx file.")
        reader.save(path_out)
        reader.close()
