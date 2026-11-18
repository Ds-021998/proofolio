"""
Sign-up.

The one decision that matters here: **a new account is always a student.**

The product rests on judgements being written only by markers. If anyone
could sign up and choose "tutor", that rule would mean nothing. So the role
is not a field on this form — it is set in the view, to student, always.
Tutors and coordinators are promoted by a coordinator from inside the course.

A student also has to supply their course's join code. Without it we would
have accounts belonging to no course, and every page in the app asks "which
course is this person in?" before it asks anything else.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Course


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Use your university address.",
    )
    join_code = forms.CharField(
        label="Course join code",
        max_length=20,
        help_text="Given to you by your course coordinator.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["username"].help_text = "Letters, digits and @ . + - _ only."

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with that email already exists.")
        return email

    def clean_join_code(self):
        """Resolve the code to a real course, or refuse.

        The error deliberately doesn't say whether the code exists — it just
        says it isn't valid — so the form can't be used to discover codes.
        """
        code = self.cleaned_data["join_code"].strip().upper()
        course = Course.objects.filter(join_code__iexact=code).first()
        if course is None:
            raise forms.ValidationError("That join code isn't valid. Check it with your coordinator.")
        self.course = course
        return code
