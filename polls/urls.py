from django.urls import path
from .views import LogsListView, WorkOrderListView, CreateLabelView, CreateWorkOrderView

urlpatterns = [
    path("", LogsListView.as_view(), name="logs"),
    path("OrdenesTrabajo/", WorkOrderListView.as_view(), name="ordenes"),
    path("OrdenesTrabajo/<int:pk>/etiquetas", CreateLabelView.as_view(), name="etiquetas"),
    path("NuevaOrden/", CreateWorkOrderView.as_view(), name="registro_orden"),
]