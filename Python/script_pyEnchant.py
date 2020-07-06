import enchant
import glob
from lxml import etree
import os
from enchant.checker import SpellChecker

def lire_TEI_XML(input_file):
	namespace = "{http://www.tei-c.org/ns/1.0}"
	parser = etree.XMLParser(recover=True)
	root = etree.parse(input_file, parser)
	contenu = ""
	for texte in root.iter("{http://www.tei-c.org/ns/1.0}text"):
		textes = texte.itertext()
		for cpt, el in enumerate(textes):
			if el != "\n":
				contenu += el
				contenu += " "
		contenu = contenu.replace("\n", " ")
	return contenu


dossier_corpus = "Corpus/test"

dossier_sortie = "%s_script_correction" % dossier_corpus

if not os.path.exists(dossier_sortie):
	os.makedirs(dossier_sortie)

chkr = SpellChecker("fr")

for fichier in glob.glob("%s/*" % dossier_corpus):
	print(fichier)
	extension = fichier.split(".")[-1]
	if extension == "txt" or extension == "xml":
		nom_fichier = fichier.split("\\")[1]
		sans_extension = nom_fichier.split(".")[-2]
		if extension == "xml":
			contenu = lire_TEI_XML(fichier)
		else:
			with open(fichier, 'r', encoding = "utf-8") as fin:
				contenu = fin.read()
		chkr.set_text(contenu)
		for err in chkr:
			if len(chkr.suggest(err.word)) > 0:
				err.replace(chkr.suggest(err.word)[0])
		correction_contenu = chkr.get_text()
		with open("%s/%s.txt" % (dossier_sortie, sans_extension), 'w', encoding="utf-8") as fout:
			fout.write(correction_contenu)