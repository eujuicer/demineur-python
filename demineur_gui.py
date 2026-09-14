"""
Démineur - interface graphique (bonus avancé optionnel de l'énoncé
demineur.md), sans programmation orientée objet.

Réutilise les fonctions "pures" de demineur.py (create_grid,
generate_mines, create_hidden_grid, reveal, has_won) et ajoute
uniquement l'affichage et les interactions avec tkinter (bibliothèque
standard). L'état de la partie est stocké dans un simple dictionnaire
passé de fonction en fonction, plutôt que dans une classe.

Le look (grille grise en relief, chiffres colorés, compteur/chrono
façon écran LCD, visage qui reagit) s'inspire du démineur de Windows.
"""

import time
import tkinter as tk
from tkinter import simpledialog

from demineur import (
    create_grid,
    generate_mines,
    create_hidden_grid,
    reveal,
    has_won,
)


GRIS = "#c0c0c0"
GRIS_OUVERT = "#dcdcdc"

COULEURS = {
    1: "#0000ff",
    2: "#008000",
    3: "#ff0000",
    4: "#000080",
    5: "#800000",
    6: "#008080",
    7: "#000000",
    8: "#808080",
}

NIVEAUX = [
    ("Facile (9x9, 10 mines)", 9, 9, 10),
    ("Moyen (16x16, 40 mines)", 16, 16, 40),
    ("Difficile (16x30, 99 mines)", 16, 30, 99),
]


# ---------------------------------------------------------------------------
# Menu de difficulté
# ---------------------------------------------------------------------------

def lancer_interface_graphique():
    """Point d'entrée : crée la fenêtre principale et affiche le menu."""
    fenetre = tk.Tk()
    fenetre.title("Démineur")
    fenetre.configure(bg=GRIS)
    afficher_menu_difficulte(fenetre)
    fenetre.mainloop()


def afficher_menu_difficulte(fenetre):
    """Affiche le menu de sélection du niveau de difficulté."""
    fenetre.resizable(True, True)
    for widget in fenetre.winfo_children():
        widget.destroy()
    fenetre.update_idletasks()

    tk.Label(
        fenetre, text="Choisissez un niveau de difficulté", bg=GRIS,
        font=("Segoe UI", 12, "bold"),
    ).pack(pady=10, padx=20)

    for texte, rows, cols, nb_mines in NIVEAUX:
        tk.Button(
            fenetre, text=texte, width=25,
            command=lambda r=rows, c=cols, m=nb_mines: demarrer_partie(fenetre, r, c, m),
        ).pack(pady=5, padx=20)


# ---------------------------------------------------------------------------
# Démarrage d'une partie
# ---------------------------------------------------------------------------

def demarrer_partie(fenetre, rows, cols, nb_mines):
    """Construit l'état d'une nouvelle partie et affiche la grille."""
    for widget in fenetre.winfo_children():
        widget.destroy()
    # Sans ce rafraîchissement forcé, Windows laisse parfois un résidu
    # visuel de l'ancienne grille affiché par-dessus la nouvelle.
    fenetre.update_idletasks()

    etat = {
        "fenetre": fenetre,
        "rows": rows,
        "cols": cols,
        "nb_mines": nb_mines,
        "hidden": None,
        "visible": create_grid(rows, cols, "?"),
        "boutons": create_grid(rows, cols, None),
        "mines_generees": False,
        "partie_terminee": False,
        "debut": None,
        "id_minuterie": None,
        "clics_compteur_mines": 0,
        "dernier_clic_compteur": 0.0,
    }

    fenetre.config(menu=construire_menu(etat))

    entete = tk.Frame(fenetre, bg=GRIS, bd=3, relief="sunken")
    entete.pack(fill="x", padx=8, pady=8)

    etat["label_mines"] = tk.Label(
        entete, text=str(nb_mines).zfill(3), bg="black", fg="red",
        font=("Consolas", 16, "bold"), width=3,
    )
    etat["label_mines"].pack(side="left", padx=6, pady=4)
    etat["label_mines"].bind("<Button-1>", lambda event: gerer_clic_compteur_mines(etat))

    etat["bouton_visage"] = tk.Button(
        entete, text="🙂", font=("Segoe UI Emoji", 14), width=2,
        command=lambda: demarrer_partie(fenetre, rows, cols, nb_mines),
    )
    etat["bouton_visage"].pack(side="left", expand=True, pady=4)

    etat["label_temps"] = tk.Label(
        entete, text="000", bg="black", fg="red",
        font=("Consolas", 16, "bold"), width=3,
    )
    etat["label_temps"].pack(side="right", padx=6, pady=4)

    grille_frame = tk.Frame(fenetre, bg=GRIS, bd=3, relief="sunken")
    grille_frame.pack(padx=8, pady=(0, 8))

    for r in range(rows):
        for c in range(cols):
            bouton = tk.Button(
                grille_frame, text="", width=2, height=1,
                font=("Consolas", 10, "bold"), bd=2, relief="raised",
                bg=GRIS, activebackground=GRIS,
            )
            bouton.grid(row=r, column=c, padx=0, pady=0)
            bouton.bind("<ButtonPress-1>", lambda event, r=r, c=c: pression_case(etat, r, c))
            bouton.bind("<ButtonRelease-1>", lambda event, r=r, c=c: relachement_case(etat, r, c))
            bouton.bind("<Button-3>", lambda event, r=r, c=c: clic_droit(etat, r, c))
            etat["boutons"][r][c] = bouton

    fenetre.resizable(False, False)
    demarrer_minuterie(etat)


