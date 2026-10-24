from django.db import models
from django.utils import timezone


from django.db import models
from django.utils import timezone


class EmployeeProfile(models.Model):

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=10, default='Unknown')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=10)
    confirmPassword = models.CharField(max_length=10)

    department = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    joining_date = models.DateField(
        default=timezone.localdate
    )

    skills = models.TextField(
        blank=True,
        default=''
    )

    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('hr', 'HR'),
        ('project_manager', 'Project Manager'),
        ('developer', 'Developer'),
        ('employee', 'Employee'),
    ]

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='employee'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

   

class LeaveRequest(models.Model):

    LEAVE_TYPES = [
        ('Casual Leave', 'Casual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Annual Leave', 'Annual Leave'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )

    leave_type = models.CharField(
        max_length=30,
        choices=LEAVE_TYPES
    )

    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()

    applied_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    reviewed_by = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leave_requests'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type}"


class Client(models.Model):

    client_name = models.CharField(max_length=150)

    company_name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client_name




class Project(models.Model):
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('In Progress', 'In Progress'),
        ('Testing', 'Testing'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    project_name = models.CharField(max_length=150)


    client = models.ForeignKey(
    Client,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)

    
    description = models.TextField()
    
    project_manager = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects'
    )

    assigned_developers = models.ManyToManyField(
        EmployeeProfile,
        related_name='assigned_projects',
        blank=True
    )

    start_date = models.DateField()
    deadline = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Planning'
    )

    progress = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name




class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Blocked', 'Blocked'),
    ]

    task_title = models.CharField(max_length=150)
    description = models.TextField()

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    assigned_to = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    deadline = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='To Do'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_title



class Bug(models.Model):

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Open'
    )

    assigned_to = models.ForeignKey(
        'EmployeeProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bugs'
    )

    reported_by = models.ForeignKey(
        'EmployeeProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_bugs'
    )
    project = models.ForeignKey(
    'Project',
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
