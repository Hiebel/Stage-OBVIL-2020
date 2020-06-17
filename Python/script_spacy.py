import sys
import json
import glob
import xml.etree.ElementTree as ET
import spacy
import fr_core_news_sm
import os

def ecrire_json(chemin , contenu):
    file = open(chemin , "w", encoding="utf-8")
    file.write(json.dumps(contenu , indent=2, ensure_ascii=False))
    file.close()

def lire_json(chemin):
    file = open(chemin , "r", encoding="utf-8")
    dic = json.load(file)
    file.close()
    return dic

dossier = sys.argv[1]

repertoire_Spacy = "Spacy2"
if not os.path.exists(repertoire_Spacy):
	os.makedirs(repertoire_Spacy)

format = int(input("Sous quel format enregister les résultats ? (0 pour json, 1 pour csv)\n"))

if format == 0:
	repertoire = "%s/Jsons" % repertoire_Spacy
else:
	repertoire = "%s/CSV" % repertoire_Spacy
	
if not os.path.exists(repertoire):
	os.makedirs(repertoire)

rep_dossier = "%s/%s" % (repertoire, dossier)
if not os.path.exists(rep_dossier):
	os.makedirs(rep_dossier)
	
namespace = "{http://www.tei-c.org/ns/1.0}"
print("Chargement du module français de Spacy")
nlp = fr_core_news_sm.load()
print("Chargement terminé")

print("Affichage du fichier en cours de traitement")
for fichier in glob.glob("%s/*" % dossier):
	nom_fichier = fichier.split("\\")[1]
	print(nom_fichier)
	tree = ET.parse(fichier)
	root = tree.getroot()
	contenu = ""
	for text in root.iter("{http://www.tei-c.org/ns/1.0}text"):
		textes = text.itertext()
		for cpt, el in enumerate(textes):
			if el != "\n":
				contenu += el
				contenu += " "
		#contenu = contenu.replace("\n", " ")
		doc = nlp(contenu)
		if format == 0:
			dic_res = {}
			for ent in doc.ents:
				resultatSpacy=ent.start_char,ent.end_char,ent.label_
				entite=list(resultatSpacy)
				dic_res[ent.text] = entite
			ecrire_json("%s/%s/%s.json" % (repertoire, dossier, nom_fichier), dic_res)
		else:
			csv = ""
			for ent in doc.ents:
				resultatSpacy=ent.start_char,ent.end_char,ent.label_
				ligne = ""
				for el in resultatSpacy[:-1]:
					ligne += "%s," % el
				ligne += resultatSpacy[-1]
				csv += ent.text + ligne + "\n"
			file = open("%s/%s/%s.csv" % (repertoire, dossier, nom_fichier), "w", encoding="utf-8")
			file.write(csv)
			file.close()