def construire_menu(etat):
    """Construit la barre de menu ('Jeu' : nouvelle partie, difficulté, quitter)."""
    fenetre = etat["fenetre"]
    barre = tk.Menu(fenetre)
    menu_jeu = tk.Menu(barre, tearoff=0)

    menu_jeu.add_command(
        label="Nouvelle partie",
        command=lambda: demarrer_partie(fenetre, etat["rows"], etat["cols"], etat["nb_mines"]),
    )
    menu_jeu.add_separator()
    for texte, rows, cols, nb_mines in NIVEAUX:
        menu_jeu.add_command(
            label=texte,
            command=lambda r=rows, c=cols, m=nb_mines: demarrer_partie(fenetre, r, c, m),
        )
    menu_jeu.add_separator()
    menu_jeu.add_command(label="Quitter", command=fenetre.destroy)

    barre.add_cascade(label="Jeu", menu=menu_jeu)
    return barre


# ---------------------------------------------------------------------------
# Interactions du joueur
# ---------------------------------------------------------------------------

def pression_case(etat, r, c):
    """Appui de la souris sur une case : affiche le visage surpris, comme
    dans le démineur de Windows."""
    if not etat["partie_terminee"] and etat["visible"][r][c] == "?":
        etat["bouton_visage"].config(text="😮")


def relachement_case(etat, r, c):
    """Relâchement du clic gauche : ouvre la case et remet le visage normal
    si la partie continue."""
    clic_gauche(etat, r, c)
    if not etat["partie_terminee"]:
        etat["bouton_visage"].config(text="🙂")


def clic_gauche(etat, r, c):
    """Ouvre la case (r, c) sous le curseur de la souris."""
    if etat["partie_terminee"] or etat["visible"][r][c] != "?":
        return

    if not etat["mines_generees"]:
        mines = generate_mines(etat["rows"], etat["cols"], etat["nb_mines"], (r, c))
        etat["hidden"] = create_hidden_grid(etat["rows"], etat["cols"], mines)
        etat["mines_generees"] = True
        etat["debut"] = time.time()

    if etat["hidden"][r][c] == "*":
        etat["visible"][r][c] = "*"
        terminer_partie(etat, victoire=False, case_explosee=(r, c))
        return

    reveal(etat["hidden"], etat["visible"], r, c)
    rafraichir_grille(etat)

    if has_won(etat["hidden"], etat["visible"]):
        terminer_partie(etat, victoire=True)


def clic_droit(etat, r, c):
    """Pose ou retire un drapeau sur la case (r, c)."""
    if etat["partie_terminee"] or etat["visible"][r][c] not in ("?", "F"):
        return

    etat["visible"][r][c] = "F" if etat["visible"][r][c] == "?" else "?"
    rafraichir_bouton(etat, r, c)
    mettre_a_jour_compteur_mines(etat)


