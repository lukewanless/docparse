import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from django.http import JsonResponse
from .models import Document
from .utils import clean_string, save_document 
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
        request_context = text_data_json['context']
        request_topic = text_data_json['topic']

        # Get document data using the index
        document_data = await database_sync_to_async(Document.objects.first)()
        classifications, replacements = await database_sync_to_async(self.get_document_details)(document_data)

        classifications = document_data.get_element_classification()
        replacements = document_data.get_replacement_list()

        # Generate text using the classification
        previous_text_type = classifications[index][0]

        context_string = f"Generate the next {request_text_type} for this document: {request_context}. It is on the topic of {request_topic}. Return only the new {request_text_type}."

        if previous_text_type == request_text_type:
            prompt = f"{context_string} It should be of similar length and style to the following text: \'{request_text}\'. Return only the new {request_text_type}."
        else:
            prompt = context_string 

        new_text = ""

        # calculate max tokens using the previous text 
        max_tokens = max(100, int(4*len(request_text.split())))
        for new_text_chunk in generate_text(prompt=prompt, max_tokens=max_tokens):
            new_text += new_text_chunk["choices"][0]["text"]
            new_text = clean_string(new_text)
            #progress = min(90,int(len(new_text.split())/750 * 100)*3)
            progress = min(99, int(len(new_text.split())*4/max_tokens*100))
            response = {
                'form_id': text_data_json['form_id'],
                'new_text': new_text,
                'disable': True, 
                'progress': progress,
            }
            await self.send(text_data=json.dumps(response))
            await asyncio.sleep(0.1) 

        # Save the updated text to the database after receiving all text chunks
        replacements[index][1] = new_text
        classifications[index][1] = request_text_type
        await database_sync_to_async(save_document)(replacement_list=replacements, element_classification=classifications)

        response = {
            'form_id': text_data_json['form_id'],
            'new_text': new_text,
            'disable': False, 
            'progress': 100,
        }
        await self.send(text_data=json.dumps(response))
        

    @staticmethod
    def get_document_details(document_data):
        classifications = document_data.get_element_classification()
        replacements = document_data.get_replacement_list()
        return classifications, replacements

