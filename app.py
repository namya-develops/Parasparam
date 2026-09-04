import os
import requests
from cs50 import SQL
from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import admin_login_required, employee_login_required
import csv
app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "parasparam-cs50x-final-project-secret-key")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///hrems.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/user/reset_password", methods = ["GET", "POST"])
def user_reset():
    if request.method == "GET":
        return render_template("user_reset.html")
    else:
        id = request.form.get("emp_id")
        password = request.form.get("emp_password")
        confirm_password = request.form.get("emp_password_confirm")
        
        if password != confirm_password:
            return render_template("apology.html", Message = "Both passwords do not match")
        elif not id or not password or not confirm_password:
            return render_template("apology.html", Message = "Incomplete Details")
        else:
            hashed_password = generate_password_hash(password)
            db.execute("UPDATE emp_data1 SET hash = ? WHERE emp_id = ?", hashed_password, id)
        
            return redirect("/user/login")

@app.route("/user/home")
@employee_login_required
def user_home():
    rows = db.execute(
        "SELECT * FROM emp_data1 WHERE emp_id = ?", session["user_id"]
    )
    user_emp_name = rows[0]['emp_name']
    project_data = db.execute("SELECT COUNT(*) AS pd FROM projects WHERE emp_id = ?", session['user_id']);
    completed_projects = db.execute("SELECT COUNT(*) AS cp FROM projects WHERE emp_id = ? AND status = ?", session['user_id'], 'completed')
    planning_stage_projects = db.execute("SELECT COUNT(*) AS psp FROM projects WHERE emp_id = ? AND status = ?", session['user_id'], 'Planning')
    inprogress_projects = db.execute("SELECT COUNT(*) AS ip FROM projects WHERE emp_id = ? AND status = ?", session['user_id'], 'in-progress')

    applied_leaves = db.execute("SELECT COUNT(*) AS app_l FROM leaves WHERE emp_id = ?", session["user_id"])
    accepted_leaves = db.execute("SELECT COUNT(*) AS acc_l FROM leaves WHERE emp_id = ? AND leave_status = ?", session["user_id"], 'Accepted')
    rejected_leaves = db.execute("SELECT COUNT(*) AS rl FROM leaves WHERE emp_id = ? AND leave_status = ?", session["user_id"], 'Rejected')
    pending_leaves = db.execute("SELECT COUNT(*)  AS pl FROM leaves WHERE emp_id = ? AND leave_status = ?", session["user_id"], 'Pending')

    notifications = db.execute("""
SELECT *
FROM notifications
WHERE emp_id = ?
ORDER BY notification_id DESC
LIMIT 3
""", session["user_id"])
    
    return render_template("employee_homepage.html" , user_emp_name = user_emp_name, project_data = project_data,
                           completed_projects = completed_projects, planning_stage_projects = planning_stage_projects, 
                           inprogress_projects = inprogress_projects, applied_leaves = applied_leaves, accepted_leaves = accepted_leaves,
                           rejected_leaves = rejected_leaves, pending_leaves = pending_leaves, notifications = notifications)


