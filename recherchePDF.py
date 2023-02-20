import mysql.connector
from dotenv import load_dotenv
from os import getenv

load_dotenv()

def recherchePDF(tag):
    db = mysql.connector.connect(
        host = getenv("host_db"),
        user = getenv("user_db"),
        password = getenv("password_db"),
        database = "eureka"
    )

    mycursor = db.cursor()

    if (tag == "") :

        sql = "SELECT titre, auteur, id_doc FROM Documents"

        mycursor.execute(sql)

    else:
        sql = "SELECT titre, auteur, id_doc FROM Documents WHERE id_doc IN (SELECT id_doc FROM Referencement WHERE id_tag = (SELECT id_tag FROM Tags WHERE nom like %s))"

        val = (tag,)

        mycursor.execute(sql, val)

    # Fetching all pdf
    myresult = mycursor.fetchall()

    # Closing the connection
    db.close()

    return myresult

def afficheTout():
    db = mysql.connector.connect(
        host = getenv("host_db"),
        user = getenv("user_db"),
        password = getenv("password_db"),
        database = "eureka"
    )

    mycursor = db.cursor()

    sql = "SELECT titre, auteur, id_doc FROM Documents"

    mycursor.execute(sql)

    # Fetching all pdf
    myresult = mycursor.fetchall()

    # Closing the connection
    db.close()

    return myresult