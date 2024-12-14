from django.contrib import admin
from .models import Measurement, Order, Master

admin.site.register(Master)
admin.site.register(Measurement)
admin.site.register(Order)

