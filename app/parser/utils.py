from parser import docx_edit 
from django.db import transaction
from .models import Document

def handle_uploaded_file(f):  
    with open('parser/static/upload/'+f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)  
    return f.name


def extract_text(f_name):
    text = docx_edit.get_document_text(path_in='parser/static/upload/'+f_name)
    classified_text = []
    replacement_list = []
    for txt in text:
        cleaned_txt = clean_string(txt)
        classified_text.append(list([docx_edit.classify_text(cleaned_txt).value,cleaned_txt]))
        replacement_list.append(tuple([cleaned_txt, cleaned_txt]))
    save_document(replacement_list=replacement_list, element_classification=classified_text, f_name=f_name)


def save_document(replacement_list, element_classification, f_name=None):
    with transaction.atomic():
        # Delete all existing instances of the Document model except the first one
        documents = Document.objects.all()
        if documents.count() > 1:
            documents.exclude(pk=documents.first().pk).delete()

        # If there's an existing document, update it; otherwise, create a new one
        if documents.exists():
            document = documents.first()
            document.set_replacement_list(replacement_list)
            document.set_element_classification(element_classification)
            if f_name is not None:
                document.f_name = f_name
            document.save()
        else:
            document = Document()
            document.set_replacement_list(replacement_list)
            document.set_element_classification(element_classification)
            if f_name is not None:
                document.f_name = f_name
            document.save()

def clean_string(s):
    # Remove leading white space
    s = s.lstrip()

    # Remove newline characters
    s = s.replace("\n", "")

    # Remove quotation marks only from the beginning and end of the string
    if s.startswith('"') or s.startswith("'"):
        s = s[1:]
    if s.endswith('"') or s.endswith("'"):
        s = s[:-1]

    return s
