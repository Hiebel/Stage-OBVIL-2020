import re

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

par_base = get_par("Fichiers_txt/PERRROT75.txt")
par_corr = get_par("Fichiers_txt/PERRROT75CORR.txt")

dic_diag = {"Idem":0, "Diff":[]}

for i, par in enumerate(par_corr):
  print(par_base[i][:10])
  print(par_corr[i][:10])
  print("")
  mots_base = par_base[i].split()
  for j, mot_corr in enumerate(par.split()):
    if j>len(mots_base)-1:
      dic_diag["Diff"].append([mot_corr, ""])
    elif mot_corr == mots_base[j]:
      dic_diag["Idem"]+=1
    else:
      dic_diag["Diff"].append([mot_corr, mots_base[j]])

print(dic_diag["Idem"], "mots communs")
print(len(dic_diag["Diff"]))
import json
name_out = "errors.json"
w = open(name_out, "w")
w.write(json.dumps(dic_diag["Diff"], indent=2, ensure_ascii=False))
w.close()

print(f"Erreurs : {name_out}")

