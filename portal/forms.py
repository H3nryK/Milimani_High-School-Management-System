from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import *
from django.forms import BaseFormSet

User = get_user_model()

class NewUserForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'password1': forms.PasswordInput(attrs={'class':'form-control'}),
            'password2': forms.PasswordInput(attrs={'class':'form-control'}),
        }
        
        def save(self, commit=False):
            User = super(NewUserForm, self).save(commit=False)
            if commit:
                User.save()
                return User

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label='New Password Confirmation',
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        strip=False,
    )

class PasswordResetForm(forms.Form):
    username = forms.CharField(label='Username')
    
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('Invalid username')
        return username
    
class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label = "New Password",
        widget = forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label = "New password confrimation",
        widget = forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.validationError(
                self.error_messages['Password_mismatch'],
                code='password_mismatch',
            )
            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['new_password1'])
        if commit:
            user.save()
        return user

class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['full_name','adm_no', 'yoa', 'subjects', 'user_class','dob', 'gender', 'contact']
        subjects = forms.ModelMultipleChoiceField(
            queryset=Subject.objects.all(),
            widget=forms.CheckboxSelectMultiple,
        )
        user_class = forms.ModelChoiceField(
            queryset = Class.objects.all(),
            widget = forms.Select(attrs={'class':'form-control'}),
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'class':'form-control'}),
            'adm_no': forms.TextInput(attrs={'class':'form-control'}),
            'yoa': forms.TextInput(attrs={'class':'form-control'}),
            'dob': forms.TextInput(attrs={'class':'form-control'}),
            'contact': forms.TextInput(attrs={'class':'form-control'}),
        }
        
class TeacherForm(forms.ModelForm):

    class Meta:
        model = Teacher
        fields = ['full_name','title', 'gender', 'contact', 'selection']
        selection = forms.ModelMultipleChoiceField(
            queryset = ClassSubject.objects.all(),
            widget = forms.CheckboxSelectMultiple,
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'contact': forms.TextInput(attrs={'class':'form-control'}),
        }
        
class ClassTeacherForm(forms.ModelForm):

    class Meta:
        model = ClassTeacher
        fields = ['full_name','title', 'gender', 'contact', 'class_T', 'selection']
        selection = forms.ModelMultipleChoiceField(
            queryset = ClassSubject.objects.all(),
            widget = forms.CheckboxSelectMultiple,
        )
        widgets = {
            'full_name': forms.TextInput(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'contact': forms.TextInput(attrs={'class':'form-control'}),
        }
        
class FinanceForm(forms.ModelForm):

    class Meta:
        model = Finance
        fields = ['full_name','title', 'gender', 'contact']
        widgets = {
            'full_name': forms.TextInput(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'contact': forms.TextInput(attrs={'class':'form-control'}),
        }
        
class AdminForm(forms.ModelForm):

    class Meta:
        model = Admin
        fields = ['full_name','title', 'gender', 'contact']
        widgets = {
            'full_name': forms.TextInput(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'contact': forms.TextInput(attrs={'class':'form-control'}),
        }

class AdminForm(forms.ModelForm):

    class Meta:
        model = Admin
        fields = ['full_name','title', 'gender', 'contact']
        widgets = {
            'full_name': forms.TextInput(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'contact': forms.TextInput(attrs={'class':'form-control'}),
        }

class SessionForm(forms.ModelForm):
    
    class Meta:
        model = Session
        fields = ['term', 'year', 'session_fees']
        widgets = {
            'session_fees': forms.TextInput(attrs={'class':'form-control'}),
        }

class CourseForm(forms.ModelForm):
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'class_selected', 'subject', 'session']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.TextInput(attrs={'class':'form-control'}),
        }

class ExamsessionForm(forms.ModelForm):
    
    class Meta:
        model = Exam
        fields = ['session', 'type']

class FeeForm(forms.ModelForm):
    adm_no = forms.CharField(label="Student's Admission Number", max_length=10)
    amount = forms.DecimalField(max_digits=10, label="Fee Deposit", decimal_places=2)
    
    class Meta:
        model = Fee_entry
        fields = ['adm_no', 'amount']
        widgets = {
            'adm_no': forms.TextInput(attrs={'class':'form-control'}),
            'amount': forms.TextInput(attrs={'class':'form-control'}),
        }

class ContactForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        fields = ['name', 'contact', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'contact': forms.TextInput(attrs={'class':'form-control'}),
            'message': forms.Textarea(attrs={'class':'form-control'}),
        }

class MarkForm(forms.ModelForm):
    
    class Meta:
        model = Mark
        fields = ['marks']
        widgets = {
            'marks': forms.TextInput(attrs={'class':'form-control'}),
        }