from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import work_orders, equipment_labels, labels, work_cells
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from zebra import Zebra
from django.db.models import Q
import datetime
import requests
import base64
from .forms import LabelForm

#Work order detail view and printing

class PrintLabelsView(View):
    template_name = "polls/print_label.html"

    def get(self, request):
        form = LabelForm(queryset=equipment_labels.objects.none())
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LabelForm(request.POST)
        if form.is_valid():
            form.save()
            label_type = request.POST.get("label_type")

            zpl_data = self.create_labels(label_type)
            return self.print_labels(zpl_data)
        else:
            messages.error(request, "Por favor corrige los errores.")
            return render(request, self.template_name, {"form": form})

    # --- MÉTODOS AUXILIARES ---
    def create_zpl(self, part_number):
        return (
            "^XA"
            "^PW251"
            "^LL80"
            "^FO10,30^BQN,2,2^FDLA," + part_number + "^FS"
            "^FO60,55^A0N,20,20^FD" + part_number + "^FS"
            "^XZ"
        )

    def zpl_barcode(self, part_number):
        return (
            "^XA"
            "^PW251"
            "^LL80"
            "^FO40,35"
            "^BY1,2,30"
            "^BCN,30,Y,N,N"
            "^FD" + part_number + "^FS"
            "^XZ"
        )

    def create_labels(self, request):
        equipments = equipment_labels.objects.all()
        if not equipments.exists():
            return HttpResponse("No hay etiquetas para esta orden.", status=400)

        labels = []

        # Recorre cada fila guardada y genera ZPL según el tipo de etiqueta
        for equipment in equipments:
            for serial in range(1, equipment.quantity + 1):
                part_number = f"{equipment.equipment}-{str(serial).zfill(2)}"
                
                # Usa el label_type de la fila
                if equipment.label_type == "qr":
                    labels.append(self.create_zpl(part_number))
                elif equipment.label_type == "barcode":
                    labels.append(self.zpl_barcode(part_number))

        return labels

    def print_labels(self, zpl_list):
        try:
            images = []
            errores = []

            for idx, label in enumerate(zpl_list, start=1):
                print(f"--- ZPL etiqueta #{idx} ---")
                print(label)
                
                # URL corregida (sin el / al final puede causar 404)
                url = "http://api.labelary.com/v1/printers/8dpmm/labels/4x2/0/"
                
                response = requests.post(
                    url,
                    data=label.encode("utf-8"),
                    headers={"Accept": "image/png"}  # Este header está correcto
                )

                if response.status_code == 200:
                    image_data = base64.b64encode(response.content).decode("utf-8")
                    images.append(f"data:image/png;base64,{image_data}")
                    errores.append(None)
                else:
                    print(f"❌ Error en etiqueta #{idx}: {response.status_code}")
                    print(f"Respuesta: {response.text}")
                    images.append(None)
                    errores.append(f"Código {response.status_code}: {response.text}")

            # Construye el HTML
            html = "<h2>Vista previa de etiquetas</h2>"
            for i, (img, error) in enumerate(zip(images, errores), start=1):
                html += f"<p><strong>Etiqueta #{i}</strong></p>"
                if img:
                    html += f"<img src='{img}' style='margin-bottom:20px;border:1px solid #ccc;'><br>"
                else:
                    html += f"<p style='color:red;'>Error: {error}</p><br>"

            return HttpResponse(html)

        except Exception as e:
            return HttpResponse(f"Error inesperado: {str(e)}", status=500)
    
    def post(self, request):
        print("🟢 Se recibió un POST en PrintLabelsView")

        form = LabelForm(request.POST)
        if form.is_valid():
            print("✅ form válido")
            form.save()

            label_type = request.POST.get("label_type")
            print(f"Tipo de etiqueta seleccionado: {label_type}")

            zpl_data = self.create_labels(label_type)
            return self.print_labels(zpl_data)
        else:
            print("❌ form no válido")
            print(form.errors)
            messages.error(request, "Por favor corrige los errores.")
            return render(request, self.template_name, {"form": form})
        
#LIST VIEWS

#Labels made in the last month
# class LogsListView(ListView):
#     model = equipment_labels
#     template_name = "polls/logs.html"
#     context_object_name = "logs"

#     #retrieves the labels printed in the last_month
#     def get_queryset(self):
#         today = timezone.now()
#         last_month = today - datetime.timedelta(days=30)
#         return equipment_labels.objects.filter(pub_date__gte=last_month).order_by("-pub_date")

#Allows the search bar to work, filter by work cell, work order, equipment or date
# class SearchResultsView(ListView):
#     model = equipment_labels
#     template_name = "polls/search.html"
#     context_object_name = "equipment_list"
    
#     #allows to filter by search
#     def get_queryset (self):
#         query = self.request.GET.get("search")
#         if query: 
#             return equipment_labels.objects.filter(
#                 Q(equipment__icontains=query) | Q(work_orders__order_number__icontains=query) | Q(work_orders__work_cell__work_cell__icontains = query)
#             )
#         return equipment_labels.objects.none() 
        
# #Active work orders before printing
# class OrdenesListView (ListView):
#     model = work_orders
#     template_name = "polls/ordenes.html"
#     context_object_name = "orders"

#     #filters last 50 active work orders
#     def get_queryset(self):
#         return work_orders.objects.filter(is_active=True).order_by("-pub_date")[:50]

# #Engineering guide
# def engineerGuide(request):
#     return render(request, "polls/engineer_guide.html")

# #CREATE AND UPDATE VIEWS

# #Add equipment to a work order
# class CreateLabelView(CreateView):
#     model = equipment_labels
#     template_name = "polls/add_tag.html"
#     fields = ["equipment", "quantity"]

#     #makes sure the information in the form is valid before registering it
#     def form_valid(self, form):
#         # Get the related work order using the primary key from the URL
#         order = get_object_or_404(work_orders, pk=self.kwargs["pk"])
#         form.instance.work_orders = order  # Assign the work_orders field correctly
#         equipment = form.cleaned_data["equipment"]
            
#         if equipment_labels.objects.filter(work_orders=order).filter(Q(equipment__iexact=equipment)).exists():
#             context = self.get_context_data()
#             context["error_message"] = f"La etiqueta para '{equipment}' ya fue ingresada."
#             return self.render_to_response(context)

#     # Save the new tag
#         form.save()
#         context = self.get_context_data()
#         context["success_message"] = "Etiqueta agregada exitosamente."
#         return self.render_to_response(context)

#     def get_context_data(self, **kwargs):
#         # Pass the work order to the template for display
#         context = super().get_context_data(**kwargs)
#         order = get_object_or_404(work_orders, pk=self.kwargs["pk"])
#         context["order"] = get_object_or_404(work_orders, pk=self.kwargs["pk"])
#         return context

# #Create work order view
# class CreateWorkOrderView (CreateView):
#     model = work_orders
#     template_name = "polls/new_work_order.html"
#     fields = ["order_number", "work_cell"]
#     success_url = reverse_lazy("ordenes")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["work_cells"] = work_cells.objects.all()  
#         return context

#     #saves the work order and checks for duplicates
#     def form_valid(self, form):
#         # Check if a work order with the same order_number already exists
#         if work_orders.objects.filter(order_number__iexact = form.cleaned_data["order_number"]).exists():
#             context = self.get_context_data()
#             context["error_message"] = f"La orden de trabajo ya ha sido ingresada."
#             return self.render_to_response(context)

#         # If no duplicate exists, save the work order
#         form.instance.created_at = timezone.now()
#         form.instance.is_active = True
#         return super().form_valid(form)
    
