# IT Company Management System - NexusCore

A Django-based web application to manage the work of an IT company.

## Features
- Role-based access for four types of users:
  - Developer
  - Project Manager
  - Admin
  - HR
- Each user sees only the pages that belong to their role
- Login and logout system
- Responsive design using Bootstrap

## Technologies Used
- Python, Django
- HTML, CSS, JavaScript
- Bootstrap
- MySQL (database)

## How to Run
1. Clone the repository:
   git clone https://github.com/iswaryajustin/IT-Company-Management-System--NexusCore.git
2. Go into the project folder:
   cd IT-Company-Management-System--NexusCore
3. Install the requirements:
   pip install django mysqlclient
4. Create a MySQL database (for example, nexuscore_db).
5. Open settings.py (inside the IT_company_management folder) and update the DATABASES section with your MySQL database name, username, and password.
6. Run the migrations:
   python manage.py migrate
7. Start the server:
   python manage.py runserver
8. Open http://127.0.0.1:8000/ in your browser.

## Author
Iswarya
