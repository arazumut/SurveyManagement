from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.forms import inlineformset_factory
from django.db.models import Count
import csv
import json
import uuid
from datetime import datetime

from .models import Survey, Question, Choice, Response, Answer, SelectedChoice
from .forms import (
    UserLoginForm, UserRegisterForm, SurveyForm, QuestionForm, 
    RatingQuestionForm, ChoiceForm, ChoiceFormSet, BaseSurveyAnswerForm
)

# Ana sayfa ve Genel Görünümler
def index(request):
    """Ana sayfayı göster"""
    active_surveys = Survey.objects.filter(is_active=True).order_by('-created_at')[:6]
    
    # Popüler anketler için verileri hazırla
    popular_surveys = []
    for survey in active_surveys:
        # Gerçek veriler ile dolduracağımız örnek veri yapısı
        survey_data = {
            'id': survey.id,
            'slug': survey.slug,
            'title': survey.title,
            'description': survey.description,
            'category': 'Genel',  # Gerçek uygulamada kategori bilgisi eklenebilir
            'responses_count': survey.responses.count(),
            'time_remaining': 30,  # Örnek değer, gerçek bir hesaplama eklenebilir
        }
        popular_surveys.append(survey_data)
    
    return render(request, 'surveys/index.html', {
        'active_surveys': active_surveys,
        'popular_surveys': popular_surveys
    })

def about(request):
    """Hakkımızda sayfası"""
    return render(request, 'surveys/about.html')

# Kullanıcı Yönetimi
def user_login(request):
    """Kullanıcı giriş sayfası"""
    if request.user.is_authenticated:
        return redirect('surveys:my_surveys')
        
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Başarıyla giriş yaptınız!')
                return redirect('surveys:my_surveys')
    else:
        form = UserLoginForm()
    
    return render(request, 'surveys/login.html', {'form': form})

