from django.urls import path
from .views import (
    LogsListView,
    WorkOrderListView,
    CreateLabelView,
    CreateWorkOrderView,
    ImprimirDetailView,
    OrdenesListView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path("", LoginView.as_view(template_name="polls/login.html"), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("Inicio/", LogsListView.as_view(), name="logs"),
    path("Inicio/Ordenes/", OrdenesListView.as_view(), name="print"),
    path("Inicio/OrdenesActivas", WorkOrderListView.as_view(), name="ordenes"),
    path("Inicio/OrdenesActivas/<int:pk>/etiquetas", CreateLabelView.as_view(), name="etiquetas"),
    path("Inicio/OrdenesActivas/<int:pk>/etiquetas/imprimir", ImprimirDetailView.as_view(), name="imprimir"),
    path("Inicio/NuevaOrden/", CreateWorkOrderView.as_view(), name="registro_orden"),
]


