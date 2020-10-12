import re
from jiwer import wer

def get_par(path):
  f = open(path, encoding="utf-8")
  lignes  = f.readlines()
  f.close()
  liste_pars = []
  current_par = ""
  for l in lignes:
    if len(l)>3:
      current_par+=re.sub("\n", "", l)
    else:
      if len(current_par)>0:
        liste_pars.append(current_par)
        current_par = ""
  return liste_pars

par_base = get_par("Fichiers_txt/PERRROT75_correction.txt")
par_corr = get_par("Fichiers_txt/PERRROT75CORR.txt")

dic_diag = {"Idem":0, "Diff":[]}

eval_paragraphs = []
for i, par in enumerate(par_corr):
  VP, FP, FN = 0, 0, 0
  print(par_base[i][:10])
  print(par_corr[i][:10])
  print("")
  mots_base = par_base[i].split()
  for j, mot_corr in enumerate(par.split()):
    if j>len(mots_base)-1:
      dic_diag["Diff"].append([mot_corr, ""])
      FN+=1
    elif mot_corr == mots_base[j]:
      dic_diag["Idem"]+=1
      VP+=1
    else:
      dic_diag["Diff"].append([mot_corr, mots_base[j]])
      FP+=1
  accuracy = VP/(VP+FP+FN) 
  WER = wer(par, par_base[i])
  eval_paragraphs.append([accuracy, WER])
print(dic_diag["Idem"], "mots communs")
print(len(dic_diag["Diff"]))

for i, x in enumerate(eval_paragraphs):
  accuracy, WER = x
  print(x)
  score_cumul = round(accuracy+WER, 1)#est égal à 1 ou très proche sauf pb de tokenization
  if score_cumul>1.1 or score_cumul<0.9: #On a une distortion entre les deux
    words_corr = par_corr[i].split()
    for j, word_base in enumerate(par_base[i].split()):
      if j<len(words_corr):
        word_corr = words_corr[j]
      else:
        word_corr = "______"
      if word_base!=word_corr:
        print(f"{j}\t{word_base}\t{word_corr}")

import json
name_out = "errors.json"
w = open(name_out, "w", encoding="utf-8")
w.write(json.dumps(dic_diag["Diff"], indent=2, ensure_ascii=False))
w.close()

print(f"Erreurs : {name_out}")

