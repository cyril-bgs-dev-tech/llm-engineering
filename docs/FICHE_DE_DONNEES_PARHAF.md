# Fiche de données PARHAF (mise à jour du 04/10/2026, chiffres de `results/measures/splits_summary.json` et des mesures de la nuit)

Statut des données : comptes rendus cliniques **fictifs** en français ; aucune donnée de patient réel ; accès soumis aux conditions de PARHAF (voir `data/cards/` et `docs/LICENCES.md`).

## Composition
- 4 254 patients au parquet public ; 4 220 dans l'intersection avec le fichier JSON ; 1 code CIM-10 invalide exclu ; **4 219 patients utilisés** ; 6 185 documents ; 104 auteurs ; 20 spécialités.
- Cible : chapitre CIM-10 du diagnostic principal (17 chapitres évalués, `AUTRE` : 18 patients des chapitres VII, VIII, XVI et XVII fusionnés, exclue de la macro-F1).
- Effectifs par chapitre (développement et test confondus) : II 1 153 ; X 486 ; XIV 382 ; XI 368 ; IX 341 ; XVIII 260 ; III 209 ; XIII 186 ; XV 172 ; XIX 169 ; VI 127 ; I 113 ; V 63 ; IV 56 ; XXI 49 ; XII 36 ; XXII 31.
- Partitions (graine 20261002, empreinte `5c06b068…`) : test scellé 633 patients (jamais lu) ; développement 3 586 en cinq plis stratifiés par patient de 717 à 718 ; plis de contrôle groupés par auteur de 663 à 763.
- Longueur : médiane 1 143 tokens par patient (tokenizer Qwen), 95e centile 2 826, 60 % au-dessus de 1 024 ; 9 patients dépassent 4 096 tokens (aucun dans les chapitres rares).

## Points d'attention mesurés
- **Déséquilibre** : cinq chapitres de 27 à 63 patients portent 85 % de la variance de la macro-F1 ; au test : 4 à 9 patients par petit chapitre.
- **Auteurs** : 26 auteurs n'écrivent que dans un chapitre (21 % des patients) ; le style identifie l'auteur à 0,917 d'exactitude (66 auteurs d'au moins 20 patients, hasard 0,015) ; 169 des 171 paires de quasi-doublons à Jaccard 0,6 sont du même auteur ; l'identifiant d'auteur n'apparaît dans le texte que pour 1 patient sur 4 254. Signature d'auteur pure d'environ 2 points (leave-one-author-out) ; écart des plis groupés 5,06 points.
- **Spécialité** : elle détermine en grande partie le chapitre (TF-IDF hors spécialité : exactitude 0,522 contre 0,818) ; un entraînement débiaisé par auteur n'y change rien.
- **Ambiguïté d'étiquette** : au pli 0, tous les modèles se trompent pour 8,2 % des patients ; le bon chapitre est dans les deux premiers dans 95 % des cas ; 65 erreurs confiantes sur cinq plis (1,8 % des patients, surtout XVIII, II, XXI) : candidates à un audit d'étiquette source.
- **Pas de données temporelles réelles** : les dates sont fictives.

## Limites d'usage
Mesure méthodologique sur textes fictifs ; aucune généralisation à d'autres corpus, à des textes réels ou à un usage clinique ; toute extension de périmètre repasse par `dataset-intake` et le claim-gate.
