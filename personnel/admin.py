from django.contrib import admin

# Register your models here.
from .models import personnel , service , TypeConge
admin.site.register(personnel)
admin.site.register(service)
admin.site.register(TypeConge)