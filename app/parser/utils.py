from parser import xml_edit
import parser.xml_edit

def handle_uploaded_file(f):  
    with open('parser/static/upload/'+f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)  
    return f.name


def extract_text(f_name):
    text = []
    doc_xml = xml_edit.XMLEdit(template_path='parser/static/upload/'+f_name) 
    for node, txt in doc_xml._itertext(doc_xml.xml_tree):
        doc_elem = []
        doc_elem.append(doc_xml.classify_doc_element(txt))
        doc_elem.append(txt)
        text.append(doc_elem)
    return {'text':text}



