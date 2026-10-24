"""
URL configuration for IT_company_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from IT_company_management_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.landing,name='landing'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('employeedashboard/',views.employeedashboard,name='employeedashboard'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('employees/',views.employees,name='employees'),
    path('edit_employee//<int:id>/',views.edit_employee,name='edit_employee'),
    path('toggle_status/<int:id>/', views.toggle_status, name='toggle_status'),
    path('delete_employee/<int:id>/',views.delete_employee,name='delete_employee'),
    path('developer_dashboard/',views.developer_dashboard,name='developer_dashboard'),
    path('edit_profile/<int:id>/',views.edit_profile,name='edit_profile'),
    path('developer_profile/',views.developer_profile, name='developer_profile'),
    path('edit_developerprofile/<int:id>/',views.edit_developerprofile,name='edit_developerprofile'),
    path('developer_applyleave/', views.developer_applyleave, name='developer_applyleave'),
    path('developer_leaves/', views.developer_leaves, name='developer_leaves'),
    path('manage_leave_requests/',views.manage_leave_requests,name='manage_leave_requests'),
    path('update_leave_status/<int:leave_id>/',views.update_leave_status,name='update_leave_status'),
    path('developer_project/', views.developer_project, name='developer_project'),
    path('manage_projects/', views.manage_projects, name='manage_projects'),
    path('add_project/', views.add_project, name='add_project'),
    path('admin_edit_project/<int:project_id>/', views.admin_edit_project, name='admin_edit_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('developer_tasks/', views.developer_tasks, name='developer_tasks'),
    path('report_bug/',views.report_bug,name='report_bug'),
    path('bugs/',views.bug_list,name='bug_list'),
    path('bugs/<int:bug_id>/update-status/',views.update_bug_status,name='update_bug_status'),
    path('admin_bug_list/',views.admin_bug_list,name='admin_bug_list'),
    path('admin_tasks/', views.admin_tasks, name='admin_tasks'),
    path('admin_reports/', views.admin_reports, name='admin_reports'),
    path('hr_dashboard/',views.hr_dashboard,name='hr_dashboard'),
    path('hr_profile/',views.hr_profile, name='hr_profile'),
    path('edit_hrprofile/<int:id>/',views.edit_hrprofile,name='edit_hrprofile'),
    path('hr_leave_requests/',views.hr_leave_requests,name='hr_leave_requests'),
    path('hr_leave_requests/<int:leave_id>/update/',views.hr_update_leave_status,name='hr_update_leave_status'),
    path('hr_apply_leave/',views.hr_apply_leave,name='hr_apply_leave'),
    path('hr_my_leave_requests/',views.hr_my_leave_requests,name='hr_my_leave_requests'),
    path( 'hr_employee_report/',views.hr_employee_report,name='hr_employee_report'),
    path('clients/', views.client_list, name='client_list'),
    path('add_client', views.add_client, name='add_client'),
    path('edit_client/<int:id>/',views.edit_client,name='edit_client'),
    path('delete_client/<int:id>/', views.delete_client,name='delete_client'),
    path('project_manager_dashboard/',views.project_manager_dashboard,name='project_manager_dashboard'),
    path('my_projects/',views.my_projects,name='my_projects'),
    path('create_project/',views.create_project,name='create_project'),
    path('edit_project/<int:project_id>/',views.edit_project,name='edit_project'),
    path('manage_tasks/', views.manage_tasks, name='manage_tasks'),
    path('add_task/', views.add_task, name='add_task'),
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('project_manager_profile/',views.project_manager_profile,name='project_manager_profile'),
    path('project_manager_edit_profile/',views.project_manager_edit_profile,name='project_manager_edit_profile'),
    path('project_manager_apply_leave/',views.project_manager_apply_leave,name='project_manager_apply_leave'),
    path('project_manager_leaves/',views.project_manager_leaves,name='project_manager_leaves'),
    path('project_manager_report_bug/',views.project_manager_report_bug,name='project_manager_report_bug'),
    path('project_manager_bug_list/',views.project_manager_bug_list,name='project_manager_bug_list'),
]
