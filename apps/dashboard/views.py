from django.shortcuts import render, redirect
from apps.courses.models import Course
from apps.profiles.models import Profile
# Create your views here.


def index(request):
    courses = Course.objects.filter(
        enrollment__user=request.user).order_by('?')[:3]

    profile = Profile.objects.get(user=request.user)

    last_course = {
        "slug": request.session.get('last_course_slug'),
        "title": request.session.get('last_course_title'),
        "image": request.session.get('last_course_image')
    }

    return render(request, "dashboard/index.html", {
        'courses': courses,
        'profile': profile,
        'last_course': last_course
    })


def redirect_home(request):
    user = request.user

    if getattr(user, 'is_instructor', False):
        return redirect('instructor:course_list')
    else:
        return redirect('student:course_list')
