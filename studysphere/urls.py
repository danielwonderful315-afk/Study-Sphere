from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [

    # ─────────────────────────────────────────
    #  AUTHENTICATION
    # ─────────────────────────────────────────

    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # Password Reset Flow (Django handles the logic, we supply custom forms/templates)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             form_class=CustomPasswordResetForm,
             email_template_name='auth/emails/password_reset_email.html',
             subject_template_name='auth/emails/password_reset_subject.txt',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html',
             form_class=CustomSetPasswordForm,
         ),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html',
         ),
         name='password_reset_complete'),

    # ─────────────────────────────────────────
    #  DASHBOARD & PROFILE
    # ─────────────────────────────────────────

   path('dashboard/', views.dashboard_view, name='dashboard'),
   path('profile/',  views.profile_view,   name='profile'),

    # ─────────────────────────────────────────
    #  BOOKS
    # ─────────────────────────────────────────

    path('books/',              views.book_list_view,   name='book_list'),
    path('books/upload/',       views.book_upload_view, name='book_upload'),
    path('books/mine/',         views.my_books_view,    name='my_books'),
    path('books/<int:pk>/',     views.book_detail_view, name='book_detail'),
    path('books/<int:pk>/read/', views.book_read_view,  name='book_read'),
    # Study Schedule
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/add/', views.schedule_add, name='schedule_add'),
    path('schedule/<int:pk>/toggle/', views.schedule_toggle, name='schedule_toggle'),
    path('schedule/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),

    # Exam Dates
    path('exams/', views.exam_list_view, name='exam_list'),
    path('exams/add/', views.exam_add, name='exam_add'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/clear/', views.notifications_clear, name='notifications_clear'),

]

# Add these to your existing studysphere/urls.py

# ─────────────────────────────────────────────
#  PHASE 2 — add these URL patterns
# ─────────────────────────────────────────────

# Study Schedule
path('schedule/',                views.schedule_view,    name='schedule'),
path('schedule/add/',            views.schedule_add,     name='schedule_add'),
path('schedule/<int:pk>/toggle/', views.schedule_toggle, name='schedule_toggle'),
path('schedule/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),

# Exam Dates
path('exams/',                   views.exam_list_view,   name='exam_list'),
path('exams/add/',               views.exam_add,         name='exam_add'),
path('exams/<int:pk>/delete/',   views.exam_delete,      name='exam_delete'),

# Notifications
path('notifications/',                        views.notifications_view,   name='notifications'),
path('notifications/<int:pk>/delete/',        views.notification_delete,  name='notification_delete'),
path('notifications/clear/',                  views.notifications_clear,  name='notifications_clear'),


