from clases.conexion import Conexion
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, Blueprint

from werkzeug.security import generate_password_hash, check_password_hash

import functools

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# INICIO
app.config.from_mapping(
    SECRET_KEY = 'dev'
)

def inicio_de_sesion_requerido(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.usuario is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# INICIO

@app.route('/')
def inicio():
    if g.usuario == None:
        return render_template("/index.html")
    else:
        return redirect(url_for('establecimiento_mostrar'))
    
@app.route('/establecimientos/')
def establecimientos():
    print(request.path)
    establecimientos = []
    conexion = Conexion()
    conextion_local = conexion.obtener_conexion()
    with conextion_local.cursor() as cursor:
        cursor.execute("""
                select 
                    e.id,
                    e.nombre as Nombre, 
                    e.ubicacion as Ubicacion, 
                    e.responsable as Responsable, 
                    group_concat(s.nombre SEPARATOR ', ') as Servicios 
                from establecimiento_servicio as es
                join establecimientos as e
                    on es.establecimiento_id = e.id
                join servicios as s
                    on es.servicio_id = s.id
                group by e.id, e.nombre, e.ubicacion, e.responsable""")
        establecimientos = cursor.fetchall()
    conextion_local.close()
    return render_template("/establecimientos/establecimientos.html", establecimientos=establecimientos)

# RUTAS ESTABLECIMIENTOS
# GET
@app.route("/establecimientos/mostrar/")
@inicio_de_sesion_requerido
def establecimiento_mostrar():
    establecimientos = []
    conexion = Conexion()
    conextion_local = conexion.obtener_conexion()
    with conextion_local.cursor() as cursor:
        cursor.execute("""
                select 
                    e.id,
                    e.nombre as Nombre, 
                    e.ubicacion as Ubicacion, 
                    e.responsable as Responsable, 
                    group_concat(s.nombre SEPARATOR ', ') as Servicios 
                from establecimiento_servicio as es
                join establecimientos as e
                    on es.establecimiento_id = e.id
                join servicios as s
                    on es.servicio_id = s.id
                group by e.id, e.nombre, e.ubicacion, e.responsable""")
        establecimientos = cursor.fetchall()
    conextion_local.close()
    return render_template("/establecimientos/mostrarEstablecimientos.html", establecimientos=establecimientos)

# POST
@app.route("/establecimientos/registrar/", methods=["POST", "GET"])
@inicio_de_sesion_requerido
def establecimiento_registrar():
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
    if request.method == 'POST':
        id = 0
        nombre = request.form["nombre"]
        responsable = request.form["responsable"]
        ubicacion = request.form["ubicacion"]
        servicios = request.form.getlist('servicios')
        with conexion_local.cursor() as cursor:
            cursor.execute('insert into `establecimientos` (`nombre`, `ubicacion`, `responsable`) values (%s, %s,  %s)', (nombre, ubicacion, responsable))
            cursor.execute('select id from `establecimientos` order by id desc limit 1')
            id = cursor.fetchone()[0]
        for servicio in servicios:
            with conexion_local.cursor() as cursor:
                cursor.execute("INSERT INTO `establecimiento_servicio` (`establecimiento_id`, `servicio_id`) VALUES (%s, %s)", (id, servicio))
        conexion_local.commit()
        conexion_local.close()
        return redirect(url_for('establecimiento_mostrar'))
    servicios = []
    with conexion_local.cursor() as cursor:
        cursor.execute("select * from servicios")
        servicios = cursor.fetchall()
    conexion_local.close()
    return render_template("/establecimientos/registrarEstablecimiento.html", servicios=servicios)


# PUT
@app.route("/establecimientos/actualizar/<id>", methods=["GET", "POST"])
@inicio_de_sesion_requerido
def establecimiento_actualizar(id):
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
    if request.method == 'POST':
        nombre = request.form["nombre"]
        responsable = request.form["responsable"]
        ubicacion = request.form["ubicacion"]
        servicios = request.form.getlist('servicios')

        with conexion_local.cursor() as cursor:
            cursor.execute(f'update `establecimientos` set `nombre`=%s, `responsable`=%s, `ubicacion`=%s where id=%s', (nombre, responsable, ubicacion, id))
            cursor.execute(f'delete from `establecimiento_servicio` where `establecimiento_id`=%s', (id))
        conexion_local.commit()
        for servicio in servicios:
            with conexion_local.cursor() as cursor:
                cursor.execute('insert into `establecimiento_servicio` (`establecimiento_id`, `servicio_id`) VALUES (%s, %s)', (id, servicio))
        conexion_local.commit()
        conexion_local.close()
        return redirect(url_for('establecimiento_mostrar'))
    establecimiento = ()
    servicios = ()
    with conexion_local.cursor() as cursor:
        cursor.execute(f"""
                select 
                    e.id,
                    e.nombre as Nombre, 
                    e.ubicacion as Ubicacion, 
                    e.responsable as Responsable, 
                    group_concat(s.nombre SEPARATOR ', ') as Servicios 
                from establecimiento_servicio as es
                join establecimientos as e
                    on es.establecimiento_id = e.id
                join servicios as s
                    on es.servicio_id = s.id
                where e.id = {id}
                group by e.id, e.nombre, e.ubicacion, e.responsable""")
        establecimiento = cursor.fetchone()

    with conexion_local.cursor() as cursor:
        cursor.execute("select * from servicios")
        servicios = cursor.fetchall()
    establecimiento_servicios = establecimiento[4]
    establecimiento_servicios = establecimiento_servicios.split(', ')
    conexion_local.close()
    return render_template("/establecimientos/editarEstablecimientos.html", establecimiento=establecimiento, establecimiento_servicios=establecimiento_servicios, servicios=servicios)

# DELETE
@app.route("/establecimientos/eliminar/<id>", methods=['DELETE', 'GET'])
@inicio_de_sesion_requerido
def establecimiento_eliminar(id):
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
    with conexion_local.cursor() as cursor:
        cursor.execute('delete from `establecimiento_servicio` where `establecimiento_id`=%s', (id))
    with conexion_local.cursor() as cursor:
        cursor.execute('delete from `establecimientos` where `id`=%s', (id,))
    conexion_local.commit()
    conexion_local.close()
    return redirect(url_for('establecimiento_mostrar'))

# RUTAS SERVICIOS QUE OFRECE ESTABLECIMIENTOS

@app.route("/servicios/registrar", methods=["GET", "POST"])
@inicio_de_sesion_requerido
def servicio_registrar():
    if request.method == 'POST':
        nombre = request.form["nombre"]
        conexion = Conexion()
        conexion_local = conexion.obtener_conexion()
        with conexion_local.cursor() as cursor:
            cursor.execute('insert into `servicios` (`nombre`) values (%s)', (nombre))
        conexion_local.commit()
        conexion_local.close()
        return redirect(url_for('establecimiento_mostrar'))
    return render_template("/servicios/registrarServicios.html")


# LOGIN AND REGISTRO DE USUARIOS

@app.route("/registro/", methods=["POST", "GET"])
def registro():
    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        email = request.form["email"]
        contraseña = request.form["contraseña"]

        conexion = Conexion()
        conexion_local = conexion.obtener_conexion()

        error = None
        usuario = None

        with conexion_local.cursor() as cursor:
            cursor.execute('select * from `usuarios` where email=%s', email)
            usuario = cursor.fetchone()

        if usuario == None:
            contraseña_encryptada = generate_password_hash(contraseña)
            with conexion_local.cursor() as cursor:
                cursor.execute('insert into `usuarios` (`nombre`, `apellidos`, `email`, `contraseña`) values (%s, %s, %s, %s)', (nombre, apellidos, email, contraseña_encryptada))
            conexion_local.commit()
            conexion_local.close()
            return redirect(url_for('login'))
        else:
            error = f'Email {email} ya está registrado'
        
        flash(error)

    return render_template('auth/registro.html')

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        contraseña = request.form["contraseña"]

        conexion = Conexion()
        conexion_local = conexion.obtener_conexion()

        error = None
        usuario = None

        with conexion_local.cursor() as cursor:
            cursor.execute('select * from `usuarios` where email=%s', email)
            usuario = cursor.fetchone()
        if usuario == None:
            error = 'Email incorrecto'
        elif not(check_password_hash(usuario[4], contraseña)):
            error = 'Contraseña incorrecta'
        
        if error is None:
            session.clear()
            session['usuario_id'] = usuario[0]
            return redirect(url_for('establecimiento_mostrar'))

        flash(error)

    return render_template('auth/login.html')

@app.before_request
def cargar_sesion_actual():
    usuario_id = session.get('usuario_id')
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()

    if usuario_id is None:
        g.usuario = None
    else:
        with conexion_local.cursor() as cursor:
            cursor.execute('select * from `usuarios` where id=%s', usuario_id)
            g.usuario = cursor.fetchone()

@app.route('/cerrar-sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('inicio'))

# 404

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('inicio'))