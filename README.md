# Parasparam — HREMS (Human Resources & Employee Management System)

#### Video Demo: <URL HERE>

## Description

Parasparam is an all-in-one Human Resources & Employee Management System
(HREMS) developed as my CS50x Final Project. The application is designed to
centralize several common HR operations into one web-based system while
providing different interfaces according to the user's role.

There are two primary roles in Parasparam: **Admin** and **Employee**.
Administrators are responsible for managing employees and organization-level
operations, while employees can access and manage information relevant to
themselves. Although both roles use the same application and database, their
interfaces and permissions are different.

The name **Parasparam** is derived from Sanskrit and represents the idea of
being "mutual" or "with each other". I chose this name because the application
is intended to provide a common platform connecting an organization and its
employees.

## Features

### 1. Authentication

**Implementation Details:**

- Employee Login: `templates/login.html`
- Admin Login: `templates/admin_login.html`
- Employee Registration: `templates/register.html`
- Admin Registration: `templates/register_admin.html`
- Employee Password Reset: `templates/user_reset.html`
- Admin Password Reset: `templates/admin_reset.html`

Parasparam provides separate authentication flows for administrators and
employees. Users must provide their respective admin ID or employee ID along
with a password to access their account.

The first administrator must be manually added to the database. After that,
administrators can register additional administrators and employees through
the application's interfaces. Employees initially receive their password
from an administrator and can subsequently reset it through the password
reset feature.

Passwords are not stored as plaintext. They are hashed using Werkzeug's
password-hashing functionality before being stored in the database. This
means that the original passwords are not directly readable from the
database.

### 2. Role-Specific Home Pages

**Implementation Details:**

- Admin interface: `templates/admin_home.html`
- Employee interface: `templates/employee_home.html`
- Employee homepage: `templates/employee_homepage.html`

The application provides separate home-page interfaces for administrators
and employees. This was done because the two roles have fundamentally
different responsibilities.

The employee homepage provides quick access to information such as project
summaries, notifications, and leave information. Notifications can inform
employees when a leave request has been approved or rejected or when a new
project has been assigned to them.

### 3. Salary Management

**Implementation Details:**

- Employee side: `templates/employee_salary_page.html`
- Admin side: `templates/employee_salary_page_admin.html`

The salary feature provides employees with a detailed breakdown of their
monthly salary instead of displaying only a final amount. The calculations
are based on the CTC salary entered by the administrator.

The salary is divided into the following components:

- Basic Salary = 60% of CTC Salary
- HRA = 40% of Basic Salary
- Other = CTC Salary - Basic - HRA - 1800
- PF = 1800
- Employee PF Share = -1800
- Earnings = CTC Salary - 1800
- Professional Tax = 200
- Take Home = Earnings - Professional Tax

Administrators can view the detailed salary breakdown of individual
employees as well as the total monthly amount that the organization has to
spend on salaries.

I chose to display the salary as a component-wise breakdown because it makes
the calculation more transparent to employees and provides administrators
with more useful payroll information.

### 4. Project Management

**Implementation Details:**

- Employee side: `templates/employee_project_page.html`
- Admin side: `templates/project_page_admin.html`

Administrators can create projects by entering a project name and
description and assign them to employees. A newly assigned project initially
has the stage "Not initiated". The employee can later update the project
stage and add relevant remarks.

An employee can be assigned multiple projects, while each project is
currently assigned to one employee through the application's interface.
This design keeps project assignment straightforward while still allowing
an employee's project page to display multiple projects.

### 5. Attendance Management

**Implementation Details:**

- Employee attendance page: `templates/employee_employee_page.html`
- Attendance administration is handled through the relevant admin
  interface and database operations in `app.py`.

Attendance data is imported by an administrator from a CSV file. The
attendance data contains information such as:

- Date
- Week Day
- Day Type
- In Time
- Out Time
- Total Working Hours
- Status

The employee can then view their attendance log along with a summary
containing total working days, full days attended, late days, half-days,
total leaves, and total attendance.

The administrator can view employee-wise required working hours, total hours
worked, and daily attendance information.

I chose CSV import for attendance because attendance records are commonly
available in tabular formats and importing them allows multiple records to
be added without manually entering every attendance entry.

### 6. Leave Management

Employees can submit leave requests by providing the required information,
including the reason and requested dates. Administrators can review these
requests and either approve or reject them.

The employee can view the status of previously submitted requests. When an
administrator approves or rejects a leave request, the employee is also
notified through the notification system.

This creates a complete workflow:

**Employee submits leave → Admin reviews → Leave is approved/rejected →
Employee receives notification.**

I chose this workflow so that the employee does not have to repeatedly check
whether a request has changed status.

### 7. Employee Management

**Implementation Details:**

- Admin side: `templates/employees_page_adm.html`
- Employee side: `templates/employees_page_user.html`

The employee-side interface displays employee information such as
designation and joining date. The administrator has additional privileges
and can edit employee information or deregister an employee.

This separation ensures that employees can view relevant organizational
information without receiving administrative permissions.

### 8. Notifications

The notification system provides employees with updates about important
events in the application. For example, an employee can receive a
notification when a leave request is approved or rejected or when a project
is assigned to them.

Notifications are particularly useful because they connect actions
performed by an administrator with the employee who is affected by that
action.

## Files

### `app.py`

`app.py` is the main Flask application. It contains the application's
routes, authentication and session handling, database queries, form
processing, and backend logic for the different Admin and Employee
features.

### `helpers.py`

`helpers.py` contains helper functions used by the application, including
functions for authentication and protecting routes that require a logged-in
user or administrator.

### `hrems.db`

`hrems.db` is the SQLite database used to store persistent application data,
including administrators, employees, attendance records, leave requests,
projects, salary information, and notifications.

### `templates/`

The `templates` directory contains the HTML and Jinja templates used to
render the application's pages. Separate templates are provided for
administrator and employee interfaces.

### `static/`

The `static` directory contains the application's CSS, JavaScript, images,
and other front-end resources.

### `requirements.txt`

`requirements.txt` contains the Python packages required to install and run
the application.

## Design Choices

One of the most important design decisions in Parasparam was separating the
Admin and Employee interfaces. Administrators need organization-wide
control, while employees primarily need access to their own information.
Giving both roles the same interface would therefore provide unnecessary
permissions and make the application harder to use.

I chose Flask for the backend because it provides enough flexibility for a
multi-feature web application while allowing me to understand how routes,
sessions, templates, forms, and database queries interact.

I chose SQLite as the database because it is lightweight and well suited to
the scale of this project while still providing the relational database
features required by the application.

For leave management, I chose to combine status tracking with
notifications. The leave history provides a persistent record of the
request, while a notification provides immediate feedback when an
administrator makes a decision.

For project management, I chose a simple one-employee-per-project
assignment through the current interface. At the same time, an employee can
have multiple projects, which allows the employee dashboard to represent
different responsibilities without making project assignment unnecessarily
complex.

# Thank You! This was Parasparam...