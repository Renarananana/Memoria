# forms.py
from django import forms
from .models import DeviceProfile, DeviceResource, DeviceCommand, DeviceOperation, Labels, ResourceProperties
from django.forms import inlineformset_factory

class DeviceProfileForm(forms.ModelForm):
  class Meta:
    model = DeviceProfile
    fields = ['name', 'manufacturer', 'model', 'labels', 'description']
  labels = forms.ModelMultipleChoiceField(queryset=Labels.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
  
class DeviceResourceForm(forms.ModelForm):
  class Meta:
    model = DeviceResource
    fields = ['name', 'description']
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs["required"] = 'required'


class DeviceCommandForm(forms.ModelForm):
  class Meta:
    model = DeviceCommand
    fields = ['name', 'readWrite']
  
class DeviceOperationForm(forms.ModelForm):
  class Meta:
    model = DeviceOperation
    fields = ['defaultValue']
  resource = forms.IntegerField(required=True, widget= forms.Select(choices=[]))
  command = forms.IntegerField(required=True)

class ResourcePropertiesForm(forms.ModelForm):
  class Meta:
    model = ResourceProperties
    fields = ['valueType', 'readWrite']
    
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs["required"] = 'required'
  
    
LabelFormSet = forms.modelformset_factory(Labels, fields=["name"], extra=0, can_delete=True)
PropertiesFormSet = forms.modelformset_factory(ResourceProperties, form = ResourcePropertiesForm, extra=0, can_delete=True, min_num=1)
OperationFormSet = forms.modelformset_factory(DeviceOperation, form = DeviceOperationForm, extra=0, can_delete=True)
ResourceFormSet = inlineformset_factory(DeviceProfile, DeviceResource, form = DeviceResourceForm, extra=0, can_delete=True, min_num=1, validate_min=True)
CommandFormSet = inlineformset_factory(DeviceProfile, DeviceCommand, form = DeviceCommandForm, extra=0, can_delete=True)
