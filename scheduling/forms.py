from django import forms

from .models import Assignment, ServiceItem, ServiceWeek


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