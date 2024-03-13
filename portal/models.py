from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
import uuid
import hashlib
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_class_teacher = models.BooleanField(default=False)
    is_finance = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    groups = models.ManyToManyField(Group, related_name='customuser_set')
    user_permissions= models.ManyToManyField(Permission, related_name='customuser_set')
    
    update_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('updated', 'Updated')], default='pending')
    date_joined = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'portal_customuser'

class Class(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    
class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ClassSubject(models.Model):
    user_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    subjects = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user_class} {self.subjects}"
    
class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    selection = models.ManyToManyField(ClassSubject)
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

class ClassTeacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='class_teacher_profile')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    selection = models.ManyToManyField(ClassSubject)
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    class_T = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username
    
class Finance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='finance_profile')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username
    
class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

class Session(models.Model):
    term = models.CharField(max_length=20, choices=[('term_1', 'Term 1'), ('term_2', 'Term 2'), ('term_3', 'Term 3')], blank=True)
    session_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    year = models.CharField(max_length=20, choices=[('2023', '2023'), ('2024','2024')], blank=True)
    started_on = models.DateField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        students = Student.objects.all()
        for student in students:
            Fee_entry.objects.create(
                student=student,
                amount=self.session_fees,
                type='Credit',
            )
            
    def __str__(self):
        return f"{self.year} {self.term}"

class Exam(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=[('exam_1','Exam 1'), ('exam_2','Exam 2'), ('exam_3','Exam 3'), ('opener', 'Opener')])
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type} {self.session}"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=255, blank=True, null=True)
    adm_no = models.CharField(unique=True, max_length=20, blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    subjects = models.ManyToManyField(Subject, blank=True)
    user_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    fee_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gender = models.CharField(max_length=20, choices=[('female', 'Female'),('male', 'Male')], blank=True)
    yoa = models.DateField(blank=True, null=True)
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return  self.adm_no

class Mark(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    user_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    marks = models.IntegerField( default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('student', 'subject', 'user_class', 'exam')
    
    def __str__(self):
        student_name = str(self.student) if self.student else "Unknown Student"
        return f"{self.marks} {self.exam} {student_name}"
    
class Fee_entry(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    ref_code = models.CharField(unique=True, max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.type == 'Credit':
            self.student.fee_balance += self.amount
            self.student.save()
        else:
            self.student.fee_balance -= self.amount
            self.student.save()
        
        if not self.ref_code:
            random_uuid = uuid.uuid4()
            hash_str = hashlib.sha256(str(random_uuid).encode('utf-8')).hexdigest()[:7]
            self.ref_code = f"MS{hash_str}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.student.adm_no} Ksh.{self.amount}"
    
class Contact(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    message = models.TextField()
    
    def __str__(self):
        return self.name
    
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    class_selected = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    start = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title