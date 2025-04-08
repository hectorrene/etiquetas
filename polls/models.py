from django.db import models

class inventario (models.Model):
    pieza = models.CharField(max_length=18)
    cantidad = models.IntegerField()
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.pieza