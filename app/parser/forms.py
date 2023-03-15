from django import forms  
from parser.validators import validate_file_extension

class DocxForm(forms.Form):  
    file = forms.FileField(validators=[validate_file_extension])
