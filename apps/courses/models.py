from django.db import models
from .models.category import Category
from .models.course import Course, CourseCategory
from .models.module import Module
from .models.progress import Progress
from .models.enrollment import Enrollment
from .models.review import Review
from .models.content import Content, Text, Video, File, Image
from .models.progress_tracking import CompletedContent
# Create your models here.
