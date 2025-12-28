from flask import Flask, render_template, request, redirect, url_for

import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    # Ingresos del mes
    cursor.execute("""
        SELECT IFNULL(SUM(ganancia), 0) 
        FROM ingresos 
        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    """)
    ingresos_mes = cursor.fetchone()[0]

    # Gastos del mes
    cursor.execute("""
        SELECT IFNULL(SUM(monto), 0) 
        FROM gastos 
        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    """)
    gastos_mes = cursor.fetchone()[0]

    # Gastos personales
    cursor.execute("""
        SELECT IFNULL(SUM(monto), 0) 
        FROM gastos 
        WHERE es_personal = 1
        AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    """)
    gastos_personales = cursor.fetchone()[0]

    # Gastos del negocio
    cursor.execute("""
        SELECT IFNULL(SUM(monto), 0) 
        FROM gastos 
        WHERE es_personal = 0
        AND strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    """)
    gastos_negocio = cursor.fetchone()[0]

    utilidad = ingresos_mes - gastos_mes

    conn.close()

    return render_template(
        "dashboard.html",
        ingresos_mes=ingresos_mes,
        gastos_mes=gastos_mes,
        gastos_personales=gastos_personales,
        gastos_negocio=gastos_negocio,
        utilidad=utilidad
    )


from flask import request, redirect, url_for

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        tipo = request.form["tipo"]
        notas = request.form["notas"]

        cursor.execute(
            "INSERT INTO clientes (nombre, telefono, tipo, notas) VALUES (?, ?, ?, ?)",
            (nombre, telefono, tipo, notas)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("clientes"))

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()

    return render_template("clientes.html", clientes=clientes)


@app.route("/ingresos", methods=["GET", "POST"])
def ingresos():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        fecha = request.form["fecha"]
        cliente = request.form["cliente"]
        tipo = request.form["tipo"]
        monto = float(request.form["monto"])
        comision = float(request.form["comision"])
        ganancia = monto - comision

        cursor.execute("""
            INSERT INTO ingresos (fecha, cliente, tipo, monto, comision, ganancia)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha, cliente, tipo, monto, comision, ganancia))

        conn.commit()
        conn.close()
        return redirect(url_for("ingresos"))

    cursor.execute("SELECT * FROM ingresos ORDER BY fecha DESC")
    ingresos = cursor.fetchall()
    conn.close()

    return render_template("ingresos.html", ingresos=ingresos)


@app.route("/gastos", methods=["GET", "POST"])
def gastos():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        fecha = request.form["fecha"]
        categoria = request.form["categoria"]
        monto = float(request.form["monto"])
        es_personal = int(request.form["es_personal"])

        cursor.execute("""
            INSERT INTO gastos (fecha, categoria, monto, es_personal)
            VALUES (?, ?, ?, ?)
        """, (fecha, categoria, monto, es_personal))

        conn.commit()
        conn.close()
        return redirect(url_for("gastos"))

    cursor.execute("SELECT * FROM gastos ORDER BY fecha DESC")
    gastos = cursor.fetchall()
    conn.close()

    return render_template("gastos.html", gastos=gastos)

@app.route("/cotizaciones")
def cotizaciones():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cotizaciones ORDER BY fecha DESC")
    cotizaciones = cursor.fetchall()

    conn.close()
    return render_template("cotizaciones.html", cotizaciones=cotizaciones)

@app.route("/cotizaciones/nueva", methods=["GET", "POST"])
def nueva_cotizacion():
    if request.method == "POST":
        cliente = request.form["cliente"]
        descripcion = request.form["descripcion"]
        monto = request.form["monto"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cotizaciones (cliente, descripcion, monto)
            VALUES (?, ?, ?)
        """, (cliente, descripcion, monto))
        conn.commit()
        conn.close()

        return redirect("/cotizaciones")

    return render_template("nueva_cotizacion.html")

@app.route("/cotizaciones/estado/<int:id>/<estado>")
def cambiar_estado(id, estado):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cotizaciones SET estado = ? WHERE id = ?
    """, (estado, id))
    conn.commit()
    conn.close()

    return redirect("/cotizaciones")

@app.route("/cotizaciones/convertir/<int:id>")
def convertir_cotizacion(id):
    conn = get_db()
    cursor = conn.cursor()

    # Obtener cotización
    cursor.execute("""
        SELECT cliente, descripcion, monto
        FROM cotizaciones
        WHERE id = ? AND estado = 'Aprobada'
    """, (id,))
    cotizacion = cursor.fetchone()

    if cotizacion:
        cliente = cotizacion["cliente"]
        monto = cotizacion["monto"]

        # Crear ingreso (sin comisión por ahora)
        cursor.execute("""
            INSERT INTO ingresos (fecha, cliente, tipo, monto, comision, ganancia)
            VALUES (date('now'), ?, 'Cotización', ?, 0, ?)
        """, (cliente, monto, monto))

        # Marcar cotización como convertida
        cursor.execute("""
            UPDATE cotizaciones SET estado = 'Convertida'
            WHERE id = ?
        """, (id,))

        conn.commit()

    conn.close()
    return redirect("/cotizaciones")





if __name__ == "__main__":
    app.run()
