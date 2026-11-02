"""Schémas du Lab 2 (PNG) : DAG, Kubeflow Pipelines, image projet, KFP et Airflow, flux du lab.

Régénérer (depuis la racine du repo) :
    uv run --no-project --with matplotlib python tools/diagrams/lab2_diagrams.py
Sortie : labs/m2-pipelines/img/*.png
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lab0_diagrams import (  # noqa: E402
    LIGHT,
    MUTED,
    NAVY,
    ORANGE,
    PALE_NAVY,
    PALE_ORANGE,
    PALE_TEAL,
    TEAL,
    WHITE,
    arrow,
    box,
    canvas,
    plt,
    title,
)

OUT = Path(__file__).resolve().parents[2] / "labs" / "m2-pipelines" / "img"
STEPS = ["ingest", "validate", "prepare", "train", "evaluate", "register"]


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, facecolor=WHITE)
    plt.close(fig)


# 0. Le Lab 2 en un coup d'œil ---------------------------------------------------------------
def flux_lab2():
    fig, ax = canvas(16, 7)
    title(
        ax,
        "Le Lab 2 en un coup d'œil",
        "Le pipeline du Lab 1 devient un DAG qui tourne dans le cluster, "
        "puis le même DAG avec Airflow, pour comparer.",
    )
    steps = [
        ("1", "Installer", "Kubeflow\nPipelines"),
        ("2", "Emballer", "le code du Lab 1\ndans une image"),
        ("3", "Décrire", "le pipeline\nen Python"),
        ("4-5", "Exécuter", "sur le cluster,\ntracé dans MLflow"),
        ("6", "Fiabiliser", "retries, ressources,\ncache"),
        ("7-9", "Comparer", "avec Airflow,\nrapport d'1 page"),
    ]
    for k, (num, name, sub) in enumerate(steps):
        x = 3 + k * 26
        box(
            ax,
            x,
            16,
            22,
            30,
            name,
            sub,
            fill=PALE_TEAL if k % 2 == 0 else PALE_NAVY,
            edge=TEAL if k % 2 == 0 else NAVY,
            ssize=9.5,
            tsize=12,
        )
        ax.text(x + 11, 49, f"étape {num}", ha="center", fontsize=10, color=MUTED)
        if k:
            arrow(ax, x - 4, 31, x, 31, "", color=NAVY, lw=1.6)
    ax.text(
        80,
        6,
        "Fin : pull request lab/m2-pipelines relue par le binôme, make check-m2 vert",
        ha="center",
        fontsize=11.5,
        color=ORANGE,
        fontweight="bold",
    )
    save(fig, "00-lab2-flux.png")


# 1. Séquence ou DAG -------------------------------------------------------------------------
def dag():
    fig, ax = canvas(16, 8.5)
    title(
        ax,
        "Un script qui enchaîne tout, ou un DAG ?",
        "DAG : un graphe d'étapes avec leurs dépendances, sans boucle. "
        "L'orchestrateur en déduit l'ordre, les reprises et le parallélisme.",
    )
    ax.text(
        3,
        63,
        "Avant : run.sh, une étape après l'autre",
        fontsize=12.5,
        color=MUTED,
        fontweight="bold",
    )
    for k, name in enumerate(["download", "validate", "train A", "train B", "evaluate"]):
        x = 3 + k * 31
        box(ax, x, 47, 25, 11, name, fill=LIGHT, edge=MUTED, tsize=11)
        if k:
            arrow(ax, x - 6, 52.5, x, 52.5, "", color=MUTED, lw=1.4)
    ax.text(
        3,
        41,
        "Une panne au milieu : tout s'arrête, personne ne le voit, on relance tout.",
        fontsize=10.5,
        color=MUTED,
    )
    ax.text(3, 33, "Après : un DAG", fontsize=12.5, color=NAVY, fontweight="bold")
    box(ax, 3, 13, 22, 11, "download", fill=PALE_TEAL, edge=TEAL, tsize=11)
    box(ax, 33, 13, 22, 11, "validate", fill=PALE_TEAL, edge=TEAL, tsize=11)
    box(ax, 66, 22, 22, 11, "train A", fill=PALE_TEAL, edge=TEAL, tsize=11)
    box(ax, 66, 4, 22, 11, "train B", fill=PALE_TEAL, edge=TEAL, tsize=11)
    box(ax, 99, 13, 22, 11, "evaluate", fill=PALE_ORANGE, edge=ORANGE, tsize=11)
    arrow(ax, 25, 18.5, 33, 18.5, "", color=NAVY)
    arrow(ax, 55, 20, 66, 27, "", color=NAVY)
    arrow(ax, 55, 17, 66, 10, "", color=NAVY)
    arrow(ax, 88, 27, 99, 20, "", color=NAVY)
    arrow(ax, 88, 10, 99, 17, "", color=NAVY)
    box(
        ax,
        126,
        4,
        32,
        29,
        "Ce qu'on gagne",
        "train A et B en parallèle\nune étape échoue :\non réessaie celle-là\nchaque run est tracé",
        fill=WHITE,
        edge=MUTED,
        ssize=10,
    )
    save(fig, "01-dag.png")


# 2. Kubeflow Pipelines : une étape = un pod ----------------------------------------------------
def kfp():
    fig, ax = canvas(16, 8.5)
    title(
        ax,
        "Kubeflow Pipelines : une étape = un pod",
        "Le pipeline est décrit en Python, compilé en YAML, envoyé au cluster ; "
        "chaque étape tourne dans son propre conteneur.",
    )
    box(
        ax,
        3,
        40,
        40,
        24,
        "Votre VM",
        "pipelines/scoring_pipeline.py\n→ scoring_pipeline.yaml\n"
        "(python -m pipelines.\nscoring_pipeline)",
        fill=LIGHT,
        edge=NAVY,
        ssize=9.5,
    )
    box(
        ax,
        3,
        6,
        40,
        24,
        "Image « projet »",
        "localhost:5001/\nscoring-pipeline:1.0.0\n= le code du Lab 1 (src/)",
        fill=PALE_ORANGE,
        edge=ORANGE,
        ssize=9.5,
    )
    box(
        ax,
        56,
        4,
        101,
        62,
        "Cluster kind — namespace kubeflow",
        "",
        fill=PALE_NAVY,
        edge=NAVY,
        title_top=True,
        tsize=12,
    )
    box(ax, 60, 46, 28, 12, "UI + API", "localhost:8080", fill=WHITE, edge=NAVY, ssize=9.5)
    box(ax, 92, 46, 30, 12, "Argo Workflows", "lance les pods", fill=WHITE, edge=NAVY, ssize=9.5)
    box(
        ax,
        126,
        46,
        28,
        12,
        "SeaweedFS interne",
        "artefacts entre étapes",
        fill=WHITE,
        edge=NAVY,
        ssize=9,
    )
    for k, name in enumerate(STEPS):
        x = 60 + k * 16
        box(ax, x, 18, 14, 14, name, "pod", fill=PALE_TEAL, edge=TEAL, tsize=9, ssize=8.5)
        if k:
            arrow(ax, x - 2, 25, x, 25, "", color=NAVY, lw=1.2)
    ax.text(
        107,
        8,
        "Chaque pod part de la même image ; les étapes se passent des fichiers typés "
        "(Dataset, Model, Metrics)",
        ha="center",
        fontsize=9.5,
        color=MUTED,
    )
    arrow(ax, 43, 52, 60, 52, "upload", color=NAVY, loff=(0, 1.2))
    arrow(ax, 43, 18, 60, 22, "docker push", color=ORANGE, loff=(0, 1.2))
    save(fig, "02-kfp-pods.png")


# 3. KFP et Airflow : même image, deux orchestrateurs --------------------------------------------
def kfp_airflow():
    fig, ax = canvas(16, 7.5)
    title(
        ax,
        "Même code, deux orchestrateurs",
        "Kubeflow et Airflow lancent tous les deux des pods avec la même image : "
        "seul l'orchestrateur change, pas le code.",
    )
    box(
        ax,
        56,
        26,
        48,
        20,
        "Image scoring-pipeline",
        "le code du Lab 1\n(src/, dataset.yaml)",
        fill=PALE_ORANGE,
        edge=ORANGE,
        ssize=10,
    )
    box(
        ax,
        3,
        26,
        42,
        20,
        "Kubeflow Pipelines",
        "dans le cluster\nUI : localhost:8080",
        fill=PALE_TEAL,
        edge=TEAL,
        ssize=10,
    )
    box(
        ax,
        115,
        26,
        42,
        20,
        "Airflow",
        "Docker Compose dans la VM\nUI : localhost:8081",
        fill=PALE_NAVY,
        edge=NAVY,
        ssize=10,
    )
    arrow(ax, 45, 36, 56, 36, "", color=TEAL)
    arrow(ax, 115, 36, 104, 36, "", color=NAVY)
    box(
        ax,
        30,
        3,
        100,
        16,
        "Les deux écrivent dans le même MLflow",
        "runs de l'expérience scoring, tag launched_by = kfp ou airflow",
        fill=WHITE,
        edge=MUTED,
        ssize=10,
    )
    save(fig, "03-kfp-airflow.png")


if __name__ == "__main__":
    for f in (flux_lab2, dag, kfp, kfp_airflow):
        f()
    print("Schémas écrits dans", OUT)
