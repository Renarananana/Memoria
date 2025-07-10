from .models import Gateway, Status
from django import forms
from django.contrib.auth.hashers import make_password


class GatewayForm(forms.ModelForm):
  class Meta:
    model = Gateway
    exclude= ["last_seen", "profiles"]
  
  status = forms.ChoiceField(choices=[
    (Status.ACTIVE, Status.ACTIVE.value),
    (Status.DISABLED, Status.DISABLED.value),
  ])
  
  password = forms.CharField(widget=forms.PasswordInput)
  
  def save(self, commit=True):
    instance = super().save(commit=False)
    password = self.cleaned_data['password']
    print(password)
    instance.set_password(password)
    if commit:
      instance.save()
    return instance

class GatewayProfilesForm(forms.Form):
    name = forms.CharField()
    test = forms.CharField()
    #labels = forms.ModelMultipleChoiceField(queryset=Labels.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    def __init__(self, *args, objeto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if objeto:
            self.fields['name'].initial = objeto.name
            self.fields['test'].initial = objeto.test

DECISIONS = [
  ('delete', 'Delete'),
  ('ignore', 'Ignore'),
  ('create-profile', 'Create Profile'),
  ('assign', 'Assign'),
]

DEVICE_DECISIONS = [
  ('delete', 'Delete'),
  ('ignore', 'Ignore'),
  ('create-device', 'Create Device')
]
class DecisionForm(forms.Form):
  item_id = forms.UUIDField(widget=forms.HiddenInput)
  decision = forms.ChoiceField(choices=DECISIONS)
  profile = forms.ChoiceField(widget=forms.HiddenInput, choices=[], required=False)

class DeviceDecisionForm(forms.Form):
  item_id = forms.UUIDField(widget=forms.HiddenInput)
  decision = forms.ChoiceField(choices=DEVICE_DECISIONS)

class AddProfileForm(forms.Form):
  profile = forms.ChoiceField(choices=[])
