from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from django.urls import reverse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.db.models import Avg, Count, Sum
from io import BytesIO
from django.core.exceptions import ObjectDoesNotExist
import matplotlib.pyplot as plt
import base64

User = get_user_model()

@login_required
def register(request):
    pending_users = CustomUser.objects.filter(update_status='pending')[:10]
    
    if request.method == 'POST':
        register_form = NewUserForm(request.POST)
        if register_form.is_valid():
            user = register_form.save()
            
            category = request.POST.get('category')
            if category == 'student':
                user.is_student = True
                user.save()
            elif category == 'teacher':
                user.is_teacher = True
                user.save()
            elif category == 'class_teacher':
                user.is_class_teacher = True
                user.save()
            elif category == 'finance':
                user.is_finance = True
                user.save()
            elif category == 'admin':
                user.is_admin = True
                user.save()
                
            user.update_status = 'pending'
            user.save()
            messages.success(request, f"Successfully created {category} account.")
            return redirect('register')
        else:
            messages.error(request, f"Sorry, couldn't create user account.")
    else:
        register_form = NewUserForm()
    
    return render(request, 'register.html', {'register_form':register_form, 'pending_users':pending_users})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {username}.")
            return redirect('dashboard')
                
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, f"See you later buddy.")
    return redirect('login')

def dashboard(request):
    courses = Course.objects.all().order_by('-start')[:15]
    return render(request, 'dashboard.html', {'courses':courses})

def password_reset_view(request):
    if request.method == 'POST':
        reset_form = PasswordResetForm(request.POST)
        if reset_form.is_valid():
            username = reset_form.cleaned_data['username']
            return redirect('set_password', username=username)
        else:
            messages.error(request, f"Sorry, that was an invalid username.")
    else:
        reset_form = PasswordResetForm()
        
    return render(request, 'password_reset.html', {'reset_form':reset_form})

def password_change_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        change_form = ChangePasswordForm(user, request.POST)
        if change_form.is_valid():
            change_form.save()
            update_session_auth_hash(request, change_form.user)
            messages.success(request, f"Successfully changed your password.")
            return redirect('dashboard')
        else:
            messages.error(request, f"Sorry, couldn't change your password.")
    else:
        change_form = ChangePasswordForm(user)
    
    return render(request, 'password_change.html', {'change_form':change_form, 'user':user})
        

def set_password_view(request, username):
    user = User.objects.get(username=username)
    
    if request.method == 'POST':
        password_form = SetPasswordForm(user, request.POST)
        if password_form.is_valid():
            password_form.save()
            return redirect('password_reset')
        else:
            messages.error(request, f"Sorry, unable to reset your password.")
    else:
        password_form = SetPasswordForm(user)
    return render(request, 'set_password.html', {'password_form':password_form, 'username':username})

@login_required
def student_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_student:
        student_profile, created = Student.objects.get_or_create(user=user)
        student_exams = Exam.objects.filter(mark__student=student_profile).distinct()
        
        performance_graph = generate_performance_graph(student_profile)
        
        class_teacher_name = get_class_teacher_name(student_profile.user_class)
        
        if request.method == 'POST':
            stu_form = StudentForm(request.POST, request.FILES, instance=student_profile)
            if stu_form.is_valid():
                stu_form.save()
                user.update_status = 'updated'
                user.save()
                messages.success(request, f"Successfully updated {user.username}'s profile.")
                return redirect('student_profile', user_id=user.id)
            else:
                messages.error(request, f"Sorry, that was an invalid input.")
               
        else:
            stu_form = StudentForm(instance=student_profile)

        if 'download_pdf' in request.POST:
            # If download button is clicked, generate and return PDF
            return generate_student_profile_pdf(student_profile)         

    return render(request, 'student_profile.html', {'user':user, 'stu_form':stu_form, 'student_profile':student_profile, 
                                                    'student_exams':student_exams, 'performance_graph':performance_graph,
                                                    'class_teacher_name':class_teacher_name})