@app.route("/user/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted

        emp_id = request.form.get("emp_id")
        password = request.form.get("emp_password")
        if not request.form.get("emp_id"):
            return render_template("apology.html", Message = "Username is missing")

        # Ensure password was submitted
        elif not request.form.get("emp_password"):
            return render_template("apology.html", Message = "Password is missing")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM emp_data1 WHERE emp_id = ?", request.form.get("emp_id")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("emp_password")
        ):
            return render_template("apology.html", Message = "invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["emp_id"]

        # Redirect user to home page
        return redirect("/user/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/user/projects")
@employee_login_required
def user_projects():
    project_data = db.execute("SELECT * FROM projects WHERE emp_id = ?", session["user_id"])
    return render_template("employee_project_page.html", project_data = project_data)

@app.route("/user/projects/update_stage", methods=["POST", "GET"])
@employee_login_required
def update_project_stage():
    if request.method == "GET":
        project_data = db.execute("SELECT * FROM projects WHERE emp_id = ?", session["user_id"])
        return render_template("update_project_status.html", project_data = project_data)
    else:
        project_name = request.form.get("project_name")
        status = request.form.get("status")
        remarks = request.form.get("remarks")
        db.execute("UPDATE projects SET status = ? WHERE project_id = (SELECT project_id FROM projects WHERE project_name = ?)", status, project_name)
        db.execute("UPDATE projects SET emp_remarks = ? WHERE project_id = (SELECT project_id FROM projects WHERE project_name = ?)", remarks, project_name)
        return redirect("/user/projects")

@app.route("/user/leave-application", methods=['GET', 'POST'])
@employee_login_required
def leave_application():
    if request.method=="GET":
        leaves = db.execute("SELECT leave_id, from_date, to_date, reason, leave_status FROM leaves WHERE emp_id = ?", session["user_id"])
        return render_template("leave_application_user.html", leaves = leaves)
    else:
        from_date = request.form.get("leave-from-date")
        to_date = request.form.get("leave-to-date")
        reason = request.form.get("leave-reason")
        db.execute("INSERT INTO leaves(emp_id, from_date, to_date, reason, leave_status) VALUES(?, ?, ?, ?, ?)",session["user_id"], from_date, to_date, reason, 'Pending')
        return redirect("/user/home")
    
@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/admin/home")
@admin_login_required
def admin_home():
    return render_template("admin_home.html")

@app.route("/admin/login", methods=["GET", "POST"])
def adm_login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("adm_id"):
            return render_template("apology.html", Message = "must provide username")

        # Ensure password was submitted
        elif not request.form.get("adm_password"):
            return render_template("apology.html", Message = "must provide password")

        # Query database for username of admin
        rows = db.execute(
            "SELECT * FROM adm_data1 WHERE adm_id = ?", request.form.get("adm_id")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["adm_hash"], request.form.get("adm_password")
        ):
            return render_template("apology.html", Message = "invalid username and/or password")

        # Remember which user has logged in
        session["adm_id"] = rows[0]["adm_id"]

        # Redirect user to home page
        return redirect("/admin/employees")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("admin_login.html")

@app.route("/admin/actions")
@admin_login_required
def adm_actions():
    leave_data = db.execute("SELECT * FROM leaves WHERE leave_status = 'Pending'")
    admins = db.execute("SELECT * FROM adm_data1")
    return render_template("register_admin.html", leave_data = leave_data, admins = admins)

@app.route("/admin/actions/leaves/accept/<int:leave_id>")
@admin_login_required
def approve_leave(leave_id):

    # Get the employee ID for this leave request
    leave = db.execute(
        "SELECT emp_id FROM leaves WHERE leave_id = ?",
        leave_id
    )

    emp_id = leave[0]["emp_id"]

    # Approve the leave
    db.execute(
        "UPDATE leaves SET leave_status = ? WHERE leave_id = ?",
        "Accepted",
        leave_id
    )

    # Create notification
    db.execute("""
        INSERT INTO notifications
        (emp_id, title, message, notification_type, created_at)
        VALUES (?, ?, ?, ?, ?)
    """,
    emp_id,
    "Leave Approved",
    "Your leave request has been approved.",
    "leave",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return redirect("/admin/actions")

@app.route("/admin/actions/leaves/reject/<int:leave_id>")
@admin_login_required
def reject_leave(leave_id):

    # Get the employee ID for this leave request
    leave = db.execute(
        "SELECT emp_id FROM leaves WHERE leave_id = ?",
        leave_id
    )

    emp_id = leave[0]["emp_id"]

    # Reject the leave
    db.execute(
        "UPDATE leaves SET leave_status = ? WHERE leave_id = ?",
        "Rejected",
        leave_id
    )

    # Create notification
    db.execute("""
        INSERT INTO notifications
        (emp_id, title, message, notification_type, created_at)
        VALUES (?, ?, ?, ?, ?)
    """,
    emp_id,
    "Leave Rejected",
    "Your leave request has been rejected.",
    "leave",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return redirect("/admin/actions")

@app.route("/admin/register_employee", methods = ["GET", "POST"])
@admin_login_required
def reg_employee():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        ctc_salary = request.form.get("ctc_salary")
        designation = request.form.get("designation")
        joining_date = request.form.get("joining_date")
        db.execute("INSERT INTO emp_data1(emp_name, hash, ctc_salary, designation, joining_date) VALUES(?,?,?,?,?)", name, generate_password_hash(password), ctc_salary, designation, joining_date)
        return redirect("/admin/employees")
    else:
        return render_template("register.html")

@app.route("/admin/reset_password", methods = ["GET", "POST"])
def admin_reset():
    if request.method == "GET":
        return render_template("admin_reset.html")
    else:
        id = request.form.get("adm_id")
        password = request.form.get("adm_password")
        confirm_password = request.form.get("adm_password_confirm")

        if password != confirm_password:
            return render_template("apology.html", Message = "Both passwords do not match")
        elif not id or not password or not confirm_password:
            return render_template("apology.html", Message = "Incomplete Details")
        else:
            hashed_password = generate_password_hash(password)
            db.execute("UPDATE adm_data1 SET adm_hash = ? WHERE adm_id = ?", hashed_password, id)

        return redirect("/admin/login")

@app.route("/admin/actions/register_admin", methods=["GET", "POST"])
@admin_login_required
def reg_admin():
    if request.method == "POST":
        name = request.form.get("adm_name")
        password = request.form.get("adm_password")
        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO adm_data1(adm_name, adm_hash) VALUES(?,?)", name, hashed_password)
        return redirect("/admin/actions")
    else:
        return render_template("register_admin.html")

@app.route("/admin/employees")
@admin_login_required
def view_employees():
    employees_data = db.execute("SELECT * FROM emp_data1")
    return render_template("employees_page_adm.html", employees_data = employees_data)

@app.route("/user/employees")
@employee_login_required
def view_employees_emp():
    employees_data = db.execute("SELECT * FROM emp_data1")
    return render_template("employees_page_user.html", employees_data = employees_data)

@app.route("/admin/attendance")
@admin_login_required
def view_adm_attendance():
    db.execute("SELECT wrk_hrs FROM attendance2 JOIN emp_data1 ON emp_data1.emp_id = attendance2.emp_id")
    employees_data = db.execute("SELECT COUNT(date) AS days, emp_id, emp_name, SUM(wrk_hrs) AS total_work_hours FROM attendance2 GROUP BY emp_name ORDER BY emp_id")
    return render_template("admin_attendance.html", employees_data = employees_data)

@app.route("/admin/upload_attendance", methods=["POST"])
@admin_login_required
def upload_attendance():

    file = request.files["attendance_file"]

    # Read the uploaded file
    content = file.stream.read().decode("utf-8-sig")

    # Automatically detect comma/tab/semicolon
    dialect = csv.Sniffer().sniff(content[:1024])

    reader = csv.DictReader(content.splitlines(), dialect=dialect)

    for row in reader:
        db.execute(
            """
            INSERT OR IGNORE INTO attendance2
            (emp_id, date, week_day, day_type, emp_name,
             in_time, out_time, wrk_hrs, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row["emp_id"],
            row["date"],
            row["week_day"],
            row["day_type"],
            row["emp_name"],
            row["in_time"],
            row["out_time"],
            row["wrk_hrs"],
            row["status"]
        )

    return redirect("/admin/attendance")

@app.route("/admin/view_attendance/<int:emp_id>")
@admin_login_required
def view_attendance(emp_id):
    attendance = db.execute("SELECT * FROM attendance2 WHERE emp_id = ? ORDER BY date DESC", emp_id)
    return jsonify(attendance)

@app.route("/admin/projects", methods=["GET", "POST"])
@admin_login_required
def projects_fun():

    if request.method == "POST":

        project_name = request.form.get("project_name")
        project_description = request.form.get("project_description")
        employees = request.form.get("employees")

        if not project_name or not project_description or not employees:
            return render_template(
                "apology.html",
                Message="Incomplete details"
            )

        db.execute(
            """
            INSERT INTO projects(project_name, project_description, emp_id)
            VALUES(?, ?, ?)
            """,
            project_name,
            project_description,
            employees
        )
        db.execute("""
            INSERT INTO notifications
            (emp_id, title, message, notification_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
        employees,
        "New Project Assigned",
        f"You have been assigned to '{project_name}'.",
        "project",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return redirect("/admin/projects")



    employees_data = db.execute(
        "SELECT emp_id, emp_name FROM emp_data1"
    )

    project_data = db.execute(
        "SELECT * FROM projects"
    )

    return render_template(
        "project_page_admin.html",
        employees_data=employees_data,
        project_data=project_data
    )

@app.route("/admin/salary")
@admin_login_required
def salary_admin_page():
    employees_data = db.execute("SELECT * FROM emp_data1")
    total_salary = db.execute("SELECT SUM(ctc_salary) AS ts FROM emp_data1")
    return render_template("employee_salary_page_admin.html", employees_data = employees_data, total_salary=total_salary)

@app.route("/user/salary")
@employee_login_required
def salary_user_page():
    emp_data = db.execute("SELECT ctc_salary FROM emp_data1 WHERE emp_id = ?", session["user_id"])
    return render_template("employee_salary.html", emp_data = emp_data)

@app.route("/view_employee/<int:emp_id>")
@employee_login_required
def view_emp(emp_id):
    emp_data = db.execute("SELECT * FROM emp_data1 WHERE emp_id = ?", emp_id)
    return render_template("view_employee_adm.html", emp_data = emp_data)

@app.route("/user/attendance")
@employee_login_required
def view_user_attendance():
    attendance_data = db.execute("SELECT date, week_day, day_type, in_time, out_time, wrk_hrs, status FROM attendance2 WHERE emp_id = ?", session["user_id"])
    total_working_days = db.execute("SELECT COUNT(*) AS total_days FROM attendance2 WHERE day_type = ? AND emp_id = ?", "working day", session["user_id"])
    regular_days = db.execute("SELECT COUNT(*) AS regular_days FROM attendance2 WHERE status = ? AND emp_id = ?", "regular", session["user_id"])
    half_days = db.execute("SELECT COUNT(*) AS half_days FROM attendance2 WHERE status = ? AND emp_id = ?", "half", session["user_id"])
    late_days = db.execute("SELECT COUNT(*) AS late_days FROM attendance2 WHERE status = ? AND emp_id = ?", "late", session["user_id"])
    leaves = total_working_days[0]['total_days'] - regular_days[0]['regular_days'] - half_days[0]['half_days'] - late_days[0]["late_days"]
    total_days = regular_days[0]['regular_days'] + half_days[0]['half_days'] + late_days[0]['late_days']
    return render_template("employee_attendance_page.html", attendance_data = attendance_data, total_working_days = total_working_days, regular_days = regular_days, half_days = half_days, late_days = late_days, leaves = leaves, total_days = total_days)
    
@app.route("/admin/view_employee/<int:emp_id>")
@admin_login_required
def view_emp_admin(emp_id):
    emp_data = db.execute("SELECT * FROM emp_data1 WHERE emp_id = ?", emp_id)
    return render_template("view_employee_adm.html", emp_data = emp_data)

@app.route("/admin/edit_employee/<int:emp_id>", methods=["GET", "POST"])
@admin_login_required
def edit_emp_admin(emp_id):
    if request.method == "GET":
        emp_data = db.execute("SELECT * FROM emp_data1 WHERE emp_id = ?", emp_id)
        return render_template("edit_employee_adm.html", emp_data = emp_data)
    else:
        name = request.form.get("name")
        ctc_salary = request.form.get("ctc_salary")
        designation = request.form.get("designation")
        joining_date = request.form.get("joining_date")
        db.execute("UPDATE emp_data1 SET emp_name = ? WHERE emp_id= ?", name, emp_id)
        db.execute("UPDATE emp_data1 SET ctc_salary = ? WHERE emp_id= ?", ctc_salary, emp_id)
        db.execute("UPDATE emp_data1 SET designation = ? WHERE emp_id= ?", designation, emp_id)
        db.execute("UPDATE emp_data1 SET joining_date = ? WHERE emp_id= ?", joining_date, emp_id)
        return redirect("/admin/employees")

@app.route("/admin/dereg_employee/<int:emp_id>")
@admin_login_required
def deregister_emp(emp_id):
    db.execute("DELETE FROM emp_data1 WHERE emp_id = ?", emp_id)
    return redirect("/admin/employees")

@app.route("/admin/dereg_admin/<int:adm_id>")
@admin_login_required
def deregister_adm(adm_id):
    db.execute("DELETE FROM adm_data1 WHERE adm_id = ?", adm_id)
    return redirect("/admin/actions")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)