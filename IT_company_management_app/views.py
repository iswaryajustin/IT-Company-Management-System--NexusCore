from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
import datetime
from datetime import date
from django.db.models import Q
from .models import EmployeeProfile,LeaveRequest,Project, Task, Bug,Client
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import ProjectForm,BugForm,ProjectForm
from django.contrib.auth import authenticate,login as auth_login

def landing(request):
    return render(request, 'landing.html')


def register(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        if password != confirmPassword:
            return render(request, 'register.html', {
                'error': 'Passwords do not match'
            })

        if EmployeeProfile.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Email already exists'
            })

        EmployeeProfile.objects.create(
            name=name,
            email=email,
            phone=phone,
            username=username,
            password=password,
            confirmPassword=confirmPassword,
            role='employee',
            is_active=True
        )

        return redirect('login')

    return render(request, 'register.html')

    
def login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:

            employee = EmployeeProfile.objects.get(
                username=username,
                password=password
            )

            request.session['employee_id'] = employee.id
            request.session['username'] = employee.username
            request.session['role'] = employee.role

            if employee.role == 'super_admin':
                return redirect('admin_dashboard')

            elif employee.role == 'hr':
                return redirect('hr_dashboard')

            elif employee.role == 'project_manager':
                return redirect('project_manager_dashboard')

            elif employee.role == 'developer':
                return redirect('developer_dashboard')

            elif employee.role == 'sales':
                return redirect('sales_dashboard')

            elif employee.role == 'accountant':
                return redirect('accountant_dashboard')

            elif employee.role == 'support':
                return redirect('support_dashboard')

            else:
                return redirect('employeedashboard')

        except EmployeeProfile.DoesNotExist:

            return render(
                request,
                'login.html',
                {'error': 'Invalid username or password'}
            )

    return render(request, 'login.html')

   

