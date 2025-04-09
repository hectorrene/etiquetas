from django.urls import path
from .views import createView

urlpatterns = [
    path('', createView.as_view(), name='create-view'),
    #path("historial/", LogsListView.as_view(), name="past_logs"),
]