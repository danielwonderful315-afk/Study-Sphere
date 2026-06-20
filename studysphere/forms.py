from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import User, Book


# ─────────────────────────────────────────────
#  REGISTRATION
# ─────────────────────────────────────────────

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        })
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
        })
    )
    matric_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Matric number (optional)',
        })
    )

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'username', 'email', 'matric_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email         = self.cleaned_data['email']
        user.first_name    = self.cleaned_data['first_name']
        user.last_name     = self.cleaned_data['last_name']
        user.matric_number = self.cleaned_data.get('matric_number', '')
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
        })


# ─────────────────────────────────────────────
#  PASSWORD RESET
# ─────────────────────────────────────────────

class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
        })


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'New password',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password',
        })


# ─────────────────────────────────────────────
#  PROFILE UPDATE
# ─────────────────────────────────────────────

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'matric_number', 'profile_picture')
        widgets = {
            'first_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control'}),
            'bio':           forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'matric_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ─────────────────────────────────────────────
#  BOOK UPLOAD
# ─────────────────────────────────────────────

class BookUploadForm(forms.ModelForm):
    class Meta:
        model  = Book
        fields = ('title', 'course_code', 'description', 'file', 'cover_image')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Introduction to Data Structures',
            }),
            'course_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. CSC 301',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this material (optional)',
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            if file.size > 50 * 1024 * 1024:  # 50MB limit
                raise forms.ValidationError("File size must be under 50MB.")
        return file
    
from django import forms
from .models import StudySchedule, ExamDate


# ─────────────────────────────────────────────
#  STUDY SCHEDULE FORM
# ─────────────────────────────────────────────

class StudyScheduleForm(forms.ModelForm):
    class Meta:
        model  = StudySchedule
        fields = ('subject', 'description', 'date', 'start_time', 'end_time')
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Mathematics, CSC 301',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'What will you study? (optional)',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end   = cleaned_data.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned_data


# ─────────────────────────────────────────────
#  EXAM DATE FORM
# ─────────────────────────────────────────────

class ExamDateForm(forms.ModelForm):
    class Meta:
        model  = ExamDate
        fields = ('course', 'course_code', 'exam_date', 'exam_time', 'venue', 'notes')
        widgets = {
            'course': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Introduction to Programming',
            }),
            'course_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. CSC 301',
            }),
            'exam_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'exam_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Hall A, Block 2',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes (optional)',
            }),
        }

    def clean_exam_date(self):
        from django.utils import timezone
        exam_date = self.cleaned_data.get('exam_date')
        if exam_date and exam_date < timezone.now().date():
            raise forms.ValidationError("Exam date cannot be in the past.")
        return exam_date    