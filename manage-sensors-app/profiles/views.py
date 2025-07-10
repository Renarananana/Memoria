from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from .forms import DeviceProfileForm, ResourceFormSet, CommandFormSet, LabelFormSet, PropertiesFormSet, OperationFormSet
from .models import Labels, ResourceProperties, DeviceOperation, DeviceProfile, DeviceCommand
import uuid
from django.forms.models import model_to_dict
import json


# Create your views here.
def profiles_list(request):
  profiles = DeviceProfile.objects.all()
  return render(request, 'profiles_list.html', {'profiles': profiles})

class DeviceProfileDeleteView(DeleteView):
  model = DeviceProfile
  success_url = reverse_lazy('profiles-list')
  template_name = 'deviceprofile_confirm_delete.html'

def device_profile_detail(request, pk):
  profile = get_object_or_404(DeviceProfile, pk=pk)
  resources = profile.resources.all()
  commands = profile.commands.all()
  return render(request, 'device_profile_detail.html', {'profile': profile, 'resources': resources, 'commands': commands})

def remove_empty_formset_data(formset):
  return list(filter(lambda form: form.cleaned_data != {}, formset))
  
def create_profile(request):
  if request.method == 'POST':
    profile_form = DeviceProfileForm(request.POST)
    label_formset = LabelFormSet(request.POST, prefix='label')
    resource_formset = ResourceFormSet(request.POST, prefix='resource')
    command_formset = CommandFormSet(request.POST, prefix='command')
    operation_formset = OperationFormSet(request.POST, prefix='operation')
    properties_formset = PropertiesFormSet(request.POST, prefix='properties')
    
    
    
        
    if not profile_form.is_valid():
      print(profile_form)
    if not label_formset.is_valid():
      print(label_formset)
    if not resource_formset.is_valid():
      print(resource_formset)
    if not properties_formset.is_valid():
      print(properties_formset)
    if not command_formset.is_valid():
      print(command_formset)
    if not operation_formset.is_valid():
      print(operation_formset)
    
    if profile_form.is_valid() and label_formset.is_valid() and resource_formset.is_valid() and properties_formset.is_valid() and command_formset.is_valid() and operation_formset.is_valid():
      
      label_forms_no_empty = remove_empty_formset_data(label_formset)
      res_forms_no_empty = remove_empty_formset_data(resource_formset)
      prop_forms_no_empty = remove_empty_formset_data(properties_formset)
      com_forms_no_empty = remove_empty_formset_data(command_formset)
      op_forms_no_empty = remove_empty_formset_data(operation_formset)
      print("profile cleaned data: ", profile_form.cleaned_data)
      print("label cleaned data: ", [form.cleaned_data for form in label_forms_no_empty])
      print("resource cleaned data: ", [form.cleaned_data for form in res_forms_no_empty])
      print("prop cleaned data: ", [form.cleaned_data for form in prop_forms_no_empty])
      print("command cleaned data: ", [form.cleaned_data for form in com_forms_no_empty])
      print("operation cleaned data: ", [form.cleaned_data for form in op_forms_no_empty])
      
      
      
      
      label_data = filter_delete(label_forms_no_empty)
      command_data = filter_delete(com_forms_no_empty)
      operation_data = filter_delete(op_forms_no_empty)
      
     
      for operation in operation_data:
        operation["resource"] = res_forms_no_empty[operation["resource"]].cleaned_data
        operation["command"] = command_formset[operation["command"]].cleaned_data
      
      resource_data = []
      properties_data = []
      for resource, prop in zip(res_forms_no_empty, prop_forms_no_empty):
        if not resource.cleaned_data["DELETE"]:
          resource_data.append(resource.cleaned_data)
          properties_data.append(prop.cleaned_data)
        
      new_profile = profile_form.save()
      print("PROFILE: ", model_to_dict(new_profile))
      
      ## SAVE LABELS
      new_labels = label_formset.save()
      print("LABELS: ", [model_to_dict(label) for label in new_labels])
      new_profile.labels.add(*new_labels)
      
      # SAVE RESOURCES
      resource_dict = {}
      for resource_form, prop_form in zip(res_forms_no_empty, prop_forms_no_empty):
        if not resource_form.cleaned_data["DELETE"]:
          new_prop = prop_form.save()
          new_res = resource_form.save(commit=False)
          new_res.properties = new_prop
          new_res.profile = new_profile
          new_res.save()
          print("RES: ",model_to_dict(new_res))
          resource_dict[resource_form.cleaned_data["name"]] = new_res
      
      
      # SAVE COMMANDS
      command_dict = {}
      for command_form in com_forms_no_empty:
        if not command_form.cleaned_data["DELETE"]:
          new_command = command_form.save(commit=False)
          new_command.profile = new_profile
          new_command.save()
          print("COMMAND: ", model_to_dict(new_command))
          command_dict[command_form.cleaned_data["name"]] = new_command

      for operation_form in op_forms_no_empty:
        print('op cleaned data: ', operation_form.cleaned_data)
        if not operation_form.cleaned_data["DELETE"] and not operation_form.cleaned_data["command"]["DELETE"]:
          new_operation = operation_form.save(commit=False)
          new_operation.resource = resource_dict[operation_form.cleaned_data["resource"]["name"]]
          new_operation.command = command_dict[operation_form.cleaned_data["command"]["name"]]
          new_operation.save()
          print("OPERATION: ", model_to_dict(new_operation))
        
    return redirect('profiles-list')  # Redirige a donde necesites
  else:
    
    profile_form = DeviceProfileForm()
    resource_formset = ResourceFormSet(prefix='resource')
    command_formset = CommandFormSet(prefix='command')
    label_formset = LabelFormSet(prefix="label", queryset=Labels.objects.none())
    properties_formset = PropertiesFormSet(prefix="properties", queryset=ResourceProperties.objects.none())
    operation_formset = OperationFormSet(prefix='operation', queryset=DeviceOperation.objects.none())
    

  return render(request, 'create_profile.html', {
    'profile_form': profile_form,
    'resource_formset': resource_formset,
    'command_formset': command_formset,
    'label_formset': label_formset,
    'properties_formset': properties_formset,
    'operation_formset': operation_formset,
  })
  

