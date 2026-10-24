from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Teacher, Student, Group, Payment
from users.models import CustomUser, Profile, Post
from .forms import TeacherForm, StudentForm, GroupForm, PaymentForm

User = get_user_model()

def est_admin(user):
    return user.is_authenticated and user.user_type == 1

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if est_admin(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Vous n'avez pas les permissions pour accéder à cette page")
            return redirect('dashboard')
    return _wrapped_view

@login_required
def dashboard(request):
    user = request.user
    context = {}
    # Admin / Staff
    if user.is_staff or user.user_type == 1 :
        context['is_admin'] = True
        context['total_students'] = Student.objects.count()
        context['total_teachers'] = Teacher.objects.count()
        context['total_groups'] = Group.objects.count()
        context['recent_payments'] = Payment.objects.select_related('student').order_by('-date')[:10]
    # Professeur
    elif user.user_type == 2 :
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            teacher = Teacher.objects.create(user=user, subject="Non défini", phone="")
        my_groups = Group.objects.filter(teacher=teacher)
        my_students = Student.objects.filter(groups__in=my_groups).distinct()
        context['is_prof'] = True
        context['teacher'] = teacher
        context['my_groups'] = my_groups
        context['my_students'] = my_students
        context['total_my_groups'] = my_groups.count()
        context['total_my_students'] = my_students.count()
    # Élève
    else:
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            student = Student.objects.filter(name=user.username).first()
            if student and not student.user:
                student.user = user
                student.save()
        if student:
            my_groups = student.groups.all()
            my_payments = Payment.objects.filter(student=student).order_by('-date')
            context['is_student'] = True
            context['student'] = student
            context['my_groups'] = my_groups
            context['my_payments'] = my_payments
            context['total_my_groups'] = my_groups.count()
            context['total_paid'] = sum([float(p.amount_paid) for p in my_payments])
        else:
            context['is_student'] = True
            context['student'] = None
            context['my_groups'] = []
            context['my_payments'] = []
            context['total_my_groups'] = 0
            context['total_paid'] = 0
    return render(request, 'core/dashboard.html', context)

@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home_chat')

    users = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )

    profiles = Profile.objects.filter(
        Q(user__username__icontains=query) |
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query) |
        Q(bio__icontains=query) |
        Q(location__icontains=query)
    )

    posts = Post.objects.filter(
        Q(content__icontains=query)
    )

    total = users.count() + profiles.count() + posts.count()

    return render(request, 'core/search_results.html', {
        'query': query,
        'results': {
            'users': users,
            'profiles': profiles,
            'posts': posts,
        },
        'total': total
    })

@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-date')
    total_centre = sum(p.centre_share for p in payments)
    total_prof = sum(p.teacher_share for p in payments)
    return render(request, 'core/payments.html', {
        'payments': payments,
        'total_centre': total_centre,
        'total_prof': total_prof
    })

# Teachers
@admin_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'core/teachers.html', {'teachers': teachers})

@admin_required
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professeur ajouté avec succès ✅')
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'core/add_teacher.html', {'form': form})

@admin_required
def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Professeur modifié avec succès ✏️')
            return redirect('teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'core/edit_teacher.html', {'form': form})

@admin_required
def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Professeur supprimé avec succès 🗑️')
        return redirect('teacher_list')
    return render(request, 'core/confirm_delete.html', {'object': teacher})

# Students
@admin_required
def student_list(request):
    students = Student.objects.all()
    return render(request, 'core/students.html', {'students': students})

@admin_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Élève ajouté avec succès 🎓')
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'core/add_student.html', {'form': form})

@admin_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Élève modifié avec succès ✏️')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'core/edit_student.html', {'form': form})

@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Élève supprimé avec succès 🗑️')
        return redirect('student_list')
    return render(request, 'core/confirm_delete.html', {'object': student})

@admin_required
def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paiement ajouté avec succès 💰')
            return redirect('payment_list')
    else:
        form = PaymentForm()
    return render(request, 'core/add_payment.html', {'form': form})

@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'core/groups.html', {'groups': groups})

@admin_required
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Groupe ajouté avec succès ✅')
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'core/add_group.html', {'form': form})

@admin_required
def edit_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Groupe modifié avec succès ✏️')
            return redirect('group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'core/edit_group.html', {'form': form, 'group': group})

@admin_required
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Groupe supprimé avec succès 🗑️')
        return redirect('group_list')
    return render(request, 'core/confirm_delete.html', {'object': group})