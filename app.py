from flask import Flask, render_template, request, redirect, url_for, flash, abort
import sqlite3
import os

# Create the Flask application
app = Flask(__name__)

# Secret key needed for flash messages and sessions
app.secret_key = "dev"

# Get the absolute path of this file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build the full path to the SQLite database
DB_PATH = os.path.join(BASE_DIR, "prodynamic.db")

# Only these tables will be exposed in the CRUD UI
# CRUD configuration
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
            "hire_date": "date",      # stored as 'YYYY-MM-DD' text in your DB
            "department_id": "int",
            "job_id": "int",
            "is_manager": "bool",     # stored as 'True'/'False' text in your seed
            "weekly_hours": "float",
        },
    },
    "Salary": {
        "pk": "salary_id",
        "cols": ["employee_id", "salary_amount"],
        "types": {"employee_id": "int", "salary_amount": "int"},
    },
}


# Opens a connection to the SQLite database.
# row_factory allows rows to behave like dictionaries.
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Returns a list of all user-defined tables in the database.
# Internal SQLite tables are excluded.
def list_tables(conn):
    return [
        r["name"]
        for r in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()
    ]

# Returns the CRUD configuration for a table.
# If the table is not allowed, return a 404 error.
def get_cfg(table_name: str):
    cfg = CRUD.get(table_name)
    if not cfg:
        abort(404)
    return cfg


# Converts form input (always strings) into the correct data type
# before inserting/updating the database.
def coerce_value(raw, typ: str):
    raw = (raw or "").strip()

    if typ == "text":
        return raw if raw != "" else None

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

    # default fallback
    return raw if raw != "" else None


# Redirect root URL to the CRUD index page.
@app.route("/")
def home():
    return redirect(url_for("crud_index"))


@app.route("/crud")
def crud_index():
    # show only the configured tables, and only if they exist in the DB
    conn = get_db()
    existing = set(list_tables(conn))
    conn.close()

    tables = [t for t in CRUD.keys() if t in existing]
    if not tables:
        return "No configured CRUD tables found in prodynamic.db", 200

    return render_template("crud_index.html", tables=tables)


# Displays all rows for a given table.
@app.route("/crud/<table_name>")
def crud_list(table_name):
    cfg = get_cfg(table_name)
    pk = cfg["pk"]
    cols = cfg["cols"]

    conn = get_db()
    existing = set(list_tables(conn))
    if table_name not in existing:
        conn.close()
        return "Table not found", 404

    select_cols = ", ".join([pk] + cols)
    rows = conn.execute(
        f'SELECT {select_cols} FROM "{table_name}" ORDER BY "{pk}" ASC LIMIT 500'
    ).fetchall()
    conn.close()

    return render_template(
        "crud_table.html",
        tables=[t for t in CRUD.keys() if t in existing],
        current_table=table_name,
        pk=pk,
        cols=cols,
        rows=rows,
    )


# Adds a new row to the selected table.
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
        col_list = ", ".join([f'"{c}"' for c in cols])

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


# Edits an existing row in the table.
@app.route("/crud/<table_name>/<int:row_id>/edit", methods=["GET", "POST"])
def crud_edit(table_name, row_id):
    cfg = get_cfg(table_name)
    pk = cfg["pk"]
    cols = cfg["cols"]
    types = cfg.get("types", {})

    select_cols = ", ".join([pk] + cols)

    conn = get_db()
    row = conn.execute(
        f'SELECT {select_cols} FROM "{table_name}" WHERE "{pk}" = ?',
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

        set_clause = ", ".join([f'"{c}" = ?' for c in cols])

        try:
            conn.execute(
                f'UPDATE "{table_name}" SET {set_clause} WHERE "{pk}" = ?',
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


# Deletes a row from the table.
@app.route("/crud/<table_name>/<int:row_id>/delete", methods=["POST"])
def crud_delete(table_name, row_id):
    cfg = get_cfg(table_name)
    pk = cfg["pk"]

    try:
        conn = get_db()
        conn.execute(f'DELETE FROM "{table_name}" WHERE "{pk}" = ?', (row_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        flash(f"Delete failed: {e}", "error")
        return redirect(url_for("crud_list", table_name=table_name))

    flash("Row deleted.", "success")
    return redirect(url_for("crud_list", table_name=table_name))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
