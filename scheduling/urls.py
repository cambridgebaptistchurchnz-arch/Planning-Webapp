from django.urls import path

from . import views

urlpatterns = [
    path("respond/<uuid:token>/", views.respond_to_assignment, name="respond_to_assignment"),
]
