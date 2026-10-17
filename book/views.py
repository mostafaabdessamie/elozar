from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Livre
from .forms import LivreForm

def est_admin(user):
    return user.is_authenticated and getattr(user, 'user_type', 0) == 1

# décorateur admin
admin_required = user_passes_test(est_admin, login_url='home')

def livre_list(request):
    livres = Livre.objects.all().order_by('-id')
    q = request.GET.get('q')
    if q:
        livres = livres.filter(titre__icontains=q)
    return render(request, 'book/livre_list.html', {'livres': livres})

def livre_detail(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    return render(request, 'book/livre_detail.html', {'livre': livre})

@login_required
@admin_required
def livre_create(request):
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livre ajouté avec succès!')
            return redirect('livre_list')
    else:
        form = LivreForm()
    return render(request, 'book/livre_form.html', {'form': form, 'title': 'Ajouter un livre'})

@login_required
@admin_required
def livre_update(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livre modifié!')
            return redirect('livre_list')
    else:
        form = LivreForm(instance=livre)
    return render(request, 'book/livre_form.html', {'form': form, 'title': 'Modifier', 'livre': livre})

@login_required
@admin_required
def livre_delete(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        livre.delete()
        messages.success(request, 'Livre supprimé!')
        return redirect('livre_list')
    return render(request, 'book/livre_confirm_delete.html', {'livre': livre})