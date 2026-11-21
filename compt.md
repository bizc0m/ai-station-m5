# Comptage prompt

ACT : compter chaque réponse assistant.

Objectif :
rendre obligatoire le comptage des prompts dans chaque session.

Règles :

1. Chaque réponse affiche un compteur prompt.
2. Format obligatoire : `PXXX/30`.
3. Exemples : `P001/30`, `P002/30`, `P037/30`.
4. Le compteur commence à `P001` au début de chaque nouvelle session.
5. Le compteur augmente de `+1` à chaque réponse assistant.
6. Si le compteur exact est inconnu :
   - ne pas inventer ;
   - afficher `P???/30` ;
   - créer ou demander le fichier compteur.
7. Fichier compteur recommandé : `SESSION.md`.
8. Format `SESSION.md` :

```yaml
prompt_count: 001
limit: 30
last_update: YYYY-MM-DD HH:MM
```

9. À chaque réponse :
   - lire le compteur ;
   - incrémenter ;
   - sauvegarder ;
   - afficher le nouveau compteur.
10. Si aucun fichier compteur n’existe :
    - créer `SESSION.md` ;
    - démarrer à `P001/30`.
11. Le compteur doit apparaître dans le footer strict.
12. Le compteur n’est jamais remplacé par `?/30`, sauf impossibilité réelle ; utiliser `P???/30`.
13. Toute impossibilité doit être signalée en ultra court :
    - `RES : compteur indisponible.`
    - `NEXT : créer SESSION.md.`

Footer obligatoire :

```txt
PXXX/30 🟢🟡🔴 | mode: MODE | Con: Excellent|Bon|Moyen|Faible | Lien: URL|— | GO|STOP
```
