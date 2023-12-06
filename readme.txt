Ce projet contient :
 - Un dossier asset contenant les sprites des pièces
 - Un dossier code contenant le programme divisé en deux fichiers :
    - chess.py qui gère tout ce qui est en rapport avec les echecs : les plateaux, le mouvement des pièces, les échecs, les prises, le choix des coups, ...
    - game.py qui gère l'interface graphique
 - Un fichier executable (équivalent à executer game.py)

Pour commencer une partie :
 - executer chess.exe (ou game.py)
 - Sur la fenêtre de paramétrage, appuyer sur create pour jouer les blanc contre la machine

J'ai personnellement écrit l'entièreté du code présent dans ces deux fichiers.
Les sprites des pièces et les couleurs des cases sont tirés du site open source lichess.org.
La seule librairie non native utilisée dans le code est pygame basé sur SDL.