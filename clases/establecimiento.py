class Establecimiento:
    def __init__(self, nombre: str, ubicacion: str):
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.servicios_ofrecidos = []
        self.responsable = None
        self.actividades_capacitacion = []