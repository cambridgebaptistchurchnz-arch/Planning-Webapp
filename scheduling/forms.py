from django import forms
from django.contrib.auth import get_user_model

from .models import Assignment, Role, ServiceItem, ServiceWeek, Volunteer

User = get_user_model()


class ServiceWeekForm(forms.ModelForm):
    class Meta:
        model = ServiceWeek
        fields = ["date", "label"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = ["item_type", "title", "duration_minutes", "notes"]


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["role", "volunteer"]


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ["name", "email", "phone", "active", "roles"]
        widgets = {
            "roles": forms.CheckboxSelectMultiple,
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "description"]


class StaffUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password. Required when creating a new login.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "is_staff", "is_active"]