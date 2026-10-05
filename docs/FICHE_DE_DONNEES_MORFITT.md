# Fiche de données : MorFITT (ancrage RM-49)

| Champ | Valeur |
|---|---|
| Nom | MorFITT : corpus multi-étiquettes de résumés d'articles scientifiques français du domaine biomédical |
| Source de téléchargement | Hugging Face `DrBenchmark/MORFITT` (parquet `source/`), copie locale `data/raw/morfitt/` (ignorée par git) |
| Source de référence | dépôt GitHub `qanastek/MORFITT` ; benchmark DrBenchmark |
| Licence | **CC BY-SA 4.0** pour les données (code Apache-2.0), lue sur le dépôt GitHub le 05/10/2026 |
| Contenu | 3 624 résumés issus de PubMed / PMC Open Access, 12 spécialités (microbiologie, étiologie, virologie, physiologie, immunologie, parasitologie, génétique, chimie, vétérinaire, chirurgie, pharmacologie, psychologie), 5 116 annotations |
| Découpage | train 1 514, validation 1 022, test 1 088 (découpage officiel) |
| Données de patients | **aucune** : textes d'articles publiés |
| Tâche | multi-étiquettes ; métrique du papier de référence : F1 pondéré |
| Usage dans le projet | ancrage externe (RM-49) : mêmes outils que PARHAF, réglage sur validation, test public évalué une fois ; lecture **après** l'ouverture du test scellé de PARHAF |
| Résultats publiés cités | F1 pondéré, test : CamemBERT-bio 67,53 ; DrBERT 68,70 ; DrLongformer-CP 71,95 (arXiv 2402.16689, tableau 3 ; lus par résumé automatique : à vérifier dans le papier) |
| Coût | aucun (téléchargement de 3,4 Mo, calcul local) |
| Partage ShareAlike | tout jeu dérivé distribué devrait porter la même licence ; le projet ne redistribue pas le corpus |
