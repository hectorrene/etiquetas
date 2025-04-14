from django.contrib import admin
from .models import work_orders, equipment_labels, labels

admin.site.register(work_orders)
admin.site.register(equipment_labels)
admin.site.register(labels)

# Adds models to the django admin site for easier management
