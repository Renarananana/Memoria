import django_tables2 as tables
from .models import Data

class DataTable(tables.Table):
  class Meta:
    model = Data
    template_name = "django_tables2/bootstrap4.html"
    fields = ("value", "timestamp")
