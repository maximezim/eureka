from flask import Flask, session, url_for, render_template, redirect, request
from recherchePDF import getInfos, modifiePDF, recherchePDF, afficheTout, supprimePDF, uploadDB, rechercheListePDF
from fetchPeriode import getDictAll, listeMatAnnees, getDictPeriode
import mysql.connector
from dotenv import load_dotenv
from os import getenv
import bcrypt
from collections import Counter

load_dotenv()
listMatMenu = listeMatAnnees()

def loadDB():
    db = mysql.connector.connect(
        host = getenv("host_db"),
        user = getenv("user_db"),
        password = getenv("password_db"),
        database = "eureka"
    )
    return db

app = Flask(__name__)
app.secret_key = getenv("secret_key")

def loggedin() :
    if (session.__contains__('loggedin')) :
        return session['loggedin']
    else :
        return False


# INDEX

@app.route("/")
def index():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    return render_template("index.html", listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin(), theme = cookie, avertissement = avertissement)


# MENU

@app.route("/search", methods=['POST'])
def recherche():
    tag = request.form['search']
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    if tag is not None and tag != "":
        # split tags by space
        tag = tag.split(" ")
        docs = []
        for t in tag:
            docs.append(recherchePDF(str(t)))
        docs = [item for sublist in docs for item in sublist]
        docs = [item for items, c in Counter(docs).most_common()
                                      for item in [items] * c]
        docs = list(dict.fromkeys(docs))
        return render_template("menu.html", listeDocu = docs, listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin(), annee = 0, theme = cookie, avertissement = avertissement)
    
    
    return render_template("menu.html", listeDocu = afficheTout(), listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin(), annee = 0, theme = cookie, avertissement = avertissement)

@app.route("/search")
def tout():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    return render_template("menu.html", listeDocu = afficheTout(), listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin(), annee = 0, theme = cookie, avertissement = avertissement)

@app.route("/supprime")
def suppPost():
    if ('loggedin' in session):
        if session['loggedin']:
            titre = request.args.get('titre')
            auteur = request.args.get('auteur')
            description = request.args.get('description')
            supprimePDF(titre, auteur, description)
            return redirect(url_for('recherche'))

    return redirect(url_for('login'))

@app.route('/modification')
def modification():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    if ('loggedin' in session):
        if session['loggedin']:
            titre = request.args.get('titre')
            auteur = request.args.get('auteur')
            description = request.args.get('description')
            source = request.args.get('source')
            annee = request.args.get('annee')
            type_doc = request.args.get('type_doc')
            matiere = request.args.get('matiere')
            tags = getInfos(titre, auteur, description)
            tagString = tags[0]
            tags.pop(0)
            for tag in tags:
                tagString += ";" + tag

            mat = []
            for i in range(3, 6):
                mat.append(getDictPeriode(i))
            dict = {}
            for i in range(0, len(mat)):
                for j in range(0, len(mat[i])):
                    dict.update(mat[i][j])

            return render_template("modification.html", matiere = matiere, type = type_doc, annee = annee, titre = titre, auteur = auteur, description = description, tags = tagString, source = source, loggedin = loggedin(), listeMatieres=dict, theme = cookie, avertissement = avertissement)

    return redirect(url_for('login'))

@app.route('/modification', methods=['POST'])
def modificationPost():
    if ('loggedin' in session):
        if session['loggedin']:
            titre = request.args.get('titre')
            auteur = request.args.get('auteur')
            description = request.args.get('description')
            newTitre = request.form['newTitre']
            newAuteur = request.form['newAuteur']
            newDescription = request.form['newDescription']
            newTags = request.form['newTags']
            annee = request.form['annee']
            type_doc = request.form['type_doc']
            matiere = request.form['matiere']
            source = request.form['newSource']

            modifiePDF(titre, auteur, description, newTitre, newAuteur, newDescription, newTags, annee, type_doc, matiere, source)

            return redirect(url_for('recherche'))

    return redirect(url_for('login'))


@app.route("/annee", methods=['GET'])
def annee():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    annee = request.args.get('annee')

    if annee not in ["3", "4", "5"]:
        return redirect(url_for('search'))
    matiere = request.args.get('matiere')

    if matiere is None:
        matiere = ""

    listeMatieres = getDictAll()
    liste = []
    listerecherche = []

    for dictMatieres in listeMatieres[int(annee) - 3]:
        for value in dictMatieres.items():
            listerecherche.append(value[1])
            
    liste = rechercheListePDF(listerecherche, int(annee), matiere)
    liste = [item for sublist in liste for item in sublist]

    return render_template("menu.html", listeDocu=liste, listeMatieres=listeMatieres, annee=annee, loggedin = loggedin(), theme = cookie, avertissement = avertissement)

