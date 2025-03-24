from django.urls import path

from .views import ShowingView

urlpatterns = [
    path("active/", ShowingView.as_view(), name="active"),
]
