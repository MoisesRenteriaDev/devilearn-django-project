from django.shortcuts import redirect, render

# Create your views here.


def index(request):
    return render(request, "dashboard/index.html")


def redirect_home(request):
    user = request.user
    
    if getattr(user, 'is_instructor', False):
        return redirect('instructor:course_list')
    else:
        return redirect("student:course_list")