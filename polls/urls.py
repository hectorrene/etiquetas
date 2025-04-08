from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("historial/", views.past_logs, name="past_logs"),
]