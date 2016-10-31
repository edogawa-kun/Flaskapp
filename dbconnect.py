from flask_mysqldb import MySQL

def conection():
    conn = MySQL.connect(host="localhost",
                         user="root",
                         passwd="arnav123",
                         db="flaskapp")
    c = conn.cursor()

    return c, conn