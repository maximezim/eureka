import mysql.connector
from dotenv import load_dotenv
from os import getenv
load_dotenv()

def loadDB():
    db = mysql.connector.connect(
        host = getenv("host_db"),
        user = getenv("user_db"),
        password = getenv("password_db"),
        database = "eureka"
    )

    return db


def recherchePDF(tag):
    db = loadDB()
    mycursor = db.cursor()

    sql = "SELECT titre, auteur, id_doc FROM Documents WHERE id_doc IN (SELECT id_doc FROM Referencement WHERE id_tag = (SELECT id_tag FROM Tags WHERE nom like %s))"
    val = (tag,)

    mycursor.execute(sql, val)
    # Fetching all pdf
    myresult = mycursor.fetchall()
    # Closing the connection
    db.close()

    return myresult

def rechercheListePDF(listeTags, annee="", matiere=""):
    # A REFAIRE POUR OPTIMISER 
    # CEST MOCHE ET CA FAIT BEAUCOUP DE REQUETES
    # AIE
    # TODO
    db = loadDB()
    mycursor = db.cursor()
    listeResult = []
    
    for tag in listeTags:
        # select documents with the tag and then select documents with the annee and then select documents with the matiere
        sql = "SELECT titre, auteur, id_doc FROM Documents WHERE id_doc IN (SELECT id_doc FROM Referencement WHERE id_tag = (SELECT id_tag FROM Tags WHERE nom like %s))"
        val = (tag,)
        mycursor.execute(sql, val)

        # Fetching all pdf
        myresult = mycursor.fetchall()

        if annee != "":
            # must have the tag annee or the tag "autre"
            sql = "SELECT titre, auteur, id_doc FROM Documents WHERE id_doc IN (SELECT id_doc FROM Referencement WHERE id_tag = (SELECT id_tag FROM Tags WHERE nom like %s)) OR id_doc IN (SELECT id_doc FROM Referencement WHERE id_tag = (SELECT id_tag FROM Tags WHERE nom like 'autre'))"
            val = (annee,)
            mycursor.execute(sql, val)

            # Fetching all pdf
            myresult = mycursor.fetchall()

        if matiere != "":
            sql = "SELECT titre, auteur, id_doc FROM Documents WHERE id_doc IN (SELECT id_doc FROM Referencement WHERE id_tag = (SELECT id_tag FROM Tags WHERE nom like %s))"
            val = (matiere,)
            mycursor.execute(sql, val)

            # Fetching all pdf
            myresult = mycursor.fetchall()
        listeResult.append(myresult)

        # delete doublons
        listeResult = [list(t) for t in set(tuple(element) for element in listeResult)]
        
        
    # Closing the connection
    db.close()

    return listeResult

def afficheTout():
    db = loadDB()
    mycursor = db.cursor()
    sql = "SELECT titre, auteur, id_doc FROM Documents"
    mycursor.execute(sql)

    # Fetching all pdf
    myresult = mycursor.fetchall()

    # Closing the connection
    db.close()

    return myresult

def isPDF(file):
    if not file.filename.endswith(".pdf"):
        return False
    # check if the content of the file is a pdf and not a fake pdf
    # TODO
    return True

def uploadDB(file, auteur, tags, description, annee, type_doc):
    # if not isPDF(file):
    #     return False
    db = loadDB()
    tags = tags.split(";")
    tags = [tag.strip() for tag in tags]

    titre = file.filename.replace("_", " ")
    titre = titre.replace(".pdf", "")

    tags.append(titre)
    tags.append(annee)
    tags.append(type_doc)

    # put the file into the server folder "static/pdf"
    file.save("static/pdf/" + titre + ".pdf")

    cpt = getenv("cpt")

    mycursor = db.cursor()

    # use cpt as id value
    sql = "INSERT INTO Documents (titre, auteur, description) VALUES (%s, %s, %s)"
    val = (titre, auteur, description)

    mycursor.execute(sql, val)

    db.commit()

    id_doc = cpt

    for tag in tags:
        # check if tag in database else create it
        sql = "SELECT * FROM Tags WHERE nom = %s"
        val = (tag,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            sql = "INSERT INTO Tags (nom) VALUES (%s)"
            val = (tag,)
            mycursor.execute(sql, val)
            db.commit()

        sql = "SELECT id_doc FROM Documents WHERE titre = %s"
        val = (titre,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        id_doc = myresult[0][0]

        sql = "INSERT INTO Referencement (id_doc, id_tag) VALUES (%s, (SELECT id_tag FROM Tags WHERE nom = %s))"
        val = (id_doc, tag)

        mycursor.execute(sql, val)

    db.commit()

    # Closing the connection
    db.close()

def deletePDF(titre):
    db = loadDB()
    mycursor = db.cursor()

    titre = titre.replace("_", " ")
    titre = titre.replace(".pdf", "")
    # get id_doc
    sql = "SELECT id_doc FROM Documents WHERE titre = %s"
    val = (titre,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    id_doc = myresult[0][0]

    # delete from Referencement
    sql = "DELETE FROM Referencement WHERE id_doc = %s"
    val = (id_doc,)
    mycursor.execute(sql, val)

    # delete from Documents
    sql = "DELETE FROM Documents WHERE id_doc = %s"
    val = (id_doc,)
    mycursor.execute(sql, val)

    db.commit()

    # Closing the connection
    db.close()