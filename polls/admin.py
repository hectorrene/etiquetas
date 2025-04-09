from django.contrib import admin
from .models import inventario, orden_trabajo, etiquetas 

admin.site.register(inventario)
admin.site.register(orden_trabajo)
admin.site.register(etiquetas)

# Register your models here.
