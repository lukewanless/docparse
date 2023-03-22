from re import A
from django.shortcuts import render, redirect
from django.http import HttpResponse
import openai
import os
import random
from parser.utils import handle_uploaded_file, extract_text, save_document
from parser.forms import DocxForm
from .models import Document
import parser.docx_edit as docx_edit
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


openai.api_key = os.environ.get("OPENAI_KEY", "")

# this is the home view for handling home page logic
def generate(request):
    try:
        # checking if the request method is POST
        if request.method == 'POST':
            # getting prompt data from the form
            print("HELLO")
            prompt = request.POST.get('prompt')
            # making a request to the API 
            response = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens=1000)
            # formatting the response input
            text = random.choice(response["choices"])["text"]
            # bundling everything in the context
            context = {
                'formatted_response': text,
                'prompt': prompt
            }
            # this will render the results in the home.html template
            return render(request, 'parser/generate.html', context)
        # this runs if the request method is GET
        else:
            # this will render when there is no request POST or after every POST request
            return render(request, 'parser/generate.html')
    # the except statement will capture any error
    except:
        # this will redirect to the 404 page after any error is caught
        return redirect('error_handler')
 
# this is the view for handling errors
def error_handler(request):
    return render(request, 'parser/404.html') 

def upload(request):
    if request.method == 'POST':
        if 'parse_document' in request.POST:
            docx = DocxForm(request.POST, request.FILES)
            # maybe add a validity checker here 
            f_name = handle_uploaded_file(request.FILES['file'])
            extract_text(f_name)
            document_data = Document.objects.first()
            text = document_data.get_element_classification()
            text_dict = {'text' : text}
            return render(request, 'parser/display_uploaded_docx.html', text_dict) 
    else:
        docx = DocxForm()
        return render(request, "parser/upload.html", {'form': docx})


def call_openai_api(request):
    if request.method == 'POST':
        # getting prompt data from the form
        index = int(request.POST.get('form_id'))
        text = request.POST.get('text_input')
        # get document data using the index 
        document_data = Document.objects.first()
        classifications = document_data.get_element_classification()
        replacements = document_data.get_replacement_list()
            
        classification = classifications[index]
        replacement = replacements[index]

        # generate text using the classification
        text_type = classification[0]
             
        prompt = f"The follwing text is a {text_type} from a document. Please return a string containing a fake replacement value. It should be of similar length and style to the following text: {text}"
        new_text = docx_edit.generate_text(prompt=prompt, max_tokens=2*len(prompt.split()))
        new_text = new_text.lstrip()
        replacement = tuple([text, new_text])
        classification[1] = new_text

        # update and save new text in classifications and replacements 
        classifications[index] = classification
        replacements[index] = replacement
        save_document(replacement_list=replacements, element_classification=classifications)

        return JsonResponse({"new_text": new_text})
    return JsonResponse({"error": "Invalid request method"}, status=400)
