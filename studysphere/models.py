from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ─────────────────────────────────────────────
#  1. CUSTOM USER
# ─────────────────────────────────────────────

class User(AbstractUser):
    """
    Extends Django's built-in User.
    Adds role, premium status, and profile picture.
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        ADMIN   = 'admin',   'Admin'

    role            = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    is_premium      = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio             = models.TextField(blank=True)
    matric_number   = models.CharField(max_length=20, blank=True)

    # Fix reverse accessor clashes with Django's built-in auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='studysphere_users',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='studysphere_users',
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# ─────────────────────────────────────────────
#  2. BOOK (PDF MATERIALS)
# ─────────────────────────────────────────────

class Book(models.Model):
    """
    Represents an uploaded academic material (PDF).
    """

    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending Approval'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    title        = models.CharField(max_length=255)
    course_code  = models.CharField(max_length=20)
    description  = models.TextField(blank=True)
    file         = models.FileField(upload_to='books/')
    cover_image  = models.ImageField(upload_to='covers/', blank=True, null=True)
    uploader     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_books')
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    is_premium   = models.BooleanField(default=False)  # True = managed premium upload
    upload_date  = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.course_code})"


class Bookmark(models.Model):
    """
    Saves a student's reading position in a book.
    One bookmark per user per book (upsert pattern).
    """

    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    book      = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookmarks')
    page      = models.PositiveIntegerField(default=1)
    saved_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')  # one bookmark per user per book

    def __str__(self):
        return f"{self.user.username} → {self.book.title} (p.{self.page})"


# ─────────────────────────────────────────────
#  3. STUDY SCHEDULE & PLANNER
# ─────────────────────────────────────────────

class StudySchedule(models.Model):
    """
    A single study session block in a student's timetable.
    """

    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    subject     = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date        = models.DateField()
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    is_done     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} | {self.subject} on {self.date}"


class ExamDate(models.Model):
    """
    An upcoming exam registered by a student.
    Drives the notification/reminder system.
    """

    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_dates')
    course      = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20)
    exam_date   = models.DateField()
    exam_time   = models.TimeField(blank=True, null=True)
    venue       = models.CharField(max_length=100, blank=True)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def days_until(self):
        delta = self.exam_date - timezone.now().date()
        return delta.days

    def __str__(self):
        return f"{self.student.username} | {self.course_code} on {self.exam_date}"


# ─────────────────────────────────────────────
#  4. NOTIFICATIONS
# ─────────────────────────────────────────────

class Notification(models.Model):
    """
    In-app notification delivered to a student.
    """

    class NotifType(models.TextChoices):
        EXAM_REMINDER = 'exam',        'Exam Reminder'
        STUDY_ALERT   = 'study',       'Study Alert'
        MOTIVATIONAL  = 'motivation',  'Motivational'
        SYSTEM        = 'system',      'System'

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message    = models.TextField()
    notif_type = models.CharField(max_length=20, choices=NotifType.choices, default=NotifType.SYSTEM)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return f"[{self.notif_type}] → {self.user.username}: {self.message[:50]}"


# ─────────────────────────────────────────────
#  5. QUIZ ENGINE
# ─────────────────────────────────────────────

class Quiz(models.Model):
    """
    A quiz tied to a course or a specific book.
    Can be created manually or AI-generated.
    """

    title           = models.CharField(max_length=255)
    course_code     = models.CharField(max_length=20)
    book            = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='quizzes')
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                        related_name='created_quizzes')
    is_ai_generated = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course_code})"


class Question(models.Model):
    """
    A single multiple-choice question inside a Quiz.
    """

    quiz          = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a      = models.CharField(max_length=300)
    option_b      = models.CharField(max_length=300)
    option_c      = models.CharField(max_length=300)
    option_d      = models.CharField(max_length=300)

    class CorrectOption(models.TextChoices):
        A = 'A', 'Option A'
        B = 'B', 'Option B'
        C = 'C', 'Option C'
        D = 'D', 'Option D'

    correct_option = models.CharField(max_length=1, choices=CorrectOption.choices)
    explanation    = models.TextField(blank=True)  # AI can populate this

    def __str__(self):
        return f"Q: {self.question_text[:60]}"


class QuizAttempt(models.Model):
    """
    Records a student's attempt at a quiz, with their score.
    """

    student  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    quiz     = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score    = models.PositiveIntegerField(default=0)
    total    = models.PositiveIntegerField(default=0)
    taken_at = models.DateTimeField(auto_now_add=True)

    @property
    def percentage(self):
        if self.total == 0:
            return 0
        return round((self.score / self.total) * 100, 1)

    def __str__(self):
        return f"{self.student.username} | {self.quiz.title} | {self.score}/{self.total}"


class QuizAnswer(models.Model):
    """
    Stores each individual answer a student gave during an attempt.
    """

    attempt    = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question   = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen     = models.CharField(max_length=1)  # A, B, C, or D
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt} | Q{self.question.id} | {self.chosen} ({'✓' if self.is_correct else '✗'})"


# ─────────────────────────────────────────────
#  6. PREMIUM UPLOAD REQUEST
# ─────────────────────────────────────────────

class PremiumUploadRequest(models.Model):
    """
    A request from a premium user asking admin to
    upload and organise materials on their behalf.
    """

    class Status(models.TextChoices):
        PENDING    = 'pending',    'Pending'
        PROCESSING = 'processing', 'Processing'
        DONE       = 'done',       'Done'
        REJECTED   = 'rejected',   'Rejected'

    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upload_requests')
    description = models.TextField()
    file        = models.FileField(upload_to='premium_requests/', blank=True, null=True)
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    admin_note  = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} | {self.status} | {self.created_at.date()}"