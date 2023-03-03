from flask import Flask, session, url_for, render_template, redirect, request
from recherchePDF import recherchePDF, afficheTout, uploadDB, rechercheListePDF
from fetchPeriode import getDictPeriode
import mysql.connector
from dotenv import load_dotenv
from os import getenv
import bcrypt

from collections import Counter
load_dotenv()

def loadDB():
    db = mysql.connector.connect(
        host = getenv("host_db"),
        user = getenv("user_db"),
        password = getenv("password_db"),
        database = "eureka"
    )
    return db

app = Flask(__name__)
app.secret_key = 'la_cle_est_secrete'

def loggedin() :
    if (session.__contains__('loggedin')) :
        return session['loggedin']
    else :
        return False

@app.route("/")
def index():
    return render_template("index.html", loggedin = loggedin())

@app.route("/search", methods=['POST'])
def recherche():
    tag = request.form['search']
    if tag is not None and tag != "":
        # split tags by space
        tag = tag.split(" ")
        docs = []
        for t in tag:
            docs.append(recherchePDF(str(t)))
        print(docs)
        docs = [item for sublist in docs for item in sublist]
        docs = [item for items, c in Counter(docs).most_common()
                                      for item in [items] * c]
        docs = list(dict.fromkeys(docs))
        return render_template("menu.html", listeDocu = docs, loggedin = loggedin())
    return render_template("menu.html", listeDocu = afficheTout(), loggedin = loggedin())

@app.route("/recherche")
def rechercheMenu():
    matiere = request.args.get('matiere')
    if matiere:
        return render_template("menu.html", listeDocu = rechercheListePDF(matiere), loggedin = loggedin())
    return render_template("menu.html", listeDocu=recherchePDF(''), loggedin = loggedin())


@app.route("/search")
def tout():
    return render_template("menu.html", listeDocu = afficheTout(), loggedin = loggedin())

@app.route('/upload', methods = ['GET'])
def home():
    if session['loggedin']:
        mat = []
        for i in range(3, 6):
            mat.append(getDictPeriode(i))
        dict = {}
        for i in range(0, len(mat)):
            for j in range(0, len(mat[i])):
                dict.update(mat[i][j])
        return render_template('upload.html', username = session['pseudo'], listeMatieres=dict, loggedin = loggedin())
    return redirect(url_for('login'))

@app.route("/upload", methods=['POST'])
def uploadPost():
    if not session['loggedin']:
        return redirect(url_for('login'))
    
    file = request.files['file']
    auteur, tags, description, titre = request.form['auteur'], request.form['tags'], request.form['description'], request.form['titre']
    
    if titre is not None and titre != "":
        file.filename = titre + ".pdf"
    
    annee, type_doc, matiere = request.form['annee'], request.form['type_doc'], request.form['matiere']

    uploadDB(file, auteur, tags, description, annee, type_doc, matiere)
    return redirect(url_for('index'))

@app.route("/annee", methods=['GET'])
def annee():
    annee = request.args.get('annee')
    matiere = request.args.get('matiere')
    if matiere is None:
        matiere = ""
    listeMatieres = getDictPeriode(annee)
    liste = []
    listerecherche = []
    for dictMatieres in listeMatieres:
        for value in dictMatieres.items():
            listerecherche.append(value[1])
    liste = rechercheListePDF(listerecherche, str(annee), matiere)
    liste = [item for sublist in liste for item in sublist]

    return render_template("menuannee.html", listeDocu=liste, listeMatieres=listeMatieres, annee=annee, loggedin = loggedin())

@app.route('/login/', methods=['GET', 'POST'])
def login():

    msg = ''

    # Vérifie que le pseudo et le mot de passe sont corrects
    if request.method == 'POST' and 'pseudo' in request.form and 'password' in request.form:
        
        # Crée les variables pour faciliter la manipulation
        pseudo = request.form['pseudo']
        password = request.form['password']

        password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(password, salt)
        
        db = loadDB()
        mycursor = db.cursor()
        sql = "SELECT Password FROM Utilisateurs WHERE Pseudo = %s"
        val = (pseudo,)
        mycursor.execute(sql, val)
        # Récupère le résultat de la requête
        utilisateur = mycursor.fetchone()
        utilisateur = utilisateur[0]
        utilisateur = utilisateur.encode('utf-8')
        utilisateur = bcrypt.hashpw(utilisateur, salt)
        if utilisateur == password:
            # Crée les données de session
            session['loggedin'] = True
            session['pseudo'] = utilisateur[0]
            return redirect(url_for('home'))

        else :
            msg = "Nom d'utilisateur ou mot de passe invalide."
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():

    # Supprime les données de session*
    session.pop('loggedin', None)
    session.pop('pseudo', None)

    return render_template('index.html', loggedin = False)

if __name__ == "__main__" :
    app.run(host="0.0.0.0",port=80,debug=True)
