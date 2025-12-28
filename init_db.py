import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ⚠️ BORRAR TABLA COTIZACIONES (solo en desarrollo)
cursor.execute("DROP TABLE IF EXISTS cotizaciones")

# TABLA CLIENTES
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    telefono TEXT,
    tipo TEXT,
    notas TEXT
)
""")

# TABLA INGRESOS
cursor.execute("""
CREATE TABLE IF NOT EXISTS ingresos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    cliente TEXT,
    tipo TEXT,
    monto REAL,
    comision REAL,
    ganancia REAL
)
""")

# TABLA GASTOS
cursor.execute("""
CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    categoria TEXT,
    monto REAL,
    es_personal INTEGER
)
""")

# ✅ TABLA COTIZACIONES (CORRECTA)
cursor.execute("""
CREATE TABLE IF NOT EXISTS cotizaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    descripcion TEXT,
    monto REAL NOT NULL,
    estado TEXT DEFAULT 'Pendiente',
    fecha TEXT DEFAULT CURRENT_DATE
)
""")

conn.commit()
conn.close()

print("Base de datos creada correctamente")
