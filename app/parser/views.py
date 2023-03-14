from django.shortcuts import render, redirect
from django.http import HttpResponse
import openai
import os
import random
from parser.utils import handle_uploaded_file
from parser.forms import DocxForm
from django.http import HttpResponse


openai.api_key = os.environ.get("OPENAI_KEY", "")

# this is the home view for handling home page logic
def home(request):
    try:
        # checking if the request method is POST
        if request.method == 'POST':
            # getting prompt data from the form
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
            return render(request, 'parser/home.html', context)
        # this runs if the request method is GET
        else:
            # this will render when there is no request POST or after every POST request
            return render(request, 'parser/home.html')
    # the except statement will capture any error
    except:
        # this will redirect to the 404 page after any error is caught
        return redirect('error_handler')
 
# this is the view for handling errors
def error_handler(request):
    return render(request, 'parser/404.html') 

def upload(request):
    if request.method == 'POST':
        docx = DocxForm(request.POST, request.FILES)
        # maybe add a validity checker here 
        handle_uploaded_file(request.FILES['file']) 
        return HttpResponse("File uploaded successfully") 
        #return redirect(display_file) 
    else:
        docx = DocxForm()
        return render(request, "parser/upload.html", {'form': docx})

