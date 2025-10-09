from django.db import models

#Model to register work cells
class work_cells(models.Model):
    work_cell = models.CharField(max_length=50, unique=True)
    size = models.CharField(
    choices=[
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large"),
    ],
    default="small",
    max_length=10,  # Ensure the max_length is sufficient for the longest value
)

    def __str__(self):
        return self.work_cell

#Model to register work orders 
class work_orders(models.Model):
    cell = models.CharField(max_length=50, default="")
    order_number = models.CharField(max_length=50, unique=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.order_number

#Model to register equipment, which later will be used to generate labels 
class equipment_labels (models.Model):
    label_type = models.CharField(choices = [
        ('qr', 'QR Code'),
        ('barcode', 'Código de Barras'),
    ])
    equipment = models.CharField(max_length=18)
    quantity = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.equipment

#Model to register label's size
class labels (models.Model):
    name = models.CharField(max_length=100, default="")
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

    def __str__(self):
        return self.name