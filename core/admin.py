from django.contrib import admin
from .models import Teacher, Student, Group, Payment

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'subject', 'phone', 'get_user_type')
    search_fields = ('user__username', 'subject')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Nom d'utilisateur"

    def get_user_type(self, obj):
        return obj.user.get_user_type_display()
    get_user_type.short_description = "Type"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'phone', 'get_username')
    list_filter = ('level',)
    search_fields = ('name', 'user__username')

    def get_username(self, obj):
        return obj.user.username if obj.user else "Sans compte"
    get_username.short_description = "Compte"

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'monthly_price', 'count_students')
    filter_horizontal = ('students',)

    def count_students(self, obj):
        return obj.students.count()
    count_students.short_description = "Nb élèves"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'amount_paid', 'date', 'centre_share', 'teacher_share')
    list_filter = ('date', 'group')
    date_hierarchy = 'date'