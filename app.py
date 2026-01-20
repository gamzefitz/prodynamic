from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "dev"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "prodynamic.db")


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


if __name__ == "__main__":
    app.run(debug=True)
