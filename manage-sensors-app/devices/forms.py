from django import forms
from .models import Device, Labels

class DeviceForm(forms.ModelForm):
  
  class Meta:
    model = Device
    exclude = ["id",]
  labels = forms.ModelMultipleChoiceField(queryset=Labels.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)


LabelFormSet = forms.modelformset_factory(Labels, fields=["name"], extra=0, can_delete=True)