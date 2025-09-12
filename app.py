from flask import Flask, render_template
from mysql.connector import Error
from Conexion.conexion import get_connection

app = Flask(__name__)

# ----------------- Rutas con plantillas -----------------
@app.route('/')
def index():
    return render_template('index.html', titulo='Inicio')

@app.route('/about')
def about():
    return render_template('about.html', titulo='Acerca de')

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return render_template('index.html', titulo='Inicio', saludo_para=nombre)

# ----------------- Rutas con HTML simple -----------------
@app.route('/contacto')
def contacto():
    return "Página de contacto: modasostenible@gmail.com"

@app.route('/direccion')
def mostrar_direccion():
    return "<h1>Dirección: ARGELIA - LOJA</h1>"

# ----------------- Verificación de conexión -----------------
@app.route("/test_db")
def test_db():
    try:
        cnx = get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        return f"<h2 style='color:green;'>✅ Conexión exitosa a MySQL. Resultado: {row[0]}</h2>"
    except Error as e:
        return f"<h2 style='color:red;'>❌ Error en la conexión a MySQL: {str(e)}</h2>"
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

# ----------------- Mostrar usuarios -----------------
@app.route("/usuarios")
def listar_usuarios():
    try:
        cnx = get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        data = cursor.fetchall()
        html = "<h2>Lista de usuarios</h2><ul>"
        for row in data:
            html += f"<li>{row['id_usuario']} - {row['nombre']} - {row['mail']}</li>"
        html += "</ul>"
        return html
    except Error as e:
        return f"<h2 style='color:red;'>❌ Error consultando usuarios: {str(e)}</h2>"
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True)
