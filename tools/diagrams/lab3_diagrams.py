"""Schémas du Lab 3 (PNG) : flux du lab, les trois gates, contrat de données, drift, tests de modèle.

Régénérer (depuis la racine du repo) :
    uv run --no-project --with matplotlib python tools/diagrams/lab3_diagrams.py
Sortie : labs/m3-validation/img/*.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

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

OUT = Path(__file__).resolve().parents[2] / "labs" / "m3-validation" / "img"
RED = "#DC2626"
PALE_RED = "#FDECEC"


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, facecolor=WHITE)
    plt.close(fig)


# 0. Le Lab 3 en un coup d'œil ---------------------------------------------------------------
def flux_lab3():
    fig, ax = canvas(16, 7)
    title(
        ax,
        "Le Lab 3 en un coup d'œil",
        "Le pipeline du Lab 2 reçoit trois contrôles automatiques (des « gates ») : "
        "s'ils échouent, rien n'est entraîné ni enregistré.",
    )
    steps = [
        ("1", "Contrat", "suite Great Expectations\ngénérée depuis\ndataset.yaml"),
        ("2-3", "Gate 1", "le contrat devient\nune étape du pipeline\n(image 1.1.0)"),
        ("4", "Preuve", "données corrompues :\nle pipeline s'arrête"),
        ("5", "Gate 2", "drift entre\nentraînement et test\n(KS, χ², PSI)"),
        ("6", "Gate 3", "le modèle passe\nEvidently et des tests\ncomportementaux"),
        ("7", "Rapports", "pages HTML\ndans l'interface\nKubeflow"),
    ]
    for k, (num, name, sub) in enumerate(steps):
        x = 3 + k * 26
        gate = name.startswith("Gate")
        box(
            ax,
            x,
            12,
            22,
            34,
            name,
            sub,
            fill=PALE_ORANGE if gate else (PALE_TEAL if k % 2 == 0 else PALE_NAVY),
            edge=ORANGE if gate else (TEAL if k % 2 == 0 else NAVY),
            ssize=9,
            tsize=12,
        )
        ax.text(x + 11, 49, f"étape {num}", ha="center", fontsize=10, color=MUTED)
        if k:
            arrow(ax, x - 4, 29, x, 29, "", color=NAVY, lw=1.6)
    ax.text(
        80,
        4,
        "Fin : pull request lab/m3-validation relue par le binôme, make check-m3 vert",
        ha="center",
        fontsize=11.5,
        color=ORANGE,
        fontweight="bold",
    )
    save(fig, "00-lab3-flux.png")


# 1. Les trois gates du pipeline ------------------------------------------------------------
def gates():
    fig, ax = canvas(16, 8)
    title(
        ax,
        "Le pipeline du lab : trois gates qui peuvent tout arrêter",
        "Un gate est une étape comme une autre : si elle échoue, Kubeflow ne lance aucune "
        "des étapes qui en dépendent (fail-fast).",
    )
    y = 34
    plain = dict(fill=PALE_TEAL, edge=TEAL, tsize=10.5, ssize=8.5)
    gate = dict(fill=PALE_ORANGE, edge=ORANGE, tsize=10.5, ssize=8.5)
    box(ax, 2, y, 15, 14, "ingest", "téléchargement", **plain)
    box(ax, 21, y, 19, 14, "validate_data", "GATE 1 : contrat\n(Great Expectations)", **gate)
    box(ax, 44, y, 15, 14, "prepare", "split train/test", **plain)
    box(ax, 63, y, 19, 14, "detect_drift", "GATE 2 : drift\n(KS / χ² + PSI)", **gate)
    box(ax, 86, y, 15, 14, "train", "modèle", **plain)
    box(ax, 105, y + 12, 17, 12, "evaluate", "métriques", **plain)
    box(ax, 105, y - 10, 17, 14, "validate_model", "GATE 3 : Evidently\n+ tests pytest", **gate)
    box(ax, 140, y, 17, 14, "register", "MLflow\n@champion", fill=PALE_NAVY, edge=NAVY, tsize=10.5, ssize=8.5)
    arrow(ax, 17, y + 7, 21, y + 7, "", color=NAVY)
    arrow(ax, 40, y + 7, 44, y + 7, "", color=NAVY)
    arrow(ax, 59, y + 7, 63, y + 7, "", color=NAVY)
    arrow(ax, 82, y + 7, 86, y + 7, "", color=NAVY)
    arrow(ax, 101, y + 9, 105, y + 16, "", color=NAVY)
    arrow(ax, 101, y + 5, 105, y - 2, "", color=NAVY)
    arrow(ax, 122, y + 18, 140, y + 10, "", color=NAVY)
    arrow(ax, 122, y - 3, 140, y + 4, "", color=NAVY)
    box(
        ax,
        10,
        4,
        66,
        18,
        "Données corrompues (gate 1 en rouge)",
        "prepare, train, register ne sont jamais lancés :\npas de modèle construit sur de mauvaises données",
        fill=PALE_RED,
        edge=RED,
        ssize=9.5,
    )
    box(
        ax,
        86,
        4,
        71,
        18,
        "Chaque gate publie un rapport HTML",
        "visible dans l'interface Kubeflow (Visualization)\net des chiffres : n_failed, n_drifted, roc_auc",
        fill=WHITE,
        edge=MUTED,
        ssize=9.5,
    )
    save(fig, "01-gates.png")


# 2. Le contrat de données ------------------------------------------------------------------
def contrat():
    fig, ax = canvas(16, 8)
    title(
        ax,
        "Un contrat de données : ce qu'une donnée valide a le droit d'être",
        "La suite Great Expectations est générée une fois depuis dataset.yaml et des données "
        "propres, versionnée dans Git, puis vérifiée à chaque run.",
    )
    box(
        ax,
        3,
        26,
        34,
        36,
        "dataset.yaml",
        "colonnes, types\ncible et classes\nattributs sensibles",
        fill=LIGHT,
        edge=NAVY,
        ssize=10,
    )
    box(
        ax,
        50,
        26,
        52,
        36,
        "Suite gx/ : 67 expectations",
        "toutes les colonnes attendues sont là\nduration ≥ 1, age entre 18 et 100\n"
        "credit_risk ∈ {good, bad}\npurpose ∈ les modalités connues\npas de valeurs manquantes",
        fill=PALE_TEAL,
        edge=TEAL,
        ssize=10,
    )
    arrow(ax, 37, 44, 50, 44, "--build-suite", color=NAVY, loff=(0, 1.5))
    box(ax, 115, 44, 42, 18, "Données propres", "tout passe : exit 0\nle pipeline continue", fill=PALE_TEAL, edge=TEAL, ssize=10)
    box(ax, 115, 20, 42, 18, "Données corrompues", "une règle casse : exit 1\nle pipeline s'arrête", fill=PALE_RED, edge=RED, ssize=10)
    arrow(ax, 102, 50, 115, 53, "", color=TEAL)
    arrow(ax, 102, 38, 115, 29, "", color=RED)
    ax.text(
        80,
        8,
        "Règle d'or : on ne regénère jamais la suite à partir des données qu'on veut contrôler.",
        ha="center",
        fontsize=11.5,
        color=ORANGE,
        fontweight="bold",
    )
    save(fig, "02-contrat.png")


# 3. Le drift : même code, données qui bougent --------------------------------------------------
def drift():
    fig, ax = canvas(16, 8)
    title(
        ax,
        "Le drift : les données d'aujourd'hui ne ressemblent plus à celles d'hier",
        "Au lab, on simule une clientèle plus jeune, qui emprunte plus et plus longtemps, "
        "puis on mesure l'écart colonne par colonne.",
    )
    # Courbes schématiques (âge) : référence vs nouvelle clientèle, 8 ans plus jeune en moyenne
    xs = np.linspace(18, 75, 300)

    def curve(mu, sd):
        return np.exp(-0.5 * ((xs - mu) / sd) ** 2)

    x0, y0, w, h = 4, 14, 70, 40
    ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor=WHITE, edgecolor=MUTED, lw=1))
    for mu, sd, col, lab in ((36, 10, NAVY, "entraînement (référence)"), (28, 8, ORANGE, "nouvelles demandes")):
        ys = curve(mu, sd)
        px = x0 + (xs - 18) / (75 - 18) * w
        py = y0 + 2 + ys / ys.max() * (h - 8)
        ax.plot(px, py, color=col, lw=2.4)
        ax.fill_between(px, y0 + 2, py, color=col, alpha=0.12)
    ax.text(x0 + w / 2, y0 - 4, "âge du demandeur", ha="center", fontsize=10, color=MUTED)
    ax.text(x0 + w - 30, y0 + h - 5, "— entraînement", fontsize=10, color=NAVY, fontweight="bold")
    ax.text(x0 + w - 30, y0 + h - 9, "— nouvelles demandes", fontsize=10, color=ORANGE, fontweight="bold")
    # Tableau : résultat réel de src/detect_drift.py sur le scénario du lab
    box(ax, 82, 14, 75, 40, "", "", fill=LIGHT, edge=NAVY)
    rows = [
        ("Colonne", "p-value KS", "PSI", "Verdict"),
        ("duration", "< 0,001", "0,89", "DRIFT"),
        ("age", "< 0,001", "0,78", "DRIFT"),
        ("credit_amount", "< 0,001", "0,40", "DRIFT"),
        ("18 autres colonnes", "—", "< 0,25", "OK"),
    ]
    for i, row in enumerate(rows):
        yy = 48 - i * 7.5
        for j, cell in enumerate(row):
            xx = 85 + [0, 25, 43, 58][j]
            bold = i == 0 or cell == "DRIFT"
            color = RED if cell == "DRIFT" else (NAVY if i == 0 else "#0F172A")
            ax.text(xx, yy, cell, fontsize=10.5, color=color, fontweight="bold" if bold else "normal")
    ax.text(
        80,
        4,
        "Verdict = significatif (p-value < 0,05) ET important (PSI ≥ 0,25) ; "
        "le lot dérive si au moins 10 % des colonnes dérivent.",
        ha="center",
        fontsize=11,
        color=ORANGE,
        fontweight="bold",
    )
    save(fig, "03-drift.png")


# 4. Tester le modèle, pas seulement son score ---------------------------------------------------
def comportement():
    fig, ax = canvas(16, 7.5)
    title(
        ax,
        "Tester le comportement du modèle, pas seulement son score",
        "Trois familles de tests (CheckList), écrites dans tests/behavior.yaml et lancées "
        "par pytest avant l'enregistrement du modèle.",
    )
    cards = [
        (
            "Performance minimale",
            "ROC AUC ≥ 0,70 sur le test\net dans chaque sous-groupe\nsensible (âge, statut,\n"
            "travailleur étranger)",
            TEAL,
            PALE_TEAL,
        ),
        (
            "Invariance",
            "changer residence_since\n(ancienneté dans le logement)\nne change presque aucune\n"
            "décision (≤ 5 %)",
            NAVY,
            PALE_NAVY,
        ),
        (
            "Directionnel",
            "emprunter 50 % de plus,\nou 50 % plus longtemps,\nne doit pas faire baisser\nle risque prédit",
            ORANGE,
            PALE_ORANGE,
        ),
    ]
    for k, (name, sub, edge, fill) in enumerate(cards):
        box(ax, 4 + k * 52, 12, 48, 44, name, sub, fill=fill, edge=edge, tsize=13, ssize=10.5)
    ax.text(
        80,
        4,
        "Un test qui échoue bloque register : le modèle n'arrive jamais dans le registre.",
        ha="center",
        fontsize=11.5,
        color=ORANGE,
        fontweight="bold",
    )
    save(fig, "04-comportement.png")


if __name__ == "__main__":
    for f in (flux_lab3, gates, contrat, drift, comportement):
        f()
    print("Schémas écrits dans", OUT)
