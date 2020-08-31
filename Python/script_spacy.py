import sys
import json
import glob
from lxml import etree
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

def lire_TEI_XML(input_file):
	namespace = "{http://www.tei-c.org/ns/1.0}text"
	parser = etree.XMLParser(recover=True)
	root = etree.parse(input_file, parser)
	contenu = ""
	for texte in root.iter(namespace):
		textes = texte.itertext()
		for cpt, el in enumerate(textes):
			if el != "\n":
				contenu += el
				contenu += " "
		contenu = contenu.replace("\n", " ")
	return contenu

# Dossier donné en paramètre du script
# C'est le nom du dossier qui contient les fichiers sur lesquels travailler
dossier = sys.argv[1]

# Liste des tags que l'on souhaite extraire
types = sys.argv[2:]

# Création du répertoire de sortie appelé "Spacy"
repertoire_Spacy = "Spacy"
if not os.path.exists(repertoire_Spacy):
	os.makedirs(repertoire_Spacy)

# Choix du format de sortie et création du dossier correspondant
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

# variable permettant de choisir la taille du contexte gauche et droite 
# le chiffre représente le nombre de caractères
taille_contexte = 30

# Boucle qui traite fichier par fichier
for fichier in glob.glob("%s/*" % dossier):
	nom_fichier = fichier.split("\\")[1]
	print(nom_fichier)
	
	# Récupération du contenu textuel du fichier (format XML-TEI ou txt)
	extension = fichier.split(".")[-1]
	if extension == "txt" or extension == "xml":
		if extension == "xml":
			contenu = lire_TEI_XML(fichier)
		else:
			with open(fichier, 'r', encoding = "utf-8") as fin:
				contenu = fin.read()
		doc = nlp(contenu)
		
		# pour la sortie en JSON
		if format == 0:
			dic_res = {}
			# boucle sur chaque entité détectée par Spacy
			for ent in doc.ents:
				if len(types) == 0 or ent.label_ in types:
					contexte = contenu[ent.start_char-taille_contexte:ent.end_char+taille_contexte]
					contexte = contexte.replace("\n", " ")
					resultatSpacy=ent.start_char,ent.end_char,ent.label_, contexte
					entite=list(resultatSpacy)
					dic_res[ent.text] = entite
					
			# définition du nom du fichier de sortie
			nom_sauvegarde = nom_fichier[:-4]
			if len(types) == 0:
				nom_sauvegarde += "_ALL"
			else:
				for el in types:
					nom_sauvegarde += "_%s" % el
					
			# création du fichier de sortie
			ecrire_json("%s/%s/%s.json" % (repertoire, dossier, nom_sauvegarde), dic_res)
			
		#pour la sortie en CSV
		else:
			csv = "Tag,Entité,Indice_Début,Indice_Fin,Contexte\n"
			# boucle sur chaque entité détectée par Spacy
			for ent in doc.ents:
				if len(types) == 0 or ent.label_ in types:
					#resultatSpacy=ent.label_, ent.text, ent.start_char, ent.end_char
					resultatSpacy=ent.label_, '"' + ent.text + '"', ent.start_char, ent.end_char
					ligne = ""
					for el in resultatSpacy:
						ligne += "%s," % el
					contexte = contenu[ent.start_char-taille_contexte:ent.end_char+taille_contexte]
					contexte = contexte.replace("\n", " ")
					ligne += contexte
					csv += ligne + "\n"
					
			# définition du nom du fichier de sortie
			nom_sauvegarde = nom_fichier[:-4]
			if len(types) == 0:
				nom_sauvegarde += "_ALL"
			else:
				for el in types:
					nom_sauvegarde += "_%s" % el
			
			# création du fichier de sortie
			file = open("%s/%s/%s.csv" % (repertoire, dossier, nom_sauvegarde), "w", encoding="utf-8")
			file.write(csv)
			file.close()