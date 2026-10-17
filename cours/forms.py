from django import forms
from .models import Question

class QuestionForm(forms.Form):
    text = forms.CharField(label='Question Text', max_length=255)
    points = forms.IntegerField(label='Points', required=False)
    
    choice_1 = forms.CharField(label='Choice 1', required=False)
    is_correct_1 = forms.BooleanField(label='Is Correct?', required=False)

    choice_2 = forms.CharField(label='Choice 2', required=False)
    is_correct_2 = forms.BooleanField(label='Is Correct?', required=False)

    choice_3 = forms.CharField(label='Choice 3', required=False)
    is_correct_3 = forms.BooleanField(label='Is Correct?', required=False)

    choice_4 = forms.CharField(label='Choice 4', required=False)
    is_correct_4 = forms.BooleanField(label='Is Correct?', required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        if not any([cleaned_data.get(f'is_correct_{i}') for i in range(1, 5)]):
            raise forms.ValidationError('At least one choice must be correct')
        return cleaned_data
    
    def save(self, lesson):
        question = Question.objects.create(
            lesson=lesson,
            text=self.cleaned_data['text'],
            points=self.cleaned_data.get('points', 1)
        )
        for i in range(1, 5):
            choice_text = self.cleaned_data.get(f'choice_{i}')
            if choice_text:
                is_correct = self.cleaned_data[f'is_correct_{i}']
                question.choices.create(text=choice_text, is_correct=is_correct)
        return question
