from django.urls import path
from ..views import instructor

app_name = 'instructor'

urlpatterns = [
    path('courses/', instructor.CourseListView.as_view(), name="course_list"),
    path('course/create', instructor.CourseCreateView.as_view(), name="course_create"),
    path('course/<int:pk>/edit/',
         instructor.CourseUpdateView.as_view(), name="course_edit"),
    path('course/<int:pk>/delete/',
         instructor.CourseDeleteView.as_view(), name="course_delete"),
    # Modules URLs
    path('course/<int:course_id>/modules/',
         instructor.ModuleListView.as_view(), name='module_list'),
    path('course/<int:course_id>/modules/add',
         instructor.ModuleCreateView.as_view(), name='module_add'),
    path('modules/<int:pk>/edit/',
         instructor.ModuleUpdateView.as_view(), name='module_edit'),
    path('module/<int:pk>/delete/',
         instructor.ModuleDeleteView.as_view(), name='module_delete'),
    # Contenido
    path('module/<int:module_id>/contents/',
         instructor.ContentListView.as_view(), name='content_list'),
    path('module/<int:module_id>/content/<model_name>/add/',
         instructor.ContentCreateUpdateView.as_view(), name="content_add"),
    path('module/<int:module_id>/content/<int:id>/<model_name>/edit/',
         instructor.ContentCreateUpdateView.as_view(), name="content_edit"),
    path('content/<int:pk>/delete/',
         instructor.ContentDeleteView.as_view(), name='content_delete'),

    # order
    path('module/order/', instructor.ModuleOrderView.as_view(), name="module_order"),
    path('content/order/', instructor.ContentOrderView.as_view(), name="content_order")
]
