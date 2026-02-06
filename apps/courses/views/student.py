from django.shortcuts import render, get_object_or_404, redirect
from ..models.course import Course
from ..models.enrollment import Enrollment
from ..models.progress_tracking import CompletedContent
from ..models.content import Content
from ..models.progress import Progress
from ..models.review import Review
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import ReviewForm
from django.db.models import Avg, Count
# Create your views here.


@login_required
def course_list(request):
    # courses = Course.objects.all()
    query = request.GET.get("q")
    filter_type = request.GET.get("filter", "all")

    if filter_type == "enrolled":
        courses = Course.objects.filter(enrollment__user=request.user)
    elif filter_type == "not_enrolled":
        courses = Course.objects.exclude(enrollment__user=request.user)
    else:
        courses = Course.objects.all()

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
        'query_string': query_string,
        "filter_type": filter_type
    })


@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    modules = course.modules.prefetch_related('contents').order_by('order')
    total_contents = sum(module.contents.count() for module in modules)

    is_enrolled = Enrollment.objects.filter(
        user=request.user, course=course).exists()

    reviews = (Review.objects.filter(course=course).select_related(
        "user").order_by("-created_at"))

    stats = reviews.aggregate(avg=Avg("rating"), total=Count("id"))

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'total_contents': total_contents,
        'is_enrolled': is_enrolled,
        'stats': stats,
        'reviews': reviews
    })


@login_required
def course_lessons(request, slug, content_id=None):
    course = get_object_or_404(Course, slug=slug)
    course_title = course.title
    modules = course.modules.prefetch_related('contents').order_by('order')

    request.session['last_course_slug'] = course.slug
    request.session['last_course_title'] = course.title
    request.session['last_course_image'] = course.image

    request.session.modified = True

    # Enrollemnt
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
            Content, id=content_id, module__course=course)

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
        order__gt=content.order
    ).order_by('order').first()

    if next_content:
        return redirect('student:course_lessons', slug=content.module.course.slug, content_id=next_content.id)

    return redirect('student:course_lessons', slug=content.module.course.slug)


def user_is_enrolled(user, course: Course) -> bool:
    is_enrolled = Enrollment.objects.filter(
        user=user, course=course).exists()

    return is_enrolled or user.is_staff


def review_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if not user_is_enrolled(request.user, course):
        messages.error(
            request, "Debes estar inscrito en el curso para evaluarlo.")
        return redirect("student:course_detail", slug=course.slug)

    try:
        instance = Review.objects.get(user=request.user, course=course)
        is_update = True
    except Review.DoesNotExist:
        instance = None
        is_update = False

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=instance)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.course = course
            review.save()

            reviews = (
                Review.objects.filter(course=course).select_related(
                    "user").order_by("-created_at")
            )

            stats = reviews.aggregate(avg=Avg("rating"), total=Count("id"))
            course.rating = stats['avg']
            course.save()

            message = "Gracias por tu reseña" if not is_update else "Reseña actualizada"
            messages.success(request, message)

            return redirect("student:course_detail", slug=course.slug)
    else:
        form = ReviewForm(instance=instance)

    return render(request, "courses/review_course.html", {
        "course": course,
        "form": form,
        "is_update": is_update
    })
