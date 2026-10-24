from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile, Message, Post, Comment, Friendship

class CustomUserForm(UserCreationForm):
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    user_type = forms.ChoiceField(choices=[(2, 'professeur'), (3, 'étudiant')], widget=forms.Select(attrs={'class': 'form-control'}))

    accept_reglement = forms.BooleanField(
        required=True,
        label="J'ai lu et j'accepte le Règlement Intérieur",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'required': 'required'})
    )
    accept_loi_0908 = forms.BooleanField(
        required=True,
        label="J'accepte la Loi 09-08 sur la protection des données personnelles et je m'engage à ne publier aucune donnée d'autrui sans consentement",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'required': 'required'})
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'profile_picture', 'email', 'password1', 'password2', 'user_type')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = self.cleaned_data.get('bio', '')
            profile.location = self.cleaned_data.get('location', '')
            profile.birth_date = self.cleaned_data.get('birth_date')
            profile.accepted_reglement = True
            profile.accepted_0908 = True
            profile.save()
        return user

class CustomUserUpdateForm(forms.ModelForm):
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'profile_picture', 'email', 'user_type')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = self.cleaned_data.get('bio', '')
            profile.location = self.cleaned_data.get('location', '')
            profile.birth_date = self.cleaned_data.get('birth_date')
            profile.save()
        return user

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'content']

class PostForm(forms.ModelForm):
    certif_original = forms.BooleanField(
        required=True,
        label="Je certifie que ce contenu est mon œuvre originale et que je respecte la Loi 09-08 (aucun visage/donnée perso sans autorisation écrite)"
    )

    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = Friendship
        fields = ['to_user']