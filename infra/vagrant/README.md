# VM du cours (Windows) — Vagrant + Ansible

Sous Windows, le cours tourne dans **une VM Linux Ubuntu 24.04** créée par Vagrant et configurée
par Ansible. Elle remplace « Docker Desktop + WSL2 » : Docker, kind, kubectl, helm, k9s et uv
y sont installés automatiquement, aux versions du cours. Ensuite, **tout le cours se fait dans
la VM**, exactement comme sur un poste Linux.

| Fichier | Rôle |
|---|---|
| `Vagrantfile` | La machine : box `bento/ubuntu-24.04`, RAM / CPU, ports redirigés vers Windows |
| `playbook.yml` | Sa configuration (Ansible, idempotent) : installe les outils vérifiés aux étapes 1, 2 et 6.1 du Lab 0 |

## Pré-requis sur Windows

| Élément | Valeur |
|---|---|
| VirtualBox | 7.2 (Vagrant 2.4.9 reconnaît VirtualBox 7.0 à 7.2) |
| Vagrant | 2.4.9 |
| Virtualisation | VT-x / AMD-V activé dans le BIOS/UEFI |
| RAM du PC | 16 Go pour tout le cours (8 Go : Labs 0 et 1 seulement) |
| Disque libre | 40 Go (box ~1 Go, disque virtuel dynamique jusqu'à 64 Go) |

## Créer la VM

Téléchargez le repo du cours (bouton **Code** > **Download ZIP** sur GitHub, ou `git clone`),
puis, dans PowerShell :

```powershell
cd mlops-cours-2026-main\infra\vagrant
vagrant up                 # 15 à 25 min la première fois (box + paquets + outils)
vagrant ssh                # vous êtes dans la VM : utilisateur vagrant, Ubuntu 24.04
```

PC de 8 Go : `$env:VM_MEMORY=6144; vagrant up`. À partir du Lab 2 (PC de 16 Go), une fois :
`setx VM_MEMORY 12288; $env:VM_MEMORY=12288; vagrant reload`. `setx` garde le réglage pour les
prochaines fenêtres PowerShell : sans lui, le `vagrant up` suivant repartirait avec 8 Go.

> **Sortie attendue de `vagrant up`** : la fin du provisioning Ansible affiche les versions
> (Docker 29.x, Docker Compose v2.x, kubectl v1.37.1, helm v4.3.0, k9s v0.51.0, kind v0.33.0,
> uv 0.12.23) puis `PLAY RECAP … failed=0`.

Dans la VM, poursuivez le Lab 0 à l'**étape 1.2** (vérification des outils, déjà installés),
puis l'étape 3 (votre clé SSH GitHub se crée dans la VM). Clonez votre repo
**dans la VM** (`cd ~ && git clone git@github.com:VOTRE_USER/mlops-cours-2026.git`), jamais dans
le dossier partagé Windows : le système de fichiers Windows ralentit `uv` et DVC et casse les
liens symboliques.

## Accès depuis le navigateur Windows

Les port-forwards du cours (`make pf`, `make kfp-ui`…) écoutent sur `127.0.0.1` **dans la
VM**. Le playbook installe un petit relais (`socat`, unités `mlops-relay@PORT`) qui les republie
sur l'interface réseau NAT de la VM, et Vagrant redirige ces ports vers le `127.0.0.1` de
Windows. Rien n'est exposé au réseau de la salle.

| Port | Service | Lab |
|---|---|---|
| 5000 | MLflow | 0+ |
| 8888 | Filer SeaweedFS (interface web) | 0+ |
| 8333 | API S3 SeaweedFS | 0+ |
| 8080 | UI Kubeflow Pipelines | 2 |
| 30080 | Passerelle Kourier / KServe (publiée par kind) | 5 |
| 8443 | Argo CD | 6 |
| 3000 / 9090 / 9093 | Grafana / Prometheus / Alertmanager | 7 |

Un port déjà pris sous Windows est déplacé par Vagrant (`auto_correct`) : lisez le message
*Fixed port collision* au démarrage, ou `vagrant port`.

## Au quotidien

| Commande (PowerShell, dans `infra\vagrant`) | Effet |
|---|---|
| `vagrant suspend` / `vagrant resume` | Mettre la VM en pause et la reprendre **avec le cluster en marche** (recommandé entre deux séances) |
| `vagrant halt` / `vagrant up` | Éteindre / rallumer. Après rallumage : `kubectl get nodes`, puis `make pf` |
| `vagrant provision` | Rejouer Ansible (idempotent) après une mise à jour de ce dossier |
| `vagrant destroy -f` | Supprimer la VM **et le cluster** (données S3 et MLflow perdues) |

## Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `VT-x is not available` / la VM ne démarre pas | Virtualisation désactivée | Activer Intel VT-x / AMD-V (SVM) dans le BIOS/UEFI |
| VM très lente, icône « tortue » dans VirtualBox ; `vagrant up` en *Timed out while waiting for the machine to boot* ; nœuds kind `NotReady`, charge très élevée | Hyper-V / WSL2 / VBS (intégrité de la mémoire) actifs : VirtualBox tourne au-dessus d'Hyper-V (mode « NEM »), beaucoup plus lent, surtout pour le disque. Vérifier : `Select-String -Path "$env:USERPROFILE\VirtualBox VMs\mlops-vm\Logs\VBox.log" -Pattern "fall back to NEM"` (une ligne = mode lent) ; `bcdedit /enum | findstr hypervisorlaunchtype` (PowerShell administrateur) | PowerShell administrateur : `bcdedit /set hypervisorlaunchtype off` ; Sécurité Windows > Sécurité de l'appareil > Isolation du noyau > Intégrité de la mémoire : désactivée ; « Activer ou désactiver des fonctionnalités Windows » : décocher Hyper-V, Plateforme de machine virtuelle, Plateforme de l'hyperviseur Windows ; redémarrer. Cela coupe aussi WSL2, Docker Desktop et le bac à sable Windows. |
| Vagrant : version de VirtualBox non supportée | Vagrant trop ancien | Installer Vagrant 2.4.9 |
| `vagrant up` bloqué sur le téléchargement de la box | Réseau lent | Box fournie sur clé USB : `vagrant box add --name bento/ubuntu-24.04 .\ubuntu-24.04.box` |
| Ansible échoue sur un téléchargement | Coupure réseau | `vagrant provision` (idempotent) |
| `docker: permission denied` dans la VM | Session ouverte pendant le provisioning | `exit` puis `vagrant ssh` |
| `uv: command not found` | Idem | `exit` puis `vagrant ssh` (ou `source ~/.bashrc`) |
| `http://localhost:5000` ne répond pas sous Windows | `make pf` pas lancé, ou relais arrêté | Dans la VM : `make pf`, puis `systemctl status mlops-relay@5000` |
