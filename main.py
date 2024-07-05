from clases.conexion import Conexion
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
bootstrap = Bootstrap5(app)


# INICIO

@app.route('/')
def inicio():
    return render_template("/index.html")

# RUTAS ESTABLECIMIENTOS

@app.route("/establecimientos/registrar")
def establecimiento_registrar():
    servicios = []
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
    with conexion_local.cursor() as cursor:
        cursor.execute("select * from servicios")
        servicios = cursor.fetchall()
    conexion_local.close()
    return render_template("/establecimientos/registrarEstablecimiento.html", servicios=servicios)

@app.route("/establecimientos/guardar", methods=["POST"])
def establecimiento_guardar():
    id = 0
    nombre = request.form["nombre"]
    responsable = request.form["responsable"]
    ubicacion = request.form["ubicacion"]
    servicios = request.form.getlist('servicios')
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
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


@app.route("/establecimientos/mostrar")
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


@app.route("/establecimientos/actualizar/<id>")
def establecimiento_actualizar(id):
    establecimiento = ()
    servicios = ()
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
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

@app.route("/establecimientos/actualizar/guardar/<id>", methods=['POST'])
def establecimiento_actualizar_guardar(id):
    nombre = request.form["nombre"]
    responsable = request.form["responsable"]
    ubicacion = request.form["ubicacion"]
    servicios = request.form.getlist('servicios')
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
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


@app.route("/establecimientos/eliminar/<id>", methods=['DELETE', 'GET'])
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

@app.route("/servicios/registrar")
def servicio_registrar():
    return render_template("/servicios/registrarServicios.html")

@app.route("/servicios/guardar", methods=["POST"])
def servicio_guardar():
    nombre = request.form["nombre"]
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
    with conexion_local.cursor() as cursor:
        cursor.execute('insert into `servicios` (`nombre`) values (%s)', (nombre))
    conexion_local.commit()
    conexion_local.close()
    return redirect(url_for('establecimiento_mostrar'))

# LOGIN AND REGISTRO DE USUARIOS

@app.route("/registro", methods=["POST", "GET"])
def registro():
    if request.method == 'POST':
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        email = request.form["email"]
        contraseña = request.form["contraseña"]
        contraseña_encryptada = generate_password_hash(contraseña)
        conexion = Conexion()
        conexion_local = conexion.obtener_conexion()
        with conexion_local.cursor() as cursor:
            cursor.execute('insert into `usuarios` (`nombre`, `apellidos`, `email`, `contraseña`) values (%s, %s, %s, %s)', (nombre, apellidos, email, contraseña_encryptada))
        conexion_local.commit()
        conexion_local.close()
        return redirect(url_for('login'))
    return render_template('auth/registro.html')

@app.route("/login")
def login():
    return render_template('auth/login.html')

# 404

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('inicio'))