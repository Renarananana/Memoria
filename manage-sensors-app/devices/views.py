from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from .forms import DeviceForm, LabelFormSet
from .models import Device, Labels
from gateway.models import Gateway
from profiles.models import DeviceProfile
from utils.http_helpers import post
import json

# Create your views here.
def devices_list(request):
  devices = Device.objects.all()
  return render(request, 'device_list.html', {'devices': devices})

class DeviceDeleteView(DeleteView):
  model = Device
  success_url = reverse_lazy('devices-list')
  template_name = 'device_confirm_delete.html'

def device_detail(request, pk):
  device = get_object_or_404(Device, pk=pk)
  resources = device.profile.resources.all()
  commands = device.profile.commands.all()
  return render(request, 'device_detail.html', {'device': device, "resources": resources, "commands": commands})

def create_device(request):
  msg = None
  if request.method == "POST":
    label_formset = LabelFormSet(request.POST, prefix='label')
    form = DeviceForm(request.POST)
    if form.is_valid() and label_formset.is_valid():
      response = create_device_edge(form.cleaned_data, label_formset.cleaned_data, form.cleaned_data["gateway"])
      print(response)
      if response.status_code == 207:
        response_data = json.loads(response.text)
        if response_data[0]["statusCode"] == 201:
          
          new_device = form.save(commit=False)
          new_device.id = response_data[0]["id"]
          new_device.save()
          new_labels = label_formset.save()
          new_device.labels.add(*new_labels)
          return redirect('devices-list')
        else:
          msg = response_data[0]["message"]
      else:
        msg = response.text
  else:
    form = DeviceForm()
    label_formset = LabelFormSet(prefix="label", queryset=Labels.objects.none())
  return render(request, 'create_device.html', {'form': form, 'label_formset': label_formset, "msg": msg})
  
def edit_device(request, pk):
  device = get_object_or_404(Device, pk=pk)
  if request.method == 'POST':
    form = DeviceForm(request.POST, instance=device)
    label_formset = LabelFormSet(request.POST, prefix='label')
    if form.is_valid() and label_formset.is_valid():
      edit_device_edge(form.cleaned_data, label_formset.cleaned_data)
      new_device = form.save()
      new_labels = label_formset.save()
      new_device.labels.add(*new_labels)
      return redirect('device-detail', pk=device.pk)
  else:
    form = DeviceForm(instance=device)
    label_formset = LabelFormSet(prefix="label", queryset=Labels.objects.none())
  return render(request, 'edit_device.html', {'form': form, 'label_formset': label_formset})


def edit_device_edge(device, labels):
  
  pass

def create_device_edge(device, labels, gateway):
  deviceLabels = []
  for label in labels:
    deviceLabels.append(label['name'])
  for label in device["labels"].values("name"):
    deviceLabels.append(label["name"])
  
  
  device_dict = {
    'name': device['name'],
    "description": device["description"],
    "adminState": device["admin_state"],
    "operatingState": device["operating_state"],
    "labels": deviceLabels,
    "serviceName": "device-mqtt",
    "profileName": device["profile"].name,
    "protocols": {
      "mqtt": {
        "CommandTopic": f"command/{device["name"]}"
      }
    }
  }
  data = [{
    "apiVersion": "v3",
    "device": device_dict
  }]
  print(data)
  
  return post(gateway, "/core-metadata/api/v3/device", json=data)

