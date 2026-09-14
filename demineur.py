"""
Démineur - version console, sans programmation orientée objet.

Ce module implémente exactement les fonctions demandées dans l'énoncé
(demineur.md) : create_grid, get_neighbors, generate_mines,
create_hidden_grid, reveal, print_grid, has_won et minesweeper.

Quelques fonctions supplémentaires (lire_touche, deplacer_curseur,
choisir_difficulte) ont été ajoutées uniquement pour structurer le
code et éviter une seule fonction monolithique, comme demandé dans
les contraintes.

Déplacement au clavier (flèches ou Z/Q/S/D) implémenté avec le module
standard msvcrt (Windows uniquement), après recherche dans la
documentation officielle de Python.
"""

import os
import random
import time
import msvcrt


# ---------------------------------------------------------------------------
# Construction de la grille
# ---------------------------------------------------------------------------

def create_grid(rows, cols, value):
    """Crée une grille (liste de listes) de taille rows x cols,
    remplie partout avec la valeur donnée."""
    grille = []
    for _ in range(rows):
        ligne = [value for _ in range(cols)]
        grille.append(ligne)
    return grille


def get_neighbors(rows, cols, r, c):
    """Retourne la liste des coordonnées (ligne, colonne) des cases
    voisines de (r, c), dans les 8 directions, en restant dans la grille."""
    voisins = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if not (dr == 0 and dc == 0):
                nr = r + dr
                nc = c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    voisins.append((nr, nc))
    return voisins


def generate_mines(rows, cols, nb_mines, forbidden_cell):
    """Génère un ensemble de positions de mines (nb_mines couples
    (ligne, colonne) uniques), sans jamais placer de mine sur
    forbidden_cell (la première case ouverte par le joueur)."""
    mines = set()
    while len(mines) < nb_mines:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        if (r, c) != forbidden_cell and (r, c) not in mines:
            mines.add((r, c))
    return mines


def create_hidden_grid(rows, cols, mines):
    """Construit la grille interne du jeu (invisible pour le joueur) :
    "*" sur les cases minées, et sur les autres cases le nombre de
    mines présentes dans les cases voisines."""
    hidden = create_grid(rows, cols, 0)

    for (r, c) in mines:
        hidden[r][c] = "*"

    for r in range(rows):
        for c in range(cols):
            if hidden[r][c] != "*":
                compteur = 0
                for (nr, nc) in get_neighbors(rows, cols, r, c):
                    if hidden[nr][nc] == "*":
                        compteur += 1
                hidden[r][c] = compteur

    return hidden


# ---------------------------------------------------------------------------
# Logique de jeu
# ---------------------------------------------------------------------------

def reveal(hidden, visible, r, c):
    """Révèle la case (r, c) dans la grille visible.

    - Si la case contient un nombre différent de 0, seule cette case
      est révélée.
    - Si la case contient 0, les cases voisines sont révélées
      récursivement (effet "tache d'huile" classique du démineur).
    """
    if visible[r][c] != "?":
        return

    visible[r][c] = hidden[r][c]

    if hidden[r][c] == 0:
        rows = len(hidden)
        cols = len(hidden[0])
        for (nr, nc) in get_neighbors(rows, cols, r, c):
            if visible[nr][nc] == "?":
                reveal(hidden, visible, nr, nc)


def has_won(hidden, visible):
    """Retourne True si toutes les cases non minées ont été révélées."""
    rows = len(hidden)
    cols = len(hidden[0])

    for r in range(rows):
        for c in range(cols):
            if hidden[r][c] != "*":
                if visible[r][c] == "?" or visible[r][c] == "F":
                    return False

    return True


# ---------------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------------

ROUGE = "\033[91m"
VERT = "\033[92m"
RESET = "\033[0m"


def afficher_defaite():
    """Affiche un message de défaite stylisé : "BOOM" en ASCII art, encadré
    de deux bombes, le tout en rouge."""
    bombe = [
        "   ,   ",
        "  (@)  ",
        " (   ) ",
        "(     )",
        " `---' ",
    ]
    boom = [
        "####   ###   ###  #   # ",
        "#   # #   # #   # ## ## ",
        "####  #   # #   # # # # ",
        "#   # #   # #   # #   # ",
        "####   ###   ###  #   # ",
    ]

    print(ROUGE)
    for ligne_bombe, ligne_boom in zip(bombe, boom):
        print(ligne_bombe + "  " + ligne_boom + "  " + ligne_bombe)
    print(RESET)


def afficher_victoire():
    """Affiche un message de victoire stylisé : un démineur en tenue,
    pouce levé, en ASCII art vert."""
    figurine = [
        "      ,---.        ",
        "     /  o  \\       ",
        "    |  ___  |      ",
        "    |_______|      ",
        "   /|       |\\     ",
        "  / |       | |__  ",
        "    |       |    \\ ",
        "    |_______|   (Y)",
        "       |  |        ",
        "      _|  |_       ",
        "     |______|      ",
    ]

    print(VERT)
    for ligne in figurine:
        print(ligne)
    print(RESET)


def print_grid(grid, curseur=None):
    """Affiche une grille (visible ou hidden) dans la console, avec les
    numéros de ligne et de colonne. La valeur 0 est affichée sous forme
    de "." pour une lecture plus claire.

    Si curseur (r, c) est fourni, la case correspondante est encadrée
    par des crochets [ ] pour indiquer la position du joueur."""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    entete = "     " + "".join(str(c).rjust(3) for c in range(cols))
    print(entete)

    for r in range(rows):
        cellules = []
        for c in range(cols):
            valeur = grid[r][c]
            texte = "." if valeur == 0 else str(valeur)
            cellules.append(f"[{texte}]" if curseur == (r, c) else f" {texte} ")
        print(str(r).rjust(3) + "  " + "".join(cellules))


