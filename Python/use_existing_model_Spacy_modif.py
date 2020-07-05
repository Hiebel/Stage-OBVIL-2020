import os, sys, glob
import random
import json

# Ajout - bibliothèque de lecture de documents XML
import xml.etree.ElementTree as ET

from collections import defaultdict
from pathlib import Path

import spacy
from spacy.lang.ar import Arabic
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span

#ici Chemin vers un modèle existant
model_name = 'models/fr_core_news_md'
#model_name = "models/ar-model-test"

# Chemin vers le dossier contenant les fichiers texte à annoter
input_dir = "input_corpus/"

# Chemin vers le dossier pour enregister les sorties
output_dir = "output/"

#ici optionel: Chemin vers une liste d'entités sous le format entité\tlabel\n
#Si on ne veut pas utiliser le fichier d'entités, laisser vide:  entities_file=""
#entities_file = "./input_resources/liste-entites-VentreParis.tsv"
entities_file = ""


#Désactiver le pipeline "ner", utile pour ne garder que les annotations des listes fournies
#True : on garde le module (annotation spacy + liste)
#False : on ne garde que les listes
ner = True
#ici je fournis les categories que je veux traiter, si vide (select_ent = []), spacy renvoie ttes ses categories, 
#sinon: select_ent = ['ORG'] ou select_ent = ['PERS', 'ORG']
#où trouver la liste des EN du modele Spacy???
select_ent = []

# Le séparateur des fichiers de sortie
# Modifier ici si besoin
separator = '\t'


#Class pour ajouter une liste d'entités
class CustomMatcher(object):
    name = ""
    def __init__(self, name, nlp, terms, label):
        """
            @name: str, le nom du pipeline
            @nlp: , le modèle de langue spacy
            @terms: list, liste de mots à ajouter
            @label: str, le label à attribuer aux nouvelles entités
        """

        self.name = name
        patterns = [nlp.make_doc(text) for text in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)



    def __call__(self, doc):
        #https://github.com/explosion/spaCy/issues/3608
        matches = self.matcher(doc)
        seen_tokens = set()
        entities = doc.ents
        new_entities = []
        for match_id, start, end in matches:
            if start not in seen_tokens and end - 1 not in seen_tokens: 
                new_entities.append(Span(doc, start, end, label=match_id)) 
                entities = [
                    e for e in entities if not (e.start < end and e.end > start)
                ]
            seen_tokens.update(range(start, end)) 
            doc.ents = entities + new_entities
        return doc


def add_pipes(nlp, entities_file=None):
    """Ajout des pipelines"""
    
    #Segmentation en phrases
    if 'sentencizer' not in nlp.pipe_names:
        sentencizer = nlp.create_pipe("sentencizer")
        nlp.add_pipe(sentencizer, first=True)



    if entities_file:
        try:
            with open(entities_file, 'r', encoding="utf-8") as fin:
                lst_entities = [(ligne.strip().split('\t')) for ligne in fin]
                #[['Nana', 'PERS'], ['Paris', 'LOCC']]

        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier '{entities_file}' n'existe pas")



        #Création d'un dictionnaire pour le 'CustomMatcher'
        #{"PERS": ['Nana', ...], "LOCC": ['Paris', ...]}

        entities = defaultdict(list)
        for entity in lst_entities:
            entities[entity[1]].append(entity[0])

        
        #Ajout des entités qui devront être matchées
        for label in entities:
            name = f"{label.lower()}_matcher"
            list_entities = entities[label]
            custom_matcher = CustomMatcher(name, nlp, list_entities, label)
            nlp.add_pipe(custom_matcher, after="ner")

    print(nlp.pipe_names)

    return nlp


