#!/usr/bin/env bash
# =============================================================================
# Suivi des binômes (enseignant) : où en est chaque repo du mini-projet ?
#
#   ./tools/suivi_binomes.sh binomes.csv            # jalon j0 (défaut)
#   JALON=j1 ./tools/suivi_binomes.sh binomes.csv   # jalon j1, j2 ou final
#
# binomes.csv : une ligne par repo, séparateur « ; », lignes « # » ignorées :
#   groupe;binome;url_du_repo
#   SE;Alice Martin & Bob Durand;https://github.com/alice/mlops-cours-2026
#   BI;Chloé & Driss (option B, repo 1);https://github.com/chloe/mlops-cours-2026
#   BI;Chloé & Driss (option B, repo 2);https://github.com/driss/mlops-cours-2026
#
# Pour chaque repo : clone (ou mise à jour) dans SUIVI_DIR, se place sur le tag
# du jalon s'il existe (sinon sur main), puis lance le pré-contrôle du cours
# (labs/m10-capstone/check.sh --sans-cluster, dans sa version du repo du cours)
# et relève quelques indicateurs Git. Rien n'est poussé, rien n'est modifié chez
# les étudiants. Repos privés : il suffit que vous y soyez collaborateur et que
# git connaisse vos identifiants GitHub (clé SSH ou gestionnaire d'identifiants).
#
# Sortie : SUIVI_DIR/rapport-<jalon>-<date>.md (tableau) et .csv, plus le
# journal complet du pré-contrôle de chaque repo dans SUIVI_DIR/journaux/.
#
# Variables : SUIVI_DIR (défaut ~/suivi-mlops), COURS_DIR (votre clone du repo
# du cours, défaut : ce repo ; son .venv sert aux vérifications Python).
# =============================================================================
set -uo pipefail
CSV=${1:-}
[ -n "$CSV" ] && [ -f "$CSV" ] || { sed -n '4,13p' "$0" | sed 's/^# \{0,1\}//'; exit 64; }
JALON=${JALON:-j0}
case "$JALON" in j0 | j1 | j2 | final) ;; *) echo "JALON inconnu : $JALON"; exit 64 ;; esac
COURS_DIR=${COURS_DIR:-$(cd "$(dirname "$0")/.." && pwd)}
SUIVI_DIR=${SUIVI_DIR:-$HOME/suivi-mlops}
CHECK="$COURS_DIR/labs/m10-capstone/check.sh"
[ -f "$CHECK" ] || { echo "Introuvable : $CHECK (COURS_DIR=$COURS_DIR)"; exit 1; }
STAMP=$(date +%Y-%m-%d_%H%M)
mkdir -p "$SUIVI_DIR/repos" "$SUIVI_DIR/journaux"
MD="$SUIVI_DIR/rapport-${JALON}-${STAMP}.md"
OUT_CSV="$SUIVI_DIR/rapport-${JALON}-${STAMP}.csv"

{
  echo "# Suivi des binômes — jalon ${JALON} — $(date '+%Y-%m-%d %H:%M')"
  echo
  echo "| Groupe | Binôme | Repo | Tag ${JALON} | Pré-contrôle | Échecs | Journal | Labs dans l'historique | Auteurs | Commits perso | Branches lab/ext | Dernier commit perso |"
  echo "|---|---|---|---|---|---|---|---|---|---|---|---|"
} >"$MD"
echo "groupe;binome;repo;tag;tag_date;checks_ok;checks_total;echecs;journal;labs;auteurs;commits_perso;branches;dernier_commit_perso" >"$OUT_CSV"

