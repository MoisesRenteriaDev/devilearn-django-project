
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from ..models import Course, Module, Content, Text, Image, File, Video
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.forms.models import modelform_factory
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
import json

CONTENT_MODELS = {
    'text': Text,
    'image': Image,
    'file': File,
    'video': Video
}


class InstructorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_instructor


class CourseListView(InstructorRequiredMixin, ListView):
    model = Course
    template_name = 'instructor/course_list.html'
    context_object_name = "courses"
    paginate_by = 8

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)


class CourseCreateView(InstructorRequiredMixin, CreateView):
    model = Course
    fields = ['title', 'slug', 'overview',
              'image', 'level', 'duration', 'categories']
    template_name = 'instructor/course_form.html'
    success_url = reverse_lazy('instructor:course_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CourseUpdateView(InstructorRequiredMixin, UpdateView):
    model = Course
    fields = ['title', 'slug', 'overview',
              'image', 'level', 'duration', 'categories']
    template_name = 'instructor/course_form.html'
    success_url = reverse_lazy('instructor:course_list')

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)


class CourseDeleteView(InstructorRequiredMixin, DeleteView):
    model = Course
    template_name = 'instructor/course_confirm_delete.html'
    success_url = reverse_lazy('instructor:course_list')

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)

# Module Views


class ModuleListView(InstructorRequiredMixin, ListView):
    model = Module
    template_name = 'instructor/module_list.html'
    context_object_name = "modules"

    def get_queryset(self):
        self.course = get_object_or_404(
            Course, id=self.kwargs['course_id'], owner=self.request.user)
        return self.course.modules.all().order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        return context


class ModuleCreateView(InstructorRequiredMixin, CreateView):
    model = Module
    fields = ['title', 'description']
    template_name = 'instructor/module_form.html'

    def form_valid(self, form):
        course = get_object_or_404(
            Course, id=self.kwargs['course_id'], owner=self.request.user)
        form.instance.course = course
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('instructor:module_list', args=[self.object.course.id])


class ModuleUpdateView(InstructorRequiredMixin, UpdateView):
    model = Module
    fields = ['title', 'description']
    template_name = 'instructor/module_form.html'

    def get_queryset(self):
        return Module.objects.filter(course__owner=self.request.user)

    def get_success_url(self):
        return reverse('instructor:module_list', args=[self.object.course.id])


class ModuleDeleteView(InstructorRequiredMixin, DeleteView):
    model = Module
    template_name = 'instructor/module_confirm_delete.html'

    def get_queryset(self):
        return Module.objects.filter(course__owner=self.request.user)

    def get_success_url(self):
        return reverse('instructor:module_list', args=[self.object.course.id])

# Content


class ContentListView(InstructorRequiredMixin, ListView):
    model = Content
    template_name = 'instructor/content_list.html'
    context_object_name = "contents"

    def get_queryset(self):
        self.module = get_object_or_404(
            Module, id=self.kwargs['module_id'], course__owner=self.request.user)
        return self.module.contents.all().select_related('content_type').order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.module
        return context


class ContentCreateUpdateView(InstructorRequiredMixin, View):
    template_name = 'instructor/content_form.html'

    def get_model(self, model_name):
        return CONTENT_MODELS.get(model_name, None)

    def get_form(self, model, *args, **kwars):
        Form = modelform_factory(
            model, exclude=['owner', 'created_at', 'updated_at'])
        return Form(*args, **kwars)

    def dispatch(self, request, module_id=None, model_name=None, id=None, *args, **kwargs):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        self.obj = None

        if id:
            try:
                content = Content.objects.select_related('content_type').get(
                    object_id=id,
                    content_type=ContentType.objects.get_for_model(self.model),
                    module=self.module
                )
                self.obj = content.item
            except Content.DoesNotExist:
                return HttpResponseForbidden("No tienes permiso o tipo invalido")

        return super().dispatch(request, module_id, model_name, id,  *args, **kwargs)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return render(request, self.template_name, {'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj,
                             data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Content.objects.create(module=self.module, item=obj)
            return redirect('instructor:content_list', module_id=self.module.id)
        return render(request, self.template_name, {'form': form, 'object': self.obj})


class ContentDeleteView(InstructorRequiredMixin, DeleteView):
    model = Content
    template_name = 'instructor/content_confirm_delete.html'

    def get_queryset(self):
        return Content.objects.filter(module__course__owner=self.request.user)

    def get_success_url(self):
        return reverse('instructor:content_list', args=[self.object.module.id])


class ModuleOrderView(InstructorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            order = data.get('order', [])

            # {2,3,4,5} -> {0: 4,1: 2,5,3}
            for index, module_id in enumerate(order):
                modules = Module.objects.filter(
                    id=module_id, course__owner=request.user).update(order=index)

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class ContentOrderView(InstructorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            order = data.get('order', [])

            # {2,3,4,5} -> {0: 4,1: 2,5,3}
            for index, content_id in enumerate(order):
                Content.objects.filter(
                    id=content_id, module__course__owner=request.user).update(order=index)
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
