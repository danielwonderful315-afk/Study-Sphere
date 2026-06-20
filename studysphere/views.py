from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.utils import timezone
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, BookUploadForm, StudyScheduleForm, ExamDateForm
from .models import Book, Bookmark, StudySchedule, ExamDate, Notification


# ─────────────────────────────────────────────
#  LANDING
# ─────────────────────────────────────────────

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


# ─────────────────────────────────────────────
#  AUTHENTICATION
# ─────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

@login_required
def dashboard_view(request):
    # Only show THIS user's approved books
    recent_books = Book.objects.filter(
        uploader=request.user,
        status=Book.Status.APPROVED
    ).order_by('-upload_date')[:6]

    # Only this user's uploads (all statuses so they can see pending too)
    my_uploads = Book.objects.filter(
        uploader=request.user
    ).order_by('-upload_date')[:5]

    my_bookmarks = Bookmark.objects.filter(
        user=request.user
    ).select_related('book')[:5]

    unread_count = request.user.notifications.filter(is_read=False).count()

    context = {
        'recent_books': recent_books,
        'my_uploads': my_uploads,
        'my_bookmarks': my_bookmarks,
        'unread_count': unread_count,
    }
    return render(request, 'dashboard.html', context)


# ─────────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────────

@login_required
def profile_view(request):
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'auth/profile.html', {'form': form})


# ─────────────────────────────────────────────
#  BOOKS — PRIVATE PER USER
# ─────────────────────────────────────────────

@login_required
def book_list_view(request):
    """Show only the logged-in user's own approved books."""
    query = request.GET.get('q', '').strip()

    books = Book.objects.filter(
        uploader=request.user,
        status=Book.Status.APPROVED
    ).order_by('-upload_date')

    if query:
        books = books.filter(
            title__icontains=query
        ) | Book.objects.filter(
            uploader=request.user,
            status=Book.Status.APPROVED,
            course_code__icontains=query
        )

    return render(request, 'books/book_list.html', {'books': books, 'query': query})


@login_required
def book_upload_view(request):
    """Upload a new PDF book."""
    form = BookUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            book = form.save(commit=False)
            book.uploader = request.user
            book.status = Book.Status.PENDING
            book.save()
            messages.success(request, "Book uploaded successfully! It will be visible after admin approval.")
            return redirect('book_list')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'books/book_upload.html', {'form': form})


@login_required
def book_detail_view(request, pk):
    """Book detail — only accessible by the uploader."""
    book = get_object_or_404(
        Book, pk=pk,
        uploader=request.user,
        status=Book.Status.APPROVED
    )
    bookmark, _ = Bookmark.objects.get_or_create(user=request.user, book=book)
    return render(request, 'books/book_detail.html', {
        'book': book,
        'bookmark': bookmark,
    })


@login_required
def book_read_view(request, pk):
    """PDF reader — only accessible by the uploader."""
    book = get_object_or_404(
        Book, pk=pk,
        uploader=request.user,
        status=Book.Status.APPROVED
    )
    bookmark, _ = Bookmark.objects.get_or_create(user=request.user, book=book)

    if request.method == 'POST':
        page = request.POST.get('page', 1)
        try:
            bookmark.page = int(page)
            bookmark.save()
        except (ValueError, TypeError):
            pass
        return redirect('book_read', pk=pk)

    return render(request, 'books/book_read.html', {
        'book': book,
        'bookmark': bookmark,
    })


@login_required
def my_books_view(request):
    """Shows the logged-in user's own uploaded books and their approval status."""
    my_books = Book.objects.filter(
        uploader=request.user
    ).order_by('-upload_date')
    return render(request, 'books/my_books.html', {'my_books': my_books})


# ─────────────────────────────────────────────
#  STUDY SCHEDULE
# ─────────────────────────────────────────────

@login_required
def schedule_view(request):
    today = timezone.now().date()
    schedules = StudySchedule.objects.filter(student=request.user).order_by('date', 'start_time')
    upcoming = schedules.filter(date__gte=today)
    past = schedules.filter(date__lt=today)
    form = StudyScheduleForm()
    return render(request, 'planner/schedule.html', {
        'upcoming': upcoming,
        'past': past,
        'form': form,
        'today': today,
    })


@login_required
def schedule_add(request):
    if request.method == 'POST':
        form = StudyScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.student = request.user
            schedule.save()
            messages.success(request, "Study session added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    return redirect('schedule')


@login_required
def schedule_toggle(request, pk):
    schedule = get_object_or_404(StudySchedule, pk=pk, student=request.user)
    schedule.is_done = not schedule.is_done
    schedule.save()
    status = "completed" if schedule.is_done else "marked as pending"
    messages.success(request, f"Session {status}.")
    return redirect('schedule')


@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(StudySchedule, pk=pk, student=request.user)
    schedule.delete()
    messages.success(request, "Study session deleted.")
    return redirect('schedule')


# ─────────────────────────────────────────────
#  EXAM DATES
# ─────────────────────────────────────────────

@login_required
def exam_list_view(request):
    today = timezone.now().date()
    upcoming_exams = ExamDate.objects.filter(
        student=request.user,
        exam_date__gte=today
    ).order_by('exam_date')
    past_exams = ExamDate.objects.filter(
        student=request.user,
        exam_date__lt=today
    ).order_by('-exam_date')
    form = ExamDateForm()
    return render(request, 'planner/exam_list.html', {
        'upcoming_exams': upcoming_exams,
        'past_exams': past_exams,
        'form': form,
        'today': today,
    })


@login_required
def exam_add(request):
    if request.method == 'POST':
        form = ExamDateForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.student = request.user
            exam.save()
            days = exam.days_until()
            Notification.objects.create(
                user=request.user,
                message=f"Exam registered: {exam.course_code} — {exam.course} on {exam.exam_date.strftime('%B %d, %Y')}.",
                notif_type=Notification.NotifType.EXAM_REMINDER,
            )
            messages.success(request, f"Exam date registered! {days} day(s) to go.")
        else:
            messages.error(request, "Please correct the errors below.")
    return redirect('exam_list')


@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(ExamDate, pk=pk, student=request.user)
    exam.delete()
    messages.success(request, "Exam date removed.")
    return redirect('exam_list')


# ─────────────────────────────────────────────
#  NOTIFICATIONS
# ─────────────────────────────────────────────

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'planner/notifications.html', {
        'notifications': notifications,
    })


@login_required
def notification_delete(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.delete()
    return redirect('notifications')


@login_required
def notifications_clear(request):
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, "All notifications cleared.")
    return redirect('notifications')