def generate_student_profile_pdf(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    student_profile, created = Student.objects.get_or_create(user=user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={student_profile.user.username}_profile.pdf'
    
    p = canvas.Canvas(response)
    
    # Write student details to PDF
    p.drawString(100, 750, f"Student Profile for {student_profile.user.username}")
    p.drawString(100, 730, f"Name: {student_profile.full_name}")
    p.drawString(100, 710, f"Date of Birth: {student_profile.dob}")
    p.drawString(100, 690, f"Class: {student_profile.user_class}")
    p.drawString(100, 670, f"Year of Admission: {student_profile.yoa}")
    p.drawString(100, 650, f"Admission Number: {student_profile.adm_no}")
    # Add more details as needed

    p.save()
    
    return response

def get_class_teacher_name(user_class):
    try:
        class_teacher = ClassTeacher.objects.get(class_T=user_class)
        return class_teacher.full_name
    except ClassTeacher.DoesNotExist:
        return None

@login_required
def teacher_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    teacher_profile, created = Teacher.objects.get_or_create(user=user)
    
    if request.method =='POST':
        teacher_form = TeacherForm(request.POST, request.FILES, instance=teacher_profile)
        if teacher_form.is_valid():
            teacher_form.save()
            user.update_status = 'updated'
            user.save()
            messages.success(request, f"Successfully updated {user.username}'s profile.")
            return redirect('teacher_profile', user_id=user.id)
        else:
            messages.error(request, f"Sorry, that was an invalid input.")
            
    else:
        teacher_form = TeacherForm(instance=teacher_profile)

    return render(request, 'teacher_profile.html', {'user':user, 'teacher_form':teacher_form,'teacher_profile':teacher_profile})

@login_required
def class_teacher_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
        
    class_teacher_profile, created = ClassTeacher.objects.get_or_create(user=user)
    
    if request.method =='POST':
        class_teacher_form = ClassTeacherForm(request.POST, request.FILES, instance=class_teacher_profile)
        if class_teacher_form.is_valid():
            class_teacher_form.save()
            user.update_status = 'updated'
            user.save()
            messages.success(request, f"Successfully updated {user.username}'s profile.")
            return redirect('class_teacher_profile', user_id=user.id)
        else:
            messages.error(request, f"Sorry, that was an invalid input.")
            
    else:
        class_teacher_form = ClassTeacherForm(instance=class_teacher_profile)

    return render(request, 'class_teacher_profile.html', {'user':user, 'class_teacher_form':class_teacher_form,'class_teacher_profile':class_teacher_profile})

@login_required
def finance_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    finance_profile, created = Finance.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        finance_form = FinanceForm(request.POST, request.FILES, instance=finance_profile)
        if finance_form.is_valid():
            finance_form.save()
            user.update_status = 'updated'
            user.save()
            messages.success(request, f"Successfully updated {user.username}'s profile.")
            return redirect('finance_profile', user_id=user.id)        
        else:
            messages.error(request, f"Sorry, that was an invalid input.")
    
    else:
        finance_form = FinanceForm(instance=finance_profile)

    return render(request, 'finance_profile.html', {'user':user, 'finance_form':finance_form, 'finance_profile':finance_profile})

@login_required
def admin_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    admin_profile, created = Admin.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        admin_form = AdminForm(request.POST, request.FILES, instance=admin_profile)
        if admin_form.is_valid():
            admin_form.save()
            user.update_status = 'updated'
            user.save()
            messages.success(request, f"Successfully updated {user.username}'s profile.")
            return redirect('admin_profile', user_id=user.id)
        else:
            messages.error(request, f"Sorry, that was an invalid input.")       
    
    else:
        admin_form = AdminForm(instance=admin_profile)

    return render(request, 'admin_profile.html', {'user':user, 'admin_form':admin_form, 'admin_profile':admin_profile})

def class_view(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(user_class=class_obj)
    return render(request, 'class_profile.html', {'class_obj':class_obj, 'students':students})

def student_view(request):
    classes = Class.objects.all()
    students = None
    selected_class = None
    list_type = None
    male_count = 0
    female_count = 0
    total_students = 0
    class_teacher = None
    total_balance = 0
        
    if request.method == 'POST':
        selected_class_id = request.POST.get('class')
        list_type = request.POST.get('list_type')

        if selected_class_id and list_type:
            selected_class = Class.objects.get(id=selected_class_id)

            if list_type == 'finance':
                students = Student.objects.filter(user_class=selected_class)
                total_balance = students.aggregate(Sum('fee_balance'))['fee_balance__sum']
                
            elif list_type == 'class_list':
                students = Student.objects.filter(user_class=selected_class)
                
                male_count = students.filter(gender='male').count()
                female_count = students.filter(gender='female').count()
                total_students = students.count()
                
            try:
                class_teacher = ClassTeacher.objects.get(class_T=selected_class)
            except ClassTeacher.DoesNotExist:
                class_teacher = None
                
    return render(request, 'student_list.html', {'classes':classes, 'students':students, 'selected_class':selected_class, 'list_type':list_type,
                                                 'male_count':male_count, 'female_count':female_count, 'class_teacher':class_teacher,
                                                 'total_students':total_students, 'total_balance':total_balance})
    
def generate_student_list(request, students, total_balance, total_students, female_count, male_count, class_teacher, selected_class, list_type):
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={selected_class.name}_list.pdf'
    
    p = canvas.Canvas(response, pagesize=letter)
    
    p.setFont("Helvetica", 12)
    
    center_x = letter[0] / 2
    
    if list_type == 'finance':
        p.drawString(center_x, 750, f"{selected_class.name}'s Fee Balance List")
        p.drawString(100, 730, f"{class_teacher.full_name}")
        p.drawString(500, 730, f"Ksh. {total_balance}")
        
        y_position = 710
        
        p.drawString(100, y_position, f"Adm No")
        p.drawString(170, y_position, f"Name")
        p.drawString(350, y_position, f"Fee Balance")
                
        p.line(100, y_position - 5, 500, y_position - 5)
         
        for student in students:
            p.drawString(100, y_position - 20, f"{student.adm_no}")
            p.drawString(170, y_position - 20, f"{student.full_name}")
            p.drawString(350, y_position - 20, f"{student.fee_balance}")
            
            p.line(100, y_position - 5, 500, y_position -5)
            
            y_position -= 20
    else:
        p.drawString(center_x, 750, f"{selected_class.name}'s Class List List")
        p.drawString(100, 730, f"{class_teacher.full_name}")
        p.drawString(100, 710, f"Population: {total_students} ({female_count} females & {male_count} males)")
        
        y_position = 690
        
        p.drawString(100, y_position, f"Adm No")
        p.drawString(170, y_position, f"Name")
                
        p.line(100, y_position - 5, 500, y_position - 5)
         
        for student in students:
            p.drawString(100, y_position - 20, f"{student.adm_no}")
            p.drawString(170, y_position - 20, f"{student.full_name}")
            
            p.line(100, y_position - 5, 500, y_position -5)
            
            y_position -= 20
        
    p.showPage()
    p.save()
    
    return response
    
def create_session(request):
    sessions = Session.objects.all().order_by('-started_on')[:10]

    if request.method == 'POST':
        session_form = SessionForm(request.POST)
        if session_form.is_valid():
            session_form.save()
            messages.success(request, f"Successfully created a new session.")
            return redirect('session')
        else:
            messages.error(request, f"Sorry, that was an invalid input.")
        
    else:
        session_form = SessionForm()
        
    return render(request, 'session.html', {'session_form':session_form, 'sessions':sessions})

def create_course(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        if course_form.is_valid():
            course_form.save()
            messages.success(request, f"Successfully created a new course.")
            return redirect('course')
        else:
            messages.success(request, f"Sorry, that was an invalid input.")
        
    else:
        course_form = CourseForm()
        
    return render(request, 'course.html', {'course_form':course_form})

def edit_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course_form = CourseForm(request.POST, instance=course)
        if course_form.is_valid():
            course_form.save()
            messages.success(request, f"Successfully updated the course.")
            return redirect('course')
        else:
            messages.error(request, f"Sorry, that was an invalid input.")
    else:
        course_form = CourseForm(instance=course)
        
    return render(request, 'edit_course.html', {'course_form': course_form, 'course_id': course_id})

def delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, f"Course deleted successfully.")
        return redirect('course')
        
    return render(request, 'delete_course.html', {'course': course})

def create_exam_session(request):
    exam_sessions = Exam.objects.all().order_by('-timestamp')[:15]
    
    if request.method == 'POST':
        exam_session_form = ExamsessionForm(request.POST)
        if exam_session_form.is_valid():
            exam_session_form.save()
            messages.success(request, f"Successfully created an exam session.")
            return redirect('exam_session')
        else:
            messages.error(request, f"Sorry, that was an invalid input.")
        
    else:
        exam_session_form = ExamsessionForm()
    
    return render(request, 'exam_session.html', {'exam_sessions':exam_sessions, 'exam_session_form':exam_session_form})

def recent_fee_view(request):
    fee_updates = Fee_entry.objects.all().order_by('-timestamp')[:15]
    if request.method == 'POST':
        fee_form = FeeForm(request.POST)
        if fee_form.is_valid():
            adm_no = fee_form.cleaned_data['adm_no']
            amount = fee_form.cleaned_data['amount']
            
            try:
                student = Student.objects.get(adm_no=adm_no)
                Fee_entry.objects.create(student=student, amount=amount)
                messages.success(request, f"Fee update for {student.full_name} added successfully")
            except Student.DoesNotExist:
                messages.success(request, f"Inavlid Admission Number")
                
            return redirect('recent_fee')
        
    else:
        fee_form = FeeForm()
        
    return render(request, 'recent_fee.html', {'fee_updates': fee_updates, 'fee_form': fee_form})

def generate_fee_report(request):
    fee_updates = Fee_entry.objects.all().order_by('-timestamp')[:15]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fee_report.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    y_position = 750

    p.drawString(100, y_position, "Recent Fee Updates")
    p.line(100, y_position - 5, 500, y_position - 5)

    for fee_update in fee_updates:
        y_position -= 20
        p.drawString(100, y_position, f"Admission No: {fee_update.student.adm_no}")
        p.drawString(200, y_position, f"Student Name: {fee_update.student.full_name}")
        p.drawString(400, y_position, f"Amount: {fee_update.amount}")

    p.save()

    return response



def statement_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student_fees = Fee_entry.objects.filter(student__id=student_id).order_by('timestamp')
    messages.info(request, f"This is {student.full_name}'s Fee statement.")
    return render(request, 'statement.html', {'student_fees':student_fees, 'student': student})

def exam_view(request):
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    exams = Exam.objects.all()
    
    if request.method == 'POST':
        selected_class_id = request.POST.get('class')
        selected_subject_id = request.POST.get('subject')
        selected_exam_id = request.POST.get('exam')
        messages.success(request, f"Successfully got your query.")
            
        return redirect(reverse('exam_marks', args=[selected_class_id, selected_subject_id, selected_exam_id]))
                
    return render(request, 'exams_entry.html', {'classes':classes, 'exams':exams, 'subjects':subjects})
    
def exam_marks(request, class_id, exam_id, subject_id):
    students = []
    
    selected_subject = get_object_or_404(Subject, id=subject_id)
    selected_class = get_object_or_404(Class, id=class_id)
    selected_exam = get_object_or_404(Exam, id=exam_id)
            
    students = Student.objects.filter(user_class_id=class_id, subjects=subject_id)
    
    if request.method == 'POST':
        marks_data = request.POST.getlist('marks')

        student_ids = [student.id for student in students]
        
        if len(marks_data) == len(student_ids):
            for i, student_id in enumerate(student_ids):
                mark_value = marks_data[i]
                
                try:
                    mark_instance = Mark.objects.get(
                        student_id=student_id,
                        exam=selected_exam,
                        user_class=selected_class,
                        subject=selected_subject
                    )
                    
                    mark_instance.marks = mark_value
                    mark_instance.save()
                    messages.success(request, f"Successfully updated exam.")
                
                except Mark.DoesNotExist:
                    
                    Mark.objects.create(
                        student_id=student_id,
                        exam=selected_exam,
                        user_class=selected_class,
                        subject=selected_subject,
                        marks=mark_value
                    )
                    messages.success(request, f"Successfully marked exam.")
    
    return render(request, 'exams_marks.html', {'students':students,'selected_class':selected_class, 'selected_subject':selected_subject, 
                                                'selected_exam':selected_exam, 'mark_form':MarkForm()})

def calculate_total_average(marks):
    total_marks = sum(mark.marks for mark in marks)
    average_marks = total_marks / len(marks) if marks else 0
    return total_marks, average_marks

def determine_grade(average_marks):
    if average_marks >= 90:
        return 'A'
    elif 70 <= average_marks < 90:
        return 'B'
    elif 50 <= average_marks < 70:
        return 'C'
    elif 30 <= average_marks < 50:
        return 'D'
    else:
        return 'E'

def exam_details(request, exam_id, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    exam = get_object_or_404(Exam, id=exam_id)
    
    if user.is_student:
        student_profile = get_object_or_404(Student, user=user)
        marks_for_exam = Mark.objects.filter(student=student_profile, exam=exam)
        
        total_marks, average_marks = calculate_total_average(marks_for_exam)
        grade = determine_grade(average_marks)
    
    return render(request, 'exams_details.html', {'student_profile':student_profile, 'exam':exam, 'user':user, 'marks_for_exam':marks_for_exam,
                                                  'grade':grade, 'total_marks':total_marks, 'average_marks':average_marks})
    
def generate_report_pdf(request, user_id, exam_id):
    user = get_object_or_404(CustomUser, id=user_id)
    exam = get_object_or_404(Exam, id=exam_id)
    student_profile = get_object_or_404(Student, user=user)
    marks_for_exam = Mark.objects.filter(student=student_profile, exam=exam)
    total_marks, average_marks = calculate_total_average(marks_for_exam)
    grade = determine_grade(average_marks)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={student_profile.adm_no}_report.pdf'
    
    p = canvas.Canvas(response, pagesize=(612, 792))  # Set the page size to letter (8.5 x 11 inches)
    
    p.setFont("Helvetica", 12)
    
    details_y = 750
    
    p.setStrokeColor('black')
    
    p.setFont("Helvetica", 12)
    p.drawString(50, details_y, f"Student: {student_profile.full_name}")
    p.drawString(50, details_y - 20, f"Class: {student_profile.user_class}")
    p.drawString(50, details_y - 40, f"Exam: {exam.type} {exam.session}")
    p.drawString(50, details_y - 60, f"D.O.B: {student_profile.dob}")
    p.drawString(50, details_y - 80, f"Admission Number: {student_profile.adm_no}")
    
    p.line(50, details_y - 80, 562, details_y - 80)
    
    col_width = [180, 70, 70, 140]
    table_x = 50
    table_y = details_y - 100
    # Calculate the available width based on default 1-inch margins on each side
    table_width = 512
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(table_x, table_y, "Subject")
    p.drawString(table_x + col_width[0], table_y, "Marks")
    p.drawString(table_x + col_width[0] + col_width[1], table_y, "Grade")
    p.drawString(table_x + col_width[0] + col_width[1] + col_width[2], table_y, "Remarks")
    
    p.line(table_x, table_y - 5, table_x + table_width, table_y - 5)
    
    p.setFont("Helvetica", 12)
    for mark in marks_for_exam:
        table_y -= 20
        p.drawString(table_x, table_y, str(mark.subject))
        p.drawString(table_x + col_width[0], table_y, str(mark.marks))
        p.drawString(table_x + col_width[0] + col_width[1], table_y, str("-"))
        p.drawString(table_x + col_width[0] + col_width[1] + col_width[2], table_y, str("-"))
    
    p.line(table_x, table_y - 5, table_x + table_width, table_y - 5)
    
    p.drawString(table_x, table_y - 30, f"Total Marks: {total_marks}")
    p.drawString(table_x, table_y - 50, f"Average Marks: {average_marks}")
    p.drawString(table_x, table_y - 70, f"Overall Grade: {grade}")
    
    p.line(table_x, table_y - 80, 562, table_y - 80)
    
    approved_by_y = table_y - 100
    p.drawString(table_x, approved_by_y, "Approved By: Principal")
    
    note_x = (562 - p.stringWidth("Note: This is a sample report pdf under testing.", "Helvetica", 10)) / 2
    note_y = 50
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(note_x, note_y, "Note: This is a sample report pdf under testing.")
    
    p.save()
    
    return response

def generate_performance_graph(student_profile):
    exams = Exam.objects.all()
    
    exam_avg_marks = []
    for exam in exams:
        try:
            marks = Mark.objects.filter(student=student_profile, exam=exam)
            avg_marks = marks.aggregate(Avg('marks'))['marks__avg']
            exam_avg_marks.append(avg_marks if avg_marks is not None else 0)
        except ObjectDoesNotExist:
            exam_avg_marks.append(0)
            
    plt.bar([exam.type for exam in exams], exam_avg_marks)
    plt.xlabel('Exams')
    plt.ylabel('Average Marks')
    plt.title(f'{student_profile.full_name}\'s Overall Performance.')
    plt.ylim(0, 100)
    
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    plt.close()
    
    img_data.seek(0)
    encoded_img_data = base64.b64encode(img_data.read()).decode('utf-8')
    
    return encoded_img_data

def search_student(request):
    if request.method == 'POST':
        adm_no = request.POST.get('adm_no')
        
        try:
            student = Student.objects.get(adm_no=adm_no)
            messages.success(request, f"You found {adm_no} - {student.full_name}")
            return redirect('student_profile', user_id=student.user.id)
        except Student.DoesNotExist:
            messages.error(request, f"Sorry {adm_no} is not in the system.")
            return redirect('dashboard')
    
    return render(request, 'base.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Thank you for your message, we'll reach out as we look into it.")
            return redirect(request.path)
        else:
            messages.error(request, f"Sorry, that was an invalid input.")
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form':form})