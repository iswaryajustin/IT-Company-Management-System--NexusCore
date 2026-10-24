from django import forms
from .models import Project,Bug, EmployeeProfile,Client



class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project

        fields = [
            'project_name',
            'client',
            'description',
            'project_manager',  
            'assigned_developers',
            'start_date',
            'deadline',
            'status',
            'progress',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'assigned_developers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['client'].queryset = Client.objects.order_by(
            'company_name'
        )

        # Show only active Project Managers
        self.fields['project_manager'].queryset = (
            EmployeeProfile.objects.filter(
                role='project_manager',
                is_active=True
            ).order_by('name')
        )

        self.fields['assigned_developers'].queryset = (
            EmployeeProfile.objects.filter(
                role='developer',
                is_active=True
            ).order_by('name')
        )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        deadline = cleaned_data.get('deadline')
        progress = cleaned_data.get('progress')

        if start_date and deadline and deadline < start_date:
            self.add_error(
                'deadline',
                'Deadline cannot be before the start date.'
            )

        if progress is not None and not 0 <= progress <= 100:
            self.add_error(
                'progress',
                'Progress must be between 0 and 100.'
            )

        return cleaned_data



class BugForm(forms.ModelForm):

    class Meta:
        model = Bug
        fields = [
            'project',
            'title',
            'description',
            'priority',
            'assigned_to',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),
            'priority': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'assigned_to': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = (
            EmployeeProfile.objects.filter(
                role='developer',
                is_active=True
            )
        )


