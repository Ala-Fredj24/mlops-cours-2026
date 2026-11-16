# Journal de bord du binôme

<!--
Mode d'emploi (à garder en tête du fichier) :
- Une entrée par séance (et par session de travail importante hors séance), la plus récente en bas.
- 3 à 5 lignes : qui a piloté, ce qui a été fait, ce qui a bloqué ou ce qui a été appris,
  la prochaine étape. Pas de roman : c'est un outil de pilotage, pas un rapport.
- Titre d'entrée au format exact « ## S<n> — AAAA-MM-JJ — <sujet> » (date réelle) :
  le pré-contrôle de rendu (make check-m10) compte les entrées datées.
- Liez les PR, issues et ADR (#12, docs/adr/0003-...). Les problèmes non résolus restent
  visibles : c'est précisément ce qui aide l'enseignant à vous débloquer.
- L'entrée d'exemple ci-dessous (date AAAA-MM-JJ) n'est pas comptée ; supprimez-la
  quand vous aurez écrit la vôtre.
-->

**Binôme :** @Ala-Fredj24, @wassimhaoues (Wassim Haoues) — option A (repo commun)
**Repo :** https://github.com/Ala-Fredj24/mlops-cours-2026
**Dataset :** german-credit (fil rouge)
**Extensions :** [À compléter au plus tard en fin de S5 : @pseudo-1 → ext/<nom> · @pseudo-2 → ext/<nom>]

<!-- Vos entrées commencent ici. Modèle :

## S1 — AAAA-MM-JJ — Lab 0 : setup

- **Pilote / copilote :**
- **Fait :**
- **Bloqué / appris :**
- **Prochaine étape :**

-->

## S1 — 2026-11-16 — Lab 1 : versioning

- **Pilote / copilote :** @wassimhaoues / @Ala-Fredj24 (Lab 0 piloté par Ala, fusionné : PR #1)
- **Fait :** stage DVC `download` + remote `s3://dvc-store/scoring` ; `prepare`/`train`/`evaluate` ; grid search 22 runs (4 types de modèles) ; `scoring-model` v3 `@champion` (run DVC, ROC AUC 0,8094, coût 108) ; Feast `scoring_v1`. `make check-m1` 18/18.
- **Bloqué / appris :** pull de `kindest/node` interrompu (réseau), relancé. Le seuil coût-optimal (0,318 avec `balanced`, 0,167 sans) compense presque entièrement `class_weight`.
- **Prochaine étape :** Ala rejoue le Lab 1 sur son cluster (encadré « Second membre du binôme »), puis pilote le Lab 2 (pipelines).
