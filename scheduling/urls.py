from django.urls import path

from . import views

urlpatterns = [
    path("respond/<uuid:token>/", views.respond_to_assignment, name="respond_to_assignment"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/week/<int:pk>/", views.service_week_detail, name="service_week_detail"),
    path("dashboard/week/<int:pk>/item/<int:item_id>/delete/", views.delete_service_item, name="delete_service_item"),
    path(
        "dashboard/week/<int:pk>/assignment/<int:assignment_id>/delete/",
        views.delete_assignment,
        name="delete_assignment",
    ),
    path(
        "dashboard/week/<int:pk>/assignment/<int:assignment_id>/email/",
        views.email_assignment,
        name="email_assignment",
    ),
    path("dashboard/week/<int:pk>/email-all/", views.email_all_pending, name="email_all_pending"),
]