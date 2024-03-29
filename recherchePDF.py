import mysql.connector
from dotenv import load_dotenv
from os import getenv, path, remove, rename
from datetime import date

load_dotenv()

def loadDB():
    db = mysql.connector.connect(
        host = getenv("host_db"),
        user = getenv("user_db"),
        password = getenv("password_db"),
        database = "eureka"
    )
    return db

def log(action, titre, utilisateur="Undefined"): 
    
    today = date.today()
    heure = today.strftime("%H:%M:%S")

    with open("static/log/log.txt", "a") as log:
        log.write(utilisateur + " " + str(today) + " " + heure + " " + action + " " + titre + ".pdf\n")

def recherchePDF(tag):
    db = loadDB()
    mycursor = db.cursor()
    tag = "%" + tag + "%"
    sql = "SELECT titre, auteur, matiere, annee, type, description, source, date FROM Documents WHERE id_doc IN (SELECT id_doc FROM Referencement WHERE id_tag IN (SELECT id_tag FROM Tags WHERE nom like %s))"
    val = (tag,)

    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    db.close()

    return myresult

def rechercheListePDF(listeTags, annee=0, matiere=""):
    db = loadDB()
    mycursor = db.cursor()
    listeResult = []

    if annee != 0:
        sql = "SELECT titre, auteur, matiere, annee, type, description, source, date FROM Documents WHERE id_doc IN (SELECT id_doc FROM Documents WHERE annee = %s)"
        val = (annee,)

    if matiere != "":
        sql += " AND id_doc IN (SELECT id_doc FROM Documents WHERE matiere = %s)"
        val += (matiere,)

    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    listeResult.append(myresult)

    db.close()

    return listeResult

def afficheTout():
    db = loadDB()
    mycursor = db.cursor()
    sql = "SELECT titre, auteur, matiere, annee, type, description, source, date FROM Documents"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    db.close()

    return myresult

def uploadDB(file, auteur, tags, description, annee, type_doc, matiere, source):
    db = loadDB()
    mycursor = db.cursor()
    
    today = date.today()
    derniereMaj = today.strftime("%d/%m/%Y")

    tags = tags.split(";")
    tags = [tag.strip() for tag in tags]
    titre = file.filename.replace("_", " ")
    titre = titre.replace("/", "-")
    titre = titre.replace(".pdf", "")

    # check if the filename is already in the database
    sql = "SELECT titre FROM Documents WHERE titre = %s"
    val = (titre,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if len(myresult) != 0:
        db.close()
        return False
    
    tags.append(titre)
    tags.append(annee)
    tags.append(type_doc)
    tags.append(matiere)
    tags.append(auteur)
    tags.append(source)

    file.save("static/pdf/" + titre + ".pdf")

    tags = [tag.lower() for tag in tags]
    tags = list(dict.fromkeys(tags))
    tags = [tag for tag in tags if tag != ""]

    # TEMPORAIRE
    specialite = "ICy"

    sql = "INSERT INTO Documents (titre, auteur, source, description, matiere, annee, specialite, type, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (titre, auteur, source, description, matiere, annee, specialite, type_doc, derniereMaj,)

    mycursor.execute(sql, val)

    db.commit()

    for tag in tags:
        # vérifie si le tag existe déjà
        sql = "SELECT id_tag FROM Tags WHERE nom = %s"
        val = (tag,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            sql = "INSERT INTO Tags (nom) VALUES (%s)"
            val = (tag,)
            mycursor.execute(sql, val)
            db.commit()

        sql = "SELECT id_doc FROM Documents WHERE titre = %s ORDER BY id_doc DESC LIMIT 1"
        val = (titre,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        id_doc = myresult[0][0]

        sql = "INSERT INTO Referencement (id_doc, id_tag) VALUES (%s, (SELECT id_tag FROM Tags WHERE nom = %s))"
        val = (id_doc, tag)

        mycursor.execute(sql, val)

    db.commit()
    db.close()

    log("Ajout", titre)
    return True

def supprimePDF(titre, auteur, description):
    db = loadDB()
    mycursor = db.cursor()
    sql = "SELECT id_doc FROM Documents WHERE titre = %s AND auteur = %s AND description = %s"
    val = (titre, auteur, description,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    id_doc = myresult[0][0]

    # supprime les éléments de la table Referencement
    sql = "DELETE FROM Referencement WHERE id_doc = %s"
    val = (id_doc,)
    mycursor.execute(sql, val)

    # supprime l'élément de la table Documents
    sql = "DELETE FROM Documents WHERE id_doc = %s"
    val = (id_doc,)
    mycursor.execute(sql, val)

    db.commit()
    db.close()

    if path.exists("static/pdf/" + titre + ".pdf"):
        remove("static/pdf/" + titre + ".pdf")

    log("Suppression", titre)

def getInfos(titre, auteur, description):
    db = loadDB()
    mycursor = db.cursor()
    sql = "SELECT id_doc FROM Documents WHERE titre = %s AND auteur = %s AND description = %s"
    val = (titre, auteur, description,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    id_doc = myresult[0][0]

    sql = "SELECT nom FROM Tags WHERE id_tag IN (SELECT id_tag FROM Referencement WHERE id_doc = %s)"
    val = (id_doc,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    tags = [tag[0] for tag in myresult]

    db.close()

    return tags

def modifiePDF(titre, auteur, description, newTitre, newAuteur, newDescription, newTags, annee, type_doc, matiere, source):
    db = loadDB()
    mycursor = db.cursor()
    sql = "SELECT id_doc FROM Documents WHERE titre = %s AND auteur = %s AND description = %s"
    val = (titre, auteur, description,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    id_doc = myresult[0][0]

    today = date.today()
    derniereMaj = today.strftime("%d/%m/%Y")

    # TEMPORAIRE
    specialite = "ICy"

    # modifie Documents
    sql = "UPDATE Documents SET titre = %s, auteur = %s, description = %s, matiere = %s, annee = %s, type = %s, specialite = %s, source = %s, date = %s WHERE id_doc = %s"
    val = (newTitre, newAuteur, newDescription, matiere, annee, type_doc, specialite, source, derniereMaj, id_doc,)

    mycursor.execute(sql, val)

    db.commit()

    newTags = newTags.split(";")
    newTags = [tag.strip() for tag in newTags]
    newTags.append(titre)
    newTags.append(annee)
    newTags.append(type_doc)
    newTags.append(matiere) if matiere != "" else None
    newTags.append(source) if source != "" else None
    newTags.append(auteur) if auteur != "" else None
    newTags = [tag.lower() for tag in newTags]
    newTags = list(dict.fromkeys(newTags))
    newTags = [tag for tag in newTags if tag != ""]

    # modifie Referencement
    sql = "DELETE FROM Referencement WHERE id_doc = %s"
    val = (id_doc,)

    mycursor.execute(sql, val)

    db.commit()
    
    for tag in newTags:
        # vérifie si le tag existe déjà
        sql = "SELECT id_tag FROM Tags WHERE nom = %s"
        val = (tag,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            sql = "INSERT INTO Tags (nom) VALUES (%s)"
            val = (tag,)
            mycursor.execute(sql, val)
            db.commit()

        sql = "INSERT INTO Referencement (id_doc, id_tag) VALUES (%s, (SELECT id_tag FROM Tags WHERE nom = %s))"
        val = (id_doc, tag,)

        mycursor.execute(sql, val)
       

    src = "static/pdf/" + titre + ".pdf"
    dst = "static/pdf/" + newTitre + ".pdf"

    rename(src, dst)
    
    db.commit()
    db.close()

    log("Modification", titre)