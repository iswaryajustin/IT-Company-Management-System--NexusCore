from django.contrib import admin
from .models import EmployeeProfile,LeaveRequest, Project, Bug, Client

admin.site.register(EmployeeProfile)

admin.site.register(LeaveRequest)

@admin.register(Project)

class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'project_name',
        'project_manager',
        'start_date',
        'deadline',
        'status',
        'progress',
    )

    list_filter = ('status', 'start_date')
    search_fields = ('project_name', 'description')
    filter_horizontal = ('assigned_developers',)



@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'priority',
        'status',
        'assigned_to',
        'reported_by',
        'created_at',
    )

    list_filter = ('priority', 'status')
    search_fields = ('title', 'description')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    list_display = (
        'client_name',
        'company_name',
        'email',
        'phone',
        'created_at',
    )

    search_fields = (
        'client_name',
        'company_name',
        'email',
    )