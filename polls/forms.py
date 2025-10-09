from django import forms  
from .models import equipment_labels

class LabelForm(forms.ModelForm):
    class Meta:
        model = equipment_labels
        fields = ["equipment", "quantity", "label_type"]  
        widgets = {
            "equipment": forms.TextInput(attrs={"class": "form-input", "required": "true"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "style": "width: 150px;"}),
            "label_type": forms.Select(attrs={"class": "form-input"}),
        }


