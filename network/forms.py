
from django import forms
from django.forms import Textarea
from .models import Post

class PostForm(forms.Form):
    content = forms.CharField(label="", required=True, widget=Textarea(attrs={"rows": "5", "class": "form-control mb-2",'placeholder': "Write what you think..."}))
