from django.shortcuts import render
from .models import Data
from devices.models import Device
from profiles.models import DeviceResource, DeviceCommand
import plotly.graph_objs as go
import plotly.io as pio
from django_tables2 import RequestConfig
from .tables import DataTable
from .forms import WriteForm
from django.forms import formset_factory
from utils.http_helpers import get, put
import json

def data_plot_view(request, device_pk, resource_pk):
  
  device = Device.objects.get(pk = device_pk)
  resource = DeviceResource.objects.get(pk = resource_pk)
  msg = None
  form = WriteForm()
  if request.method == "POST":
    if "read" in request.POST:
      try:
        msg = get(device.gateway, f"/core-command/api/v3/device/name/{device.name}/{resource.name}")
      except Exception as e:
        msg = {"status_code": 500, "text": str(e)}
    else:
      form = WriteForm(request.POST)
      if form.is_valid():
        data = form.cleaned_data["data"]
        body = {resource.name: data}
        msg = put(device.gateway, f"/core-command/api/v3/device/name/{device.name}/{resource.name}", json=body)
  plot_html, table = generate_plot(device, resource)
  RequestConfig(request, paginate={"per_page": 10}).configure(table)
  return render(request, 'data_plot.html', {'plot_html': plot_html, 'table': table, "form": form, "resource": resource, "msg": msg})

def generate_plot(device, resource):
  data_qs = Data.objects.filter(
    device = device,
    resource = resource
  )
  table =DataTable(data_qs)
  timestamps = [d.timestamp for d in data_qs]
  numeric = {
    "Uint8", "Uint16", "Uint32", "Uint64",
    "Int8", "Int16", "Int32", "Int64",
    "Float32", "Float64",
    "Uint8Array", "Uint16Array", "Uint32Array", "Uint64Array",
    "Int8Array", "Int16Array", "Int32Array", "Int64Array",
    "Float32Array", "Float64Array"
  }
  if resource.properties.valueType in numeric:
    values = [float(d.value) for d in data_qs]
    # Si hay datos validos:
    if timestamps and values:
      fig = go.Figure()
      fig.add_trace(go.Scatter(x=timestamps, y=values, mode='lines+markers', name='Valor'))

      fig.update_layout(
        title=f'{resource.name} vs Timestamp',
        xaxis_title='Timestamp',
        yaxis_title=f'{resource.name}',
        template='plotly_white'
      )

      plot_html = pio.to_html(fig, full_html=False)
    else:
      plot_html = "<p>No data to plot</p>"
  else:
    values = [d.value for d in data_qs]
    plot_html = None
  return plot_html, table

def command_view(request, device_pk, command_pk):
  device = Device.objects.get(pk = device_pk)
  command = DeviceCommand.objects.get(pk = command_pk)
  msg = None
  readings = None
  WriteFormSet = formset_factory(WriteForm, extra=0)
  formset = WriteFormSet(initial=[{"resource_name": operation.resource.name, "resource_valueType": operation.resource.properties.valueType} for operation in command.operations.all()])
  if request.method == "POST":
    if "read" in request.POST:
      try:
        msg = get(device.gateway, f"/core-command/api/v3/device/name/{device.name}/{command.name}")
        data = json.loads(msg.text)
        if msg.status_code == 200:
          msg = {"status_code": 200, "text": "Readings recieved"}
        readings = data.get("event", {}).get("readings", [])
      except Exception as e:
        msg = {"status_code": 500, "text": str(e)}
    else:
      formset = WriteFormSet(request.POST)
      if formset.is_valid():
        body = {}
        for form in formset:
          body[form.cleaned_data["resource_name"]] = form.cleaned_data["data"]
        msg = put(device.gateway, f"/core-command/api/v3/device/name/{device.name}/{command.name}", json=body)
  return render(request, 'command.html', {"form": formset, "command": command, "msg": msg, 'readings': readings})