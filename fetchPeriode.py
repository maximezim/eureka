def getDictPeriode(annee):
    # liste avec les matieres de chaque periode
    liste = []
    for i in range(1, 5):
        nameToDb = {}
        nom = "static/listeMatieres/"+ str(annee) + "/" + str(i)+".txt"
        with open(nom, "r") as f:
            for line in f:
                (key, val) = line.split(":")
                val = val[:-1] if val[-1] == "\n" else val
                # remove space at the beginning of val
                val = val[1:] if val[0] == " " else val
                nameToDb[key] = val
        f.close()
        liste.append(nameToDb)
    return liste