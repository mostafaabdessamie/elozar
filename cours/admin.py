from django.contrib import admin
from .models import Cours, Lesson, Question, Choice, StudentScore

class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'content')
    ordering = ('order',)  

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    search_fields = ('title', 'description')

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1  
    

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'lesson', 'points')
    search_fields = ('text',)
    inlines = [ChoiceInline]

class StudentScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'score')
    search_fields = ('student__username', 'lesson__title')

# Register models with the admin site
admin.site.register(Cours, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(StudentScore, StudentScoreAdmin)