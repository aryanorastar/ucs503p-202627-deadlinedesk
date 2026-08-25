from django import forms
from django.core.exceptions import ValidationError

from .models import Assignment, ChecklistItem, Company, Grade, PlacementRound, Submission


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "description"]


class PlacementRoundForm(forms.ModelForm):
    class Meta:
        model = PlacementRound
        fields = ["company", "title", "opens_at", "closes_at"]
        widgets = {
            "opens_at": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
            "closes_at": DateTimeLocalInput(format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opens_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["closes_at"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned = super().clean()
        opens_at = cleaned.get("opens_at")
        closes_at = cleaned.get("closes_at")
        if opens_at and closes_at and closes_at <= opens_at:
            self.add_error("closes_at", "Closing time must be after opening time.")
        return cleaned


class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ["title", "required", "position"]


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_at", "late_policy", "grace_minutes", "penalty_percent"]
        widgets = {"due_at": DateTimeLocalInput(format="%Y-%m-%dT%H:%M")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["due_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["grace_minutes"].help_text = "Used only for the grace-window policy."
        self.fields["penalty_percent"].help_text = "Used only for accept-with-penalty."

    def clean(self):
        cleaned = super().clean()
        policy = cleaned.get("late_policy")
        if policy == Assignment.LatePolicy.GRACE and not cleaned.get("grace_minutes"):
            self.add_error("grace_minutes", "Enter a grace-window duration.")
        if policy == Assignment.LatePolicy.PENALTY and not cleaned.get("penalty_percent"):
            self.add_error("penalty_percent", "Enter a late penalty percentage.")
        return cleaned


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["file", "note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3})}

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if uploaded_file.size > 5 * 1024 * 1024:
            raise ValidationError("Maximum upload size is 5 MB.")
        extension = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
        if extension not in {"pdf", "txt", "md", "docx", "zip", "py", "java", "cpp", "js"}:
            raise ValidationError("Use PDF, text, source-code, DOCX, or ZIP files.")
        return uploaded_file


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["score", "max_score", "feedback"]
        widgets = {"feedback": forms.Textarea(attrs={"rows": 4})}

    def clean(self):
        cleaned = super().clean()
        score = cleaned.get("score")
        max_score = cleaned.get("max_score")
        if score is not None and max_score is not None and score > max_score:
            self.add_error("score", "Score cannot exceed the maximum score.")
        return cleaned
