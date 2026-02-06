from django.urls import path
from ..views import student

app_name = 'student'

urlpatterns = [
    path("courses/", student.course_list, name="course_list"),  # /courses
    path("detail/<str:slug>", student.course_detail, name="course_detail"),
    path("<str:slug>/lessons/<int:content_id>/",
         student.course_lessons, name="course_lessons"),
    path("<str:slug>/lessons/", student.course_lessons, name="course_lessons"),
    path('content/<int:content_id>/complete/',
         student.mark_complete, name="mark_complete"),
    path("<slug:slug>/review/", student.review_course, name="review_course")
]
