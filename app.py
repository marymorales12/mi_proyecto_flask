from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '¡Hola! Bienvenido a mi aplicación Flask.'

@app.route('/usuario/<Mary>')
def usuario(Mary):
    return f'Bienvenido, {Mary}!'

    
@app.route('/contacto/<Mary>')
def contacto(Mary):
    return "Página de contacto: modasostenible@gmail.com"

@app.route('/direccion/<Mary>')
def mostrar_direccion(Mary):
    return '<h1>Dirección: ARGELIA - LOJA</h1>'

if __name__ == '__main__':
    app.run(debug=True)