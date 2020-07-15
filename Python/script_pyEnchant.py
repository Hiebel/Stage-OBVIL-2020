import enchant
import glob
from lxml import etree
import os
from enchant.checker import SpellChecker
import csv

# Fonction de lecture de fichier au format XML-TEI qui renvoie le contenu textuel de la balise "text"
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


# Chemin vers le dossier contenant les fichiers texte ou XML-TEI à corriger
dossier_corpus = "Corpus/test2"

# Chemin vers le dossier pour enregister les sorties
dossier_sortie = "%s_script_correction" % dossier_corpus

# Création du dossier de sortie s'il n'existe pas
if not os.path.exists(dossier_sortie):
	os.makedirs(dossier_sortie)

# Instance du vérificateur orthographique (la langue est entre parenthèses)
chkr = SpellChecker("fr")

# Chemin du fichier csv qui contiendra la liste des erreurs avec la correction proposée et le fichier d'origine
fichier_erreurs = "%s/erreurs.csv" % dossier_sortie

with open(fichier_erreurs, "w", encoding="utf-8", newline='') as csvfile:
	fieldnames = ["Erreur détectée", "Correction proposée", "Fichier"]
	spamwriter = csv.writer(csvfile, delimiter=",")
	spamwriter.writerow(fieldnames)
	
	for fichier in glob.glob("%s/*" % dossier_corpus):
		extension = fichier.split(".")[-1]
		if extension == "txt" or extension == "xml":
			print("Traitement du fichier %s" % fichier)
			nom_fichier = fichier.split("\\")[1]
			sans_extension = nom_fichier.split(".")[-2]
			if extension == "xml":
				contenu = lire_TEI_XML(fichier)
			else:
				with open(fichier, 'r', encoding = "utf-8") as fin:
					contenu = fin.read()
			chkr.set_text(contenu)
			for err in chkr:
				ligne = []
				ligne.append(err.word)
				if len(chkr.suggest(err.word)) > 0:
					err.replace(chkr.suggest(err.word)[0])
					ligne.append(chkr.suggest(err.word)[0])
				else:
					ligne.append("Pas de correction trouvée")
				ligne.append(nom_fichier)
				spamwriter.writerow(ligne)
			correction_contenu = chkr.get_text()
			with open("%s/%s_correction.txt" % (dossier_sortie, sans_extension), 'w', encoding="utf-8") as fout:
				fout.write(correction_contenu)