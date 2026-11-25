# Démineur (console, Python)

Implémentation de l'énoncé [`demineur.md`](demineur.md) : démineur en mode
console, sans programmation orientée objet. Ce README ne couvre que ce qui a
été ajouté par rapport à l'énoncé — les règles du jeu, la liste des fonctions
demandées et les contraintes sont décrites dans `demineur.md`.

## Lancer le jeu

```bash
python demineur.py
```

Un petit menu permet de choisir la difficulté (Facile / Moyen /
Difficile), puis la partie démarre dans la console.

## Contrôles : navigation au curseur (au lieu des commandes texte)

L'énoncé propose des commandes tapées au clavier (`o ligne colonne`,
`f ligne colonne`). Cette implémentation les remplace par un curseur
déplaçable dans la grille, plus rapide à jouer :

| Touche                     | Effet                                                   |
|----------------------------|----------------------------------------------------------|
| Flèches ou `Z`/`Q`/`S`/`D`  | Déplacer le curseur (haut/gauche/bas/droite)             |
| `Entrée`                   | Ouvrir la case sous le curseur                           |
| `Espace`                   | Poser ou retirer un drapeau sur la case sous le curseur  |
| `Échap`                    | Abandonner la partie                                     |

La case du curseur s'affiche entre crochets `[ ]`. Ce mode nécessite
Windows : il utilise le module standard `msvcrt` pour lire les touches
sans attendre la touche Entrée après chaque déplacement.

## Fonctions ajoutées en plus de l'énoncé

- `lire_touche()` — lit une touche au clavier (flèches, Z/Q/S/D, Entrée,
  Espace, Échap) et retourne une action normalisée.
- `deplacer_curseur(r, c, direction, rows, cols)` — calcule la nouvelle
  position du curseur en restant dans la grille.
- `afficher_defaite()` / `afficher_victoire()` — écrans de fin de partie
  en ASCII art coloré (voir plus bas).
- `choisir_difficulte()` — petit menu de sélection du niveau.

## Bonus implémentés (parmi ceux listés dans demineur.md)

- Impossible de poser un drapeau sur une case déjà révélée.
- Affichage amélioré (numéros de lignes/colonnes, `.` pour les cases à 0,
  curseur encadré).
- Compteur de coups joués.
- Temps de jeu affiché en fin de partie.
- Plusieurs niveaux de difficulté (Facile 9x9, Moyen 16x16, Difficile 16x30).

### Bonus avancés non implémentés

- Empêcher la génération de mines *autour* de la première case (et pas
  seulement dessus) : demanderait de faire évoluer `generate_mines` pour
  accepter une zone interdite plutôt qu'une seule case.
- Interface graphique (optionnelle dans l'énoncé).

## Écrans de fin de partie

En plus du message texte, la partie se termine par un écran en ASCII art
coloré (codes ANSI, sans dépendance externe) :

- **Défaite** : "BOOM" encadré de deux bombes, en rouge.
- **Victoire** : un démineur en tenue, pouce levé, en vert.

## Structure du projet

```
demineur-python/
├── demineur.py           # Le jeu
├── demineur.md           # Énoncé de l'exercice
├── tests/
│   └── test_demineur.py  # Tests unitaires (pytest)
├── requirements.txt
├── .gitignore
└── README.md
```

## Tests

Les fonctions pures du jeu (tout sauf `minesweeper`, qui lit le clavier)
sont testées avec `pytest` :

```bash
pip install -r requirements.txt
pytest -v
```

Si `pytest` n'est pas reconnu après l'installation (dossier `Scripts` de
Python absent du PATH), utiliser `python -m pytest -v` à la place.
