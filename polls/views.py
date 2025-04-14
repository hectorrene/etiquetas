from django.shortcuts import redirect
from django.http import HttpResponse
from .models import work_orders, equipment_labels
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import qrcode
import datetime

#VISTAS DE CONSULTAS

#View para ver las etiquetas impresas en el ultimo mes
class LogsListView(ListView):
    model = equipment_labels
    template_name = "polls/logs.html"
    context_object_name = "logs"

    def get_queryset(self):
        today = timezone.now()
        last_month = today - datetime.timedelta(days=30)
        return equipment_labels.objects.filter(pub_date__gte=last_month).order_by("-pub_date")

#View para ver las ordenes de trabajo activas
class WorkOrderListView(ListView):
    model = work_orders
    template_name = "polls/work_order.html"
    context_object_name = "orders"
    
    def get_queryset(self):
        return work_orders.objects.order_by("-pub_date")[:50]

#View para ver los detalles de una orden de trabajo antes de imprimirla , generación de QR e impresión
class ImprimirDetailView (DetailView):
    model = work_orders
    template_name = "polls/print_label.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        labels = equipment_labels.objects.filter(work_orders=self.object)
        context["labels"] = labels
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        label_id = request.POST.get("label_id")
        action = request.POST.get("action")

        # Permite borrar etiquetas antes de imprimir
        if action == "delete" and label_id:
            try:
                label = equipment_labels.objects.get(id=label_id, work_orders=self.object)
                label.delete()
                messages.success(request, "Etiqueta eliminada exitosamente.")
            except equipment_labels.DoesNotExist:
                messages.error(request, "Etiqueta no encontrada.")


        return redirect("imprimir", pk=self.object.pk) 
    
    #Manda generar el pdf
    def get(self, request, *args, **kwargs):
        if request.GET.get("pdf") == "true":
            return self.pdf()
        return super().get(request, *args, **kwargs)
    
    #hace el pdf y el codigo QR
    def pdf(self):
        self.object = self.get_object()
        buffer = io.BytesIO()
        custom_size = (1.2390 * 72, 0.3950 * 72)
        p = canvas.Canvas(buffer, pagesize=custom_size)

        labels = equipment_labels.objects.filter(work_orders=self.object)

        for label in labels:
            for serial in range(1, label.quantity + 1):
                p.setFont("Helvetica", 3)
                data = label.equipment + "-" + str(serial).zfill(2)  # Serial number with leading zeros

                qr = qrcode.QRCode(version=2, box_size=10, border=5)
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                img_buffer.seek(0)

                p.drawImage(ImageReader(img_buffer), 5, 2, width=custom_size[1], height=custom_size[1])
                p.drawString(30, 10, f"{label.equipment}-{str(serial).zfill(2)}")
                p.showPage()  # Termina la página actual

        p.save()  # Aquí sí: después de todo el for
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orden_{self.object.order_number}.pdf"'
        return response
    
#View para ver las ordenes de trabajo activas antes de imprimirlas
class OrdenesListView (ListView):
    model = work_orders
    template_name = "polls/ordenes.html"
    context_object_name = "orders"

    def get_queryset(self):
        return work_orders.objects.order_by("-pub_date")[:50]

#VISTAS DE CREACION Y EDICION

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
    
