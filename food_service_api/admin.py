from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(Food)
admin.site.register(Order)