def employeedashboard(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    return render(request, 'employeedashboard.html', {
        'employee': employee
    })




def edit_profile(request, id):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    # Allow employees to edit only their own profile
    if int(employee_id) != int(id):
        return redirect('employeedashboard')

    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    if request.method == 'POST':
        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.phone = request.POST.get('phone')

        # Save employee skills
        employee.skills = request.POST.get('skills', '').strip()

        employee.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('employeedashboard')

    return render(request, 'edit_profile.html', {
        'user': employee
    })




def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_superuser:
            auth_login(request, user)

            # Mark this session as an authenticated Django admin
            request.session['is_admin'] = True

            # Prevent an old EmployeeProfile session from being reused
            request.session.pop('employee_id', None)
            request.session.pop('role', None)

            messages.success(
                request,
                'Admin login successful'
            )
            return redirect('admin_dashboard')

        messages.error(
            request,
            'Invalid username or password'
        )

    return render(request, 'admin_login.html')

    

def admin_dashboard(request):

    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    total_employees = EmployeeProfile.objects.filter(
        is_active=True
    ).count()

    total_clients = Client.objects.count()

    total_projects = Project.objects.count()

    open_bugs = Bug.objects.exclude(
        status__in=['Resolved', 'Closed']
    ).count()

    recent_projects = Project.objects.order_by('-id')[:4]

    in_progress_tasks = Task.objects.filter(
        status='In Progress'
    ).count()

    pending_review_tasks = Task.objects.filter(
        status='Pending Review'
    ).count()

    completed_tasks = Task.objects.filter(
        status='Completed'
    ).count()

    overdue_tasks = Task.objects.filter(
        deadline__lt=date.today()
    ).exclude(
        status='Completed'
    ).count()

    context = {
        'admin': request.user,
        'total_employees': total_employees,
        'total_clients': total_clients,
        'total_projects': total_projects,
        'open_bugs': open_bugs,
        'recent_projects': recent_projects,
        'in_progress_tasks': in_progress_tasks,
        'pending_review_tasks': pending_review_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
    }

    return render(request, 'admin_dashboard.html', context)


def admin_tasks(request):

    tasks = Task.objects.select_related(
        'project',
        'assigned_to'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')

    if search:
        tasks = tasks.filter(
            Q(task_title__icontains=search) |
            Q(project__project_name__icontains=search) |
            Q(assigned_to__name__icontains=search)
        )

    if status in dict(Task.STATUS_CHOICES):
        tasks = tasks.filter(status=status)

    if priority in dict(Task.PRIORITY_CHOICES):
        tasks = tasks.filter(priority=priority)

    context = {
        'tasks': tasks,
        'search': search,
        'selected_status': status,
        'selected_priority': priority,
        'statuses': Task.STATUS_CHOICES,
        'priorities': Task.PRIORITY_CHOICES,
        'admin': request.user,
    }

    return render(request, 'admin_tasks.html', context)



def employees(request):
    search = request.GET.get('search', '').strip()

    employees = EmployeeProfile.objects.all().order_by('id')

    if search:
        employees = employees.filter(
            name__icontains=search
        ) | employees.filter(
            username__icontains=search
        ) | employees.filter(
            role__icontains=search
        ) | employees.filter(
            email__icontains=search
        )

    context = {
        'employees': employees,
        'employee_count': employees.count(),
        'search': search,
        'admin':request.user
    }

    return render(request, 'employees.html', context)


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import EmployeeProfile


def edit_employee(request, id):
    employee = get_object_or_404(EmployeeProfile, id=id)

    if request.method == 'POST':
        employee.name = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.phone = request.POST.get('phone')
        employee.role = request.POST.get('role')
        employee.designation = request.POST.get('designation')

        # New employee details
        employee.employee_id = request.POST.get('employee_id') or None
        employee.department = request.POST.get('department', '')
        employee.skills = request.POST.get('skills', '')

        joining_date = request.POST.get('joining_date')
        if joining_date:
            employee.joining_date = joining_date

        employee.save()

        messages.success(request, 'Employee details updated successfully.')
        return redirect('employees')

    return render(request, 'edit_employee.html', {
        'employee': employee
    })


#  Activate/Deactivate user
def toggle_status(request, id):
    employee = EmployeeProfile.objects.get(id=id)

    employee.is_active = not employee.is_active
    employee.save()

    return redirect('employees')

def delete_employee(request, id):

    employee = EmployeeProfile.objects.get(id=id)

    employee.delete()

    return redirect('employees')




def developer_dashboard(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile,
        id=employee_id,
        is_active=True
    )

    if employee.role != 'developer':
        return redirect('login')

    # Projects assigned to this developer
    projects = Project.objects.filter(
        assigned_developers=employee
    ).distinct()

    # Tasks assigned to this developer
    tasks = Task.objects.filter(
        assigned_to=employee
    )

    # Bugs assigned to this developer
    bugs = Bug.objects.filter(
        assigned_to=employee
    )

    # Dashboard counts
    total_projects = projects.count()
    total_tasks = tasks.count()

    open_bugs = bugs.exclude(
        status__in=['Fixed', 'Closed', 'Resolved']
    ).count()

    completed_tasks = tasks.filter(
        status='Completed'
    ).count()

    # Leave requests for this developer
    leave_requests = LeaveRequest.objects.filter(
        employee=employee
    )

    # Calculate leave balance for the current calendar year
    total_annual_leaves = 12  # Change this to your company's annual allowance

    today = timezone.localdate()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)

    approved_leaves = leave_requests.filter(
        status='Approved',
        from_date__lte=year_end,
        to_date__gte=year_start
    )

    used_leaves = 0

    for leave in approved_leaves:
        # Count only the days that fall within the current year
        leave_start = max(leave.from_date, year_start)
        leave_end = min(leave.to_date, year_end)

        used_leaves += (leave_end - leave_start).days + 1

    leave_balance = max(
        0,
        total_annual_leaves - used_leaves
    )

    # Dashboard context
    context = {
        'employee': employee,
        'projects': projects,
        'tasks': tasks.order_by('deadline')[:5],
        'bugs': bugs.order_by('-created_at')[:5],
        'leave_requests': leave_requests,

        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'open_bugs': open_bugs,

        'leave_balance': leave_balance,
        'today': today,
    }

    return render(
        request,
        'developer_dashboard.html',
        context
    )


def developer_profile(request):
    if 'employee_id' not in request.session:
        return redirect('login')

    employee = EmployeeProfile.objects.filter(
        id=request.session['employee_id'],
        role='developer',
        is_active=True
    ).first()

    if not employee:
        request.session.flush()
        return redirect('login')

    return render(
        request,
        'developer_profile.html',
        {'employee': employee}
    )



def edit_developerprofile(request, id):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    # Allow developers to edit only their own profile
    if int(employee_id) != int(id):
        return redirect('developer_profile')

    try:
        employee = EmployeeProfile.objects.get(
            id=employee_id,
            role='developer',
            is_active=True
        )
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    if request.method == 'POST':
        employee.name = request.POST.get('name', '').strip()
        employee.email = request.POST.get('email', '').strip()
        employee.phone = request.POST.get('phone', '').strip()
        employee.skills = request.POST.get('skills', '').strip()

        employee.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('developer_profile')

    return render(
        request,
        'edit_developerprofile.html',
        {'employee': employee}
    )




def developer_applyleave(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        reason = request.POST.get('reason', '').strip()

        if not all([leave_type, from_date, to_date, reason]):
            messages.error(request, 'Please fill in all fields.')

        elif from_date > to_date:
            messages.error(
                request,
                'To date cannot be before From date.'
            )

        elif leave_type not in dict(LeaveRequest.LEAVE_TYPES):
            messages.error(request, 'Invalid leave type.')

        else:
            LeaveRequest.objects.create(
                employee=employee,
                leave_type=leave_type,
                from_date=from_date,
                to_date=to_date,
                reason=reason
            )

            messages.success(
                request,
                'Leave request submitted successfully!'
            )
            return redirect('developer_dashboard')

    return render(request, 'developer_applyleave.html', {
        'employee': employee
    })



def developer_leaves(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    leaves = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-applied_date')

    return render(request, 'developer_leaves.html', {
        'employee': employee,
        'leaves': leaves
    })




def manage_leave_requests(request):
    if not request.user.is_superuser:
        return redirect('admin_login')

    leaves = LeaveRequest.objects.select_related(
        'employee'
    ).order_by('-applied_date')

    return render(request, 'manage_leave_requests.html', {
        'leaves': leaves,'admin':request.user
    })


def update_leave_status(request, leave_id):

    if not request.user.is_superuser:
        return redirect('admin_login')

    leave = get_object_or_404(LeaveRequest, id=leave_id)

    new_status = request.POST.get('status')

    if leave.status != 'Pending':
        messages.warning(request, 'This request has already been reviewed.')

    elif new_status not in ['Approved', 'Rejected']:
        messages.error(request, 'Invalid leave status.')

    else:
        leave.status = new_status
        leave.reviewed_at = timezone.now()
        leave.save(update_fields=['status', 'reviewed_at'])

        messages.success(
            request,
            f'Leave request {new_status.lower()} successfully.'
        )

    return redirect('manage_leave_requests')




def developer_project(request):
    employee_id = request.session.get('employee_id')

    # Check whether the employee is logged in
    if not employee_id:
        return redirect('login')

    # Get the logged-in employee
    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    # Get only projects assigned to this employee
    projects = Project.objects.filter(
        assigned_developers=employee
    ).select_related('project_manager').distinct().order_by('deadline')

    return render(
        request,
        'developer_project.html',
        {
            'employee': employee,
            'projects': projects,
        }
    )



def manage_projects(request):
    if not request.user.is_superuser:
        return redirect('login')

    projects = Project.objects.all().order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')

    if search:
        projects = projects.filter(
            project_name__icontains=search
        )

    if status:
        projects = projects.filter(status=status)

    return render(request, 'manage_projects.html', {
        'admin': request.user,
        'projects': projects,
        'search': search,
        'selected_status': status,
        'status_choices': Project.STATUS_CHOICES,
    })



def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Project added successfully.')
            return redirect('manage_projects')
    else:
        form = ProjectForm()

    return render(request, 'project_form.html', {
        'form': form,
        'page_title': 'Add Project',
    })



def admin_edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('manage_projects')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'project_form.html', {
        'form': form,
        'page_title': 'Edit Project',
    })



def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')

    return redirect('manage_projects')




def developer_tasks(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    tasks = Task.objects.filter(
        assigned_to=employee
    ).select_related('project').order_by('deadline')

    return render(request, 'developer_tasks.html', {
        'employee': employee,
        'tasks': tasks,
    })



def report_bug(request):
    employee_id = request.session.get('employee_id')

    # Allow a logged-in Django superuser Admin
    if request.user.is_authenticated and request.user.is_superuser:
        employee = EmployeeProfile.objects.filter(
            role='super_admin',
            is_active=True
        ).first()

    # Otherwise, check the EmployeeProfile login
    elif employee_id:
        employee = get_object_or_404(
            EmployeeProfile,
            id=employee_id,
            is_active=True
        )

        # Developers and other unauthorized roles cannot report bugs
        if employee.role not in [
            'super_admin',
            'hr',
            'project_manager'
        ]:
            messages.error(
                request,
                'You do not have permission to assign bugs.'
            )
            return redirect('bug_list')

    else:
        return redirect('login')

    form = BugForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        bug = form.save(commit=False)
        bug.reported_by = employee
        bug.save()

        messages.success(
            request,
            'Bug reported and assigned successfully!'
        )
        return redirect('bug_list')

    return render(
        request,
        'report_bug.html',
        {'form': form, 'employee': employee,'admin':request.user}
    )

 
def project_manager_report_bug(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile,
        id=employee_id,
        is_active=True
    )
    
    # Allow only Project Managers
    if employee.role != 'project_manager':
        messages.error(
            request,
            'You do not have permission to report bugs.'
        )
        return redirect('login')

    form = BugForm(request.POST or None)
   

    form.fields['project'].queryset = Project.objects.filter(
    project_manager=employee
    )
    
    if request.method == 'POST' and form.is_valid():
        bug = form.save(commit=False)
        bug.reported_by = employee
        bug.save()

        messages.success(
            request,
            'Bug reported successfully!'
        )

        return redirect('project_manager_bug_list')

    return render(
        request,
        'project_manager_report_bug.html',
        {
            'form': form,
            'employee': employee
        }
    )

def bug_list(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile,
        id=employee_id,
        is_active=True
    )

    employee_name = employee.name
    employee_role = employee.get_role_display()

    if employee.role == 'developer':
        bugs = Bug.objects.filter(assigned_to=employee)

    elif employee.role in ['super_admin', 'hr', 'project_manager']:
        bugs = Bug.objects.all()

    else:
        bugs = Bug.objects.filter(reported_by=employee)

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        bugs = bugs.filter(title__icontains=search)

    if status in dict(Bug.STATUS_CHOICES):
        bugs = bugs.filter(status=status)

    bugs = bugs.order_by('-created_at')

    return render(request, 'bug_list.html', {
        'bugs': bugs,
        'statuses': Bug.STATUS_CHOICES,
        'search': search,
        'selected_status': status,
        'employee': employee,
        'employee_name': employee_name,
        'employee_role': employee_role,
        'bug_count': bugs.count(),
    })



def project_manager_bug_list(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    manager = get_object_or_404(
        EmployeeProfile,
        id=employee_id,
        role='project_manager',
        is_active=True
    )

    bugs = Bug.objects.all().order_by('-id')

    return render(
        request,
        'project_manager_bug_list.html',
        {
            'manager': manager,
            'bugs': bugs,
        }
    )


def update_bug_status(request, bug_id):
    employee_id = request.session.get('employee_id')

    # Check Django superuser login
    is_django_admin = (
        request.user.is_authenticated
        and request.user.is_superuser
    )

    employee = None

    if is_django_admin:
        allowed = True

    elif employee_id:
        employee = get_object_or_404(
            EmployeeProfile,
            id=employee_id,
            is_active=True
        )

        bug = get_object_or_404(Bug, id=bug_id)

        # Developers can update only bugs assigned to them
        if employee.role == 'developer':
            allowed = bug.assigned_to_id == employee.id

        # Admin, HR and Project Manager can update bugs
        elif employee.role in [
            'super_admin', 'hr', 'project_manager'
        ]:
            allowed = True

        else:
            allowed = False

    else:
        return redirect('login')

    bug = get_object_or_404(Bug, id=bug_id)

    if not allowed:
        return HttpResponseForbidden(
            'You do not have permission to update this bug.'
        )

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Bug.STATUS_CHOICES):
            bug.status = new_status
            bug.save(update_fields=['status'])

            return redirect('bug_list')

    return render(
        request,
        'update_bug_status.html',
        {
            'bug': bug,
            'statuses': Bug.STATUS_CHOICES,
            'employee': employee,
        }
    )


def admin_reports(request):

    today = date.today()

    # Employee reports
    total_employees = EmployeeProfile.objects.count()

    active_employees = EmployeeProfile.objects.filter(
        is_active=True
    ).count()

    inactive_employees = EmployeeProfile.objects.filter(
        is_active=False
    ).count()

    # Client report
    total_clients = Client.objects.count()

    # Project reports
    total_projects = Project.objects.count()

    completed_projects = Project.objects.filter(
        status='Completed'
    ).count()

    ongoing_projects = Project.objects.filter(
        status='In Progress'
    ).count()

    # Task reports
    total_tasks = Task.objects.count()

    completed_tasks = Task.objects.filter(
        status='Completed'
    ).count()

    in_progress_tasks = Task.objects.filter(
        status='In Progress'
    ).count()

    pending_tasks = Task.objects.filter(
        status='To Do'
    ).count()

    blocked_tasks = Task.objects.filter(
        status='Blocked'
    ).count()

    overdue_tasks = Task.objects.filter(
        deadline__lt=today
    ).exclude(
        status='Completed'
    ).count()

    context = {
        'admin': request.user,

        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,

        'total_clients': total_clients,

        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,

        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'blocked_tasks': blocked_tasks,
        'overdue_tasks': overdue_tasks,
    }

    return render(request, 'admin_reports.html', context)
  
def admin_bug_list(request):
    is_django_admin = (
        request.user.is_authenticated
        and request.user.is_superuser
    )

    employee_id = request.session.get('employee_id')

    if not is_django_admin:
        if not employee_id:
            return redirect('admin_login')

        employee = get_object_or_404(
            EmployeeProfile,
            id=employee_id,
            is_active=True
        )

        if employee.role != 'super_admin':
            return render(
                request,
                'access_denied.html',
                status=403
            )

    bugs = Bug.objects.select_related(
        'assigned_to',
        'reported_by'
    ).order_by('-created_at')

    total_bugs = Bug.objects.count()

    return render(request, 'admin_bug_list.html', {
        'bugs': bugs,
        'total_bugs': total_bugs,
    })



def hr_dashboard(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile,
        id=employee_id,
        is_active=True
    )

    if employee.role != 'hr':
        return redirect('login')

    today = timezone.localdate()

    # Total active employees
    total_employees = EmployeeProfile.objects.filter(
        is_active=True
    ).count()

    # Pending leave requests
    pending_leaves = LeaveRequest.objects.filter(
        status='Pending'
    ).count()

    # Employees registered during the current month
    new_joiners = EmployeeProfile.objects.filter(
        is_active=True,
        created_at__year=today.year,
        created_at__month=today.month
    ).count()

    # Inactive employees
    inactive_employees = EmployeeProfile.objects.filter(
        is_active=False
    ).count()

    context = {
        'employee': employee,
        'today': today,
        'total_employees': total_employees,
        'pending_leaves': pending_leaves,
        'new_joiners': new_joiners,
        'inactive_employees': inactive_employees,
    }

    return render(request, 'hr_dashboard.html', context)



def hr_profile(request):
    if 'employee_id' not in request.session:
        return redirect('login')

    employee = EmployeeProfile.objects.filter(
        id=request.session['employee_id'],
        role='hr',
        is_active=True
    ).first()

    if not employee:
        request.session.flush()
        return redirect('login')

    return render(
        request,
        'hr_profile.html',
        {'employee': employee}
    )



def edit_hrprofile(request, id):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    # Allow HR to edit only their own profile
    if int(employee_id) != int(id):
        return redirect('hr_profile')

    try:
        employee = EmployeeProfile.objects.get(
            id=employee_id,
            role='hr',
            is_active=True
        )
    except EmployeeProfile.DoesNotExist:
        request.session.flush()
        return redirect('login')

    if request.method == 'POST':
        employee.name = request.POST.get('name', '').strip()
        employee.email = request.POST.get('email', '').strip()
        employee.phone = request.POST.get('phone', '').strip()
        employee.skills = request.POST.get('skills', '').strip()

        employee.save()

        messages.success(
            request,
            'Profile updated successfully.'
        )

        return redirect('hr_profile')

    return render(
        request,
        'edit_hrprofile.html',
        {'employee': employee}
    )



def hr_leave_requests(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile,
        id=employee_id
    )

    if employee.role != 'hr':
        return redirect('hr_profile')

    leaves = LeaveRequest.objects.select_related(
        'employee', 'reviewed_by'
    ).order_by('-applied_date')

    return render(request, 'hr_leave_requests.html', {
        'employee': employee,
        'leave_requests': leaves,
    })


def hr_update_leave_status(request, leave_id):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile,
        id=employee_id
    )

    # Prevent HR from approving their own leave request
    leave = get_object_or_404(
        LeaveRequest,
        id=leave_id
    )

    if leave.employee_id == employee.id:
        messages.error(
            request,
            'You cannot approve or reject your own leave request.'
        )
        return redirect('hr_leave_requests')

    new_status = request.POST.get('status')

    if leave.status != 'Pending':
        messages.warning(
            request,
            'This request has already been reviewed.'
        )

    elif new_status not in ['Approved', 'Rejected']:
        messages.error(request, 'Invalid leave status.')

    else:
        leave.status = new_status
        leave.reviewed_by = employee
        leave.reviewed_at = timezone.now()

        leave.save(update_fields=[
            'status',
            'reviewed_by',
            'reviewed_at'
        ])

    return redirect('hr_leave_requests')

def hr_apply_leave(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(EmployeeProfile, id=employee_id)

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        reason = request.POST.get('reason', '').strip()

        allowed_types = [
            'Casual Leave',
            'Sick Leave',
            'Annual Leave',
            'Other'
        ]

        # Check the submitted details
        if leave_type not in allowed_types or not from_date or not to_date or not reason:
            return render(request, 'hr_apply_leave.html', {
                'employee': employee,
                'error': 'Please fill in all the required fields.'
            })

        try:
            start_date = datetime.date.fromisoformat(from_date)
            end_date = datetime.date.fromisoformat(to_date)
        except ValueError:
            return render(request, 'hr_apply_leave.html', {
                'employee': employee,
                'error': 'Please enter valid dates.'
            })

        if end_date < start_date:
            return render(request, 'hr_apply_leave.html', {
                'employee': employee,
                'error': 'To Date cannot be earlier than From Date.'
            })

        # Save the HR employee's leave request
        LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            from_date=start_date,
            to_date=end_date,
            reason=reason
        )

        return redirect('hr_apply_leave')

    return render(request, 'hr_apply_leave.html', {
        'employee': employee
    })


def hr_my_leave_requests(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile,
        id=employee_id
    )

    leave_requests = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-applied_date')

    return render(request, 'hr_leave_requests.html', {
        'employee': employee,
        'leave_requests': leave_requests
    })




def hr_employee_report(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    employee = get_object_or_404(
        EmployeeProfile, id=employee_id
    )

    if employee.role != 'hr':
        return redirect('login')

    # Summary counts
    total_employees = EmployeeProfile.objects.count()
    active_employees = EmployeeProfile.objects.filter(
        is_active=True
    ).count()
    inactive_employees = EmployeeProfile.objects.filter(
        is_active=False
    ).count()

    # Employee list
    employees = EmployeeProfile.objects.all().order_by('name')

    # Search
    search_query = request.GET.get('search', '').strip()

    if search_query:
        employees = employees.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(role__icontains=search_query)
        )

    context = {
        'employee': employee,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'employees': employees,
        'search_query': search_query,
    }

    return render(
        request,
        'hr_employee_report.html',
        context
    )


def client_list(request):
    query = request.GET.get('q', '')

    clients = Client.objects.all().order_by('-created_at')

    if query:
        clients = clients.filter(
            Q(client_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'admin': request.user,
        'clients': clients,
        'query': query,
        'total_clients': Client.objects.count(),
    }

    return render(request, 'client_list.html', context)



def add_client(request):

    if request.method == 'POST':

        client_name = request.POST.get('client_name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([
            client_name, company_name,
            email, phone, address
        ]):
            messages.error(request, 'Please fill in all fields.')

        elif Client.objects.filter(email__iexact=email).exists():
            messages.error(request, 'This email already exists.')

        else:
            Client.objects.create(
                client_name=client_name,
                company_name=company_name,
                email=email,
                phone=phone,
                address=address
            )

            messages.success(request, 'Client added successfully.')
            return redirect('client_list')

    return render(request, 'add_client.html')


def edit_client(request, id):

    client = get_object_or_404(Client, id=id)

    if request.method == 'POST':

        client_name = request.POST.get('client_name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([
            client_name, company_name,
            email, phone, address
        ]):
            messages.error(request, 'Please fill in all fields.')

        elif Client.objects.filter(
            email__iexact=email
        ).exclude(id=client.id).exists():
            messages.error(request, 'This email is already in use.')

        else:
            client.client_name = client_name
            client.company_name = company_name
            client.email = email
            client.phone = phone
            client.address = address

            client.save()

            messages.success(request, 'Client updated successfully.')
            return redirect('client_list')

    return render(
        request,
        'edit_client.html',
        {'client': client}
    )



def delete_client(request, id):

    client = get_object_or_404(Client, id=id)

    if request.method == 'POST':
        try:
            client.delete()
            messages.success(request, 'Client deleted successfully.')
        except Exception:
            messages.error(
                request,
                'This client cannot be deleted because related records exist.'
            )

    return redirect('client_list')


def get_project_manager(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return None

    try:
        employee = EmployeeProfile.objects.get(
            id=employee_id,
            is_active=True,
            role='project_manager'
        )
        return employee
    except EmployeeProfile.DoesNotExist:
        return None


def project_manager_dashboard(request):
    manager = get_project_manager(request)

    if manager is None:
        return redirect('login')

    projects = Project.objects.filter(
        project_manager=manager
    )

    tasks = Task.objects.filter(
        project__in=projects
    )
    today = timezone.localdate()
    context = {
        'manager': manager,
        'today': today,
        'total_projects': projects.count(),
        'active_projects': projects.filter(
            status='In Progress'
        ).count(),
        'completed_projects': projects.filter(
            status='Completed'
        ).count(),
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.exclude(
            status='Completed'
        ).count(),
        'recent_projects': projects.order_by(
            '-created_at'
        )[:5],
    }

    return render(
        request,
        'project_manager_dashboard.html',
        context
    )


def my_projects(request):
    manager = get_project_manager(request)

    if manager is None:
        return redirect('login')

    projects = Project.objects.filter(
        project_manager=manager
    ).order_by('-created_at')

    context = {
        'manager': manager,
        'manager_name': manager.name,
        'manager_role': manager.get_role_display(),
        'projects': projects,
    }

    return render(request, 'my_projects.html', context)

def create_project(request):
    manager = get_project_manager(request)

    if manager is None:
        return redirect('login')

    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.project_manager = manager
            project.save()
            form.save_m2m()

            return redirect('my_projects')
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'manager': manager,
        'manager_name': manager.name,
        'manager_role': manager.get_role_display(),
    }

    return render(request, 'create_project.html', context)


def edit_project(request, project_id):
    manager = get_project_manager(request)

    if manager is None:
        return redirect('login')

    project = get_object_or_404(
        Project,
        id=project_id,
        project_manager=manager
    )

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect('my_projects')
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'manager': manager,
        'manager_name': manager.name,
        'manager_role': manager.get_role_display(),
    }

    return render(request, 'edit_project.html', context)



