# Prompt Master - Audit + optimisation v0.2

Date : 2026-08-09
Statut : STABLE-DEPENDANT
Source auditee : `prompt-master-systematique.txt`
Sortie : rapport + proposition de compression par dictionnaire
Preuve : audit local, 377 lignes, 4098 mots, 27347 caracteres

## Verdict

Le Prompt Master est pertinent sur le fond, mais trop verbeux.

Les consignes principales sont prises en compte :
- mode normal vs mode DEV
- verification avant affirmation
- Git sans push automatique
- tests avant livraison
- scope strict
- suivi projet
- canaux Stable / Dev / Exp
- sessions longues via tmux
- footer strict obligatoire en Mode DEV strict

Le probleme n'est pas la qualite des regles. Le probleme est la redondance.

## Problemes trouves

### 1. Trop de repetitions

Occurrences mesurees :
- `dev` : 44
- `test` : 27
- `prompt` : 26
- `git` : 24
- `commit` : 13
- `lien` : 13
- `jamais` : 13
- `confirmation` : 9

Impact :
- charge inutile dans le contexte
- risque de contradictions futures
- plus difficile a maintenir
- plus difficile pour un autre agent de savoir quelle regle domine

### 2. Meme regle presente a plusieurs endroits

Exemples :
- `push seulement apres confirmation` apparait dans Git, Prompt Master, rapport final et canaux.
- `tester avant livraison` apparait dans Qualite, Test, Execution, Strict.
- `suivi projet` est detaille dans Suivi, puis resume dans Prompt generique.
- `format reutilisable` est present dans Qualite, Format reutilisable, Prompt generique.

Action recommandee :
- garder une seule regle canonique
- utiliser des references courtes ailleurs

### 3. Le dictionnaire existe mais ne compresse pas assez

Le dictionnaire actuel traduit surtout des symboles (`PATH`, `->`, `=`).
Il ne factorise pas les grandes procedures.

Action recommandee :
- ajouter un dictionnaire de blocs :
  - `GIT_SAFE`
  - `TEST_REAL`
  - `SCOPE_STRICT`
  - `PROJECT_TRACKING`
  - `DELIVERABLE`
  - `STRICT_FOOTER`
  - `SESSION_RECOVERY`

### 4. Trop de sections proches

Sections proches :
- Qualite
- Verification et outils
- Test
- Execution
- Rapport final DEV
- Mode DEV strict

Action recommandee :
- transformer en couches :
  1. Toujours actif
  2. Mode normal
  3. Mode DEV
  4. Mode DEV strict
  5. Dictionnaire de procedures

### 5. Le prompt generique duplique le Prompt Master

La section `PROMPT GENERIQUE - ASSISTANT DEV APP` repete des regles deja presentes.

Action recommandee :
- en faire un raccourci :
  - `PROFILE_DEV_APP = MODE_DEV + UI_APP + PROJECT_TRACKING + GIT_SAFE + TEST_REAL`

## Ce qui est bon et doit rester

- Contexte utilisateur prioritaire.
- Gate Mode DEV.
- Interdiction d'inventer.
- Confirmation avant action irreversible.
- Push interdit sans accord explicite.
- Tests reels avant livraison.
- Scope strict.
- Suivi `CHAT.md` et `RESTORE.md`.
- Canaux Stable / Dev / Exp.
- Footer strict obligatoire uniquement en Mode DEV strict.
- Regle `tmux` pour sessions longues.

## Optimisation recommandee

Passer de :

```text
377 lignes / 4098 mots
```

a :

```text
120-170 lignes / environ 1600-2200 mots
```

Methode :
- conserver les regles critiques en texte clair
- compresser les procedures repetitives en dictionnaire
- remplacer les redites par des alias
- garder les templates de sortie courts

## Dictionnaire propose

```text
GIT_SAFE =
  verifier status/remote avant modification ;
  proteger changements utilisateur ;
  commit atomique si tests OK ;
  push uniquement sur accord explicite ;
  signaler depot/remote absent.

TEST_REAL =
  tester avant d'annoncer ;
  build/lint/unit/integration/launch/feature/regression/link selon contexte ;
  si impossible : [NON TESTE] + limite.

SCOPE_STRICT =
  toucher seulement le perimetre demande ;
  pas de refactor/renommage/design/architecture hors scope ;
  action irreversible = confirmation.

PROJECT_TRACKING =
  maintenir suivi-(projet) : STATE, Features, todo, REGRESSION, OPEN_SOURCE, SETUP, RELEASES, CHAT, RESTORE ;
  mettre a jour CHAT/RESTORE apres cycle long.

DELIVERABLE =
  fournir chemin/lien cliquable ;
  livrable utilisable ;
  prompt/texte reutilisable en un bloc ;
  copier avec pbcopy si demande ou utile.

SESSION_RECOVERY =
  pour travail long : tmux ;
  opencode dans bon cwd ;
  verifier tmux/process avant d'affirmer recuperable ;
  documenter reprise dans RESTORE.

STRICT_FOOTER =
  obligatoire en Mode DEV strict ;
  valeurs inconnues = — ou indisponible ;
  format fixe.
```

## Recommandation

Ne pas remplacer directement le Prompt Master actuel.

Faire plutot :
1. creer `prompt-master-compact-dictionnaire_v0.1.txt`
2. le tester sur 5 taches reelles
3. comparer oublis / qualite / longueur
4. seulement ensuite promouvoir comme source officielle

## Risque

Une compression trop forte peut faire perdre :
- les garde-fous juridiques/irreversibles
- le comportement Git attendu
- la nuance Mode normal vs Mode DEV
- la reprise projet apres crash

Conclusion : dictionnaire oui, mais avec alias explicites et tests d'usage.
