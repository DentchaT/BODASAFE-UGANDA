from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/applicant/', views.register_applicant, name='register_applicant'),
    path('register/secretary/', views.register_secretary, name='register_secretary'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Secretary URLs
    path('secretary/dashboard/', views.secretary_dashboard, name='secretary_dashboard'),
    path('secretary/advert/create/', views.create_advert, name='create_advert'),
    path('secretary/advert/<int:advert_id>/review/', views.review_submissions, name='review_submissions'),
    
    # Applicant URLs
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    path('advert/<int:advert_id>/', views.advert_detail, name='advert_detail'),

    #Payments
    path('advert/<int:advert_id>/pay/', views.make_payment, name='make_payment'),
]