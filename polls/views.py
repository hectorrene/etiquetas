from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import work_orders, equipment_labels, labels, work_cells
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from zebra import Zebra
from django.db.models import Q
import datetime


#LIST VIEWS

#Labels made in the last month
class LogsListView(ListView):
    model = equipment_labels
    template_name = "polls/logs.html"
    context_object_name = "logs"

    #retrieves the labels printed in the last_month
    def get_queryset(self):
        today = timezone.now()
        last_month = today - datetime.timedelta(days=30)
        return equipment_labels.objects.filter(pub_date__gte=last_month).order_by("-pub_date")

class SearchResultsView(ListView):
    model = equipment_labels
    template_name = "polls/search.html"
    context_object_name = "equipment_list"
    
    #allows to filter by search
    def get_queryset (self):
        query = self.request.GET.get("search")
        if query: 
            return equipment_labels.objects.filter(
                Q(equipment__icontains=query) | Q(work_orders__order_number__icontains=query)
            )
        return equipment_labels.objects.none() 

#Active work orders
class WorkOrderListView(ListView):
    model = work_orders
    template_name = "polls/work_order.html"
    context_object_name = "orders"
    
    #retrieves the active work orders
    def get_queryset(self):
        return work_orders.objects.filter(is_active=True).order_by("-pub_date")[:50]

#Work order detail view and printing
class ImprimirDetailView (DetailView):
    model = work_orders
    template_name = "polls/print_label.html"
    
    #retrieves the equipment assosiated with the work order
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["work_order"] = self.object
        labels = equipment_labels.objects.filter(work_orders=self.object)
        context["labels"] = labels
        return context
    
    # Handles the POST request to delete a label
    def pots_delete (self, request, *args, **kwargs):
        self.object = self.get_object()
        label_id = request.POST.get("label_id")
        action = request.POST.get("action")

        if action == "delete" and label_id:
            try:
                label = equipment_labels.objects.get(id=label_id, work_orders=self.object)
                label.delete()
                messages.success(request, "Etiqueta eliminada exitosamente.")
            except equipment_labels.DoesNotExist:
                messages.error(request, "Etiqueta no encontrada.")

        return redirect("imprimir", pk=self.object.pk) 

    #Handles the GET request to call the zpl generator and the printer
    def get_print (self, request, *args, **kwargs):
        if request.GET.get("print") == "true":
            option = request.GET.get("option")
            if option == "qr":
                work_order = self.get_object()
                work_order.is_active = False
                work_order.save()
                zpl = self.create_labels()
                return self.print_labels(zpl)
            elif option == "barcode":
                print ("barcode process")
            else: 
                messages.error(request, "Opcion no valida.")

    #creates the zpl format of the labels
    def create_zpl (self, part_number): 
        zpl = f"""
                ^XA
                ^PW251
                ^LL80

                ^FO10,30^BQN,2,2
                ^FDLA,{part_number}^FS

                ^FO60,55^A0N,20,20^FD{part_number}^FS

                ^XZ
            """    
        return zpl
    
    #sends the information of the work order to the zpl generator
    def create_labels (self):
        equipments = equipment_labels.objects.filter(work_orders=self.object)
        if not equipments.exists():
            return HttpResponse("No hay etiquetas asociadas con esta orden de trabajo.", status=400)
        labels = []

        # goes trough each equipment piece and sends the information to the zpl generator
        for equipment in equipments:
            for serial in range (1, equipment.quantity + 1):
                part_number = equipment.equipment + "-" + str(serial).zfill(2)
                labels.append(self.create_zpl(part_number))
        return labels
    
    #prints the labels using the zebra printer
    def print_labels (self, zpl):
        try:
            z = Zebra()
            z.setqueue("ZDesigner ZT610-300dpi ZPL")  
            z.output("".join(zpl))
        except Exception as e:
            messages.error(self.request, f"Error al imprimir: {str(e)}")
        
#Active work orders before printing
class OrdenesListView (ListView):
    model = work_orders
    template_name = "polls/ordenes.html"
    context_object_name = "orders"

    #filters last 50 active work orders
    def get_queryset(self):
        return work_orders.objects.filter(is_active=True).order_by("-pub_date")[:50]

#Engineering guide
def engineerGuide(request):
    return render(request, "polls/engineer_guide.html")

#CREATE AND UPDATE VIEWS

#Add equipment to a work order
class CreateLabelView(CreateView):
    model = equipment_labels
    template_name = "polls/add_tag.html"
    fields = ["equipment", "quantity"]

    def form_valid(self, form):
        # Get the related work order using the primary key from the URL
        order = get_object_or_404(work_orders, pk=self.kwargs["pk"])
        form.instance.work_orders = order  # Assign the work_orders field correctly
        equipment = form.cleaned_data["equipment"]
        
        if equipment_labels.objects.filter(work_orders=order, equipment=equipment).exists():
            context = self.get_context_data()
            context["error_message"] = f"La etiqueta para '{equipment}' ya fue ingresada."
            return self.render_to_response(context)

    # Save the new tag
        form.save()
        context = self.get_context_data()
        context["success_message"] = "Etiqueta agregada exitosamente."
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # Pass the work order to the template for display
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(work_orders, pk=self.kwargs["pk"])
        context["order"] = get_object_or_404(work_orders, pk=self.kwargs["pk"])
        return context

#Create work order view
class CreateWorkOrderView (CreateView):
    model = work_orders
    template_name = "polls/new_work_order.html"
    fields = ["order_number", "work_cell"]
    success_url = reverse_lazy("ordenes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["work_cells"] = work_cells.objects.all()  
        return context

    #saves the work order and checks for duplicates
    def form_valid(self, form):
        # Check if a work order with the same order_number already exists
        if work_orders.objects.filter(order_number=form.cleaned_data["order_number"]).exists():
            print("DUPLICADO DETECTADO")
            context = self.get_context_data()
            context["error_message"] = f"La orden de trabajo para '{form.cleaned_data['order_number']}' ya fue ingresada."
            return self.render_to_response(context)

        # If no duplicate exists, save the work order
        form.instance.created_at = timezone.now()
        form.instance.is_active = True
        return super().form_valid(form)
    