def gerer_clic_compteur_mines(etat):
    """Easter egg : trois clics rapprochés sur le compteur de mines
    proposent de tricher en changeant le nombre de mines de la partie."""
    maintenant = time.time()
    if maintenant - etat["dernier_clic_compteur"] > 1:
        etat["clics_compteur_mines"] = 0
    etat["clics_compteur_mines"] += 1
    etat["dernier_clic_compteur"] = maintenant

    if etat["clics_compteur_mines"] >= 3:
        etat["clics_compteur_mines"] = 0
        proposer_triche_mines(etat)


def proposer_triche_mines(etat):
    """Ouvre une popup pour changer le nombre de mines, puis relance une
    partie (fraîche) avec la nouvelle valeur."""
    rows, cols = etat["rows"], etat["cols"]
    nouvelle_valeur = simpledialog.askinteger(
        "Easter egg",
        f"Nombre de mines (entre 1 et {rows * cols - 1}) :",
        parent=etat["fenetre"],
        initialvalue=etat["nb_mines"],
        minvalue=1,
        maxvalue=rows * cols - 1,
    )
    if nouvelle_valeur is not None:
        demarrer_partie(etat["fenetre"], rows, cols, nouvelle_valeur)


# ---------------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------------

def rafraichir_grille(etat):
    """Met à jour l'apparence de tous les boutons de la grille."""
    for r in range(etat["rows"]):
        for c in range(etat["cols"]):
            rafraichir_bouton(etat, r, c)


def rafraichir_bouton(etat, r, c, case_explosee=None):
    """Met à jour l'apparence d'un seul bouton en fonction de la grille visible."""
    bouton = etat["boutons"][r][c]
    valeur = etat["visible"][r][c]

    if valeur == "?":
        bouton.config(text="", relief="raised", bd=2, bg=GRIS, activebackground=GRIS)
    elif valeur == "F":
        bouton.config(text="🚩", relief="raised", bd=2, bg=GRIS, activebackground=GRIS)
    elif valeur == "*":
        fond = "#ff0000" if (r, c) == case_explosee else GRIS_OUVERT
        bouton.config(text="💣", relief="sunken", bd=1, bg=fond, activebackground=fond)
    elif valeur == 0:
        bouton.config(text="", relief="sunken", bd=1, bg=GRIS_OUVERT, activebackground=GRIS_OUVERT)
    else:
        bouton.config(
            text=str(valeur), fg=COULEURS.get(valeur, "black"),
            relief="sunken", bd=1, bg=GRIS_OUVERT, activebackground=GRIS_OUVERT,
        )


def mettre_a_jour_compteur_mines(etat):
    """Met à jour le compteur de mines restantes (estimé à partir du
    nombre de drapeaux posés)."""
    nb_drapeaux = sum(1 for ligne in etat["visible"] for valeur in ligne if valeur == "F")
    restantes = etat["nb_mines"] - nb_drapeaux
    etat["label_mines"].config(text=str(restantes).zfill(3) if restantes >= 0 else "-" + str(-restantes).zfill(2))


def demarrer_minuterie(etat):
    """Lance le rafraîchissement périodique du temps écoulé."""
    actualiser_minuterie(etat)


def actualiser_minuterie(etat):
    """Met à jour le compteur de temps toutes les 500ms tant que la partie
    n'est pas terminée."""
    if etat["partie_terminee"]:
        return

    if etat["debut"] is not None:
        secondes = min(int(time.time() - etat["debut"]), 999)
        etat["label_temps"].config(text=str(secondes).zfill(3))

    etat["id_minuterie"] = etat["fenetre"].after(500, lambda: actualiser_minuterie(etat))


def terminer_partie(etat, victoire, case_explosee=None):
    """Termine la partie : révèle les mines si défaite, arrête le minuteur
    et met à jour le visage."""
    etat["partie_terminee"] = True

    if etat["id_minuterie"] is not None:
        etat["fenetre"].after_cancel(etat["id_minuterie"])

    if not victoire:
        for r in range(etat["rows"]):
            for c in range(etat["cols"]):
                if etat["hidden"][r][c] == "*":
                    etat["visible"][r][c] = "*"

    for r in range(etat["rows"]):
        for c in range(etat["cols"]):
            rafraichir_bouton(etat, r, c, case_explosee)

    etat["bouton_visage"].config(text="😎" if victoire else "😵")


if __name__ == "__main__":
    lancer_interface_graphique()
