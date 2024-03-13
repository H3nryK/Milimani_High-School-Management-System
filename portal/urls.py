from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('password_reset/<str:username>/', set_password_view, name='set_password'),
    path('password_change/<int:user_id>/', password_change_view, name='password_change'),
    
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'), 
    path('student_list/', student_view, name='student_list'),
    path('class_profile/<int:class_id>/', class_view, name='class_profile'),

    path('courses/', create_course, name='course'),
    path('edit/<int:course_id>/', edit_course, name='edit_course'),
    path('delete/<int:course_id>/', delete_course, name='delete_course'),
    
    path('student_profile/<int:user_id>/', student_profile, name='student_profile'),
    path('generate_profile_pdf/<int:user_id>/', generate_student_profile_pdf, name='generate_profile_pdf'),

    path('search_student/', search_student, name='search_student'),
    path('generate_class_list/', generate_student_list, name='generate_student_list'),
    path('teacher_profile/<int:user_id>/', teacher_profile, name='teacher_profile'),
    path('class_teacher_profile/<int:user_id>/', class_teacher_profile, name='class_teacher_profile'),
    path('finance_profile/<int:user_id>/', finance_profile, name='finance_profile'),
    path('admin_profile/<int:user_id>/', admin_profile, name='admin_profile'),
    
    path('create_session/', create_session, name='session'),
    path('recent_fee/', recent_fee_view, name='recent_fee'),
    path('generate_fee_pdf/', generate_fee_report, name='generate_fee_pdf'),
    path('statement/<int:student_id>/', statement_view, name='statement'),
    
    path('exam/', exam_view, name='exam'),
    path('exam_session/', create_exam_session, name='exam_session'),
    path('exam_marks/<int:class_id>/<int:subject_id>/<int:exam_id>/', exam_marks, name='exam_marks'),
    path('exam_details/<int:exam_id>/<int:user_id>/', exam_details, name='exam_details'),
    path('generate_report_pdf/<int:exam_id>/<int:user_id>/', generate_report_pdf, name='generate_report_pdf'),
    
    path('contact/', contact_view, name='contact'),
]
