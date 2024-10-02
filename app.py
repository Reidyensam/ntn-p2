from flask import Flask, render_template, request, flash, redirect, url_for
from db import *

app = Flask(__name__)
app.secret_key = 'Arqui123'

# Lista temporal de productos (esto debería provenir de la base de datos)
productos = [
    {'id': 1, 'nombre': 'TV 4K', 'categoria': 'electronicos',
        'precio_inicial': 300.00, 'foto_url': '/static/img/tv.jpg'},
    {'id': 2, 'nombre': 'Coche', 'categoria': 'vehiculos',
        'precio_inicial': 15000.00, 'foto_url': '/static/img/coche.jpg'},
    {'id': 3, 'nombre': 'Sofá', 'categoria': 'muebles',
        'precio_inicial': 200.00, 'foto_url': '/static/img/sofa.jpg'}
]

subastas = [
    {'id': 1, 'nombre_producto': 'TV 4K',
        'precio_actual': 350.00, 'imagen': '/static/img/tv.jpg'},
    {'id': 2, 'nombre_producto': 'Coche', 'precio_actual': 15500.00,
        'imagen': '/static/img/coche.jpg'},
    {'id': 3, 'nombre_producto': 'Sofá', 'precio_actual': 220.00,
        'imagen': '/static/img/sofa.jpg'}
]

# Ruta para explorar subastas


@app.route('/cliente/explorar-subastas')
def explorar_subastas():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Consulta para obtener subastas
    cursor.execute("SELECT * FROM subastas")
    subastas = cursor.fetchall()

    conexion.close()
    return render_template('cliente/explorar_subastas.html', subastas=subastas)

# Ruta para ver el detalle de una subasta


@app.route('/cliente/detalle-subasta/<int:subasta_id>', methods=['GET', 'POST'])
def detalle_subasta(subasta_id):
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Obtener detalles de la subasta
    cursor.execute("SELECT * FROM subastas WHERE id = %s", (subasta_id,))
    subasta = cursor.fetchone()

    if not subasta:
        return "Subasta no encontrada", 404

    # Obtener el historial de pujas de la subasta
    cursor.execute(
        "SELECT * FROM pujas WHERE subasta_id = %s ORDER BY monto DESC", (subasta_id,))
    historial_pujas = cursor.fetchall()

    if request.method == 'POST':
        nueva_puja = float(request.form['monto'])
        if nueva_puja > subasta['precio_actual']:
            cursor.execute("INSERT INTO pujas (subasta_id, pujador, monto) VALUES (%s, %s, %s)",
                           (subasta_id, 'Cliente', nueva_puja))
            cursor.execute(
                "UPDATE subastas SET precio_actual = %s WHERE id = %s", (nueva_puja, subasta_id))
            conexion.commit()
        else:
            return "La puja debe ser mayor al precio actual", 400

    conexion.close()
    return render_template('cliente/detalle_subasta.html', subasta=subasta, historial_pujas=historial_pujas)

# Ruta para el historial de subastas del cliente


@app.route('/cliente/historial-subastas')
def historial_subastas_cliente():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Consulta para obtener el historial de subastas del cliente
    # Suponiendo cliente con ID 1
    cursor.execute("SELECT * FROM subastas WHERE comprador_id = 1")
    historial = cursor.fetchall()

    conexion.close()
    return render_template('cliente/historial_subasta_cliente.html', historial=historial)

# TODO arreglar query
# Ruta para ver el perfil del cliente


@app.route('/cliente/perfil')
def perfil_cliente():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Consulta para obtener datos del cliente
    # Suponiendo cliente con ID 1
    cursor.execute("SELECT * FROM clientes WHERE id = 1")
    cliente = cursor.fetchone()

    conexion.close()
    return render_template('cliente/perfil_cliente.html', cliente=cliente)

# Ruta para gestionar productos del subastador


@app.route('/subastador/gestion-productos', methods=['GET'])
def gestion_productos():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    categoria_filtro = request.args.get('categoriaFiltro', 'todos')

    if categoria_filtro == 'todos':
        cursor.execute("SELECT * FROM productos")
    else:
        cursor.execute(
            "SELECT * FROM productos WHERE categoria = %s", (categoria_filtro,))

    productos = cursor.fetchall()
    conexion.close()
    return render_template('subastador/gestion_productos.html', productos=productos)

# Ruta para editar un producto


@app.route('/subastador/editar-producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio_inicial = request.form['precio_inicial']
        categoria = request.form['categoria']

        cursor.execute("UPDATE productos SET nombre = %s, precio_inicial = %s, categoria = %s WHERE id = %s",
                       (nombre, precio_inicial, categoria, id))
        conexion.commit()
        conexion.close()
        return redirect(url_for('gestion_productos'))

    conexion.close()
    return render_template('subastador/editar_producto.html', producto=producto)

# Ruta para eliminar un producto


@app.route('/subastador/eliminar-producto/<int:id>')
def eliminar_producto(id):
    conexion = db_connection()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for('gestion_productos'))

# Ruta para la página principal


@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el dashboard del cliente


@app.route('/cliente/dashboard')
def cliente_dashboard():
    return render_template('cliente/index_cliente.html')

# Ruta para el dashboard del subastador


