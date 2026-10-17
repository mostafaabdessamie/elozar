from django.contrib import admin
from .models import Livre

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'image', 'pdf')
    search_fields = ('titre',)
    list_display_links = ('titre',)