# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Book, Bookmark,
    StudySchedule, ExamDate,
    Notification,
    Quiz, Question, QuizAttempt, QuizAnswer,
    PremiumUploadRequest,
)


# ─────────────────────────────────────────────
#  USER
# ─────────────────────────────────────────────

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'role', 'is_premium', 'is_staff', 'date_joined')
    list_filter   = ('role', 'is_premium', 'is_staff')
    search_fields = ('username', 'email', 'matric_number')

    fieldsets = UserAdmin.fieldsets + (
        ('StudySphere Info', {
            'fields': ('role', 'is_premium', 'profile_picture', 'bio', 'matric_number')
        }),
    )


# ─────────────────────────────────────────────
#  BOOKS
# ─────────────────────────────────────────────

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ('title', 'course_code', 'uploader', 'status', 'is_premium', 'upload_date')
    list_filter   = ('status', 'is_premium')
    search_fields = ('title', 'course_code', 'uploader__username')
    actions       = ['approve_books', 'reject_books']

    def approve_books(self, request, queryset):
        queryset.update(status=Book.Status.APPROVED)
        self.message_user(request, f"{queryset.count()} book(s) approved.")
    approve_books.short_description = "Approve selected books"

    def reject_books(self, request, queryset):
        queryset.update(status=Book.Status.REJECTED)
        self.message_user(request, f"{queryset.count()} book(s) rejected.")
    reject_books.short_description = "Reject selected books"


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display  = ('user', 'book', 'page', 'saved_at')
    search_fields = ('user__username', 'book__title')


# ─────────────────────────────────────────────
#  STUDY PLANNER
# ─────────────────────────────────────────────

@admin.register(StudySchedule)
class StudyScheduleAdmin(admin.ModelAdmin):
    list_display  = ('student', 'subject', 'date', 'start_time', 'end_time', 'is_done')
    list_filter   = ('is_done', 'date')
    search_fields = ('student__username', 'subject')


@admin.register(ExamDate)
class ExamDateAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course_code', 'course', 'exam_date', 'exam_time', 'venue')
    list_filter   = ('exam_date',)
    search_fields = ('student__username', 'course_code', 'course')


# ─────────────────────────────────────────────
#  NOTIFICATIONS
# ─────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'notif_type', 'message', 'is_read', 'created_at')
    list_filter   = ('notif_type', 'is_read')
    search_fields = ('user__username', 'message')


# ─────────────────────────────────────────────
#  QUIZ ENGINE
# ─────────────────────────────────────────────

class QuestionInline(admin.TabularInline):
    model  = Question
    extra  = 1
    fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'explanation')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display  = ('title', 'course_code', 'book', 'is_ai_generated', 'created_by', 'created_at')
    list_filter   = ('is_ai_generated',)
    search_fields = ('title', 'course_code')
    inlines       = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ('question_text', 'quiz', 'correct_option')
    search_fields = ('question_text', 'quiz__title')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display  = ('student', 'quiz', 'score', 'total', 'taken_at')
    search_fields = ('student__username', 'quiz__title')


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display  = ('attempt', 'question', 'chosen', 'is_correct')
    list_filter   = ('is_correct',)


# ─────────────────────────────────────────────
#  PREMIUM UPLOAD REQUESTS
# ─────────────────────────────────────────────

@admin.register(PremiumUploadRequest)
class PremiumUploadRequestAdmin(admin.ModelAdmin):
    list_display  = ('student', 'status', 'created_at', 'updated_at')
    list_filter   = ('status',)
    search_fields = ('student__username',)
