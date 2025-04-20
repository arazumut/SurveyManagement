from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
import random
import string

def generate_unique_code(length=10):
    """Generate a random code for survey access"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class Survey(models.Model):
    """Survey model to store survey details"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    access_code = models.CharField(max_length=20, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Generate slug from title
        if not self.slug:
            self.slug = slugify(self.title)
            
        # Generate unique access code
        if not self.access_code:
            self.access_code = generate_unique_code()
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    """Question model for survey questions"""
    TEXT_SHORT = 'text_short'
    TEXT_LONG = 'text_long'
    RADIO = 'radio'
    CHECKBOX = 'checkbox'
    RATING = 'rating'
    DATE = 'date'
    
    QUESTION_TYPES = [
        (TEXT_SHORT, 'Kısa Metin'),
        (TEXT_LONG, 'Paragraf'),
        (RADIO, 'Tek Seçenekli'),
        (CHECKBOX, 'Çok Seçenekli'),
        (RATING, 'Derecelendirme'),
        (DATE, 'Tarih'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Additional fields for rating type questions
    min_rate = models.IntegerField(default=1, null=True, blank=True)
    max_rate = models.IntegerField(default=5, null=True, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.text} ({self.get_question_type_display()})"

class Choice(models.Model):
    """Choice model for radio and checkbox questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.text

class Response(models.Model):
    """Model to store survey responses"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent_id = models.CharField(max_length=100, blank=True)  # Can be user_id, session_id, or IP
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to {self.survey.title} at {self.submitted_at}"

class Answer(models.Model):
    """Model to store individual question answers"""
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    date_answer = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"Answer to {self.question.text}"

class SelectedChoice(models.Model):
    """Model to store selected choices for radio/checkbox questions"""
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='selected_choices')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Selected: {self.choice.text}"