def manage_tasks(request):

    # Get the logged-in employee ID
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    # Retrieve the logged-in employee
    manager = EmployeeProfile.objects.filter(
        id=employee_id,
        is_active=True
    ).first()

    if not manager:
        request.session.flush()
        return redirect('login')

    # Retrieve tasks
    tasks = Task.objects.select_related(
        'project',
        'assigned_to'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')

    if search:
        tasks = tasks.filter(
            Q(task_title__icontains=search) |
            Q(project__project_name__icontains=search) |
            Q(assigned_to__name__icontains=search)
        )

    if status in dict(Task.STATUS_CHOICES):
        tasks = tasks.filter(status=status)

    if priority in dict(Task.PRIORITY_CHOICES):
        tasks = tasks.filter(priority=priority)

    context = {
        'manager': manager,
        'manager_name': manager.name,
        'manager_role': manager.get_role_display(),

        'tasks': tasks,
        'projects': Project.objects.all().order_by('project_name'),
        'developers': EmployeeProfile.objects.filter(
            role='developer',
            is_active=True
        ).order_by('name'),
        'priorities': Task.PRIORITY_CHOICES,
        'statuses': Task.STATUS_CHOICES,
        'search': search,
        'selected_status': status,
        'selected_priority': priority,
    }

    return render(request, 'manage_tasks.html', context)



def add_task(request):
    if request.method != 'POST':
        return redirect('manage_tasks')

    task_title = request.POST.get('task_title', '').strip()
    description = request.POST.get('description', '').strip()
    project_id = request.POST.get('project', '')
    developer_id = request.POST.get('assigned_to', '')
    priority = request.POST.get('priority', '')
    deadline = request.POST.get('deadline', '')
    status = request.POST.get('status', '')

    if not all([
        task_title, description, project_id,
        developer_id, priority, deadline, status
    ]):
        messages.error(request, 'Please fill in all fields.')
        return redirect('manage_tasks')

    if priority not in dict(Task.PRIORITY_CHOICES):
        messages.error(request, 'Invalid priority.')
        return redirect('manage_tasks')

    if status not in dict(Task.STATUS_CHOICES):
        messages.error(request, 'Invalid task status.')
        return redirect('manage_tasks')

    try:
        deadline_date = datetime.date.fromisoformat(deadline)
    except ValueError:
        messages.error(request, 'Enter a valid deadline.')
        return redirect('manage_tasks')

    project = get_object_or_404(Project, id=project_id)

    developer = get_object_or_404(
        EmployeeProfile,
        id=developer_id,
        role='developer',
        is_active=True
    )

    Task.objects.create(
        task_title=task_title,
        description=description,
        project=project,
        assigned_to=developer,
        priority=priority,
        deadline=deadline_date,
        status=status
    )

    messages.success(request, 'Task added successfully.')
    return redirect('manage_tasks')




def edit_task(request, task_id):

    # Get logged-in employee
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('login')

    manager = get_object_or_404(
        EmployeeProfile,
        id=employee_id,
        is_active=True
    )

    # Retrieve the task to edit
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':

        task_title = request.POST.get('task_title', '').strip()
        description = request.POST.get('description', '').strip()
        project_id = request.POST.get('project', '')
        developer_id = request.POST.get('assigned_to', '')
        priority = request.POST.get('priority', '')
        deadline = request.POST.get('deadline', '')
        status = request.POST.get('status', '')

        if not all([
            task_title, description, project_id,
            developer_id, priority, deadline, status
        ]):
            messages.error(request, 'Please fill in all fields.')

        elif priority not in dict(Task.PRIORITY_CHOICES):
            messages.error(request, 'Invalid priority.')

        elif status not in dict(Task.STATUS_CHOICES):
            messages.error(request, 'Invalid task status.')

        else:
            try:
                deadline_date = datetime.date.fromisoformat(deadline)
            except ValueError:
                messages.error(request, 'Enter a valid deadline.')
            else:
                project = get_object_or_404(Project, id=project_id)

                developer = get_object_or_404(
                    EmployeeProfile,
                    id=developer_id,
                    role='developer',
                    is_active=True
                )

                task.task_title = task_title
                task.description = description
                task.project = project
                task.assigned_to = developer
                task.priority = priority
                task.deadline = deadline_date
                task.status = status
                task.save()

                messages.success(
                    request,
                    'Task updated successfully.'
                )
                return redirect('manage_tasks')

    context = {
        'manager': manager,
        'manager_name': manager.name,
        'manager_role': manager.get_role_display(),

        'task': task,
        'projects': Project.objects.all().order_by('project_name'),
        'developers': EmployeeProfile.objects.filter(
            role='developer',
            is_active=True
        ).order_by('name'),
        'priorities': Task.PRIORITY_CHOICES,
        'statuses': Task.STATUS_CHOICES,
    }

    return render(request, 'edit_task.html', context)


def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        messages.success(request, 'Task deleted successfully.')

    return redirect('manage_tasks')



def project_manager_profile(request):
    if 'employee_id' not in request.session:
        return redirect('login')

    manager = get_object_or_404(
        EmployeeProfile,
        id=request.session['employee_id'],
        role='project_manager',
        is_active=True
    )

    return render(
        request,
        'project_manager_profile.html',
        {'manager': manager}
    )



def project_manager_edit_profile(request):
    if 'employee_id' not in request.session:
        return redirect('login')

    manager = get_object_or_404(
        EmployeeProfile,
        id=request.session['employee_id'],
        role='project_manager',
        is_active=True
    )

    if request.method == 'POST':
        manager.name = request.POST.get('name', '').strip()
        manager.email = request.POST.get('email', '').strip()
        manager.phone = request.POST.get('phone', '').strip()
        manager.skills = request.POST.get('skills', '').strip()

        manager.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('project_manager_profile')

    return render(
        request,
        'project_manager_edit_profile.html',
        {'manager': manager}
    )




def project_manager_apply_leave(request):
    if 'employee_id' not in request.session:
        return redirect('login')

    manager = get_object_or_404(
        EmployeeProfile,
        id=request.session['employee_id'],
        role='project_manager',
        is_active=True
    )

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        reason = request.POST.get('reason', '').strip()

        if not all([leave_type, from_date, to_date, reason]):
            messages.error(request, 'Please fill in all fields.')

        elif from_date < timezone.localdate().isoformat():
            messages.error(request, 'The start date cannot be in the past.')

        elif to_date < from_date:
            messages.error(
                request,
                'The end date cannot be before the start date.'
            )

        else:
            LeaveRequest.objects.create(
                employee=manager,
                leave_type=leave_type,
                from_date=from_date,
                to_date=to_date,
                reason=reason,
                status='Pending'
            )

            messages.success(
                request,
                'Leave request submitted successfully.'
            )
            return redirect('project_manager_leaves')

    return render(
        request,
        'project_manager_apply_leave.html',
        {'manager': manager}
    )



def project_manager_leaves(request):
    if 'employee_id' not in request.session:
        return redirect('login')

    manager = get_object_or_404(
        EmployeeProfile,
        id=request.session['employee_id'],
        role='project_manager',
        is_active=True
    )

    leaves = LeaveRequest.objects.filter(
        employee=manager
    ).order_by('-applied_date')

    return render(
        request,
        'project_manager_leaves.html',
        {
            'manager': manager,
            'leaves': leaves
        }
    )



