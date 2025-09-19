# app.py
from flask import Flask, render_template  # # Importa Flask y el motor de plantillas

app = Flask(__name__)  # # Crea la aplicación Flask

# # Ruta: Página de inicio. Renderiza la plantilla index.html
@app.route('/')
def index():
    return render_template('index.html', titulo='Inicio')  # # Pasa un título como variable

# # Ruta: Página "Acerca de". Renderiza la plantilla about.html
@app.route('/about')
def about():
    return render_template('about.html', titulo='Acerca de')

# # Ruta: Saludo con parámetro en la URL. Cambiamos <Mary> por <nombre> (más genérico)
@app.route('/usuario/<nombre>')
def usuario(nombre):
    # # Reutilizamos index.html para mostrar un saludo opcional si viene 'saludo_para'
    return render_template('index.html', titulo='Inicio', saludo_para=nombre)

# # Ruta: Contacto (contenido simple sin plantilla)
@app.route('/contacto')
def contacto():
    return "Página de contacto: modasostenible@gmail.com"

# # Ruta: Dirección (contenido HTML simple sin plantilla)
@app.route('/direccion')
def mostrar_direccion():
    return "<h1>Dirección: ARGELIA - LOJA</h1>"

# # Punto de entrada de la app. Activa el modo debug para recarga automática
if __name__ == '__main__':
    app.run(debug=True)
