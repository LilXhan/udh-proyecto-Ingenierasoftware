from flask import Flask, render_template, request
from clases.conexion import Conexion

app = Flask(__name__)

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
    nombre = request.form["nombre"]
    responsable = request.form["responsable"]
    ubicacion = request.form["ubicacion"]
    servicios = request.form.getlist('servicios')
    conexion = Conexion()
    conexion_local = conexion.obtener_conexion()
    with conexion_local.cursor() as cursor:
        sql = "INSERT INTO `establecimientos` (`nombre`, `ubicacion`, `responsable`) VALUES (%s, %s,  %s)"
        cursor.execute(sql, (nombre, ubicacion, responsable))
        # cursor.execute("INSERT INTO `establecimiento_servicio` (`establecimiento_id`, `servicio_id`) VALUES (%s, %s)", (last_id, servicio))
    conexion_local.commit()
    conexion_local.close()
    return f"usuario: {servicios}"

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

@app.route("/establecmientos/actualizar/<id>")
def establecimiento_actualizar(id):
    usuario = {}
    conexion = Conexion()
    conextion_local = conexion.obtener_conexion()
    with conextion_local.cursor() as cursor:
        cursor.execute(f'SELECT * FROM usuario where id = {id}')
        usuario = cursor.fetchall()
    conextion_local.close()
    return render_template("editarEstablecimientos.html", usuario=usuario)


# RUTAS SERVICIOS QUE OFRECE ESTABLECIMIENTOS