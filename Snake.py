import pygame
import random
import heapq
import datetime
import math
import os
pygame.init()



# Paramètres de la fenêtre
largeur_fenetre = 1200
hauteur_fenetre = 800
taille_case = 40

# Variable globale pour stocker le chemin prédit par l'algorithme A*
chemin_predit = []

moments_avant_mort = []

# Variable globale pour stocker la tête du serpent précédente
tete_precedente = (0,0)
direction_precedente = (0, 0)

# Couleurs
couleur_fond = (170, 240, 170)  # Couleur d'herbe
couleur_serpent = (0, 255, 0)
couleur_nourriture = (255, 0, 0)
couleur_grille = (0, 100, 0)  # Couleur de la grille

fichier = open("C:\\Users\\Quent\\Documents\\Programmation\\Test Bard\\AI Snake\\score_max.txt", "r")
score_max = int(fichier.read())
fichier.close()

nombre_essaie = 1

fichier = open("C:\\Users\\Quent\\Documents\\Programmation\\Test Bard\\AI Snake\\log.csv", "w")
fichier.write("date" + ";" + "heure" + ";" + "score" + ";" + "score_max" + ";" + "nombre_essai" + "\n")
fichier.close()

# Création de la fenêtre
fenetre = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
pygame.display.set_caption("Snake Game")

# Fonction pour afficher le serpent
def afficher_serpent(serpent):
    global direction_precedente,tete_precedente

    for i, position in enumerate(serpent):
            if i == 0:
                # Calculer la direction de la tête du serpent
                direction_x = position[0] - tete_precedente[0]
                direction_y = position[1] - tete_precedente[1]

                # Si le serpent ne change pas de direction, utiliser la direction précédente
                if direction_x == 0 and direction_y == 0:
                    direction_x, direction_y = direction_precedente

                # Dessiner la tête du serpent
                pygame.draw.rect(fenetre, couleur_serpent, pygame.Rect(position[0], position[1], taille_case, taille_case))

                # Dessiner l'œil (un petit cercle noir au coin supérieur gauche de la tête)
                if direction_x == -taille_case:  # Serpent va à gauche
                    oeil_x = position[0] + 5
                elif direction_x == taille_case:  # Serpent va à droite
                    oeil_x = position[0] + taille_case - 7
                else:
                    oeil_x = position[0] + 5  # Serpent va en haut ou en bas

                if direction_y == -taille_case:  # Serpent va en haut
                    oeil_y = position[1] + 5
                elif direction_y == taille_case:  # Serpent va en bas
                    oeil_y = position[1] + taille_case - 7
                else:
                    oeil_y = position[1] + 5  # Serpent va à gauche ou à droite

                pygame.draw.circle(fenetre, (0, 0, 0), (oeil_x, oeil_y), 2)

                # Dessiner la bouche (un petit trait au coin inférieur droit de la tête)
                bouche_x1 = position[0] + 5
                bouche_y1 = position[1] + 15
                bouche_x2 = position[0] + 15
                bouche_y2 = position[1] + 15
                pygame.draw.line(fenetre, (0, 0, 0), (bouche_x1, bouche_y1), (bouche_x2, bouche_y2), 2)

                # Mettre à jour la tête précédente et la direction précédente
                tete_precedente = position
                direction_precedente = (direction_x, direction_y)

            else:
                pygame.draw.rect(fenetre, couleur_serpent, pygame.Rect(position[0], position[1], taille_case, taille_case))



# Fonction pour afficher la nourriture
def afficher_nourriture(nourriture):
    pygame.draw.ellipse(fenetre, couleur_nourriture, pygame.Rect(nourriture[0], nourriture[1], taille_case, taille_case))

# Fonction pour afficher la grille
def afficher_grille():
    for x in range(0, largeur_fenetre, taille_case):
        pygame.draw.line(fenetre, couleur_grille, (x, 0), (x, hauteur_fenetre))
    for y in range(0, hauteur_fenetre, taille_case):
        pygame.draw.line(fenetre, couleur_grille, (0, y), (largeur_fenetre, y))

