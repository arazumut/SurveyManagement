from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Survey, Question, Choice, Response, Answer

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Kullanıcı Adı'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Şifre'
    }))

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'E-posta Adresi'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Kullanıcı Adı'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Şifre'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Şifre (Tekrar)'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Anket Başlığı'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Anket Açıklaması',
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'is_active': 'Yayında'
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'required', 'order']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Soru Metni'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'question_type_select'
            }),
            'required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }
        labels = {
            'text': 'Soru',
            'question_type': 'Soru Tipi',
            'required': 'Zorunlu',
            'order': 'Sıra'
        }

class RatingQuestionForm(QuestionForm):
    class Meta(QuestionForm.Meta):
        fields = QuestionForm.Meta.fields + ['min_rate', 'max_rate']
        widgets = dict(QuestionForm.Meta.widgets, **{
            'min_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'max_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2
            })
        })
        labels = dict(QuestionForm.Meta.labels, **{
            'min_rate': 'Minimum Değer',
            'max_rate': 'Maksimum Değer'
        })

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'order']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seçenek Metni'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }
        labels = {
            'text': 'Seçenek',
            'order': 'Sıra'
        }

class ChoiceFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # En az bir seçenek olduğundan emin olalım
        if any(self.errors):
            return
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                   for form in self.forms):
            raise forms.ValidationError('En az bir seçenek gereklidir.')

# Dinamik form oluşturma için kullanılacak FormHelper
class BaseSurveyAnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey')
        super(BaseSurveyAnswerForm, self).__init__(*args, **kwargs)
        
        for question in survey.questions.all():
            if question.question_type == Question.TEXT_SHORT:
                self.fields[f'question_{question.id}'] = forms.CharField(
                    label=question.text,
                    required=question.required,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            elif question.question_type == Question.TEXT_LONG:
                self.fields[f'question_{question.id}'] = forms.CharField(
                    label=question.text,
                    required=question.required,
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
                )
            elif question.question_type == Question.RADIO:
                choices = [(choice.id, choice.text) for choice in question.choices.all()]
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    required=question.required,
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                )
            elif question.question_type == Question.CHECKBOX:
                choices = [(choice.id, choice.text) for choice in question.choices.all()]
                self.fields[f'question_{question.id}'] = forms.MultipleChoiceField(
                    label=question.text,
                    choices=choices,
                    required=question.required,
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                )
            elif question.question_type == Question.RATING:
                choices = [(i, str(i)) for i in range(question.min_rate, question.max_rate + 1)]
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    required=question.required,
                    widget=forms.RadioSelect(attrs={'class': 'rating-input'})
                )
            elif question.question_type == Question.DATE:
                self.fields[f'question_{question.id}'] = forms.DateField(
                    label=question.text,
                    required=question.required,
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    })
                ) 