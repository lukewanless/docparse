import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from django.http import JsonResponse
from .models import Document
from .utils import clean_string, save_document, docx_edit 
from .docx_edit import generate_text 


class RegenerateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Getting prompt data from the form
        index = int(text_data_json['form_id'])
        request_text = text_data_json['text_input']
        request_text_type = text_data_json['selected_option']

        # Get document data using the index
        document_data = await database_sync_to_async(Document.objects.first)()
        classifications, replacements = await database_sync_to_async(self.get_document_details)(document_data)

        classifications = document_data.get_element_classification()
        replacements = document_data.get_replacement_list()

        # Generate text using the classification
        previous_text_type = classifications[index][1]

        if previous_text_type == request_text_type:
            prompt = f"The following text is a {request_text_type} from a document. Please return a string containing a fake replacement value. It should be of similar length and style to the following text: {request_text}"
        else:
            prompt = f"Generate a {request_text_type}. Return only the {request_text_type} as a string"

        new_text = ""
        for new_text_chunk in generate_text(prompt=prompt, max_tokens=1000):
            new_text += new_text_chunk["choices"][0]["text"]
            new_text = clean_string(new_text)
            response = {
                'form_id': text_data_json['form_id'],
                'new_text': new_text,
            }
            await self.send(text_data=json.dumps(response))
            await asyncio.sleep(0.1)
        # Save the updated text to the database after receiving all text chunks
        replacements[index][1] = new_text
        classifications[index][1] = request_text_type
        await database_sync_to_async(save_document)(replacement_list=replacements, element_classification=classifications)


    @staticmethod
    def get_document_details(document_data):
        classifications = document_data.get_element_classification()
        replacements = document_data.get_replacement_list()
        return classifications, replacements

def call_openai_api(text_data_json):
        # getting prompt data from the form
        index = int(text_data_json['form_id'])
        request_text = text_data_json['text_input']
        request_text_type = text_data_json['selected_option']
        
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


