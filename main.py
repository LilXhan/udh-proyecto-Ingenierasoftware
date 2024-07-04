from clases.conexion import Conexion
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
bootstrap = Bootstrap5(app)


# INICIO

@app.route('/')
def inicio():
    return render_template("/index.html")