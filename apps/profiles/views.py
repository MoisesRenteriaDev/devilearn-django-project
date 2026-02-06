from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView, CreateView
from .models import Profile
from .forms import ProfileForm, CustomRegisterForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect
# Create your views here.


def index(request):
    return render(request, "profiles/profile.html")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['profile_picture'] = profile.photo.url if profile.photo else "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-icon-of-social-media-user-vector.jpg"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, "Tu perfil se ha actualizado correctamente.")
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('student:course_list')

    def form_valid(self, form):
        user = form.save()
        # user = form.save(commit=False)
        # user.is_active = False
        # user.save()
        login(self.request, user)
        return redirect(self.success_url)


class CustomPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'settings/change_password.html'
    success_url = reverse_lazy('change_password')
    success_message = "Contraseña actualizada correctamente"
