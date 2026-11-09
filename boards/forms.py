from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Project, Task, TaskComment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "autocomplete": "email"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Website refresh"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "maxlength": 500,
                    "placeholder": "What is this project about?",
                }
            ),
        }


class MemberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Add by username"}
        ),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        try:
            self.member = User.objects.get(username__iexact=username)
        except User.DoesNotExist as exc:
            raise forms.ValidationError(
                "No account was found with that username."
            ) from exc
        return username


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assignee", "status", "priority", "due_date"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Give this task a name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "maxlength": 1000,
                    "placeholder": "Add useful details or acceptance notes",
                }
            ),
            "assignee": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        self.fields["assignee"].queryset = project.members.order_by("username")
        self.fields["assignee"].required = False
        self.fields["assignee"].empty_label = "Unassigned"

    def clean_assignee(self):
        assignee = self.cleaned_data.get("assignee")
        if assignee and not self.project.members.filter(pk=assignee.pk).exists():
            raise forms.ValidationError("Choose a member of this project.")
        return assignee


class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "maxlength": 500,
                    "placeholder": "Share an update or ask a question...",
                    "data-counter-input": "",
                }
            )
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "autofocus": True, "autocomplete": "username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "autocomplete": "current-password"}
        )
    )
