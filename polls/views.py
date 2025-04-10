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

class LogsListView(ListView):
    model = equipment_labels
    template_name = "polls/logs.html"
    context_object_name = "logs"

class WorkOrderListView(ListView):
    model = work_orders
    template_name = "polls/work_order.html"
    context_object_name = "orders"

class CreateLabelView(CreateView):
    model = equipment_labels
    template_name = "polls/add_tag.html"
    fields = ["equipment", "quantity"]

    def form_valid(self, form):
        # Get the related work order using the primary key from the URL
        order = get_object_or_404(work_orders, pk=self.kwargs["pk"])
        form.instance.work_orders = order  # Assign the work_orders field correctly
        form.save()
        context = self.get_context_data()
        context["success_message"] = "Etiqueta agregada exitosamente."
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # Pass the work order to the template for display
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(work_orders, pk=self.kwargs["pk"])
        context["order"] = get_object_or_404(work_orders, pk=self.kwargs["pk"])
        context["tags"] = order.piezas.all()
        return context
    
class CreateWorkOrderView (CreateView):
    model = work_orders
    template_name = "polls/new_work_order.html"
    fields = ["order_number"]
    success_url = "/OrdenesTrabajo/"

    def form_valid(self, form):
        form.instance.created_at = timezone.now()
        return super().form_valid(form)

