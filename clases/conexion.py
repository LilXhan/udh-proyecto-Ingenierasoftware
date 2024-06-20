import pymysql
import pymysql.cursors

class Conexion:
    host = "localhost"
    user = "root"
    password = "root"
    bd = "dbCentrosTuristicos"

    def obtener_conexion(self):
        return pymysql.connect(host = self.host,
                               user=self.user,
                               password=self.password,
                               db=self.bd)