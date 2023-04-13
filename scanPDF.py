import requests
from os import getenv, path, remove, rename
from dotenv import load_dotenv
from recherchePDF import *
import time 

load_dotenv()

apiKey = getenv("virusTotalAPI")

def scanPDF(pdfFile, titre, auteur, description, apiKey=apiKey):

    url = "https://www.virustotal.com/api/v3/files"
    pdfFile = pdfFile.replace(".pdf", "")
    file = "static/pdf/" + pdfFile + ".pdf"
    files = {"file": (path.basename(file), open(path.abspath(file), "rb"), "application/pdf")}
    headers = {"accept": "application/json",
               "x-apikey": apiKey,
               "Accept-Encoding": "gzip, deflate"
               }
    
    response = requests.post(url, files=files, headers=headers)

    if response.status_code != 200:
        supprimePDF(titre, auteur, description)
        return False
    if response.status_code == 200:
        response = response.json()
        fileID = response.get("data").get("id")

    url = "https://www.virustotal.com/api/v3/analyses/" + fileID

    response = requests.get(url, headers=headers)

    # affiche la réponse en texte brut

    print(response.text)


    if response.status_code != 200:
        supprimePDF(titre, auteur, description)
        return False
    if response.status_code == 200:
        response = response.json()
        status = response.get("data").get("attributes").get("status")

    while status != "completed":
        time.sleep(10)
        response = requests.get(url, headers=headers)
        response = response.json()
        status = response.get("data").get("attributes").get("status")


    response = response.get("data").get("attributes").get("results")

    for k in response:
        if response[k].get("category") == "malicious" or response[k].get("category") == "harmful":
            supprimePDF(titre, auteur, description)
            return False
        if response[k].get("category") == "malware":
            supprimePDF(titre, auteur, description)
            return False
        if response[k].get("category") == "suspicious":
            supprimePDF(titre, auteur, description)
            return False
    return True


def isPDF(pdfFile):
    # check if the extension is .pdf
    if pdfFile[-4:] != ".pdf":
        return False
    
