import qrcode
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.base import ContentFile
import base64
from .models import work_orders, equipment_labels, labels
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from reportlab.pdfgen import canvas


#View para ver las etiquetas impresas en el ultimo mes
class LogsListView(ListView):
    model = equipment_labels
    template_name = "polls/logs.html"
    context_object_name = "logs"

#View para ver las ordenes de trabajo activas
class WorkOrderListView(ListView):
    model = work_orders
    template_name = "polls/work_order.html"
    context_object_name = "orders"

#View para agregarle etiquetas a una orden de trabajo
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

#View para crear una orden de trabajo
class CreateWorkOrderView (CreateView):
    model = work_orders
    template_name = "polls/new_work_order.html"
    fields = ["order_number"]
    success_url = reverse_lazy("ordenes")

    def form_valid(self, form):
        # Check if a work order with the same order_number already exists
        if work_orders.objects.filter(order_number=form.cleaned_data["order_number"]).exists():
            print("DUPLICADO DETECTADO")
            context = self.get_context_data()
            context["error_message"] = f"La orden de trabajo para '{form.cleaned_data['order_number']}' ya fue ingresada."
            return self.render_to_response(context)

        # If no duplicate exists, save the work order
        form.instance.created_at = timezone.now()
        return super().form_valid(form)
    
#View para ver los detalles de una orden de trabajo antes de imprimirla 
class ImprimirDetailView (DetailView):
    model = work_orders
    template_name = "polls/print_label.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        labels = equipment_labels.objects.filter(work_orders=self.object)
        context["labels"] = labels
        return context
    
#View para ver las ordenes de trabajo activas antes de imprimirlas 
class OrdenesListView (ListView):
    model = work_orders
    template_name = "polls/ordenes.html"
    context_object_name = "orders"

def print (request,pk):
    order = get_object_or_404(work_orders, pk=pk)
    etiquetas = equipment_labels.objects.filter(work_orders=order)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="etiquetas_{order.order_number}.pdf"'
    p = canvas.Canvas(response)
    y = 750  # Posición inicial en el eje Y
    
    for etiqueta in etiquetas:
        # Generar el código QR
        qr = qrcode.make(etiqueta.equipment)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        # Dibujar el código QR en el PDF
        p.drawImage(buffer, 50, y, width=100, height=100)
        p.drawString(200, y + 40, f"Equipo: {etiqueta.equipment}")
        p.drawString(200, y + 20, f"Cantidad: {etiqueta.quantity}")
        y -= 150  # Mover hacia abajo para la siguiente etiqueta

        if y < 100:  # Si no hay espacio, crear una nueva página
            p.showPage()
            y = 750

    p.save()
    return response