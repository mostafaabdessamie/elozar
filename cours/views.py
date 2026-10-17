from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cours, Lesson, Question, Choice, StudentScore, Enrollment
from .forms import QuestionForm

@login_required
def course_list(request):
    courses = Cours.objects.all()
    return render(request, 'cours/course_list.html', {'courses': courses})

@login_required
def enroll_student(request, course_id):
    course = get_object_or_404(Cours, id=course_id)

    # تحقق مما إذا كان المستخدم طالبًا وليس مدرسًا أو مشرفًا
    if request.user.user_type != 3:
        messages.error(request, "Seuls les élèves peuvent s'inscrire à ce cours.")
        return redirect('course_detail', course_id=course.id)

    # التحقق من عدم التسجيل المسبق
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        Enrollment.objects.create(student=request.user, course=course).save()
        messages.success(request, 'Inscription réussie!')
    else:
        messages.info(request, 'Vous êtes déjà inscrit.')

    return redirect('course_detail', course_id=course.id)

@login_required
def unenroll_student(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.user != enrollment.course.teacher:
        messages.error(request, "Vous n'avez pas la permission de désinscrire cet élève.")
        return redirect('manage_teacher_courses')

    enrollment.delete()
    messages.success(request, "L'élève a été désinscrit avec succès.")

    return redirect('manage_teacher_courses')

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('order')
    students = Enrollment.objects.filter(course=course).select_related('student')

    return render(request, 'cours/course_detail.html', {
        'course': course, 
        'lessons': lessons, 
        'students': students
    })


@login_required
def lesson_list(request):
    lessons = Lesson.objects.all()
    return render(request, 'cours/lesson_list.html', {'lessons': lessons})

@login_required
def create_course(request):
    if request.method == 'POST' and request.user.user_type == 2:
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        course = Cours.objects.create(
            title=title,
            description=description,
            image=image,
            teacher=request.user
        )
        messages.success(request, 'Cours créé avec succès!')
        return redirect('course_list')
    else:
        messages.error(request, 'Échec de la création du cours. Veuillez vérifier les données.')
    return render(request, 'cours/create_course.html')

@login_required
def create_lesson(request):
    if request.method == 'POST' and request.user.user_type == 2:
        course_id = request.POST.get('course')
        course = get_object_or_404(Cours, id=course_id)

        if request.user != course.teacher:
            messages.error(request, 'Vous n\'êtes pas autorisé à ajouter une leçon à ce cours.')
            return redirect('course_list')

        title = request.POST.get('title')
        content = request.POST.get('content')
        video = request.FILES.get('profile_video')
        image = request.FILES.get('image')
        pdf = request.FILES.get('pdf')
        order = request.POST.get('order', 0)

        lesson = Lesson.objects.create(
            course=course,
            title=title,
            content=content,
            video=video,
            image=image,
            pdf=pdf,
            order=order
        )
        messages.success(request, 'Leçon créée avec succès!')
        return redirect('course_detail', course_id=course.id)

    courses = Cours.objects.filter(teacher=request.user)
    return render(request, 'cours/create_lesson.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('order')
    return render(request, 'cours/course_detail.html', {'course': course, 'lessons': lessons})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'cours/lesson_detail.html', {'lesson': lesson})

@login_required
def update_course(request, course_id):
    course = get_object_or_404(Cours, id=course_id)

    if request.user.user_type != 2 and request.user != course.teacher:
        messages.error(request, 'Vous n\'êtes pas autorisé à modifier ce cours.')
        return redirect('course_list')

    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.save()
        messages.success(request, 'Cours mis à jour avec succès!')
        return redirect('course_detail', course_id=course.id)

    return render(request, 'cours/update_course.html', {'course': course})

@login_required
def update_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.user != lesson.course.teacher:
        messages.error(request, 'Vous n\'êtes pas autorisé à modifier cette leçon.')
        return redirect('course_list')

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
def delete_course(request, course_id):
    course = get_object_or_404(Cours, id=course_id)

    if request.user != course.teacher:
        messages.error(request, 'Vous n\'êtes pas autorisé à supprimer ce cours.')
        return redirect('course_list')

    course.delete()
    messages.success(request, 'Cours supprimé avec succès!')
    return redirect('course_list')

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.user != lesson.course.teacher:
        messages.error(request, 'Vous n\'êtes pas autorisé à supprimer cette leçon.')
        return redirect('course_list')

    lesson.delete()
    messages.success(request, 'Leçon supprimée avec succès!')
    return redirect('course_detail', course_id=lesson.course.id)

@login_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Cours, id=course_id)

    if request.user != course.teacher:
        messages.error(request, 'Vous n\'êtes pas autorisé à gérer les leçons de ce cours.')
        return redirect('course_list')

    lessons = Lesson.objects.filter(course=course)
    return render(request, 'cours/manage_lessons.html', {'course': course, 'lessons': lessons})

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

        student_score, created = StudentScore.objects.get_or_create(student=request.user, lesson=lesson)
        student_score.score = score
        student_score.save()

        messages.success(request, f'Votre score est enregistré: {score} points!')
        return redirect('lesson_result', lesson_id=lesson.id)

    return render(request, 'cours/quiz/lesson_quiz.html', {'lesson': lesson, 'questions': questions})

@login_required
def lesson_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    student_score = StudentScore.objects.get(student=request.user, lesson=lesson)

    if request.user != student_score.student:
        messages.error(request, 'Vous n\'êtes pas autorisé à voir ce résultat.')
        return redirect('course_list')

    return render(request, 'cours/quiz/lesson_result.html', {'lesson': lesson, 'student_score': student_score})

@login_required
def add_question(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.user != lesson.course.teacher:
        messages.error(request, 'Vous n\'êtes pas autorisé à ajouter des questions à cette leçon.')
        return redirect('course_list')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            points = form.cleaned_data['points']

            question = Question.objects.create(
                lesson=lesson,
                text=text,
                points=points
            )

            for i in range(1, 5):
                choice_text = form.cleaned_data.get(f'choice_{i}')
                is_correct = form.cleaned_data.get(f'is_correct_{i}')
                if choice_text:
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=is_correct
                    )

            messages.success(request, 'Question ajoutée avec succès!')
            return redirect('lesson_quiz', lesson_id=lesson.id)
    else:
        form = QuestionForm()

    return render(request, 'cours/quiz/add_question.html', {'lesson': lesson, 'form': form})
@login_required
def manage_students(request, course_id):
    course = get_object_or_404(Cours, id=course_id)

    if request.user != course.teacher:
        messages.error(request, 'Vous n\'êtes pas autorisé à gérer les étudiants de ce cours.')
        return redirect('course_list')

    students = Enrollment.objects.filter(course=course).select_related('student')

    return render(request, 'cours/manage_students.html', {
        'course': course,
        'students': students
    })

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
        student_count = enrollments.count()  
        course_data.append({
            'course': course,
            'lessons': lessons,
            'student_count': student_count,
            'enrollments': enrollments  
        })

    return render(request, 'cours/manage_teacher_courses.html', {'course_data': course_data})