def user_logout(request):
    """Kullanıcı çıkış fonksiyonu"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız!')
    return redirect('surveys:index')

def user_register(request):
    """Kullanıcı kayıt sayfası"""
    if request.user.is_authenticated:
        return redirect('surveys:my_surveys')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu!')
            return redirect('surveys:my_surveys')
    else:
        form = UserRegisterForm()
    
    return render(request, 'surveys/register.html', {'form': form})

@login_required
def user_profile(request):
    """Kullanıcı profili sayfası"""
    surveys_count = Survey.objects.filter(created_by=request.user).count()
    active_surveys = Survey.objects.filter(created_by=request.user, is_active=True).count()
    
    context = {
        'surveys_count': surveys_count,
        'active_surveys': active_surveys,
    }
    
    return render(request, 'surveys/profile.html', context)

# Anket Yönetimi
@login_required
def my_surveys(request):
    """Kullanıcının anketlerini listeleme sayfası"""
    surveys = Survey.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'surveys/my_surveys.html', {'surveys': surveys})

@login_required
def create_survey(request):
    """Yeni anket oluşturma sayfası"""
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            messages.success(request, 'Anket başarıyla oluşturuldu! Şimdi sorular ekleyebilirsiniz.')
            return redirect('surveys:edit_survey', slug=survey.slug)
    else:
        form = SurveyForm()
    
    return render(request, 'surveys/create_survey.html', {'form': form})

@login_required
def edit_survey(request, slug):
    """Anket düzenleme sayfası"""
    survey = get_object_or_404(Survey, slug=slug, created_by=request.user)
    questions = survey.questions.all().order_by('order')
    
    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anket başarıyla güncellendi!')
            return redirect('surveys:my_surveys')
    else:
        form = SurveyForm(instance=survey)
    
    context = {
        'form': form,
        'survey': survey,
        'questions': questions
    }
    
    return render(request, 'surveys/edit_survey.html', context)

@login_required
def delete_survey(request, slug):
    """Anket silme fonksiyonu"""
    survey = get_object_or_404(Survey, slug=slug, created_by=request.user)
    
    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'Anket başarıyla silindi!')
        return redirect('surveys:my_surveys')
    
    return render(request, 'surveys/delete_survey.html', {'survey': survey})

@login_required
def toggle_survey_active(request, slug):
    """Anket aktiflik durumunu değiştirme"""
    survey = get_object_or_404(Survey, slug=slug, created_by=request.user)
    
    if request.method == 'POST':
        survey.is_active = not survey.is_active
        survey.save()
        status = 'aktif' if survey.is_active else 'pasif'
        messages.success(request, f'Anket durumu {status} olarak güncellendi!')
        return redirect('surveys:my_surveys')
    
    return render(request, 'surveys/toggle_active.html', {'survey': survey})

# Soru ve Seçenek Yönetimi
@login_required
def add_question(request, slug):
    """Ankete soru ekleme sayfası"""
    survey = get_object_or_404(Survey, slug=slug, created_by=request.user)
    
    # Soru tipi seçimine bağlı olarak doğru formu kullan
    question_type = request.GET.get('type', Question.TEXT_SHORT)
    
    if request.method == 'POST':
        # Soru tipine göre form seçimi
        if question_type == Question.RATING:
            form = RatingQuestionForm(request.POST)
        else:
            form = QuestionForm(request.POST)
            
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            
            messages.success(request, 'Soru başarıyla eklendi!')
            
            # Eğer seçenekli bir soru ise, seçenek ekleme sayfasına yönlendir
            if question.question_type in [Question.RADIO, Question.CHECKBOX]:
                return redirect('surveys:manage_choices', question_id=question.id)
            
            return redirect('surveys:edit_survey', slug=survey.slug)
    else:
        # Otomatik sıra numarası atama
        next_order = survey.questions.count() + 1
        
        # Soru tipine göre form oluşturma
        if question_type == Question.RATING:
            form = RatingQuestionForm(initial={
                'question_type': question_type,
                'order': next_order,
                'min_rate': 1,
                'max_rate': 5
            })
        else:
            form = QuestionForm(initial={
                'question_type': question_type,
                'order': next_order
            })
    
    context = {
        'form': form,
        'survey': survey,
        'question_type': question_type
    }
    
    return render(request, 'surveys/add_question.html', context)

@login_required
def edit_question(request, question_id):
    """Soru düzenleme sayfası"""
    question = get_object_or_404(Question, id=question_id)
    survey = question.survey
    
    # Kullanıcının anketini düzenlediğinden emin ol
    if survey.created_by != request.user:
        messages.error(request, 'Bu soruyu düzenleme yetkiniz yok!')
        return redirect('surveys:my_surveys')
    
    if request.method == 'POST':
        # Soru tipine göre form seçimi
        if question.question_type == Question.RATING:
            form = RatingQuestionForm(request.POST, instance=question)
        else:
            form = QuestionForm(request.POST, instance=question)
            
        if form.is_valid():
            form.save()
            messages.success(request, 'Soru başarıyla güncellendi!')
            return redirect('surveys:edit_survey', slug=survey.slug)
    else:
        # Soru tipine göre form oluşturma
        if question.question_type == Question.RATING:
            form = RatingQuestionForm(instance=question)
        else:
            form = QuestionForm(instance=question)
    
    context = {
        'form': form,
        'question': question,
        'survey': survey
    }
    
    return render(request, 'surveys/edit_question.html', context)

@login_required
def delete_question(request, question_id):
    """Soru silme fonksiyonu"""
    question = get_object_or_404(Question, id=question_id)
    survey = question.survey
    
    # Kullanıcının anketini düzenlediğinden emin ol
    if survey.created_by != request.user:
        messages.error(request, 'Bu soruyu silme yetkiniz yok!')
        return redirect('surveys:my_surveys')
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Soru başarıyla silindi!')
        return redirect('surveys:edit_survey', slug=survey.slug)
    
    return render(request, 'surveys/delete_question.html', {'question': question, 'survey': survey})

@login_required
def manage_choices(request, question_id):
    """Seçenek yönetimi sayfası"""
    question = get_object_or_404(Question, id=question_id)
    survey = question.survey
    
    # Kullanıcının anketini düzenlediğinden emin ol
    if survey.created_by != request.user:
        messages.error(request, 'Bu sorunun seçeneklerini düzenleme yetkiniz yok!')
        return redirect('surveys:my_surveys')
    
    # Sadece radio ve checkbox tipi sorular seçeneklere sahip olabilir
    if question.question_type not in [Question.RADIO, Question.CHECKBOX]:
        messages.error(request, 'Bu soru tipi seçenek içermez!')
        return redirect('surveys:edit_survey', slug=survey.slug)
    
    # Formset oluştur
    ChoiceFormSet = inlineformset_factory(
        Question, 
        Choice, 
        form=ChoiceForm, 
        formset=ChoiceFormSet,
        extra=3, 
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = ChoiceFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Seçenekler başarıyla güncellendi!')
            return redirect('surveys:edit_survey', slug=survey.slug)
    else:
        formset = ChoiceFormSet(instance=question)
    
    context = {
        'formset': formset,
        'question': question,
        'survey': survey
    }
    
    return render(request, 'surveys/manage_choices.html', context)

# Anket Cevaplama
def view_survey(request, slug):
    """Anket görüntüleme/doldurma sayfası"""
    survey = get_object_or_404(Survey, slug=slug, is_active=True)
    
    # Kullanıcının daha önce anketi doldurup doldurmadığını kontrol et
    has_responded = False
    respondent_id = request.COOKIES.get('survey_' + str(survey.id))
    
    if respondent_id:
        has_responded = Response.objects.filter(
            survey=survey, 
            respondent_id=respondent_id
        ).exists()
    
    if has_responded:
        messages.info(request, 'Bu anketi daha önce doldurdunuz.')
        return render(request, 'surveys/already_responded.html', {'survey': survey})
    
    # Dinamik form oluştur
    form = BaseSurveyAnswerForm(survey=survey)
    
    context = {
        'survey': survey,
        'form': form,
        'questions': survey.questions.all().order_by('order')
    }
    
    return render(request, 'surveys/view_survey.html', context)

def access_survey_by_code(request, access_code):
    """Erişim kodu ile anket erişimi"""
    survey = get_object_or_404(Survey, access_code=access_code, is_active=True)
    return redirect('surveys:view_survey', slug=survey.slug)

def submit_survey(request, slug):
    """Anket yanıtlarını kaydetme"""
    survey = get_object_or_404(Survey, slug=slug, is_active=True)
    
    if request.method == 'POST':
        form = BaseSurveyAnswerForm(request.POST, survey=survey)
        
        if form.is_valid():
            # Benzersiz yanıtlayan kimliği oluştur
            respondent_id = str(uuid.uuid4())
            
            # Yanıt kaydı oluştur
            response = Response.objects.create(
                survey=survey,
                respondent_id=respondent_id
            )
            
            # Her soru için cevapları kaydet
            for question in survey.questions.all():
                field_name = f'question_{question.id}'
                
                # Sorunun zorunlu olup olmadığını kontrol et
                if question.required and not form.cleaned_data.get(field_name):
                    messages.error(request, f'"{question.text}" sorusu zorunludur!')
                    return redirect('surveys:view_survey', slug=slug)
                
                # Farklı soru tipleri için farklı kaydetme yöntemleri
                if field_name in form.cleaned_data:
                    answer = Answer.objects.create(
                        response=response,
                        question=question
                    )
                    
                    # Soru tipine göre cevabı kaydet
                    if question.question_type in [Question.TEXT_SHORT, Question.TEXT_LONG]:
                        answer.text_answer = form.cleaned_data[field_name]
                        answer.save()
                    elif question.question_type == Question.DATE:
                        answer.date_answer = form.cleaned_data[field_name]
                        answer.save()
                    elif question.question_type == Question.RATING:
                        answer.text_answer = form.cleaned_data[field_name]  # Rating değerini metin olarak kaydet
                        answer.save()
                    elif question.question_type == Question.RADIO:
                        # Tek seçimli sorular için seçimi kaydet
                        choice_id = form.cleaned_data[field_name]
                        choice = Choice.objects.get(id=choice_id)
                        SelectedChoice.objects.create(answer=answer, choice=choice)
                    elif question.question_type == Question.CHECKBOX:
                        # Çoklu seçimli sorular için seçimleri kaydet
                        choice_ids = form.cleaned_data[field_name]
                        for choice_id in choice_ids:
                            choice = Choice.objects.get(id=choice_id)
                            SelectedChoice.objects.create(answer=answer, choice=choice)
            
            # Teşekkür sayfasına yönlendir ve çerez ayarla
            response = redirect('surveys:thank_you', slug=slug)
            response.set_cookie(f'survey_{survey.id}', respondent_id, max_age=60*60*24*365)  # 1 yıl
            return response
        else:
            messages.error(request, 'Lütfen formu kontrol edin ve tekrar deneyin.')
    
    return redirect('surveys:view_survey', slug=slug)

def thank_you(request, slug):
    """Anket tamamlandıktan sonra teşekkür sayfası"""
    survey = get_object_or_404(Survey, slug=slug)
    return render(request, 'surveys/thank_you.html', {'survey': survey})

# Sonuç Görüntüleme
@login_required
def survey_results(request, slug):
    """Anket sonuçları sayfası"""
    survey = get_object_or_404(Survey, slug=slug)
    
    # Kullanıcının kendi anketi mi kontrol et (admin her anketi görebilir)
    if not request.user.is_staff and survey.created_by != request.user:
        messages.error(request, 'Bu anketin sonuçlarını görüntüleme yetkiniz yok!')
        return redirect('surveys:my_surveys')
    
    # Tüm yanıtları al
    responses = Response.objects.filter(survey=survey)
    response_count = responses.count()
    
    # Her soru için istatistikler hazırla
    questions_data = []
    
    for question in survey.questions.all().order_by('order'):
        question_data = {
            'id': question.id,
            'text': question.text,
            'type': question.question_type,
            'answers': []
        }
        
        # Soru tipine göre farklı istatistikler
        if question.question_type in [Question.RADIO, Question.CHECKBOX]:
            # Seçenek bazlı istatistik
            choices = Choice.objects.filter(question=question).order_by('order')
            
            for choice in choices:
                choice_count = SelectedChoice.objects.filter(
                    answer__question=question,
                    answer__response__in=responses,
                    choice=choice
                ).count()
                
                percentage = 0
                if response_count > 0:
                    if question.question_type == Question.RADIO:
                        percentage = (choice_count / response_count) * 100
                    else:  # CHECKBOX için oran farklı hesaplanabilir
                        percentage = (choice_count / response_count) * 100
                
                question_data['answers'].append({
                    'choice_text': choice.text,
                    'count': choice_count,
                    'percentage': round(percentage, 1)
                })
                
        elif question.question_type == Question.RATING:
            # Derecelendirme istatistikleri
            answers = Answer.objects.filter(
                question=question,
                response__in=responses
            ).exclude(text_answer='')
            
            ratings = {}
            for i in range(question.min_rate, question.max_rate + 1):
                ratings[str(i)] = 0
            
            for answer in answers:
                if answer.text_answer in ratings:
                    ratings[answer.text_answer] += 1
            
            for rating, count in ratings.items():
                percentage = 0
                if response_count > 0:
                    percentage = (count / response_count) * 100
                
                question_data['answers'].append({
                    'rating': rating,
                    'count': count,
                    'percentage': round(percentage, 1)
                })
            
        else:
            # Metin ve tarih cevapları için listele
            answers = Answer.objects.filter(
                question=question,
                response__in=responses
            )
            
            for answer in answers:
                if question.question_type == Question.DATE:
                    answer_text = answer.date_answer.strftime('%d.%m.%Y') if answer.date_answer else ''
                else:
                    answer_text = answer.text_answer or ''
                
                question_data['answers'].append({
                    'text': answer_text,
                })
        
        questions_data.append(question_data)
    
    context = {
        'survey': survey,
        'response_count': response_count,
        'questions_data': questions_data,
        'chart_data': json.dumps(questions_data)
    }
    
    return render(request, 'surveys/survey_results.html', context)

@login_required
def export_results(request, slug):
    """Anket sonuçlarını CSV olarak dışa aktarma"""
    survey = get_object_or_404(Survey, slug=slug)
    
    # Kullanıcının kendi anketi mi kontrol et (admin her anketi görebilir)
    if not request.user.is_staff and survey.created_by != request.user:
        messages.error(request, 'Bu anketin sonuçlarını dışa aktarma yetkiniz yok!')
        return redirect('surveys:my_surveys')
    
    # CSV dosya adı oluştur
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"anket_sonuclari_{survey.slug}_{timestamp}.csv"
    
    # HTTP yanıtı oluştur
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # CSV Writer oluştur
    writer = csv.writer(response)
    
    # Başlık satırını yaz
    headers = ['Respondent ID', 'Submission Date']
    questions = survey.questions.all().order_by('order')
    
    for question in questions:
        headers.append(question.text)
    
    writer.writerow(headers)
    
    # Her yanıt için satır oluştur
    for response_obj in Response.objects.filter(survey=survey).order_by('-submitted_at'):
        row = [
            response_obj.respondent_id,
            response_obj.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        
        # Her soru için cevabı al
        for question in questions:
            try:
                answer = Answer.objects.get(response=response_obj, question=question)
                
                if question.question_type in [Question.TEXT_SHORT, Question.TEXT_LONG, Question.RATING]:
                    row.append(answer.text_answer or '')
                elif question.question_type == Question.DATE:
                    row.append(answer.date_answer.strftime('%Y-%m-%d') if answer.date_answer else '')
                elif question.question_type == Question.RADIO:
                    selected = answer.selected_choices.first()
                    row.append(selected.choice.text if selected else '')
                elif question.question_type == Question.CHECKBOX:
                    selected = answer.selected_choices.all()
                    row.append(', '.join([choice.choice.text for choice in selected]))
                else:
                    row.append('')
            except Answer.DoesNotExist:
                row.append('')
        
        writer.writerow(row)
    
    return response
