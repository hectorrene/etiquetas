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
    engineerGuide,
    SearchResultsView
)

#URL's for each view in the app

urlpatterns = [
    path("", LoginView.as_view(template_name="polls/login.html"), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("Inicio/", LogsListView.as_view(), name="logs"),
    path("search/", SearchResultsView.as_view(), name="search"),
    path("Ordenes/", OrdenesListView.as_view(), name="print"),
    path("OrdenesActivas", WorkOrderListView.as_view(), name="ordenes"),
    path("OrdenesActivas/<int:pk>/etiquetas", CreateLabelView.as_view(), name="etiquetas"),
    path("OrdenesActivas/<int:pk>/etiquetas/imprimir", ImprimirDetailView.as_view(), name="imprimir"),
    path("NuevaOrden/", CreateWorkOrderView.as_view(), name="registro_orden"),
    path("Guia/", engineerGuide, name="guia"),
]


