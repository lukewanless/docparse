from django import forms  
class DocxForm(forms.Form):  
    file = forms.FileField() # for creating file input 