@app.route('/subastador/dashboard')
def subastador_dashboard():
    return render_template('subastador/index_sub.html')

# Ruta para gestionar subastas


@app.route('/subastador/gestion-subastas')
def gestion_subastas():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Obtener todas las subastas del subastador
    # Suponiendo subastador con ID 1
    cursor.execute("SELECT * FROM subastas WHERE subastador_id = 1")
    subastas = cursor.fetchall()
    conexion.close()
    return render_template('subastador/gestionsub.html', subastas=subastas)

# Ruta para ver subastas activas


@app.route('/subastador/subasta-activa')
def subasta_activa():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Obtener subastas activas
    cursor.execute("SELECT * FROM subastas WHERE estado = 'activa'")
    subastas = cursor.fetchall()
    conexion.close()
    return render_template('subastador/subasta_activa.html', subastas=subastas)

# Ruta para el historial de subastas


@app.route('/subastador/historial-subastas')
def historial_subastas():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM subastas WHERE estado = 'finalizada'")
    historial = cursor.fetchall()
    conexion.close()
    return render_template('subastador/historial.html', historial=historial)


# Ruta para estadísticas y reportes
@app.route('/subastador/estadisticas-reportes')
def estadisticas_reportes():
    # Aquí irían consultas que proporcionen estadísticas e informes, como número de subastas, ganancia total, etc.
    return render_template('subastador/estadisticas_reportes.html')

# Ruta para notificaciones


@app.route('/subastador/notificaciones')
def notificaciones():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Suponiendo subastador con ID 1
    cursor.execute("SELECT * FROM notificaciones WHERE subastador_id = 1")
    notificaciones = cursor.fetchall()
    conexion.close()
    return render_template('subastador/notificaciones.html', notificaciones=notificaciones)


# Ruta para la página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener los datos del formulario
        email = request.form.get('email')
        password = request.form.get('password')

        # Usar la función db_connection() para conectar a la base de datos
        conexion = db_connection()
        if conexion:
            cursor = conexion.cursor(dictionary=True)

            # Verificar si el usuario existe en la base de datos
            # Cambiar la consulta en el login para reflejar la estructura correcta de la base de datos
            cursor.execute('''
                SELECT cliente.*, persona.correo
                FROM cliente
                INNER JOIN persona ON cliente.persona_id = persona.id_persona
                WHERE persona.correo = %s AND cliente.contrasena = %s
                ''', (email, password))

            user = cursor.fetchone()
            conexion.close()  # Cierra la conexión después de la consulta

            if user:
                return redirect('cliente/dashboard')
            else:
                flash(
                    'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.', 'error')
                return redirect(url_for('login'))
        else:
            flash('Error al conectar a la base de datos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Ruta para la página de registro


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('nombre')
        lastname = request.form.get('apellido')
        email = request.form.get('correo')
        password = request.form.get('password')
        tipo = request.form.get('rol')

        print(f"Nombre: {name}")
        print(f"Apellido: {lastname}")
        print(f"Correo: {email}")
        print(f"Contraseña: {password}")
        print(f"Tipo: {tipo}")

        # Verifica que todos los campos se han llenado
        if not all([name, lastname, email, password, tipo]):
            return "Todos los campos son obligatorios", 400

        # Inserta datos en la base de datos
        insert_perfil(name, lastname, email, password, tipo)

        return redirect(url_for('explorar_subastas'))

    return render_template('register.html')


def insert_perfil(name, lastname, email, password, tipo):
    conexion = db_connection()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()

        # Inserción en la tabla persona
        cursor.execute(
            "INSERT INTO persona (nombre, apellido, correo) VALUES (%s, %s, %s)",
            (name, lastname, email)
        )
        conexion.commit()

        id_persona = cursor.lastrowid  # Obtiene el ID de la persona insertada

        # Inserción en la tabla cliente u organizador según el tipo de usuario
        if tipo == 'Cliente':
            cursor.execute(
                "INSERT INTO cliente (contrasena, persona_id) VALUES (%s, %s)",
                (password, id_persona)
            )
        elif tipo == 'Organizador':
            cursor.execute(
                "INSERT INTO organizador (usuario, contrasena, persona_id) VALUES (%s, %s, %s)",
                (f"{name} {lastname}", password, id_persona)
            )
        else:
            return "Tipo de usuario no válido", 400

        conexion.commit()

    except Error as e:
        print(f"Error al insertar en persona/cliente/organizador: {e}")
    finally:
        cursor.close()
        conexion.close()


def insert_cliente(name, lastname, id_perfil):
    conexion = db_connection()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO Cliente (NOMBRES, APELLIDOS,ID_PERFIL) VALUES (%s, %s, %s)",
            (name, lastname, id_perfil)
        )
        conexion.commit()
    except Error as e:
        print(f"Error al insertar en Cliente: {e}")
    finally:
        cursor.close()
        conexion.close()


def insert_subastador(name, lastname, id_perfil):
    conexion = db_connection()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO subastador (NOMBRES, APELLIDOS, ID_PERFIL) VALUES (%s, %s, %s)",
            (name, lastname, id_perfil)
        )

        conexion.commit()
    except Error as e:
        print(f"Error al insertar en Subastador: {e}")
    finally:
        cursor.close()
        conexion.close()


# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
