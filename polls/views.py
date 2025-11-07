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
 
class PrintLabelsView(View):
    template_name = "polls/print_label.html"
    ZEBRA_PRINTER_NAME = "ZDesigner ZT411-300dpi ZPL"
 
    def get(self, request):
        form = LabelForm()
        return render(request, self.template_name, {"form": form})
 
    def post(self, request):
        print("🟢 Se recibió un POST en PrintLabelsView")
 
        form = LabelForm(request.POST)
        if form.is_valid():
            print("✅ form válido")
            form.save()
 
            label_type = request.POST.get("label_type")
            print(f"Tipo de etiqueta seleccionado: {label_type}")
 
            zpl_data = self.create_labels(request)
            return self.print_labels(zpl_data)
        else:
            print("❌ form no válido")
            print(form.errors)
            messages.error(request, "Por favor corrige los errores.")
            return render(request, self.template_name, {"form": form})
 
    # --- MÉTODOS AUXILIARES ---
 
    def create_zpl(self, part_number):
        return (
            "^XA\n"
            # Configuración básica para 2 columnas
            "^PW354\n"              # Ancho: 3cm = 354 dots a 300dpi
            "^LL118\n"              # Alto: 1cm = 118 dots a 300dpi
            "^LH0,0\n"              # Home position
           
            # Código QR - MUCHO más centrado
            "^FO50,10\n"           # Posición: 100 dots desde izq, 35 desde arriba
            "^BQN,2,4\n"            # QR code: N=normal, magnification=2, error correction=3 (Q=25%)
            "^FDLA," + part_number + "^FS\n"
           
            # Texto al lado del QR
            "^FO490,60\n"           # Posición del texto más a la derecha
            "^A0N,18,18\n"          # Font 0, orientación normal, altura 18, ancho 18
             + part_number + 
            "^XZ"
        )
 
    def zpl_barcode(self, part_number):
        """
        Etiqueta de código de barras para 3cm × 1cm
        Configurado para 2 columnas - CENTRADO MÁS A LA DERECHA Y ABAJO
        """
        return (
            "^XA\n"
            # Configuración básica para 2 columnas
            "^PW354\n"              # Ancho: 3cm = 354 dots a 300dpi
            "^LL118\n"              # Alto: 1cm = 118 dots a 300dpi
            "^LH0,0\n"              # Home position
           
            # Código de barras Code 128 - MUCHO más centrado
            "^FO80,50\n"           # Posición más a la derecha y abajo
            "^BY2,2,60\n"           # Bar width=2, ratio=2, height=40 dots
            "^BCN,40,N,N,N\n"       # Code 128, altura 40, sin texto interpretado arriba
            "^FD" + part_number + "^FS\n"
           
            # Texto legible debajo del código
            "^FO120,75\n"           # Debajo del barcode, alineado
            "^A0N,16,16\n"          # Font más pequeño para que quepa
 
            "^XZ"
        )
 
    def create_labels(self, request):
        """Crea todas las etiquetas en formato ZPL"""
        equipments = equipment_labels.objects.all()
        if not equipments.exists():
            return HttpResponse("No hay etiquetas para esta orden.", status=400)
 
        labels = []
        for equipment in equipments:
            for serial in range(1, equipment.quantity + 1):
                part_number = f"{equipment.equipment}-{str(serial).zfill(2)}"
                if equipment.label_type == "qr":
                    labels.append(self.create_zpl(part_number))
                elif equipment.label_type == "barcode":
                    labels.append(self.zpl_barcode(part_number))
        return labels
 
    def print_labels(self, zpl_list):
        """
        Si hay impresora Zebra con el nombre especificado → imprime directamente.
        Si no la encuentra → genera vista previa (Labelary).
        """
        try:
            z = Zebra()
            printers = z.getqueues()
            print(f"🖨️ Impresoras instaladas: {printers}")
 
            selected_printer = next(
                (p for p in printers if self.ZEBRA_PRINTER_NAME.lower() in p.lower()),
                None
            )
 
            if selected_printer:
                # --- IMPRESIÓN DIRECTA ---
                z.setqueue(selected_printer)
                print(f"📦 Usando impresora: {selected_printer}")
 
                for idx, zpl in enumerate(zpl_list, start=1):
                    print(f"🧾 Enviando etiqueta #{idx}...")
                    z.output(zpl.encode("utf-8"))
                    print("✅ Impresa correctamente")
 
                return HttpResponse(f"✅ Todas las etiquetas fueron enviadas a '{selected_printer}' correctamente.")
 
            else:
                # --- SIN IMPRESORA DETECTADA: usar vista previa ---
                print(f"⚠️ No se encontró la impresora '{self.ZEBRA_PRINTER_NAME}'. Mostrando vista previa...")
 
                images = []
                errores = []
                for idx, label in enumerate(zpl_list, start=1):
                    # Usar dimensiones correctas en Labelary: 1.2in × 0.4in (aprox 3cm × 1cm)
                    url = "http://api.labelary.com/v1/printers/12dpmm/labels/1.2x0.4/0/"
                    response = requests.post(
                        url,
                        data=label.encode("utf-8"),
                        headers={"Accept": "image/png"}
                    )
 
                    if response.status_code == 200:
                        image_data = base64.b64encode(response.content).decode("utf-8")
                        images.append(f"data:image/png;base64,{image_data}")
                        errores.append(None)
                    else:
                        errores.append(f"Código {response.status_code}: {response.text}")
                        images.append(None)
 
                html = f"<h2>Vista previa (no se encontró la impresora '{self.ZEBRA_PRINTER_NAME}')</h2>"
                for i, (img, err) in enumerate(zip(images, errores), start=1):
                    html += f"<p><strong>Etiqueta #{i}</strong></p>"
                    if img:
                        html += f"<img src='{img}' style='margin-bottom:20px;border:1px solid #ccc;'><br>"
                    else:
                        html += f"<p style='color:red;'>Error: {err}</p><br>"
 
                return HttpResponse(html)
 
        except Exception as e:
            print(f"❌ Error al imprimir o generar vista previa: {str(e)}")
            return HttpResponse(f"Error: {str(e)}", status=500)
 