from django.shortcuts import redirect, render, get_object_or_404
from ..models import Course
from ..models.enrollment import Enrollment
from ..models.progress_tracking import CompletedContent
from ..models.content import Content
from ..models.progress import Progress
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def course_list(request):
    courses = Course.objects.all()
    query = request.GET.get("q")

    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(owner__first_name__icontains=query)
        )

    paginator = Paginator(courses, 8)
    page_number = request.GET.get("page")
    courses_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if "page" in query_params:
        query_params.pop("page")
    query_string = query_params.urlencode()

    return render(request, "courses/courses.html", {
        'courses_obj': courses_obj,
        'query': query,
        'query_string': query_string
    })

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    modules = course.modules.prefetch_related('contents').order_by('order')
    total_contents = sum(module.contents.count() for module in modules)
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'total_contents': total_contents
    })

@login_required
def course_lessons(request, slug, content_id=None):
    course = get_object_or_404(Course, slug=slug)
    course_title = course.title
    modules = course.modules.prefetch_related('contents').order_by('order')

    # Enrollment
    Enrollment.objects.get_or_create(user=request.user, course=course)

    # get all contents
    all_contents = [c for m in modules for c in m.contents.all()]
    total_contents = len(all_contents)

    completed = CompletedContent.objects.filter(
        user=request.user, content__in=all_contents).values_list('content_id', flat=True)

    # progress by module
    for module in modules:
        module.completed_count = module.contents.filter(
            id__in=completed).count()
        module.total_count = module.contents.count()

    current_content = None
    if content_id:
        current_content = get_object_or_404(
            Content, id=content_id, module__course=course
        )

    progress = (len(completed) / total_contents * 100) if total_contents else 0

    Progress.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={'progress': progress}
    )

    return render(request, 'courses/course_lessons.html',
                  {
                      'course_title': course_title,
                      'modules': modules,
                      'course': course,
                      'completed_ids': set(completed),
                      'current_content': current_content,
                      'progress': int(progress)
                  })

@login_required
def mark_complete(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    CompletedContent.objects.get_or_create(user=request.user, content=content)

    next_content = Content.objects.filter(
        module=content.module,
        order__gt=content.order,
    ).order_by('order').first()

    if next_content:
        return redirect('student:course_lessons', slug=content.module.course.slug, content_id=next_content.id)

    return redirect("student:course_lessons", slug=content.module.course.slug)
