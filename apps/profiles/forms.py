from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from .models import User as CustomUser

TIMEZONE_CHOICES = [
    ("UTC-6", "UTC-6 Ciudad de México"),
    ("UTC-5", "UTC-5 Bogotá"),
    ("UTC-3", "UTC-3 Buenos Aires")
]


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last name")

    class Meta:
        model = Profile
        fields = ['photo', 'company', 'profession', 'timezone']
        widgets = {
            'timezone': forms.Select(choices=TIMEZONE_CHOICES)
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = self.instance.user

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            profile.save()

        return profile


class CustomRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name",
                  "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado")
        return email