# Fonction pour afficher le score
def afficher_score(score,score_max):
    police = pygame.font.SysFont(None, 30)
    texte_score = police.render("Score: " + str(score), True, (0,0,0))
    fenetre.blit(texte_score, (10, 10))
    texte_score_max = police.render("Score max: " + str(score_max), True, (0,0,0))
    fenetre.blit(texte_score_max, (120, 10))
    texte_score_max = police.render("Essai: " + str(nombre_essaie), True, (0,0,0))
    fenetre.blit(texte_score_max, (largeur_fenetre - 120, 10))


# Fonction pour vérifier si la position est sur le serpent
def position_sur_serpent(position, serpent):
    return position in serpent

# Fonction pour générer une nouvelle position pour la nourriture
def generer_nouvelle_position(serpent):
    while True:
        nouvelle_position = (random.randint(0, (largeur_fenetre - taille_case) // taille_case) * taille_case,
                             random.randint(0, (hauteur_fenetre - taille_case) // taille_case) * taille_case)
        if not position_sur_serpent(nouvelle_position, serpent):
            return nouvelle_position
        
# Fonction pour tracer le chemin prédit par l'algorithme A*
def afficher_chemin_predit(chemin, couleur):
    if not chemin:
        return

    for i in range(1, len(chemin)):
        x_actuel, y_actuel = chemin[i-1]
        x_suivant, y_suivant = chemin[i]
        pygame.draw.line(fenetre, couleur, (x_actuel + taille_case // 2, y_actuel + taille_case // 2),
                         (x_suivant + taille_case // 2, y_suivant + taille_case // 2), 4)

# Fonction pour calculer la distance entre deux points
def distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

# Fonction pour calculer la distance pondérée entre deux points
def distance_ponderee(point1, point2,serpent):
    # Utilisons la distance euclidienne comme base, et ajoutons un facteur de pondération
    distance = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

    # Récupérer la position du serpent
    serpent_positions = serpent[:-1]  # Ignorer la tête du serpent pour éviter de se calculer lui-même

    # Pondération supplémentaire pour garder le serpent compact
    for position in serpent_positions:
        distance += 0.1 / (distance + 1)  # Plus le serpent est proche, plus le coût augmente

    return distance

# Fonction pour trouver le chemin entre deux points en utilisant l'algorithme A* avec pénalité pour le voisinage du mur
def trouver_chemin(depart, arrivee, obstacles):
    frontiere = [(0, depart)]
    heapq.heapify(frontiere)
    chemin_precedent = {depart: None}
    cout_g = {depart: 0}

    while frontiere:
        _, actuel = heapq.heappop(frontiere)

        if actuel == arrivee:
            chemin = []
            while actuel is not None:
                chemin.append(actuel)
                actuel = chemin_precedent[actuel]
            chemin.reverse()
            return chemin

        for voisin in [(actuel[0] - taille_case, actuel[1]),
                       (actuel[0] + taille_case, actuel[1]),
                       (actuel[0], actuel[1] - taille_case),
                       (actuel[0], actuel[1] + taille_case)]:

            if voisin in obstacles or voisin[0] < 0 or voisin[0] >= largeur_fenetre or voisin[1] < 0 or voisin[1] >= hauteur_fenetre:
                continue

            # Calculer une pénalité si le voisin est proche du mur
            pénalité = 0
            if voisin[0] < 2 * taille_case or voisin[0] >= largeur_fenetre - 2 * taille_case or voisin[1] < 2 * taille_case or voisin[1] >= hauteur_fenetre - 2 * taille_case:
                pénalité = 2000

            nouveau_cout_g = cout_g[actuel] + 1 + pénalité

            if voisin not in cout_g or nouveau_cout_g < cout_g[voisin]:
                cout_g[voisin] = nouveau_cout_g
                cout_h = distance(voisin, arrivee)
                cout_f = nouveau_cout_g + cout_h
                heapq.heappush(frontiere, (cout_f, voisin))
                chemin_precedent[voisin] = actuel

    return None

# Fonction pour trouver le chemin entre la tête du serpent et sa queue
def trouver_chemin_vers_queue(tete_serpent, queue_serpent, obstacles):
    chemin_queue = trouver_chemin(tete_serpent, queue_serpent, obstacles)
    return chemin_queue

# Fonction pour trouver le chemin entre la tête du serpent et la nourriture en utilisant la stratégie
def trouver_chemin_strategie(tete_serpent, nourriture, serpent, obstacles):
    chemin_nourriture = trouver_chemin(tete_serpent, nourriture, serpent)

    if not chemin_nourriture:
        return None

    return chemin_nourriture

# Fonction pour contrôler le bot
def controle_bot(serpent, nourriture):
    tete_serpent = serpent[0]
    tete_x, tete_y = tete_serpent
    nourriture_x, nourriture_y = nourriture

    chemin = trouver_chemin_strategie(tete_serpent, nourriture, serpent, serpent)
    if chemin is not None and len(chemin) > 1:
        prochaine_case = chemin[1]
        direction_x = prochaine_case[0] - tete_x
        direction_y = prochaine_case[1] - tete_y
        direction = (direction_x, direction_y)
    else:
        # Si le chemin vers la nourriture est bloqué, le serpent va préférer longer son corps plutôt que de s'éloigner et doit éviter les murs
        direction = (0, 0)

        # Trouver les voisins accessibles
        voisins_accessibles = []
        for mouvement in [(taille_case, 0), (-taille_case, 0), (0, taille_case), (0, -taille_case)]:
            nouvelle_position = (tete_x + mouvement[0], tete_y + mouvement[1])
            if nouvelle_position[0] >= 0 and nouvelle_position[0] < largeur_fenetre and nouvelle_position[1] >= 0 and nouvelle_position[1] < hauteur_fenetre and nouvelle_position not in serpent:
                voisins_accessibles.append(nouvelle_position)

        # Si des voisins sont accessibles, choisir celui qui permet de rejoindre la queue du serpent
        chemin_vers_queue = None
        for voisin in voisins_accessibles:
            chemin_temp = trouver_chemin_vers_queue(voisin, serpent[-1], serpent + [voisin])
            if chemin_temp and (not chemin_vers_queue or len(chemin_temp) > len(chemin_vers_queue)):
                chemin_vers_queue = chemin_temp

        if chemin_vers_queue:
            prochaine_case = chemin_vers_queue[1]
            direction_x = prochaine_case[0] - tete_x
            direction_y = prochaine_case[1] - tete_y
            direction = (direction_x, direction_y)
        else:
            # Si aucun voisin ne permet de rejoindre la queue, choisir le voisin qui permet de rester près du corps
            # et éviter les murs
            meilleur_voisin = None
            distance_max = 0
            for voisin in voisins_accessibles:
                distance_min = min(distance(voisin, partie_serpent) for partie_serpent in serpent[1:])
                if distance_min > distance_max:
                    meilleur_voisin = voisin
                    distance_max = distance_min

            if meilleur_voisin:
                prochaine_case = meilleur_voisin
                direction_x = prochaine_case[0] - tete_x
                direction_y = prochaine_case[1] - tete_y
                direction = (direction_x, direction_y)

    return direction





def log(score,serpent):
    #enregistrement de la date, du score max, du nombre d'essaie et du temps de jeu
    #la date dans une colonne, l'heure dans une colonne, le reste dans une colonne. Le tout séparer par un ";"
    #le fichier est enregistrer dans le dossier du jeu
    date = datetime.datetime.now()
    date = str(date)
    date = date.split(" ")
    date = date[0]
    heure = datetime.datetime.now()
    heure = str(heure)
    heure = heure.split(" ")
    heure = heure[1]
    heure = heure.split(".")
    heure = heure[0]
    fichier = open("C:\\Users\\Quent\\Documents\\Programmation\\Test Bard\\AI Snake\\log.csv", "a")
    fichier.write(date + ";" + heure + ";" + str(score) + ";" + str(score_max) + ";" + str(nombre_essaie) + ";" + str(serpent) + "\n")
    fichier.close()

# Fonction pour vérifier si le serpent est mort (collision avec lui-même ou les bords du terrain)
def serpent_meurt(serpent):
    tete_serpent = serpent[0]

    # Vérifier s'il y a collision avec le corps du serpent (sauf la tête)
    if tete_serpent in serpent[1:]:
        return True

    # Vérifier s'il y a collision avec les bords du terrain
    tete_x, tete_y = tete_serpent
    if tete_x < 0 or tete_x >= largeur_fenetre or tete_y < 0 or tete_y >= hauteur_fenetre:
        return True

    return False


# Fonction principale du jeu
def jeu_snake():
    global tete_precedente, direction_precedente, chemin_predit,score_max

    serpent = [(largeur_fenetre // 2, hauteur_fenetre // 2)]
    # Variable globale pour stocker la tête du serpent précédente
    tete_precedente = serpent[0]

    direction = (0, 0)
    nourriture = generer_nouvelle_position(serpent)
    score = 0
    clock = pygame.time.Clock()


    temps_maj_chemin = 0
    intervalle_maj_chemin = 100  # Mettre à jour le chemin prédit toutes les 2 secondes
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Score: " + str(score))
                pygame.quit()
                quit()

        # Contrôle du bot
        direction = controle_bot(serpent, nourriture)

        nouvelle_tete = (serpent[0][0] + direction[0], serpent[0][1] + direction[1])

        if nouvelle_tete == nourriture:
            nourriture = generer_nouvelle_position(serpent)
            serpent.insert(0, nouvelle_tete)
            score += 1
        else:
            serpent.pop()
            serpent.insert(0, nouvelle_tete)

        # Contrôle du bot : Mettre à jour le chemin prédit toutes les 2 secondes
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - temps_maj_chemin >= intervalle_maj_chemin:
            chemin_predit_vers_nourriture = trouver_chemin_strategie(serpent[0], nourriture, serpent, serpent)
            chemin_predit_vers_queue = trouver_chemin_vers_queue(serpent[0], serpent[-1], serpent)

            if chemin_predit_vers_nourriture:
                chemin_predit_vers_nourriture = chemin_predit_vers_nourriture[1:]  # On enlève la première case qui correspond à la tête du serpent

            temps_maj_chemin = temps_actuel

        # Vérifier les collisions
        if (nouvelle_tete in serpent[1:] or
                nouvelle_tete[0] < 0 or nouvelle_tete[0] >= largeur_fenetre or
                nouvelle_tete[1] < 0 or nouvelle_tete[1] >= hauteur_fenetre):
            #print("Score: " + str(score))
            if(score_max < score):
                score_max = score
                fichier = open("C:\\Users\\Quent\\Documents\\Programmation\\Test Bard\\AI Snake\\score_max.txt", "w")
                fichier.write(str(score_max))
                fichier.close()
            log(score,serpent)
            global nombre_essaie
            nombre_essaie += 1
            if(nombre_essaie > 1):
                pygame.quit()
                os.system('shutdown -s -t 0')
                quit()
            jeu_snake()

        fenetre.fill(couleur_fond)
        afficher_grille()
        afficher_nourriture(nourriture)
        afficher_chemin_predit(chemin_predit_vers_nourriture, (0, 0, 255, 0))  # Afficher en violet avec un alpha de 0.2 la simulation du serpent vers la pomme
        afficher_serpent(serpent)
        afficher_score(score,score_max)
        pygame.display.update()

        tete_precedente = serpent[0]

        clock.tick(1000)

jeu_snake()