#Annotation d'un texte et création du format requis pour l'entraînement
def creation_dataset(output_file, doc, filename, output_std=False, n=-1, separator='\t', select_ent=[]):
    """ Annotation d'un texte avec le module NER de Spacy
        Ecris dans un fichier le résultat, au format nécessaire
        pour l'entraînement d'un modèle
        output_file: le chemin du fichier à écrire
        doc: le document transformé par spacy (doc = nlp(un texte))
        output_std: affiche sur la sortie standard l'annotation
        n: un chiffre représentant un nombre de phrases à parcourir
    """

    #["Android Pay expands to Canada", {"entities": [[0, 11, "PRODUCT"], [23, 30, "GPE"]]}],
    sentences = []
    entities_counter = defaultdict(dict)
    output = []
    prev_len = 0

    for i, sentence in enumerate(doc.sents):
        entities = {'entities': []}
        for entity in sentence.ents:
        
            if not select_ent:
                pass
            elif not entity.label_ in select_ent:
                continue

            #Spacy considère l'ensemble du document comme une seule chaîne
            #Besoin de rapporter les indices à une seule phrase de taille n
            start = entity.start_char - prev_len
            end = entity.end_char - prev_len
            ent = [start, end, entity.label_]
            entities['entities'].append(ent)
            entity_text = ' '.join(entity.text.split())
            if output_std:
                print(entity_text,
                      entity.start_char, entity.end_char,
                      entity.label_)

            entities_counter[entity_text][entity.label_] = entities_counter[entity_text].get(entity.label_, 0)+1
            text = sentence.text.replace('\n', '*')
            fname = filename.split('\\')[-1]
            output.append([entity.label_, fname, text, entity_text, start, end])

        prev_len += len(sentence.text_with_ws)
        if entities['entities']:
            sent = ' '.join(sentence.text.split())
            sentences.append([sent, entities])

        i += 1
        if i == n:
            break
  
    # Ajout - Détection de l'extension pour le nom
    extension = input_file.split(".")[-1]
    output_file_json = os.path.join(output_dir, fname.replace('.%s' % extension, '-annot.json'))
    print(f"Création du fichier : '{output_file_json}'")
    with open(output_file_json, 'w', encoding="utf-8") as fout:
        json.dump(sentences, fout, ensure_ascii=False)
   

    output_file_occ = output_file_json.replace('-annot.json', '-occ.tsv')
    print(f"Création du fichier : '{output_file_occ}'")
    with open(output_file_occ, 'w', encoding="utf-8") as fout:
        for entity in entities_counter:
            for label, occ in entities_counter[entity].items():
                fout.write(f"{label}{separator}{entity}{separator}{occ}\n")

    output_file_entity = output_file_json.replace('-annot.json', '-ent.tsv')
    print(f"Création du fichier : '{output_file_entity}'")
    with open(output_file_entity, 'w', encoding="utf-8") as fout:
        for line in output:
            fout.write(f"{separator.join(map(str, line))}\n")


def make_doc(nlp, text, ner=None):
    if ner:
        doc = nlp(text)
    else:
        doc = nlp(text, disable=["tagger", "ner"])
    return doc

# Ajout - Fontion de lecture du contenu textuel d'un fichier XML-TEI
def lire_TEI_XML(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()
    contenu = ""
    for texte in root.iter("{http://www.tei-c.org/ns/1.0}text"):
        textes = texte.itertext()
        for cpt, el in enumerate(textes):
            if el != "\n":
                contenu += el
                contenu += " "
        contenu = contenu.replace("\n", " ")
    return contenu

#Chargement du modèle
try:
    nlp = spacy.load(model_name)
except OSError:
    raise OSError(f"Le modèle '{model_name}' n'existe pas")

nlp = add_pipes(nlp, entities_file)

for input_file in glob.iglob(f"{input_dir}/*"):
    
	#Ajout - Détection de l'extension pour la lecture
    extension = input_file.split(".")[-1]
	
	#Lecture du jeu de données d'entraînement
    if extension == "txt" or extension == "xml":
        try:
            with open(input_file, 'r', encoding="utf-8") as fin:
                if extension == "txt":
                    text = fin.read()
                elif extension == "xml":
                    text = lire_TEI_XML(input_file)
        except FileNotFoundError:
            print(f"Le fichier '{input_file}' n'existe pas")
            sys.exit(1)

        doc = make_doc(nlp, text, ner)

        #Tu peux modifier le séparateur pour les fichiers ci-dessous
        #Actuellement, c'est une tabulation '\t'
        creation_dataset(output_dir, doc, input_file, output_std=False, separator=separator, select_ent=select_ent)

os.system("pause")
