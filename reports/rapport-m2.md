# Rapport Lab 2 :

Rapport de : Ala eddine Fredj
**Machine :** Intel Core i7-13620H, 15 Go de RAM, Ubuntu 24.04 · **Dataset :** `german-credit`

# 1. Contexte

J'ai repris le pipeline de credit scoring du Lab 1 et je l'ai fait tourner sur deux
orchestrateurs. Il compte six étapes : ingest, validate, prepare, train, evaluate et register.
Dans les deux cas, chaque étape tourne dans un pod du cluster kind `mlops-lab` avec la même
image (`scoring-pipeline:1.0.0`), qui contient le code du Lab 1 sans aucune modification. Le
module `pipelines/stage.py`, le serveur MLflow et le seuil de promotion sont communs. Les deux
pipelines donnent exactement le même résultat que `dvc repro` : ROC AUC de 0,809, seuil de
0,318 et coût métier de 108.

# 2. Résultats quantitatifs

| Mesure                                       | KFP                      | Airflow |
|---                                           |---                         |---|
| Installation de zéro (min)                   | ≈ 35                       | ≈ 15|
| Jusqu'au premier run réussi (min)            | ≈ 45                       | ≈ 3 |
| Run complet (min)                            | 4,3 au premier, puis 2,2   | 1,6 |
| Relance avec les mêmes paramètres (min)      | 2,3 (3 étapes en cache)    | 1,3 |
| Modifier une étape et voir le résultat (min) | ≈ 3 (estimé)               | ≈ 2 |
| Lignes de code propres à l'outil             | 284                        | 71 |
| Mémoire utilisée (Go)                        | ≈ 1,0                      | ≈ 1,9 |

Le module `stage.py` (156 lignes) est partagé et n'est compté dans aucune des deux colonnes.

# 3. Analyse qualitative

# Developer experience

KFP m'a demandé beaucoup plus d'effort. Il faut écrire des composants typés, mettre les imports
à l'intérieur des fonctions, compiler en YAML puis envoyer une nouvelle version à chaque
changement. Son installation a aussi été pénible : avec ma connexion lente, kustomize échouait
et j'ai dû cloner les manifests en local. En revanche, `kfp.local` m'a permis de tester tout le
pipeline en une minute sans cluster, et les artefacts typés évitent de gérer les fichiers à la
main. Avec Airflow, le DAG est court et se lit facilement, et il a marché presque du premier
coup. Par contre, c'est à moi de gérer le dossier de travail sur S3 et de faire passer les
valeurs par XCom.

# Scaling

Les deux outils lancent un pod par étape et permettent de fixer les ressources. Pour le ML, le
cache de KFP fait la différence : quand je change seulement un hyperparamètre, seul `train` est
relancé. Airflow rejoue tout. Sur 1 000 lignes ça ne coûte rien, mais avec une grosse ingestion
ce serait vite cher.

# Debugging

Dans KFP, chaque artefact est relié à son run et au run MLflow, donc je retrouve d'où vient un
modèle en un clic. Dans Airflow, je dois ouvrir les logs de chaque tâche et chercher les
fichiers dans S3. Les logs des pods restent accessibles dans les deux interfaces.

# 4. Recommandation

Je choisirais KFP pour une équipe ML qui travaille déjà sur Kubernetes et qui réentraîne souvent
ses modèles : le cache, les artefacts typés et la traçabilité valent l'installation plus
lourde. Je choisirais Airflow si l'entreprise l'utilise déjà pour ses pipelines de données, ou
si l'entraînement n'est qu'une étape parmi d'autres dans une chaîne planifiée. Dans ce cas, il
faut garder le calcul dans des pods (KubernetesPodOperator) et n'utiliser XCom que pour de
petites valeurs.

# 5. Limites de la comparaison

Tout a été mesuré sur mon seul PC, avec un cluster kind et une connexion lente qui gonfle les
temps d'installation. Le dataset ne fait que 1 000 lignes, donc je n'ai pas vraiment testé le
parallélisme ni la montée en charge. Je n'ai pas essayé KFP sur un cluster managé (GKE, EKS)
ni à plusieurs utilisateurs. Airflow tournait en CeleryExecutor avec Docker Compose, pas en
KubernetesExecutor. Enfin, les temps de modification d'une étape sont des estimations.
