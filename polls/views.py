import qrcode
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.base import ContentFile
import base64
from .models import inventario, etiquetas
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView

class createView (CreateView):
    model = inventario
    template_name = "polls/index.html"
    fields = ["pieza", "cantidad", "orden_trabajo"]
    success_url = "/imprimir/"






















# def create_pieza (request):
#     inventarios = inventario.objects.all()

#     if request.method == "POST":
#         action = request.POST.get("action")

#         if action == "create":  
#             pieza = request.POST.get("pieza")
#             cantidad = request.POST.get("cantidad")
#             pub_date = timezone.now()

#             inventario.objects.create(
#                 pieza=pieza,
#                 cantidad=cantidad,
#                 pub_date=pub_date
#             )

#         elif action == "update":
#             pieza = request.POST.get("pieza")
#             cantidad = request.POST.get("cantidad")
#             pub_date = timezone.now()
#             inventario.objects.create(
#                 pieza=pieza,
#                 cantidad=cantidad,
#                 pub_date=pub_date
#             )
        
#         elif action == "delete":
#             inventario_id = request.POST.get("inventario_id")
#             if inventario_id:
#                 inventario.objects.filter (id=inventario_id).delete() 
    
#     return render(request, 'polls/index.html', {'inventarios': inventarios})

# class LogsListView(ListView):
#     model = inventario
#     template_name = "polls/past_logs.html"
#     context_object_name = "logs"

# # def index(request):
# #     if request.method == "POST":
# #         #The data received from the POST request form
# #         pieza = request.POST.get("pieza")
# #         cantidad = request.POST.get("cantidad")
# #         pub_date = timezone.now()

# #         #Save it in the database
# #         inventario.objects.create(
# #             pieza = pieza, 
# #             cantidad = cantidad, 
# #             pub_date = pub_date
# #         )
        
# #         if pieza:
# #             qr = qrcode.make(pieza)
# #             buffer = BytesIO()
# #             qr.save(buffer, format="PNG")
# #             img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
# #             return render(request, "polls/index.html", {
# #                 "qr_code": img_base64,
# #                 "pieza": pieza
# #             })
        
# #     return render(request, "polls/index.html")