from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.forms import formset_factory, Select
from .forms import GatewayForm, GatewayProfilesForm, DecisionForm, DeviceDecisionForm, AddProfileForm
from .models import Gateway, GatewayProfiles
from profiles.models import DeviceProfile
from devices.models import Device
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from utils.http_helpers import get, post, delete
import uuid
import json
from django.views.decorators.csrf import csrf_exempt
import subprocess


def get_gateway_profiles(gateway, path):
  profiles = []
  devices_left =True
  offset = 0
  try:
    while devices_left:
      response = get(gateway, path, params={"offset": offset})
      if response.status_code != 200:
        break
      data = response.json()
      if data["totalCount"] <20:
        devices_left=False
      offset += 20
      
      profiles.extend(data["profiles"])
  except Exception as e:
    print(e)
  
  return profiles
def get_gateway_devices(gateway, path):
  devices = []
  devices_left =True
  offset = 0
  try:
    while devices_left:
      response = get(gateway, path, params={"offset": offset})
      if response.status_code != 200:
        break
      data = response.json()
      if data["totalCount"] <20:
        devices_left=False
      offset += 20
      
      devices.extend(data["devices"])
  except Exception as e:
    print(e)
  
  return devices


# Create your views here.
class GatewatDeleteView(DeleteView):
  model = Gateway
  success_url = reverse_lazy('gateway-list')
  template_name = 'device_confirm_delete.html'
  

def gateway_list(request):
  gateways = Gateway.objects.all()
  return render(request, "gateway_list.html", {"gateways": gateways})


def create_gateway(request):
  if request.method == "POST":
    form = GatewayForm(request.POST)
    if form.is_valid():
      new_gateway = form.save()
      return redirect('gateways-list')
    else:
      print(form)
      return HttpResponse(form)
  else:
    form = GatewayForm()
    return render(request, 'create_gateway.html', {'form': form})

def update_gateway_profiles(request, pk):
  gateway = get_object_or_404(Gateway, pk= pk)
  gateway_profiles = get_gateway_profiles(gateway, "/core-metadata/api/v3/deviceprofile/all")
  ids = [profile["id"] for profile in gateway_profiles]
  ids_synched = list(GatewayProfiles.objects.filter(uid__in=ids).values_list("id", flat=True))
  ids_no_synched = list(set(ids) - set(ids_synched))
  not_synched = [profile for profile in gateway_profiles if profile["id"] in ids_no_synched]
  if request.method == 'POST':
    form = GatewayProfilesForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('gateway-detail', pk=gateway.pk)
  else:
    form = GatewayProfilesForm()
  return render(request, 'update_gateway_profiles.html', {'form': form, 'not_synched': not_synched})

def add_profile(request, pk):
  msg = None
  gateway = get_object_or_404(Gateway, pk= pk)
  choices = DeviceProfile.objects.exclude(
    id__in=GatewayProfiles.objects.filter(gateway=gateway).values_list('profile__id', flat=True)
  )
  if request.method == "POST":
    form = AddProfileForm(request.POST)
    form.fields["profile"].choices = choices.values_list('id', 'name')
    if form.is_valid():
      profile = DeviceProfile.objects.get(id=form.cleaned_data["profile"])
      response = gateway_create_profile(profile, gateway)
      if response.status_code == 207:
        response_data = json.loads(response.text)
        if response_data[0]["statusCode"] == 201:
          GatewayProfiles.objects.create(uid = response_data[0]["id"], gateway = gateway, profile= profile)
          return redirect('gateway-detail', pk=gateway.pk)
        msg = response_data[0]["message"]
  else:
    form = AddProfileForm()
    form.fields["profile"].choices = choices.values_list('id', 'name')
  return render(request, 'add_profile.html', {'form': form, 'msg': msg})
    
def gateway_create_profile(profile, gateway):
  profileLabels = []
  for label in profile.labels.all():
    profileLabels.append(label.name)
  
  deviceResources = []
  for resource in profile.resources.all():
    deviceResources.append({
      "name": resource.name,
      "description": resource.description,
      "properties": {
        "valueType": resource.properties.valueType,
        "readWrite": resource.properties.readWrite
      }
    })
  
  
  deviceCommands = []
  for command in profile.commands.all():
    com_operations = [{ "deviceResource": operation.resource.name, "defaultValue": operation.defaultValue } for operation in command.operations.all()]
    deviceCommands.append({
      "name": command.name,
      "readWrite": command.readWrite,
      "resourceOperations": com_operations
    })
  
  
  profile_dict = {
    'name': profile.name,
    "manufacturer": profile.manufacturer,
    "model": profile.model,
    "labels": profileLabels,
    "description": profile.description,
    "deviceResources": deviceResources,
    "deviceCommands": deviceCommands
  }
  data = [{
    "requestId": str(uuid.uuid4()),
    "apiVersion": "v3",
    "profile": profile_dict
  }]
  return post(gateway, "/core-metadata/api/v3/deviceprofile", json=data)

