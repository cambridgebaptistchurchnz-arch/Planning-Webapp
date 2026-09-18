from django.contrib.auth.views import LogoutView
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
    path("volunteers/", views.volunteer_list, name="volunteer_list"),
    path("volunteers/new/", views.volunteer_edit, name="volunteer_add"),
    path("volunteers/<int:pk>/edit/", views.volunteer_edit, name="volunteer_edit"),
    path("volunteers/<int:pk>/delete/", views.volunteer_delete, name="volunteer_delete"),
    path("roles/", views.role_list, name="role_list"),
    path("roles/new/", views.role_edit, name="role_add"),
    path("roles/<int:pk>/edit/", views.role_edit, name="role_edit"),
    path("roles/<int:pk>/delete/", views.role_delete, name="role_delete"),
    path("users/", views.user_list, name="user_list"),
    path("users/new/", views.user_edit, name="user_add"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
    path("logout/", LogoutView.as_view(next_page="/admin/login/?next=/dashboard/"),name="logout"),
]