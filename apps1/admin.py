from django.contrib import admin

# Register your models here.
from .models import DatasetModel
admin.site.register(DatasetModel)