while IFS=';' read -r groupe binome url || [ -n "${groupe:-}" ]; do
  groupe=$(echo "${groupe:-}" | tr -d '\r')
  url=$(echo "${url:-}" | tr -d '\r ')
  [ -z "$groupe" ] || [ "${groupe#\#}" != "$groupe" ] || [ "$groupe" = groupe ] && continue
  [ -n "$url" ] || continue
  slug=$(echo "$url" | sed -E 's#^(https://github.com/|git@github.com:)##; s#\.git$##; s#/#__#g')
  dir="$SUIVI_DIR/repos/$slug"
  echo "==> ${groupe} · ${binome} · ${url}"

  if [ -d "$dir/.git" ]; then
    git -C "$dir" checkout -q -f --detach 2>/dev/null
    git -C "$dir" fetch -q --tags --force origin 2>/dev/null
    ok_clone=$?
  else
    git clone -q "$url" "$dir" 2>/dev/null
    ok_clone=$?
  fi
  if [ "$ok_clone" -ne 0 ]; then
    echo "| ${groupe} | ${binome} | ${url} | — | inaccessible | — | — | — | — | — | — | — |" >>"$MD"
    echo "${groupe};${binome};${url};;;;;;;;;;;inaccessible" >>"$OUT_CSV"
    echo "    repo inaccessible (public ? vous êtes collaborateur ?)"
    continue
  fi

  # Historique du cours (repo modèle) : exclu des indicateurs, un fork le contient en entier
  git -C "$dir" fetch -q "$COURS_DIR" "+HEAD:refs/cours/main" 2>/dev/null
  if git -C "$dir" rev-parse -q --verify refs/cours/main >/dev/null; then
    not_cours=(--not refs/cours/main)
  else
    not_cours=()
  fi

  if git -C "$dir" rev-parse -q --verify "refs/tags/${JALON}" >/dev/null; then
    ref="refs/tags/${JALON}"
    tag="oui"
    tag_date=$(git -C "$dir" log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M' "$ref")
  else
    ref=$(git -C "$dir" symbolic-ref -q --short refs/remotes/origin/HEAD || echo origin/main)
    tag="non"
    tag_date=""
  fi
  git -C "$dir" checkout -q -f --detach "$ref"

  # Pré-contrôle du cours (version de l'enseignant), sans cluster ni appel réseau
  [ -e "$dir/.venv" ] || { [ -d "$COURS_DIR/.venv" ] && ln -s "$COURS_DIR/.venv" "$dir/.venv"; }
  mkdir -p "$dir/labs/m10-capstone"
  cp "$CHECK" "$dir/labs/m10-capstone/check.sh"
  log="$SUIVI_DIR/journaux/${slug}-${JALON}-${STAMP}.log"
  URL_CHECK=0 LOG_DIR="$SUIVI_DIR/journaux/${slug}-details" \
    bash "$dir/labs/m10-capstone/check.sh" --sans-cluster --jalon "$JALON" >"$log" 2>&1
  git -C "$dir" checkout -q -f "$ref" -- . 2>/dev/null
  git -C "$dir" clean -q -fd labs 2>/dev/null

  bilan=$(grep -E "échec\(s\) sur [0-9]+ vérifications|[0-9]+/[0-9]+ vérifications OK" "$log" | tail -1)
  total=$(echo "$bilan" | grep -oE '[0-9]+ vérifications|[0-9]+/[0-9]+' | grep -oE '[0-9]+' | tail -1)
  echecs=$(echo "$bilan" | grep -oE '^[0-9]+ échec' | grep -oE '[0-9]+' || true)
  [ -n "$echecs" ] || echecs=0
  [ -n "$total" ] || total=0
  okc=$((total - echecs))
  liste=$(grep '^❌ .*→' "$log" | sed -E 's/^❌ //; s/  →.*//' | paste -sd ',' - | sed 's/,/, /g' | tr '|' '/')
  [ -n "$liste" ] || liste="—"
  journal=0
  [ -f "$dir/docs/journal.md" ] &&
    journal=$(grep -cE '^## S[0-9]+ — [0-9]{4}-[0-9]{2}-[0-9]{2} — ' "$dir/docs/journal.md" || true)
  # Labs cités dans l'historique (fusions de PR « …/lab/mX-… » ou titres « lab/mX : … »)
  labs=$(git -C "$dir" log --format=%s "$ref" "${not_cours[@]}" | grep -oE 'lab/m[0-9]+' | sort -u -V | paste -sd ' ' -)
  [ -n "$labs" ] || labs="—"
  # Auteurs et commits des étudiants seulement (toutes les branches, hors historique du cours)
  auteurs=$(git -C "$dir" log --remotes=origin --format=%ae "${not_cours[@]}" | sort -u | grep -c .)
  perso=$(git -C "$dir" rev-list --count --remotes=origin "${not_cours[@]}")
  branches=$(git -C "$dir" branch -r --format='%(refname:lstrip=3)' | grep -E '^(lab|ext)/' |
    paste -sd ' ' -)
  [ -n "$branches" ] || branches="—"
  dernier=$(git -C "$dir" log -1 --remotes=origin --format=%cd --date=format:'%Y-%m-%d' \
    "${not_cours[@]}")
  [ -n "$dernier" ] || dernier="aucun"

  echo "| ${groupe} | ${binome} | [repo](${url}) | ${tag} ${tag_date} | ${okc}/${total} | ${liste} | ${journal} | ${labs} | ${auteurs} | ${perso} | ${branches} | ${dernier} |" >>"$MD"
  echo "${groupe};${binome};${url};${tag};${tag_date};${okc};${total};${echecs};${journal};${labs};${auteurs};${perso};${branches};${dernier}" >>"$OUT_CSV"
  echo "    tag ${JALON} : ${tag} · pré-contrôle ${okc}/${total} · journal ${journal} · labs : ${labs} · commits perso : ${perso} · branches : ${branches}"
done <"$CSV"

{
  echo
  echo "Auteurs, commits perso, branches et dernier commit : travail des étudiants seulement (hors historique"
  echo "du repo du cours, toutes branches poussées). Labs : fusions lab/mX présentes sur le jalon (ou main)."
  echo "Pré-contrôle lancé avec --sans-cluster : les make check-mX (cluster) ne sont pas rejoués ;"
  echo "le jalon se lit sur le tag s'il existe, sinon sur main. Détail par repo : ${SUIVI_DIR}/journaux/."
} >>"$MD"
echo
echo "Rapport : $MD"
echo "Tableur : $OUT_CSV"
