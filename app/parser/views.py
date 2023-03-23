from re import A
from django.shortcuts import render, redirect
from django.http import HttpResponse
import openai
import os
import random
from parser.utils import handle_uploaded_file, extract_text, save_document, clean_string
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
            options = [option.value for option in docx_edit.DocElements]
            input_dict = {'text' : text, 'options' : options}
            return render(request, 'parser/display_uploaded_docx.html', input_dict, ) 
    else:
        docx = DocxForm()
        return render(request, "parser/upload.html", {'form': docx})


def call_openai_api(request):
    if request.method == 'POST':
        # getting prompt data from the form
        index = int(request.POST.get('form_id'))
        request_text = request.POST.get('text_input')
        request_text_type = request.POST.get('selected_option')
        
        # get document data using the index 
        document_data = Document.objects.first()
        classifications = document_data.get_element_classification()
        replacements = document_data.get_replacement_list()
            

        # generate text using the classification
        previous_text_type = classifications[index][1]

        if previous_text_type == request_text_type:
            prompt = f"The follwing text is a {request_text_type} from a document. Please return a string containing a fake replacement value. It should be of similar length and style to the following text: {request_text}"
        else:
            prompt = f"Generate a {request_text_type}. Return only the {request_text_type} as a string"

        new_text = clean_string(docx_edit.generate_text(prompt=prompt, max_tokens=2*len(prompt.split())))
        replacements[index][1] = new_text
        classifications[index][1] = request_text_type

        save_document(replacement_list=replacements, element_classification=classifications)

        return JsonResponse({"new_text": new_text})
    return JsonResponse({"error": "Invalid request method"}, status=400)

def completed(request):
    # load in the replacements list
    doc = Document.objects.first()
    replacements = doc.get_replacement_list()
    docx_edit.replace_text(path_in='parser/static/upload/'+doc.f_name, path_out='parser/static/upload/replaced.docx', replacements=replacements)
    # call the replacements function and return a new file in download link 

    return render(request, 'parser/completed.html')

def save(request):
    if request.method == 'POST':
        text_list = request.POST.getlist('texts[]')
        # need to get the original values in the document then zip it with 
        # the new values and save this in the database 
        print(text_list)
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})
