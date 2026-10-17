from django import forms
from .models import Teacher, Student, Group, Payment

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'phone']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'level', 'phone', 'user']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'teacher', 'students', 'monthly_price']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'group', 'amount_paid']