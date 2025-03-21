from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("active/", views.get_active_showings, name="active"),
    path("<int:showing_id>/", views.get_showing, name="showing"),
    path("parse/", views.parse_showings, name="parse"),
    path("get_movies/", views.get_all_movies, name="get_movies"),
]
