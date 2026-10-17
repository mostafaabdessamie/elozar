from django.db import models

class Livre(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre du livre")
    image = models.ImageField(upload_to='livres/images/', verbose_name="Image du livre")
    pdf = models.FileField(upload_to='livres/pdfs/', verbose_name="Fichier PDF")

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
        ordering = ['-id']