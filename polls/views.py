import qrcode
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.base import ContentFile
import base64
from .models import inventario
from django.utils import timezone


def index(request):
    if request.method == "POST":
        #The data received from the POST request form
        pieza = request.POST.get("pieza")
        cantidad = request.POST.get("cantidad")
        pub_date = timezone.now()

        #Save it in the database
        inventario.objects.create(
            pieza = pieza, 
            cantidad = cantidad, 
            pub_date = pub_date
        )
        
        if pieza:
            qr = qrcode.make(pieza)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return render(request, "polls/index.html", {
                "qr_code": img_base64,
                "pieza": pieza
            })
        
    return render(request, "polls/index.html")

def past_logs (request):
    latest_logs = inventario.objects.order_by("-pub_date")[:100]
    return render(request, "polls/past_logs.html", {
        "logs": latest_logs,
    })

def template (request):
    return render(request, "polls/base.html")