@app.route("/divers", methods=['GET'])
def divers():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    listeMatieres = getDictAll()
    liste = rechercheListePDF(["divers", "Autre"], 6)
    liste = [item for sublist in liste for item in sublist]
    return render_template("menu.html", listeDocu=liste, listeMatieres=listeMatieres, annee=0, loggedin = loggedin(), theme = cookie, avertissement = avertissement)

# UPLOAD

@app.route('/upload', methods = ['GET'])
def upload():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    if ('loggedin' in session):
        if session['loggedin']:
            mat = []
            for i in range(3, 6):
                mat.append(getDictPeriode(i))
            dict = {}
            for i in range(0, len(mat)):
                for j in range(0, len(mat[i])):
                    dict.update(mat[i][j])
            dict["Autre"] = "divers"
            return render_template('upload.html', username = session['pseudo'], listeMatieres=dict, loggedin = loggedin(), msg ="", theme = cookie, avertissement = avertissement)
    return redirect(url_for('login'))

@app.route("/upload", methods=['POST'])
def uploadPost():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    if ('loggedin' in session):
        if session['loggedin']:
            file = request.files['file']
            auteur, tags, description, titre, source = request.form['auteur'], request.form['tags'], request.form['description'], request.form['titre'], request.form['source']
            
            if titre is not None and titre != "":
                file.filename = titre + ".pdf"
            
            annee, type_doc, matiere = request.form['annee'], request.form['type_doc'], request.form['matiere']

            res = uploadDB(file, auteur, tags, description, annee, type_doc, matiere, source)

            mat = []
            for i in range(3, 6):
                mat.append(getDictPeriode(i))
            dict = {}
            for i in range(0, len(mat)):
                for j in range(0, len(mat[i])):
                    dict.update(mat[i][j])
            if res == False:
                return render_template('upload.html', username = session['pseudo'], listeMatieres=dict, loggedin = loggedin(), msg = "Erreur lors de l'upload", theme = cookie, avertissement = avertissement)
            
            return render_template('upload.html', username = session['pseudo'], listeMatieres=dict, loggedin = loggedin(), msg = titre + " uploadé", theme = cookie, avertissement = avertissement)
    return redirect(url_for('login'))


# LOGIN

@app.route('/login/', methods=['GET', 'POST'])
def login():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")

    msg = ''

    # Vérifie que le pseudo et le mot de passe sont corrects
    if request.method == 'POST' and 'pseudo' in request.form and 'password' in request.form:
        pseudo = request.form['pseudo']
        password = (request.form['password']).encode('utf-8')
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(password, salt)
        
        db = loadDB()
        mycursor = db.cursor()
        sql = "SELECT Password FROM Utilisateurs WHERE Pseudo = %s"
        val = (pseudo,)
        mycursor.execute(sql, val)
        # Récupère le résultat de la requête
        utilisateur = mycursor.fetchone()
        utilisateur = utilisateur[0] if utilisateur else None
        if utilisateur is None:
            msg = "Nom d'utilisateur ou mot de passe invalide."
            return render_template('login.html', msg = msg)
        utilisateur = utilisateur.encode('utf-8')
        utilisateur = bcrypt.hashpw(utilisateur, salt)
        if utilisateur == password:
            # Crée les données de session
            session['loggedin'] = True
            session['pseudo'] = utilisateur[0]
            return redirect(url_for('index'))

        else :
            msg = "Nom d'utilisateur ou mot de passe invalide."
    return render_template('login.html', msg = msg, theme = cookie, avertissement = avertissement)


# LOGOUT

@app.route('/logout')
def logout():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")

    # Supprime les données de session*
    session.pop('loggedin', None)
    session.pop('pseudo', None)

    return render_template('index.html', listeMatieres = getDictAll(), loggedin = False, theme = cookie, avertissement = avertissement)


# ABOUT

@app.route('/about')
def about():
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    return render_template("about.html", loggedin = loggedin(), theme = cookie, avertissement = avertissement)

# 404

@app.errorhandler(404)
def page_not_found(e):
    cookie = request.cookies.get('theme', default="light")
    avertissement = request.cookies.get('avertissement', default="true")
    return render_template('404.html', theme = cookie, avertissement = avertissement), 404

if __name__ == "__main__" :
    app.run(host="0.0.0.0",port=80,debug=True)