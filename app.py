from flask import Flask, session, url_for, render_template, redirect, request
from recherchePDF import recherchePDF, afficheTout, uploadDB, rechercheListePDF
from fetchPeriode import getDictPeriode
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

app = Flask(__name__)

app.secret_key = 'la_cle_est_secrete'

@app.route("/")
def index():
    return render_template("index.html", loggedin = session['loggedin'])

@app.route("/search", methods=['POST'])
def recherche():
    nameToDb = {}
    with open("nameToDb.txt", "r") as f:
        for line in f:
            (key, val) = line.split(":")
            val = val[:-1] if val[-1] == "\n" else val
            # remove space at the beginning of val
            val = val[1:] if val[0] == " " else val
            val.encode("utf-8")
            nameToDb[key] = val
    f.close()
    tag = request.form['search']
    listeDocu = recherchePDF(tag)
    if tag is None or tag == "":
        listeDocu = afficheTout()
    return render_template("menu.html", listeDocu = listeDocu, listeMatieres = nameToDb, loggedin = session['loggedin'])

@app.route("/recherche")
def rechercheMenu():
    nameToDb = {}
    with open("nameToDb.txt", "r") as f:
        for line in f:
            (key, val) = line.split(":")
            val = val[:-1] if val[-1] == "\n" else val
            # remove space at the beginning of val
            val = val[1:] if val[0] == " " else val
            val.encode("utf-8")
            nameToDb[key] = val
    f.close()
    matiere = request.args.get('matiere')
    if matiere:
        # perform search with filter
        listeDocu = recherchePDF(matiere)
    else:
        # perform search without filter
        listeDocu = recherchePDF('')
    return render_template("menu.html", listeDocu=listeDocu, listeMatieres=nameToDb, loggedin = session['loggedin'])


@app.route("/search")
def tout():
    nameToDb = {}
    with open("nameToDb.txt", "r") as f:
        for line in f:
            (key, val) = line.split(":")
            val = val[:-1] if val[-1] == "\n" else val
            # remove space at the beginning of val
            val = val[1:] if val[0] == " " else val
            nameToDb[key] = val
    f.close()
    listeDocu = afficheTout()
    return render_template("menu.html", listeDocu = listeDocu, listeMatieres = nameToDb, loggedin = session['loggedin'])

@app.route('/upload', methods = ['GET'])
def home():

    # Vérifie que l'utilisateur est connecté
    if session['loggedin']:
        mat = []
        for i in range(3, 6):
            mat.append(getDictPeriode(i))

        # create dictionnary from mat
        dict = {}
        for i in range(0, len(mat)):
            for j in range(0, len(mat[i])):
                dict.update(mat[i][j])


        return render_template('upload.html', username = session['pseudo'], listeMatieres=dict)

    return redirect(url_for('login'))

@app.route("/upload", methods=['POST'])
def uploadPost():
    # passw = request.form['password']
    # load_dotenv()
    # if passw != getenv("password_db"):
    #     return redirect(url_for('getUpload'))
    file = request.files['file']
    auteur = request.form['auteur']
    tags = request.form['tags']
    description = request.form['description']

    titre = request.form['titre']
    if titre is not None and titre != "":
        file.filename = titre + ".pdf"
    
    annee = request.form['annee']
    type_doc = request.form['type_doc']
    matiere = request.form['choix']

    uploadDB(file, auteur, tags, description, annee, type_doc, matiere)
    return redirect(url_for('index'))

@app.route("/annee", methods=['GET'])
def annee():
    annee = request.args.get('annee')
    matiere = request.args.get('matiere')
    if matiere is None:
        matiere = ""
    # Get the list of dictionaries with subjects for each period
    listeMatieres = getDictPeriode(annee)
    # liste docu = liste des documents retournés par la recherche avec les clés de nameToDb
    liste = []
    # get all the values of the keys for all periods
    listerecherche = []
    for dictMatieres in listeMatieres:
        for value in dictMatieres.items():
            listerecherche.append(value[1])
    liste = rechercheListePDF(listerecherche, str(annee), matiere)
    # merge all the lists in one
    liste = [item for sublist in liste for item in sublist]
    return render_template("menuannee.html", listeDocu=liste, listeMatieres=listeMatieres, annee=annee, loggedin = session['loggedin'])

@app.route('/login/', methods=['GET', 'POST'])
def login():

    msg = ''

    # Vérifie que le pseudo et le mot de passe sont corrects
    if request.method == 'POST' and 'pseudo' in request.form and 'password' in request.form:
        
        # Crée les variables pour faciliter la manipulation
        pseudo = request.form['pseudo']
        password = request.form['password']

        db = loadDB()
        mycursor = db.cursor()

        # Vérifie que le compte existe
        sql = "SELECT * FROM Utilisateurs WHERE Pseudo = %s AND Password = %s"
        val = (pseudo, password,)
        mycursor.execute(sql, val)
        
        # Récupère le résultat de la requête
        utilisateur = mycursor.fetchone()

        # Si le compte existe
        if utilisateur:
            # Crée les données de session
            session['loggedin'] = True
            session['pseudo'] = utilisateur[0]

            return redirect(url_for('home'))


    msg = "Nom d'utilisateur ou mot de passe invalide."
 
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():

    # Supprime les données de session
    session['loggedin'] = False
    session.pop('pseudo', None)

    return render_template('index.html', loggedin = session['loggedin'])

if __name__ == "__main__" :
    app.run(host="0.0.0.0",port=80,debug=True)