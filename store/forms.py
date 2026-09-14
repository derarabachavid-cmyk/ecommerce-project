from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "autocomplete": "username",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email address",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        ),
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm password",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                "This username is already registered."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "This email is already registered."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

    def save(self):
        """
        Create and return a Django User.
        This fixes:
        'RegisterForm' object has no attribute 'save'
        """

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )

        return user


class LoginForm(AuthenticationForm):
    pass


class CheckoutForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Full name",
                "autocomplete": "name",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email address",
                "autocomplete": "email",
            }
        ),
    )

    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Delivery address / place",
                "autocomplete": "street-address",
            }
        ),
    )

    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "City",
                "autocomplete": "address-level2",
            }
        ),
    )

    def clean_address(self):
        address = self.cleaned_data["address"].strip()

        if not address:
            raise ValidationError(
                "Delivery address is required."
            )

        return address

    def clean_city(self):
        city = self.cleaned_data["city"].strip()

        if not city:
            raise ValidationError(
                "City is required."
            )

        return city