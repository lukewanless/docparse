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
    for txt in text:
        doc_elem = []
        doc_elem.append(docx_edit.classify_text(txt).name)
        doc_elem.append(txt)
        classified_text.append(doc_elem)
    replacement_list = [[] for _ in range(len(classified_text))]
    save_document(replacement_list=replacement_list, element_classification=classified_text)
    #return {'text': classified_text}


def save_document(replacement_list, element_classification):
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
            document.save()
        else:
            document = Document()
            document.set_replacement_list(replacement_list)
            document.set_element_classification(element_classification)
            document.save()
