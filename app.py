from flask import Flask, render_template, request, redirect, url_for, flash, abort
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "dev"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "prodynamic.db")

CRUD = {
    "Department": {
        "pk": "department_id",
        "cols": ["department_name"],
        "types": {"department_name": "text"},
    },
    "Job": {
        "pk": "job_id",
        "cols": ["job_title", "department_id"],
        "types": {"job_title": "text", "department_id": "int"},
    },
    "Employee": {
        "pk": "employee_id",
        "cols": [
            "first_name",
            "last_name",
            "email",
            "hire_date",
            "department_id",
            "job_id",
            "is_manager",
            "weekly_hours",
        ],
        "types": {
            "first_name": "text",
            "last_name": "text",
            "email": "text",
            "hire_date": "date",      # stored as datetime text like '2022-01-15'
            "department_id": "int",
            "job_id": "int",
            "is_manager": "bool",     # in your data it's 'False'/'True'
            "weekly_hours": "float",  # DECIMAL(4,1)
        },
    },
    "Salary": {
        "pk": "salary_id",
        "cols": ["employee_id", "salary_amount"],
        "types": {"employee_id": "int", "salary_amount": "int"},
    },
}



def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn):
    return [
        r["name"]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]

def get_cfg(table_name: str):
    cfg = CRUD.get(table_name)
    if not cfg:
        abort(404)
    return cfg


def coerce_value(raw, typ: str):
    raw = (raw or "").strip()

    if typ == "text":
        return raw

    if typ == "int":
        return int(raw) if raw != "" else None

    if typ == "float":
        return float(raw) if raw != "" else None

    if typ == "date":
        # accept YYYY-MM-DD (matches your seed data)
        return raw if raw != "" else None

    if typ == "bool":
        # supports select values True/False and checkbox "on"
        if raw.lower() in ("1", "true", "yes", "on"):
            return "True"
        return "False"



@app.route("/")
def home():
    conn = get_db()
    tables = list_tables(conn)
    conn.close()
    # redirect to Salary if it exists, otherwise first table, otherwise show empty
    if "Salary" in tables:
        return redirect(url_for("table_view", table_name="Salary"))
    if tables:
        return redirect(url_for("table_view", table_name=tables[0]))
    return "No tables found in prodynamic.db", 200


@app.route("/table/<table_name>")
def table_view(table_name):
    conn = get_db()
    tables = list_tables(conn)

    if table_name not in tables:
        conn.close()
        return "Table not found", 404

    cols = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
    col_names = [c["name"] for c in cols]

    rows = conn.execute(f'SELECT * FROM "{table_name}" LIMIT 500').fetchall()
    conn.close()

    return render_template(
        "table.html",
        tables=tables,
        current_table=table_name,
        col_names=col_names,
        rows=rows,
    )


# ---- Salary CRUD stays as-is ----

@app.route("/salary/add", methods=["GET", "POST"])
def add_salary():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip()
        salary_amount = request.form.get("salary_amount", "").strip()

        if not employee_id.isdigit() or not salary_amount.isdigit():
            flash("employee_id and salary_amount must be whole numbers.")
            return render_template("form.html", mode="add", row=None)

        conn = get_db()
        conn.execute(
            'INSERT INTO "Salary" (employee_id, salary_amount) VALUES (?, ?)',
            (int(employee_id), int(salary_amount)),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("table_view", table_name="Salary"))

    return render_template("form.html", mode="add", row=None)


