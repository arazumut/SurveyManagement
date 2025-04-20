from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Ana sayfa ve genel görünümler
    path('', views.index, name='index'),
    path('hakkimizda/', views.about, name='about'),
    
    # Anket yönetimi
    path('anketlerim/', views.my_surveys, name='my_surveys'),
    path('anket/olustur/', views.create_survey, name='create_survey'),
    path('anket/<slug:slug>/duzenle/', views.edit_survey, name='edit_survey'),
    path('anket/<slug:slug>/sil/', views.delete_survey, name='delete_survey'),
    path('anket/<slug:slug>/yayinla/', views.toggle_survey_active, name='toggle_survey_active'),
    
    # Soru ve seçenek yönetimi
    path('anket/<slug:slug>/soru/ekle/', views.add_question, name='add_question'),
    path('soru/<int:question_id>/duzenle/', views.edit_question, name='edit_question'),
    path('soru/<int:question_id>/sil/', views.delete_question, name='delete_question'),
    path('soru/<int:question_id>/secenekler/', views.manage_choices, name='manage_choices'),
    
    # Anket cevaplama
    path('anket/<slug:slug>/', views.view_survey, name='view_survey'),
    path('anket/kod/<str:access_code>/', views.access_survey_by_code, name='access_survey_by_code'),
    path('anket/<slug:slug>/gonder/', views.submit_survey, name='submit_survey'),
    path('anket/<slug:slug>/tesekkurler/', views.thank_you, name='thank_you'),
    
    # Sonuç görüntüleme
    path('anket/<slug:slug>/sonuclar/', views.survey_results, name='survey_results'),
    path('anket/<slug:slug>/sonuclar/export/', views.export_results, name='export_results'),
    
    # Kullanıcı yönetimi
    path('giris/', views.user_login, name='login'),
    path('cikis/', views.user_logout, name='logout'),
    path('kayit/', views.user_register, name='register'),
    path('profil/', views.user_profile, name='profile'),
] 