def synch_profiles(request, pk):
  gateway = get_object_or_404(Gateway, pk= pk)
  gateway_profiles = get_gateway_profiles(gateway, "/core-metadata/api/v3/deviceprofile/all")
  ids = [profile["id"] for profile in gateway_profiles]
  
  gateway_profiles_app = GatewayProfiles.objects.filter(gateway=gateway)
  for gp in gateway_profiles_app:
    if gp.uid not in ids:
      gp.delete()
  
  ids_synched = list(GatewayProfiles.objects.filter(uid__in=ids).values_list("uid", flat=True))
  ids_no_synched = list(set(ids) - set(str(uid) for uid in ids_synched))
  not_synched = [profile for profile in gateway_profiles if profile["id"] in ids_no_synched]
  assign_arr = [True for _ in ids_no_synched]
  DecisionFormSet = formset_factory(DecisionForm, extra=0)
  profiles_choices = DeviceProfile.objects.all()
  
  
  
  if request.method == 'POST':
    formset = DecisionFormSet(request.POST)
    for i, form in enumerate(formset):
      choices = []
      for profile in profiles_choices:
        if profile.name == gateway_profiles[i]["name"]:
          choices.append((profile.id, profile.name))
      if choices:
        form.fields["profile"].widget = Select()
        form.fields["profile"].choices = choices
    if formset.is_valid():
      for form in formset:
        item_id = form.cleaned_data["item_id"]
        decision = form.cleaned_data["decision"]
        match decision:
          case "delete":
            print('delete')
            new_profile_data = None
            for profile in gateway_profiles:
              if profile["id"] == str(item_id):
                new_profile_data = profile
            delete_profile_gateway(new_profile_data["name"], pk)
          case "create-profile":
            new_profile_data = None
            for profile in gateway_profiles:
              if profile["id"] == str(item_id):
                new_profile_data = profile
            create_profile(new_profile_data)
          case "assign":
            profile = DeviceProfile.objects.get(id=form.cleaned_data["profile"])
            GatewayProfiles.objects.create(uid = item_id, profile = profile, gateway= gateway)
          case "ignore":
            continue
            
      return redirect('gateway-detail', pk=gateway.pk)
  else:
    formset = DecisionFormSet(initial=[{'item_id': id_} for id_ in ids_no_synched])
    for i,form in enumerate(formset.forms):
      choices = []
      for profile in profiles_choices:
        if profile.name == gateway_profiles[i]["name"]:
          choices.append((profile.id, profile.name))
      if choices:
        form.fields["profile"].widget = Select()
        form.fields["profile"].choices = choices
      else:
        form.fields["decision"].choices = [(k, v) for k, v in form.fields['decision'].choices if k != 'assign']
        assign_arr[i] = False
  return render(request, 'update_gateway_profiles.html', {'formset': formset, 'assign_arr': assign_arr, 'not_synched': not_synched})

def synch_devices(request, pk):
  gateway = get_object_or_404(Gateway, pk= pk)
  gateway_devices = get_gateway_devices(gateway, "/core-metadata/api/v3/device/all")
  ids = [device["id"] for device in gateway_devices]
  
  gateway_devices_app = Device.objects.filter(gateway=gateway)
  for gd in gateway_devices_app:
    if gd.id not in ids:
      gd.delete()
  
  ids_synched = list(Device.objects.filter(id__in=ids).values_list("id", flat=True))
  ids_no_synched = list(set(ids) - set(str(uid) for uid in ids_synched))
  not_synched = [device for device in gateway_devices if device["id"] in ids_no_synched]
  DecisionFormSet = formset_factory(DeviceDecisionForm, extra=0)
  
  if request.method == 'POST':
    formset = DecisionFormSet(request.POST)
    print(formset)
    if formset.is_valid():
      print("VALID")
      for form in formset:
        item_id = form.cleaned_data["item_id"]
        decision = form.cleaned_data["decision"]
        match decision:
          case "delete":
            print("delete")
            for device in gateway_devices:
              if device["id"] == str(item_id):
                delete_device_gateway(device["name"], pk)
                break
          case "create-profile":
            for device in gateway_devices:
              if device["id"] == str(item_id):
                create_device(device)
                break
          case "ignore":
            pass
            
      return redirect('gateway-detail', pk=gateway.pk)
  else:
    formset = DecisionFormSet(initial=[{'item_id': id_} for id_ in ids_no_synched])
    print("FORMSET:", formset)
    print(formset.forms)
  return render(request, 'update_gateway_devices.html', {'formset': formset, "not_synched": not_synched})
  
    
