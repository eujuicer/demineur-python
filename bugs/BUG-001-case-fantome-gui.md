# BUG-001 — Case "fantôme" non rafraîchie dans l'interface graphique

- **Statut** : Ouvert (non résolu)
- **Composant** : `demineur_gui.py` (interface graphique tkinter)
- **Branche** : `feature/interface-graphique`
- **Sévérité** : Faible / cosmétique (n'affecte pas la logique de jeu,
  uniquement l'affichage)
- **Priorité** : Moyenne (nuit à la crédibilité visuelle du jeu)
- **Environnement** : Windows 11, Python 3.14.7, tkinter (bibliothèque
  standard, version fournie avec Python)

## Résumé

Après avoir changé le nombre de mines via l'easter egg (triple-clic sur
le compteur de mines) et rejoué une partie, au moins une case de la
grille reste affichée avec un rendu incohérent (ni le style "fermé"
(gris, relief `raised`) ni le style "ouvert" (gris clair, relief
`sunken`) correspondant à son état réel dans `etat["visible"]`) : elle
apparaît comme un carré blanc/plat, visuellement isolée du reste de la
grille.

## Étapes de reproduction

1. Lancer `python demineur_gui.py`.
2. Choisir un niveau de difficulté (testé avec Facile, 9x9).
3. Cliquer 3 fois rapidement sur le compteur de mines (coin haut gauche,
   affichage noir/rouge) pour déclencher l'easter egg.
4. Dans la popup, saisir une nouvelle valeur (testé avec `1` mine) et
   valider.
5. Jouer la nouvelle partie : ouvrir plusieurs cases autour de la zone
   revelée (chiffres "1").

## Résultat attendu

Chaque case affichée reflète fidèlement `etat["visible"][r][c]` : gris
avec relief `raised` si `"?"`, gris clair avec relief `sunken` si un
chiffre/0, `🚩` si `"F"`, `💣` si `"*"`.

## Résultat obtenu

Une case reste affichée avec un rendu qui ne correspond à aucun des
styles attendus (carré blanc plat, sans bordure/relief visible),
alors qu'elle devrait normalement afficher soit un chiffre soit rien
(0) avec le fond gris clair standard. Voir capture d'écran fournie par
l'utilisateur (case isolée à gauche de la grille, non jointe à ce
fichier).

Reproduit à l'identique après une seconde tentative de correction
(voir "Correctif tenté" ci-dessous) : le bug persiste.

## Correctif tenté (sans succès)

Un appel à `fenetre.update_idletasks()` a été ajouté juste après la
destruction des anciens widgets dans `demarrer_partie()` et
`afficher_menu_difficulte()`, en supposant un problème de rafraîchissement
d'affichage Windows non flush avant la reconstruction de la grille.
**Ce correctif n'a pas résolu le problème** : le bug a été reproduit à
nouveau après application du correctif.

## Hypothèses de cause (non confirmées)

- Résidu de rendu ("ghosting") propre à tkinter/Windows lorsqu'un grand
  nombre de `Button` sont détruits (`widget.destroy()`) puis recréés à
  l'identique (mêmes coordonnées de grille) en une seule fois, dans
  `demarrer_partie()`.
- `update_idletasks()` ne traite que les tâches "idle" (géométrie,
  redessin planifié) mais pas nécessairement les événements de
  peinture (`Expose`) en attente côté OS ; un `fenetre.update()` complet
  (traitement de la file d'événements) n'a pas encore été testé.
- Piste alternative non testée : au lieu de détruire/recréer tous les
  boutons de la grille à chaque partie, réutiliser/reconfigurer les
  widgets existants (`.config(...)`) quand la taille de grille ne
  change pas (ce qui est le cas pour l'easter egg, qui ne change que
  `nb_mines`).

## Notes

- Bug découvert en testant l'easter egg du compteur de mines
  (fonctionnalité ajoutée pour permettre de changer `nb_mines` en cours
  de jeu à des fins de triche/debug).
- N'affecte pas la logique de jeu testée par ailleurs (génération des
  mines, révélation, victoire/défaite) : uniquement un défaut
  d'affichage.
