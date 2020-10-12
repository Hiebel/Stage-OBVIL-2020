import re

f = open("Fichiers_txt/PERRROT75CORR.txt", encoding="utf-8")
tokens_corr = f.read().split()
f.close()

f = open("Fichiers_txt/PERRROT75.txt", encoding="utf-8")
tokens_base = f.read().split()
f.close()

#léger problème d'alignement à résoudre
print(len(tokens_corr))
print(len(tokens_base))

dic_diag = {"Idem":0, "Diff":[]}

for i, mot_corr in enumerate(tokens_corr[:100]):
  if mot_corr == tokens_base[i]:
    dic_diag["Idem"]+=1
  else:
    dic_diag["Diff"].append([mot_corr, tokens_base[i]])

print(dic_diag)
print(dic_diag["Idem"], "mots communs")
print(len(dic_diag["Diff"]), "différences : ",dic_diag["Diff"])


