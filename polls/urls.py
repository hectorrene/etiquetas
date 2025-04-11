from django.urls import path
from .views import LogsListView, WorkOrderListView, CreateLabelView, CreateWorkOrderView, ImprimirDetailView, OrdenesListView, print

urlpatterns = [
    path("", LogsListView.as_view(), name="logs"),
    path("Ordenes/", OrdenesListView.as_view(), name="print"),
    path("OrdenesActivas", WorkOrderListView.as_view(), name="ordenes"),
    path("OrdenesActivas/<int:pk>/etiquetas", CreateLabelView.as_view(), name="etiquetas"),
    path("OrdenesActivas/<int:pk>/etiquetas/imprimir", ImprimirDetailView.as_view(), name="imprimir"),
    path("OrdenesActivas/<int:pk>/etiquetas/imprimir/pdf", print, name="pdf"),
    path("NuevaOrden/", CreateWorkOrderView.as_view(), name="registro_orden"),
]



