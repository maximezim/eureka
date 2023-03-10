from flask import Flask, session, url_for, render_template, redirect, request
from recherchePDF import recherchePDF, afficheTout, uploadDB, rechercheListePDF, deletePDF
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

@app.route("/")
def index():
    return render_template("index.html", listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin())

@app.route("/search", methods=['POST'])
def recherche():
    tag = request.form['search']
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
        return render_template("menu.html", listeDocu = docs, listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin())
    return render_template("menu.html", listeDocu = afficheTout(), listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin())

@app.route("/recherche")
def rechercheMenu():
    matiere = request.args.get('matiere')
    if matiere:
        return render_template("menu.html", listeDocu = rechercheListePDF(matiere), listeAnnees = listMatMenu, loggedin = loggedin())
    return render_template("menu.html", listeDocu=recherchePDF(''), listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin())

@app.route("/search")
def tout():
    return render_template("menu.html", listeDocu = afficheTout(), listeAnnees = listMatMenu, listeMatieres = getDictAll(), loggedin = loggedin())

@app.route('/upload', methods = ['GET'])
def home():
    if ('loggedin' in session):
        if session['loggedin']:
            mat = []
            for i in range(3, 6):
                mat.append(getDictPeriode(i))
            dict = {}
            for i in range(0, len(mat)):
                for j in range(0, len(mat[i])):
                    dict.update(mat[i][j])
            return render_template('upload.html', username = session['pseudo'], listeMatieres=dict, loggedin = loggedin(), msg ="")
    return redirect(url_for('login'))

@app.route("/upload", methods=['POST'])
def uploadPost():
    if ('loggedin' in session):
        if session['loggedin']:
            file = request.files['file']
            auteur, tags, description, titre = request.form['auteur'], request.form['tags'], request.form['description'], request.form['titre']
            
            if titre is not None and titre != "":
                file.filename = titre + ".pdf"
            
            annee, type_doc, matiere = request.form['annee'], request.form['type_doc'], request.form['matiere']

            uploadDB(file, auteur, tags, description, annee, type_doc, matiere)

            mat = []
            for i in range(3, 6):
                mat.append(getDictPeriode(i))
            dict = {}
            for i in range(0, len(mat)):
                for j in range(0, len(mat[i])):
                    dict.update(mat[i][j])

            return render_template('upload.html', username = session['pseudo'], listeMatieres=dict, loggedin = loggedin(), msg = titre + " upload??")
    return redirect(url_for('login'))

@app.route("/supp", methods=['GET'])
def supp():
    if ('loggedin' in session):
        if session['loggedin']:
            return render_template("suppression.html", msg = "", loggedin = loggedin())
    return redirect(url_for('login'))

@app.route("/supp", methods=['POST'])
def suppPost():
    if ('loggedin' in session):
        if session['loggedin']:
            titre = request.form['titre']
            deletePDF(titre)
            return render_template("suppression.html", msg = titre + " supprim??", loggedin = loggedin())
    return redirect(url_for('login'))

@app.route("/annee", methods=['GET'])
def annee():
    annee = request.args.get('annee')
    if annee not in ["3", "4", "5"]:
        return redirect(url_for('index'))
    matiere = request.args.get('matiere')
    if matiere is None:
        matiere = ""
    listeMatieres = getDictAll()
    liste = []
    listerecherche = []
    for dictMatieres in listeMatieres[int(annee) - 3]:
        for value in dictMatieres.items():
            listerecherche.append(value[1])
    liste = rechercheListePDF(listerecherche, str(annee), matiere)
    liste = [item for sublist in liste for item in sublist]

    return render_template("menuannee.html", listeDocu=liste, listeMatieres=listeMatieres, annee=annee, loggedin = loggedin())

@app.route('/login/', methods=['GET', 'POST'])
def login():

    msg = ''

    # V??rifie que le pseudo et le mot de passe sont corrects
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
        # R??cup??re le r??sultat de la requ??te
        utilisateur = mycursor.fetchone()
        utilisateur = utilisateur[0] if utilisateur else None
        if utilisateur is None:
            msg = "Nom d'utilisateur ou mot de passe invalide."
            return render_template('login.html', msg = msg)
        utilisateur = utilisateur.encode('utf-8')
        utilisateur = bcrypt.hashpw(utilisateur, salt)
        if utilisateur == password:
            # Cr??e les donn??es de session
            session['loggedin'] = True
            session['pseudo'] = utilisateur[0]
            return redirect(url_for('index'))

        else :
            msg = "Nom d'utilisateur ou mot de passe invalide."
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():

    # Supprime les donn??es de session*
    session.pop('loggedin', None)
    session.pop('pseudo', None)

    return render_template('index.html', listeMatieres = getDictAll(), loggedin = False)

if __name__ == "__main__" :
    app.run(host="0.0.0.0",port=80,debug=True)