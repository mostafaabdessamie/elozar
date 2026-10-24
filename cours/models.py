from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

User = get_user_model()
    
class Cours(models.Model):
    title = models.CharField(max_length=255, verbose_name="Titre du cours")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='cours/images/', blank=True, null=True, verbose_name="Image de couverture")
    
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='courses',
        verbose_name="Enseignant"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    # --- RESPONSABILITÉ LÉGALE (Loi 09-08) ---
    accepted_terms = models.BooleanField(default=False, verbose_name="Conditions acceptées")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'acceptation des conditions")
    accepted_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP d'acceptation")

    # Optionnel: pour l'admin
    is_validated = models.BooleanField(default=True, verbose_name="Validé par admin")

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.teacher.username}"
    
    @property
    def has_legal_proof(self):
        return self.accepted_terms and self.accepted_at is not None

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    course = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='lessons')
    video = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    image = models.ImageField(upload_to='lessons/images/', blank=True, null=True)
    pdf = models.FileField(upload_to='lessons/pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # تاريخ آخر تعديل
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Lessons"

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='enrollments')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student.username} inscrit à {self.course.title}"

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    points = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"Q: {self.text} ({self.lesson.title})"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Choices"

    def __str__(self):
        return f"{'✅' if self.is_correct else '❌'} {self.text}"

class StudentScore(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'lesson')
        verbose_name_plural = "Student Scores"

    def __str__(self):
        return f"{self.student.username} - {self.score} points ({self.lesson.title})"
