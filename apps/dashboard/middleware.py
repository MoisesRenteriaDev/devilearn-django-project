
from django.shortcuts import redirect
from django.urls import reverse


class RedirectAuthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = [reverse('login')]

        if request.user.is_authenticated and request.path in protected_paths:

            if getattr(request.user, 'is_instructor', False):
                return redirect('instructor:course_list')

            return redirect('student:course_list')

        return self.get_response(request)
