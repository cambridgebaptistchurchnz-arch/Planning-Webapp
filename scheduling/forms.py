from django import forms

from .models import Assignment, Role, ServiceItem, ServiceWeek, Volunteer


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
        fields = ["order", "item_type", "title", "duration_minutes", "notes"]


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["role", "volunteer"]


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ["name", "email", "phone", "active"]


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["name", "description"]