def delete_profile_gateway(name, pk):
  gateway = Gateway.objects.get(pk=pk)
  try:
    response = delete(gateway, f"/core-metadata/api/v3/deviceprofile/name/{name}")
    print(response)
  except Exception as e:
    print(e)

def delete_device_gateway(name, pk):
  gateway = Gateway.objects.get(pk=pk)
  try:
    response = delete(gateway, f"/core-metadata/api/v3/device/name/{name}")
    print(response)
  except Exception as e:
    print(e)

def create_profile(new_profile_data):
  pass

def create_device(new_device_data):
  pass

def edit_gateway(request, pk):
  gateway = get_object_or_404(Gateway, pk=pk)
  print(gateway)
  if request.method == 'POST':
    form = GatewayForm(request.POST, instance=gateway)
    if form.is_valid():
      form.save()
      return redirect('gateway-detail', pk=gateway.pk)
  else:
    form = GatewayForm(instance=gateway)
  return render(request, 'edit_gateway.html', {'form': form})

def gateway_detail(request, pk):
  gateway = get_object_or_404(Gateway, pk=pk)
  gp = GatewayProfiles.objects.filter(gateway=gateway)
  print(gateway.password)
  print(gateway.get_password())
  devices= Device.objects.filter(gateway=gateway)
  return render(request, 'gateway_detail.html', {"gateway": gateway, "gateway_profiles": gp, "gateway_devices": devices})
  
def gateway_ping(request, pk):
  gateway = get_object_or_404(Gateway, pk=pk)
  gateway.update_status()
  return redirect('gateway-detail', pk=pk)
  
def disable_gateway(request, pk):
  gateway = get_object_or_404(Gateway, pk=pk)
  gateway.disable()
  print(request)
  return redirect('gateway-detail', pk=pk)

def activate_gateway(request, pk):
  gateway = get_object_or_404(Gateway, pk=pk)
  gateway.activate()
  return redirect('gateway-detail', pk=pk)

def new_token(request, pk):
  gateway = get_object_or_404(Gateway, pk=pk)
  gateway.create_token()
  return render(request, 'new_token.html', {'gateway': gateway, 'token': gateway.get_token()})

@csrf_exempt
def sign_csr(request):
  name = request.GET.get('name')
  # Extraer token del header Authorization: Bearer <token>
  auth_header = request.headers.get("Authorization", "")
  if not auth_header.startswith("Bearer "):
    return HttpResponseForbidden("Missing Token")

  token = auth_header[7:]  # Quitar "Bearer "

  try:
    gateway = Gateway.objects.get(name=name)
  except Gateway.DoesNotExist:
    return HttpResponseForbidden(f"Gateway {name} does not exist")

  if gateway.get_token() != token:
    return HttpResponseForbidden(f"Invalid Token")
  
  # Leer CSR desde el body (como archivo PEM)
  csr_pem = request.body
  if not csr_pem:
    return JsonResponse({"error": "CSR not given"}, status=400)

  # Guardar CSR temporal
  csr_path = f"/tmp/{gateway.name}.csr"
  cert_path = f"/tmp/{gateway.name}_cert.pem"

  with open(csr_path, "wb") as f:
    f.write(csr_pem)

  # Firmar CSR con la CA
  cmd = [
    "openssl", "ca", "-batch", "-config", "openssl.cnf", "-policy",
    "signing_policy", "-extensions", "signing_req", "-out",
    cert_path, "-infiles", csr_path
  ]
  resultado = subprocess.run(cmd, capture_output=True)
  print("RESULT:", resultado)
  if resultado.returncode != 0:
    return JsonResponse({"error": "Error signing certificate", "detail:": resultado.stderr.decode()}, status=500)

  # Leer certificado firmado
  with open(cert_path, "rb") as f:
    cert_data = f.read()

  # Retornar certificado firmado para que la gateway lo descargue
  response = HttpResponse(cert_data, content_type="application/x-pem-file")
  response['Content-Disposition'] = f'attachment; filename="certificate.crt"'

  return response
