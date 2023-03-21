from django.db import models
import json
#add reciever call to delete all other objects
# do this before testing other functionality

# Create your models here.
class Document(models.Model):
    replacement_list = models.TextField(blank=True, null=True)
    element_classification = models.TextField()

    def set_replacement_list(self, data):
        self.replacement_list = json.dumps(data)

    def get_replacement_list(self):
        return json.loads(self.replacement_list)

    def set_element_classification(self, data):
        self.element_classification = json.dumps(data)

    def get_element_classification(self):
        return json.loads(self.element_classification)