@app.route("/salary/edit/<int:salary_id>", methods=["GET", "POST"])
def edit_salary(salary_id):
    conn = get_db()
    row = conn.execute(
        'SELECT salary_id, employee_id, salary_amount FROM "Salary" WHERE salary_id = ?',
        (salary_id,),
    ).fetchone()

    if row is None:
        conn.close()
        flash("Record not found.")
        return redirect(url_for("table_view", table_name="Salary"))

    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip()
        salary_amount = request.form.get("salary_amount", "").strip()

        if not employee_id.isdigit() or not salary_amount.isdigit():
            conn.close()
            flash("employee_id and salary_amount must be whole numbers.")
            return render_template("form.html", mode="edit", row=row)

        conn.execute(
            'UPDATE "Salary" SET employee_id = ?, salary_amount = ? WHERE salary_id = ?',
            (int(employee_id), int(salary_amount), salary_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("table_view", table_name="Salary"))

    conn.close()
    return render_template("form.html", mode="edit", row=row)


@app.route("/salary/delete/<int:salary_id>", methods=["POST"])
def delete_salary(salary_id):
    conn = get_db()
    conn.execute('DELETE FROM "Salary" WHERE salary_id = ?', (salary_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("table_view", table_name="Salary"))

@app.route("/employees")
def employees_index():
    conn = get_db()
    rows = conn.execute(
        "SELECT employee_id, first_name, last_name FROM Employee ORDER BY employee_id ASC"
    ).fetchall()
    conn.close()
    return render_template("employees_index.html", rows=rows)


@app.route("/employees/add", methods=["GET", "POST"])
def employees_add():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()

        if not first_name or not last_name:
            flash("First name and last name are required.", "error")
            return render_template("employees_form.html", mode="add", row=None)

        conn = get_db()
        conn.execute(
            "INSERT INTO Employee (first_name, last_name) VALUES (?, ?)",
            (first_name, last_name),
        )
        conn.commit()
        conn.close()
        flash("Employee added.", "success")
        return redirect(url_for("employees_index"))

    return render_template("employees_form.html", mode="add", row=None)


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
def employees_edit(employee_id):
    conn = get_db()
    row = conn.execute(
        "SELECT employee_id, first_name, last_name FROM Employee WHERE employee_id = ?",
        (employee_id,),
    ).fetchone()

    if row is None:
        conn.close()
        flash("Employee not found.", "error")
        return redirect(url_for("employees_index"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()

        if not first_name or not last_name:
            conn.close()
            flash("First name and last name are required.", "error")
            return render_template("employees_form.html", mode="edit", row=row)

        conn.execute(
            "UPDATE Employee SET first_name = ?, last_name = ? WHERE employee_id = ?",
            (first_name, last_name, employee_id),
        )
        conn.commit()
        conn.close()
        flash("Employee updated.", "success")
        return redirect(url_for("employees_index"))

    conn.close()
    return render_template("employees_form.html", mode="edit", row=row)


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def employees_delete(employee_id):
    conn = get_db()
    conn.execute("DELETE FROM Employee WHERE employee_id = ?", (employee_id,))
    conn.commit()
    conn.close()
    flash("Employee deleted.", "success")
    return redirect(url_for("employees_index"))

@app.route("/departments")
def departments_index():
    conn = get_db()
    rows = conn.execute(
        "SELECT department_id, department_name FROM Department ORDER BY department_id ASC"
    ).fetchall()
    conn.close()
    return render_template("departments_index.html", rows=rows)


@app.route("/departments/add", methods=["GET", "POST"])
def departments_add():
    if request.method == "POST":
        department_name = request.form.get("department_name", "").strip()

        if not department_name:
            flash("Department name is required.", "error")
            return render_template("departments_form.html", mode="add", row=None)

        conn = get_db()
        conn.execute(
            "INSERT INTO Department (department_name) VALUES (?)",
            (department_name,),
        )
        conn.commit()
        conn.close()
        flash("Department added.", "success")
        return redirect(url_for("departments_index"))

    return render_template("departments_form.html", mode="add", row=None)


@app.route("/departments/<int:department_id>/edit", methods=["GET", "POST"])
def departments_edit(department_id):
    conn = get_db()
    row = conn.execute(
        "SELECT department_id, department_name FROM Department WHERE department_id = ?",
        (department_id,),
    ).fetchone()

    if row is None:
        conn.close()
        flash("Department not found.", "error")
        return redirect(url_for("departments_index"))

    if request.method == "POST":
        department_name = request.form.get("department_name", "").strip()

        if not department_name:
            conn.close()
            flash("Department name is required.", "error")
            return render_template("departments_form.html", mode="edit", row=row)

        conn.execute(
            "UPDATE Department SET department_name = ? WHERE department_id = ?",
            (department_name, department_id),
        )
        conn.commit()
        conn.close()
        flash("Department updated.", "success")
        return redirect(url_for("departments_index"))

    conn.close()
    return render_template("departments_form.html", mode="edit", row=row)


@app.route("/departments/<int:department_id>/delete", methods=["POST"])
def departments_delete(department_id):
    conn = get_db()
    conn.execute("DELETE FROM Department WHERE department_id = ?", (department_id,))
    conn.commit()
    conn.close()
    flash("Department deleted.", "success")
    return redirect(url_for("departments_index"))

@app.route("/crud/<table_name>")
def crud_list(table_name):
    cfg = get_cfg(table_name)
    pk = cfg["pk"]
    cols = cfg["cols"]

    conn = get_db()
    tables = list_tables(conn)

    if table_name not in tables:
        conn.close()
        return "Table not found", 404

    select_cols = ", ".join([pk] + cols)
    rows = conn.execute(
        f'SELECT {select_cols} FROM "{table_name}" ORDER BY {pk} ASC LIMIT 500'
    ).fetchall()
    conn.close()

    return render_template(
        "crud_table.html",
        tables=tables,
        current_table=table_name,
        pk=pk,
        cols=cols,
        rows=rows,
    )


@app.route("/crud/<table_name>/add", methods=["GET", "POST"])
def crud_add(table_name):
    cfg = get_cfg(table_name)
    cols = cfg["cols"]
    types = cfg.get("types", {})

    if request.method == "POST":
        try:
            values = [coerce_value(request.form.get(c), types.get(c, "text")) for c in cols]
        except ValueError:
            flash("Invalid number entered.", "error")
            return render_template("crud_form.html", table_name=table_name, cols=cols, row=None, types=types)

        placeholders = ", ".join(["?"] * len(cols))
        col_list = ", ".join(cols)

        try:
            conn = get_db()
            conn.execute(
                f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})',
                values,
            )
            conn.commit()
            conn.close()
        except Exception as e:
            flash(f"Insert failed: {e}", "error")
            return render_template("crud_form.html", table_name=table_name, cols=cols, row=None, types=types)

        flash("Row added.", "success")
        return redirect(url_for("crud_list", table_name=table_name))

    return render_template("crud_form.html", table_name=table_name, cols=cols, row=None, types=types)


@app.route("/crud/<table_name>/<int:row_id>/edit", methods=["GET", "POST"])
def crud_edit(table_name, row_id):
    cfg = get_cfg(table_name)
    pk = cfg["pk"]
    cols = cfg["cols"]
    types = cfg.get("types", {})

    select_cols = ", ".join([pk] + cols)
    conn = get_db()
    row = conn.execute(
        f'SELECT {select_cols} FROM "{table_name}" WHERE {pk} = ?',
        (row_id,),
    ).fetchone()

    if row is None:
        conn.close()
        flash("Row not found.", "error")
        return redirect(url_for("crud_list", table_name=table_name))

    if request.method == "POST":
        try:
            values = [coerce_value(request.form.get(c), types.get(c, "text")) for c in cols]
        except ValueError:
            conn.close()
            flash("Invalid number entered.", "error")
            return render_template("crud_form.html", table_name=table_name, cols=cols, row=row, types=types)

        set_clause = ", ".join([f"{c} = ?" for c in cols])

        try:
            conn.execute(
                f'UPDATE "{table_name}" SET {set_clause} WHERE {pk} = ?',
                values + [row_id],
            )
            conn.commit()
            conn.close()
        except Exception as e:
            conn.close()
            flash(f"Update failed: {e}", "error")
            return render_template("crud_form.html", table_name=table_name, cols=cols, row=row, types=types)

        flash("Row updated.", "success")
        return redirect(url_for("crud_list", table_name=table_name))

    conn.close()
    return render_template("crud_form.html", table_name=table_name, cols=cols, row=row, types=types)


@app.route("/crud/<table_name>/<int:row_id>/delete", methods=["POST"])
def crud_delete(table_name, row_id):
    cfg = get_cfg(table_name)
    pk = cfg["pk"]

    try:
        conn = get_db()
        conn.execute(f'DELETE FROM "{table_name}" WHERE {pk} = ?', (row_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        flash(f"Delete failed: {e}", "error")
        return redirect(url_for("crud_list", table_name=table_name))

    flash("Row deleted.", "success")
    return redirect(url_for("crud_list", table_name=table_name))




if __name__ == "__main__":
    app.run(debug=True)