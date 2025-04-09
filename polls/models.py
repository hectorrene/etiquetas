from django.db import models

class orden_trabajo(models.Model):
    numero_orden = models.CharField(max_length=50, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OT-{self.numero_orden}"

class inventario (models.Model):
    orden_trabajo = models.ForeignKey(orden_trabajo, on_delete=models.CASCADE, related_name='piezas')
    pieza = models.CharField(max_length=18)
    cantidad = models.IntegerField(default=0)
    
    def __str__(self):
        return self.pieza
    
class etiquetas (models.Model):
    nombre = models.CharField(max_length=100, default="")
    width = models.DecimalField(
        max_digits = 5, 
        decimal_places = 2, 
        default = 0,
    )
    height = models.DecimalField(
        default=0,
        max_digits = 5, 
        decimal_places = 2, 
    )
    zpl_template = models.TextField(help_text="Código ZPL con placeholders como {{qr}}, {{pieza}}, etc.")