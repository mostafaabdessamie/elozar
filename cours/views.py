from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Cours, Lesson, Question, Choice, StudentScore, Enrollment
from .forms import QuestionForm
from django.utils import timezone

# ---- PERMISSIONS ----
def is_course_owner(user, course):
    return user.is_authenticated and user.user_type == 2 and user == course.teacher

def check_course_owner(user, course):
    if not is_course_owner(user, course):
        raise PermissionDenied("Vous n'êtes pas le propriétaire de ce cours.")

# ---- COURS PUBLIC ----

@login_required
def course_list(request):
    courses = Cours.objects.all().select_related('teacher')
    return render(request, 'cours/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('order')
    students = Enrollment.objects.filter(course=course).select_related('student')
    return render(request, 'cours/course_detail.html', {
        'course': course, 
        'lessons': lessons, 
        'students': students,
        'is_owner': is_course_owner(request.user, course)
    })

@login_required
def lesson_list(request):
    lessons = Lesson.objects.all().select_related('course')
    return render(request, 'cours/lesson_list.html', {'lessons': lessons})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'cours/lesson_detail.html', {'lesson': lesson})

# ---- GESTION COURS - PROPRIÉTAIRE SEULEMENT ----
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def create_course(request):
    if request.user.user_type != 2:
        messages.error(request, "Seuls les enseignants peuvent créer un cours.")
        return redirect('course_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        accept_responsabilite = request.POST.get('accept_responsabilite')
        accept_droits = request.POST.get('accept_droits')
        accept_loi = request.POST.get('accept_loi')

        if not accept_responsabilite or not accept_droits or not accept_loi:
            messages.error(request, "Vous devez accepter toutes les conditions de responsabilité et légales pour créer un cours.")
            return render(request, 'cours/create_course.html', {
                'title': title,
                'description': description,
            })
        
        Cours.objects.create(
            title=title,
            description=description,
            image=image,
            teacher=request.user,
            accepted_terms=True,
            accepted_at=timezone.now(),
            accepted_ip=get_client_ip(request),
            is_validated=True
        )
        messages.success(request, 'Cours créé avec succès! Vous êtes responsable du contenu publié.')
        return redirect('course_list')
        
    return render(request, 'cours/create_course.html')

@login_required
def update_course(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    try:
        check_course_owner(request.user, course)
    except PermissionDenied:
        messages.error(request, "⛔ Vous n'êtes pas autorisé à modifier ce cours. Seul le créateur peut le faire.")
        return redirect('course_list')
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        if request.FILES.get('image'):
            course.image = request.FILES.get('image')
        course.save()
        messages.success(request, 'Cours mis à jour avec succès!')
        return redirect('course_detail', course_id=course.id)
    return render(request, 'cours/update_course.html', {'course': course})

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    try:
        check_course_owner(request.user, course)
    except PermissionDenied:
        messages.error(request, "⛔ Vous n'êtes pas autorisé à supprimer ce cours.")
        return redirect('course_list')
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Cours supprimé avec succès!')
        return redirect('course_list')
    return render(request, 'cours/confirm_delete.html', {'course': course})

# ---- GESTION LEÇONS - PROPRIÉTAIRE SEULEMENT ----

@login_required
def create_lesson(request):
    if request.user.user_type != 2:
        messages.error(request, "Accès refusé.")
        return redirect('course_list')
    if request.method == 'POST':
        course = get_object_or_404(Cours, id=request.POST.get('course'))
        check_course_owner(request.user, course)
        Lesson.objects.create(
            course=course,
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            video=request.FILES.get('profile_video'),
            image=request.FILES.get('image'),
            pdf=request.FILES.get('pdf'),
            order=request.POST.get('order', 0)
        )
        messages.success(request, 'Leçon créée avec succès!')
        return redirect('course_detail', course_id=course.id)
    courses = Cours.objects.filter(teacher=request.user)
    return render(request, 'cours/create_lesson.html', {'courses': courses})

@login_required
def update_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    check_course_owner(request.user, lesson.course)
    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.content = request.POST.get('content')
        lesson.video = request.FILES.get('profile_video', lesson.video)
        lesson.image = request.FILES.get('image', lesson.image)
        lesson.pdf = request.FILES.get('pdf', lesson.pdf)
        lesson.order = request.POST.get('order', lesson.order)
        lesson.save()
        messages.success(request, 'Leçon mise à jour avec succès!')
        return redirect('course_detail', course_id=lesson.course.id)
    return render(request, 'cours/update_lesson.html', {'lesson': lesson})

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    check_course_owner(request.user, lesson.course)
    course_id = lesson.course.id
    lesson.delete()
    messages.success(request, 'Leçon supprimée avec succès!')
    return redirect('course_detail', course_id=course_id)

@login_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    check_course_owner(request.user, course)
    lessons = Lesson.objects.filter(course=course)
    return render(request, 'cours/manage_lessons.html', {'course': course, 'lessons': lessons})

@login_required
def manage_students(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    
    # الأستاذ ممنوع
    if request.user.user_type == 2:
        raise PermissionDenied("⛔ Cette page est réservée aux étudiants.")

    # خاص يكون مسجل فالكور
    if not Enrollment.objects.filter(course=course, student=request.user).exists():
        messages.error(request, "Vous devez être inscrit à ce cours pour voir les camarades.")
        return redirect('course_detail', course_id=course.id)

    students = Enrollment.objects.filter(course=course).select_related('student')
    return render(request, 'cours/manage_students.html', {'course': course, 'students': students})

@login_required
def unenroll_student(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    check_course_owner(request.user, enrollment.course)
    enrollment.delete()
    messages.success(request, "L'élève a été désinscrit avec succès.")
    return redirect('manage_teacher_courses')

@login_required
def manage_teacher_courses(request):
    if request.user.user_type != 2: 
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('course_list')
    courses = Cours.objects.filter(teacher=request.user)
    course_data = []
    for course in courses:
        lessons = Lesson.objects.filter(course=course)
        enrollments = Enrollment.objects.filter(course=course)  
        course_data.append({
            'course': course,
            'lessons': lessons,
            'student_count': enrollments.count(),
            'enrollments': enrollments  
        })
    return render(request, 'cours/manage_teacher_courses.html', {'course_data': course_data})

# ---- ELEVES ----

@login_required
def enroll_student(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    if request.user.user_type != 3:
        messages.error(request, "Seuls les élèves peuvent s'inscrire.")
        return redirect('course_detail', course_id=course.id)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, 'Inscription réussie!')
    else:
        messages.info(request, 'Vous êtes déjà inscrit.')
    return redirect('course_detail', course_id=course.id)

# ---- QUIZ ----

@login_required
def lesson_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Question.objects.filter(lesson=lesson)
    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                try:
                    choice = Choice.objects.get(id=selected_choice_id)
                    if choice.is_correct:
                        score += question.points
                except Choice.DoesNotExist:
                    pass
        student_score, _ = StudentScore.objects.get_or_create(student=request.user, lesson=lesson)
        student_score.score = score
        student_score.save()
        messages.success(request, f'Votre score est enregistré: {score} points!')
        return redirect('lesson_result', lesson_id=lesson.id)
    return render(request, 'cours/quiz/lesson_quiz.html', {'lesson': lesson, 'questions': questions})

@login_required
def lesson_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    student_score = get_object_or_404(StudentScore, student=request.user, lesson=lesson)
    return render(request, 'cours/quiz/lesson_result.html', {'lesson': lesson, 'student_score': student_score})

@login_required
def add_question(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    check_course_owner(request.user, lesson.course)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(
                lesson=lesson,
                text=form.cleaned_data['text'],
                points=form.cleaned_data['points']
            )
            for i in range(1, 5):
                choice_text = form.cleaned_data.get(f'choice_{i}')
                is_correct = form.cleaned_data.get(f'is_correct_{i}')
                if choice_text:
                    Choice.objects.create(question=question, text=choice_text, is_correct=is_correct)
            messages.success(request, 'Question ajoutée avec succès!')
            return redirect('lesson_quiz', lesson_id=lesson.id)
    else:
        form = QuestionForm()
    return render(request, 'cours/quiz/add_question.html', {'lesson': lesson, 'form': form})