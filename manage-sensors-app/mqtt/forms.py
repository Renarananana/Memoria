from django import forms

class WriteForm(forms.Form):
  data = forms.CharField(max_length=100)
  
class WriteCommandForm(forms.Form):
  resource_name = forms.CharField(widget=forms.HiddenInput)
  resource_valueType = forms.CharField(widget=forms.HiddenInput)
  data = forms.CharField(max_length=100)