def edit_profile(request, pk):
  profile = get_object_or_404(DeviceProfile, pk=pk)
  resources = profile.resources.all()
  
  
  if request.method == 'POST':
    profile_form = DeviceProfileForm(request.POST, instance=profile)
    label_formset = LabelFormSet(request.POST, prefix='label')
    resource_formset = ResourceFormSet(request.POST, prefix='resource', instance=profile)
    command_formset = CommandFormSet(request.POST, prefix='command', instance=profile)
    operation_formset = OperationFormSet(request.POST, prefix='operation', instance=profile.commands.operations)
    properties_formset = PropertiesFormSet(request.POST, prefix='properties')
       
    if not profile_form.is_valid():
      print(profile_form)
    if not label_formset.is_valid():
      print(label_formset)
    if not resource_formset.is_valid():
      print(resource_formset)
    if not properties_formset.is_valid():
      print(properties_formset)
    if not command_formset.is_valid():
      print(command_formset)
    if not operation_formset.is_valid():
      print(operation_formset)
    
    if profile_form.is_valid() and label_formset.is_valid() and resource_formset.is_valid() and properties_formset.is_valid() and command_formset.is_valid() and operation_formset.is_valid():
      
      label_forms_no_empty = remove_empty_formset_data(label_formset)
      res_forms_no_empty = remove_empty_formset_data(resource_formset)
      prop_forms_no_empty = remove_empty_formset_data(properties_formset)
      com_forms_no_empty = remove_empty_formset_data(command_formset)
      op_forms_no_empty = remove_empty_formset_data(operation_formset)
      print("profile cleaned data: ", profile_form.cleaned_data)
      print("label cleaned data: ", [form.cleaned_data for form in label_forms_no_empty])
      print("resource cleaned data: ", [form.cleaned_data for form in res_forms_no_empty])
      print("prop cleaned data: ", [form.cleaned_data for form in prop_forms_no_empty])
      print("command cleaned data: ", [form.cleaned_data for form in com_forms_no_empty])
      print("operation cleaned data: ", [form.cleaned_data for form in op_forms_no_empty])
      
      
      
      
      label_data = filter_delete(label_forms_no_empty)
      command_data = filter_delete(com_forms_no_empty)
      operation_data = filter_delete(op_forms_no_empty)
      
     
      for operation in operation_data:
        operation["resource"] = res_forms_no_empty[operation["resource"]].cleaned_data
        operation["command"] = command_formset[operation["command"]].cleaned_data
      
      resource_data = []
      properties_data = []
      for resource, prop in zip(res_forms_no_empty, prop_forms_no_empty):
        if not resource.cleaned_data["DELETE"]:
          resource_data.append(resource.cleaned_data)
          properties_data.append(prop.cleaned_data)
      
      # response = send_data_edge(profile_form.cleaned_data, label_data, resource_data, properties_data, command_data, operation_data)
      # if response.status_code != 207:
      #   print("Status code:", response.status_code)

      #   # Imprimir el cuerpo de la respuesta como texto
      #   print("Respuesta:", response.text)
      #   return redirect('profiles-list')
      
      
      
      new_profile = profile_form.save()
      print("PROFILE: ", model_to_dict(new_profile))
      
      ## SAVE LABELS
      new_labels = label_formset.save()
      print("LABELS: ", [model_to_dict(label) for label in new_labels])
      new_profile.labels.add(*new_labels)
      
      # SAVE RESOURCES
      resource_dict = {}
      for resource_form, prop_form in zip(res_forms_no_empty, prop_forms_no_empty):
        if not resource_form.cleaned_data["DELETE"]:
          new_prop = prop_form.save()
          new_res = resource_form.save(commit=False)
          new_res.properties = new_prop
          new_res.profile = new_profile
          new_res.save()
          print("RES: ",model_to_dict(new_res))
          resource_dict[resource_form.cleaned_data["name"]] = new_res
      
      
      # SAVE COMMANDS
      command_dict = {}
      for command_form in com_forms_no_empty:
        if not command_form.cleaned_data["DELETE"]:
          new_command = command_form.save(commit=False)
          new_command.profile = new_profile
          new_command.save()
          print("COMMAND: ", model_to_dict(new_command))
          command_dict[command_form.cleaned_data["name"]] = new_command

      for operation_form in op_forms_no_empty:
        print('op cleaned data: ', operation_form.cleaned_data)
        if not operation_form.cleaned_data["DELETE"] and not operation_form.cleaned_data["command"]["DELETE"]:
          new_operation = operation_form.save(commit=False)
          new_operation.resource = resource_dict[operation_form.cleaned_data["resource"]["name"]]
          new_operation.command = command_dict[operation_form.cleaned_data["command"]["name"]]
          new_operation.save()
          print("OPERATION: ", model_to_dict(new_operation))
        
    return redirect('profiles-list')  # Redirige a donde necesites
  else:
    properties_qs = ResourceProperties.objects.filter(deviceresource__in=resources)
    
    commands = profile.commands.all()
    
    print(commands)
    operations_qs = DeviceOperation.objects.filter(command__in=commands)
    print(operations_qs)
    
    profile_form = DeviceProfileForm(instance=profile)
    resource_formset = ResourceFormSet(prefix='resource', instance=profile)
    command_formset = CommandFormSet(prefix='command', instance=profile)
    label_formset = LabelFormSet(prefix="label", queryset=Labels.objects.none())
    properties_formset = PropertiesFormSet(prefix="properties", queryset=properties_qs)
    operation_formset = OperationFormSet(prefix='operation', queryset=operations_qs)
    
    res_dict = {}
    resource_choices = []
    for i, res_form in enumerate(resource_formset):
      res_dict[res_form.instance.name] = i
      resource_choices.append((i, res_form.instance.name))
    for op_form in operation_formset:
      op_form.fields['resource'].widget.choices = resource_choices
      op_form.fields['resource'].initial = res_dict[op_form.instance.resource.name]

  return render(request, 'edit_profile.html', {
    'profile_form': profile_form,
    'resource_formset': resource_formset,
    'command_formset': command_formset,
    'label_formset': label_formset,
    'properties_formset': properties_formset,
    'operation_formset': operation_formset,
  })


def filter_delete(to_filter_list:list):
  return [x.cleaned_data for x in to_filter_list if x.cleaned_data and x.cleaned_data["DELETE"]==False]
    
    