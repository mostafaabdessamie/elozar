from django.db import models
from django.conf import settings

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Professour", null=True, blank=True)
    subject = models.CharField(max_length=100, verbose_name="Matière")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")

    def __str__(self):
        return f"{self.user.username} - {self.subject}"

class Student(models.Model):
    LEVELS = [('primaire','Primaire'),('college','Collège'),('lycee','Lycée')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="eleve", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="Nom complet") 
    level = models.CharField(max_length=20, choices=LEVELS, verbose_name="Niveau")
    phone = models.CharField(max_length=20, verbose_name="Téléphone parent")

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="groups")
    students = models.ManyToManyField(Student, related_name="groups", blank=True)
    monthly_price = models.DecimalField(max_digits=6, decimal_places=2, default=300)

    def __str__(self): return self.name

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    @property
    def centre_share(self): return float(self.amount_paid) * 0.30
    @property
    def teacher_share(self): return float(self.amount_paid) * 0.70
    