from django.urls import path
from .views import *

urlpatterns = [
    path('cours/', course_list, name='course_list'),
    path('cours/create/', create_course, name='create_course'),
    path('cours/<int:course_id>/', course_detail, name='course_detail'),
    path('cours/<int:course_id>/update/', update_course, name='update_course'),
    path('cours/<int:course_id>/delete/', delete_course, name='delete_course'),
    path('cours/<int:course_id>/manage_lessons/', manage_lessons, name='manage_lessons'),
        
    path('leçon/', lesson_list, name='lesson_list'),
    path('leçon/create/', create_lesson, name='create_lesson'),
    path('leçon/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('leçon/<int:lesson_id>/update/', update_lesson, name='update_lesson'),
    path('leçon/<int:lesson_id>/delete/', delete_lesson, name='delete_lesson'),
    
    path('leçon/<int:lesson_id>/quiz/', lesson_quiz, name='lesson_quiz'),
    path('leçon/<int:lesson_id>/result/', lesson_result, name='lesson_result'),
    path('leçon/add_question/<int:lesson_id>/', add_question, name='add_question'),
    
    path('enroll_student/<int:course_id>', enroll_student, name='enroll_student'),
    path('unenroll_student/<int:enrollment_id>/', unenroll_student, name='unenroll_student'),
    
    path('manage_students/', manage_students, name='manage_students'),
    path('manage_teacher_courses/', manage_teacher_courses, name='manage_teacher_courses'),
    
]