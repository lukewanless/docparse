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

        print(previous_text_type, request_text_type)
        
        context_string = f"You are an LLM that replaces text from a real document with fake text that looks similar and realistic in order to obscure sensitive information. You generate document section by section. Here is a list of tuples containing the type of text in each section followed by the text as you go down the document. The document topic is {request_topic}. The generated text should be consistent with what has been generated so far: {request_context}."

        if previous_text_type == request_text_type:
            prompt = f"{context_string} The following text is a {request_text_type} from the document. Please return a string containing a fake replacement value. It should be of similar length and style to the following text: \'{request_text}\'."
        else:
            prompt = f"{context_string} Generate a {request_text_type}. Return only the {request_text_type} as a string."

        print(prompt)

        new_text = ""
        for new_text_chunk in generate_text(prompt=prompt, max_tokens=1000):
            new_text += new_text_chunk["choices"][0]["text"]
            new_text = clean_string(new_text)
            progress = min(99,int(len(new_text.split())/750 * 100)*3)
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