# ---------------------------------------------------------------------------
# Lecture du clavier (déplacement du curseur dans la grille)
# ---------------------------------------------------------------------------

def lire_touche():
    """Lit une touche au clavier (Windows) sans attendre la touche Entrée,
    et retourne une action normalisée :
    'HAUT', 'BAS', 'GAUCHE', 'DROITE' (flèches ou Z/Q/S/D),
    'OUVRIR' (Entrée), 'DRAPEAU' (Espace), 'QUITTER' (Echap),
    ou None si la touche n'est pas reconnue."""
    touche = msvcrt.getch()

    # Les touches spéciales (flèches...) arrivent en deux temps : un
    # préfixe (b"\x00" ou b"\xe0") suivi d'un code.
    fleches = {b"H": "HAUT", b"P": "BAS", b"K": "GAUCHE", b"M": "DROITE"}
    if touche in (b"\x00", b"\xe0"):
        return fleches.get(msvcrt.getch())

    autres_touches = {
        b"z": "HAUT", b"Z": "HAUT",
        b"s": "BAS", b"S": "BAS",
        b"q": "GAUCHE", b"Q": "GAUCHE",
        b"d": "DROITE", b"D": "DROITE",
        b"\r": "OUVRIR",
        b" ": "DRAPEAU",
        b"\x1b": "QUITTER",
    }
    return autres_touches.get(touche)


def deplacer_curseur(r, c, direction, rows, cols):
    """Retourne la nouvelle position (r, c) du curseur après déplacement
    dans la direction donnée, en restant à l'intérieur de la grille."""
    r += -1 if direction == "HAUT" else 1 if direction == "BAS" else 0
    c += -1 if direction == "GAUCHE" else 1 if direction == "DROITE" else 0

    r = max(0, min(rows - 1, r))
    c = max(0, min(cols - 1, c))
    return (r, c)


# ---------------------------------------------------------------------------
# Boucle principale du jeu
# ---------------------------------------------------------------------------

def minesweeper(rows, cols, nb_mines):
    """Fonction principale du démineur : gère les entrées utilisateur,
    la logique du jeu, et fait appel à toutes les autres fonctions."""
    visible = create_grid(rows, cols, "?")
    hidden = None
    mines_generees = False

    curseur_r, curseur_c = rows // 2, cols // 2

    nb_coups = 0
    debut = time.time()
    partie_terminee = False
    victoire = False

    while not partie_terminee:
        os.system("cls")
        print("=== DEMINEUR ===")
        print(f"Grille {rows}x{cols} avec {nb_mines} mines.")
        print("Deplacement : fleches ou Z/Q/S/D. Entree : ouvrir. Espace : drapeau. Echap : quitter.")
        print()
        print_grid(visible, (curseur_r, curseur_c))

        action = lire_touche()

        if action in ("HAUT", "BAS", "GAUCHE", "DROITE"):
            curseur_r, curseur_c = deplacer_curseur(curseur_r, curseur_c, action, rows, cols)

        elif action == "QUITTER":
            print("\nPartie abandonnée.")
            return

        elif action == "DRAPEAU" and visible[curseur_r][curseur_c] in ("?", "F"):
            visible[curseur_r][curseur_c] = "F" if visible[curseur_r][curseur_c] == "?" else "?"

        elif action == "OUVRIR":
            r, c = curseur_r, curseur_c
            if visible[r][c] == "?":
                # Les mines ne sont générées qu'au premier coup joué, et
                # jamais sur la case choisie en premier.
                if not mines_generees:
                    mines = generate_mines(rows, cols, nb_mines, (r, c))
                    hidden = create_hidden_grid(rows, cols, mines)
                    mines_generees = True

                nb_coups += 1
                if hidden[r][c] == "*":
                    visible[r][c] = "*"
                    partie_terminee = True
                    victoire = False
                else:
                    reveal(hidden, visible, r, c)
                    if has_won(hidden, visible):
                        partie_terminee = True
                        victoire = True

    duree = time.time() - debut

    if not victoire:
        # On révèle toutes les mines pour montrer la grille complète.
        for r in range(rows):
            for c in range(cols):
                if hidden[r][c] == "*":
                    visible[r][c] = "*"

    os.system("cls")
    print("=== DEMINEUR ===")
    print()
    print_grid(visible)
    print()

    if victoire:
        afficher_victoire()
        print(f"Bravo, vous avez gagné en {nb_coups} coups et {duree:.1f} secondes !")
    else:
        afficher_defaite()
        print(f"Boom, vous avez perdu apres {nb_coups} coups et {duree:.1f} secondes.")


# ---------------------------------------------------------------------------
# Choix du niveau de difficulté et point d'entrée
# ---------------------------------------------------------------------------

def choisir_difficulte():
    """Affiche un petit menu de difficulté et retourne (rows, cols, nb_mines)."""
    print("Choisissez un niveau de difficulte :")
    print("1 - Facile    (9x9,   10 mines)")
    print("2 - Moyen     (16x16, 40 mines)")
    print("3 - Difficile (16x30, 99 mines)")

    choix = input("Votre choix (1/2/3, Entree = Facile) : ").strip()

    if choix == "2":
        return (16, 16, 40)
    elif choix == "3":
        return (16, 30, 99)
    else:
        return (9, 9, 10)


if __name__ == "__main__":
    rows, cols, nb_mines = choisir_difficulte()
    minesweeper(rows, cols, nb_mines)
