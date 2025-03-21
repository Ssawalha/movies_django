from django.urls import path

from .views import GetActiveShowingsView, ParseDataView

urlpatterns = [
    path("active/", GetActiveShowingsView.as_view(), name="active"),
    path("parse/", ParseDataView.as_view(), name="parse"),
]
