#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  2 11:36:44 2023

@author: gab
"""
import sys
sys.path.append('..')

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.interpolate import splrep, BSpline

## SCORE

def calcul_scores(df, ni) :
    col = df.columns.tolist()
    if 'joueurA' in col :
        name_A = df['joueurA'][ni]
        name_B = df['joueurB'][ni]
    else :
        name_A = df['joueur_frappe'][ni]
        name_B = df['joueur_sur'][ni]

    # Initialiser les scores des deux joueurs à zéro
    scoreA = 0
    scoreB = 0
    
    # Créer des listes vides pour stocker les scores des deux joueurs
    scoresA = []
    scoresB = []
    
    time_mem = 0
    
    # Parcourir le DataFrame
    for i, row in df.iterrows():
        scoresA.append(scoreA)
        scoresB.append(scoreB)
        joueur = row['nom']
        time = row['debut']
        if time < time_mem :    # changement de video clip
            scoreA = 0
            scoreB = 0
        else :
            # Si le point est en faute (derniere touche de balle = perdant)
            if row['faute'] == 'out' or row['faute'] == 'filet' :
                if name_A == joueur :
                    scoreB += 1
                else :
                    scoreA += 1
            # Si le point est gagnant (derniere touche de balle = gagnant)
            elif row['faute'] == 'pt_gagne':
                if name_B == joueur :
                    scoreB += 1
                else :
                    scoreA += 1
                
        time_mem = time
    
    # Ajouter les listes de scores au DataFrame
    df['scoreA'] = scoresA
    df['scoreB'] = scoresB
    df['diff_score'] = df['scoreA'] - df['scoreB']    # + pour A, - pour B
    df['proba_gagne'] = list(map(fonction_domination_score, df['scoreA'], df['scoreB']))
    
def proba_A_gagne(scoreA, scoreB):  # en prenant seulement en compte le score
    if scoreA == scoreB :
        return 0.5
    
    p = scoreA / (scoreA + scoreB)  # proba que A gagne un point indépendant
    q = scoreB / (scoreA + scoreB)  # proba que A perde un point indépendant
    
    if scoreA >= 11 or scoreB >= 11 :
        if scoreB < scoreA - 1 :
            return 1
        elif scoreB > scoreA + 1 :
            return 0      
        elif scoreB == scoreA - 1 :
            return p + q*0.5
        elif scoreB == scoreA + 1 :
            return p*0.5
    if scoreA + scoreB < 5 :
        return (proba_A_gagne(scoreA +1, scoreB) + proba_A_gagne(scoreA, scoreB + 1))/2
    return(p*proba_A_gagne(scoreA +1, scoreB) + q*proba_A_gagne(scoreA, scoreB + 1)) # 1 si A gagne, 0 si B gagne
    
def fonction_domination_score(scoreA, scoreB):  # entre -1 et 1
    P = proba_A_gagne(scoreA, scoreB)
    return( 2*P - 1)

## PHYSIQUE

dico_inversion_colonne = {'m' : 'm', 'g' : 'd', 'd' : 'g', 'h' : 'e', 'i' : 'f', 'f' : 'i', 'e' : 'h'}
dico_coord_colonne = {'i' : 1, 'h' : 2, 'g' : 3, 'm' : 4, 'd' : 5, 'e' : 6, 'f' : 7}

def calcul_angle(zone_A, zone_B, zone_jeu):
    colonne_A = zone_A[0]
    colonne_A_refB = dico_inversion_colonne[colonne_A]
    colonne_B = zone_B[0]
    colonne_balle = zone_jeu[0]
    delta_x_A_balle = dico_coord_colonne[colonne_A_refB] - dico_coord_colonne[colonne_balle]
    delta_x_B_balle = dico_coord_colonne[colonne_balle] - dico_coord_colonne[colonne_B]
    A_jeu = np.array([ delta_x_A_balle, int(zone_A[1]) + int(zone_jeu[1])-1 ] )
    B_jeu = np.array([ delta_x_B_balle, int(zone_B[1]) - int(zone_jeu[1]) ] )
    A_jeu = A_jeu/np.linalg.norm(A_jeu)
    B_jeu = B_jeu/np.linalg.norm(B_jeu)
    alpha = np.dot(A_jeu, B_jeu) # il doit etre proche de 1 pour que le receptionneur ne soit pas en difficulté
    return alpha 
    

def sigmoide_centree(x):
    return( 2/(1+math.exp(-x)) - 1)


def calcul_diff_position(df, nom_A, nom_B):
    """ définir une fonction difficulté de la position :
        - proportion de coups offensifs/deffensifs dans l'échange actuel
        - éloignement avec la table (+ le joueur est loin de la table, plus on estime que c'est dur pour lui')
        - angle + distance avec le rebond
        - distance parcourue lors de l'échange (fatigue)'
        """
    diffA = 0
    diffB = 0
    agressivite = 0
    fatigue = 0
    angle = 0
    coup_attaque_A = 0
    coup_attaque_B = 0
    nombre_de_coups = 0
    distance_parcourue_echange_A = 0
    distance_parcourue_echange_B = 0
    distance_parcourue_set_A = 0
    distance_parcourue_set_B = 0
    pre_xA = 0
    pre_yA = 2.74
    pre_xB = 0
    pre_yB = 2.74
    # Créer des listes vides pour stocker les données des deux joueurs
    diffsA = []
    diffsB = []
    Aggre = []
    Fatig = []
    Angle = []
    time_mem = 0
    
    # Parcourir le DataFrame
    for i, row in df.iterrows():
        
        diffsA.append(diffA)
        Aggre.append(agressivite)
        Fatig.append(fatigue)
        Angle.append(angle)
        diffsB.append(diffB)
        
        xA = row['distance_x_jA']   # positions actuelles
        yA = row['distance_y_jA']
        xB = row['distance_x_jB']
        yB = row['distance_y_jB']
        
        if abs(xA - pre_xA) > 1000 or abs(yA - pre_yA)>1000 :
            xA = pre_xA
            yA = pre_yA
        if abs(yB - pre_yB) > 1000 or abs(xB - pre_xB)>1000 :
            xB = pre_xB
            yB = pre_yB
        distA = np.sqrt((xA - pre_xA)**2 + (abs(yA) - abs(pre_yA))**2)  # calcul des distances
        distB = np.sqrt((xB - pre_xB)**2 + (abs(yB) - abs(pre_yB))**2)
        distance_parcourue_echange_A += distA   # mise à jour des distances
        distance_parcourue_echange_B += distB
        distance_parcourue_set_A += distA
        distance_parcourue_set_B += distB
        pre_xA = xA     #   mémorisation des positions
        pre_yA = yA
        pre_xB = xB
        pre_yB = yB
        
        
        time = row['debut']
        zoneA = row['zone_joueur_jA']
        zoneB = row['zone_joueur_jA']
        zone_jeu = row['zone_jeu']
        joueur = row['nom']
        type_coup = row['type_coup']
        
        distance_table_A = (int(zoneA[1])-4)/4   # entre 0 et 1
        distance_table_B = (int(zoneB[1])-4)/4   # entre 0 et 1
        
        if time < time_mem :    # on change de match
            break
            diffA = 0
            diffB = 0
            coup_attaque_A = 0
            coup_attaque_B = 0
            nombre_de_coups = 0
            distance_parcourue_echange_A = 0
            distance_parcourue_echange_B = 0
            distance_parcourue_set_A = 0
            distance_parcourue_set_B = 0
            pre_xA = 0
            pre_yA = 2.74
            pre_xB = 0
            pre_yB = 2.74
        elif type_coup == 'offensif' :
            nombre_de_coups += 1
            if joueur == nom_A :
                coup_attaque_A += 1
            else :
                coup_attaque_B += 1
        elif type_coup == 'defensif' or type_coup == 'intermediaire' :
            nombre_de_coups += 1
            if joueur == nom_A :
                coup_attaque_B += 1
            else :
                coup_attaque_A += 1
        elif type_coup == np.nan :  # si service on réinitialise les attaques
            nombre_de_coups += 1    
            distance_parcourue_echange_A = 0
            distance_parcourue_echange_B = 0
            
        # angle entre -1 et 1 (1 bien pour A, -1 bien pour B)
        if isinstance(zone_jeu, str) :  # Si la balle rebondit sur la table
            if joueur == nom_A :
                angle = (calcul_angle(zoneA, zoneB, zone_jeu)-1)/2
            elif joueur == nom_B:
                angle = (1-calcul_angle(zoneB, zoneA, zone_jeu))/2
        else :
            angle = 0
            
        if coup_attaque_A == 0 and coup_attaque_B == 0 :
            agressivite = 0
        else :
            agressivite = (coup_attaque_A - coup_attaque_B)/(coup_attaque_A + coup_attaque_B)
        fatigue = (distance_parcourue_echange_B - distance_parcourue_echange_A)/(distance_parcourue_echange_B + distance_parcourue_echange_A)
        
        diffA = 0.2*agressivite + 0.2*fatigue + 0.6*angle
        diffB = 0
        time_mem = time
    diffA = 0.2*agressivite + 0.2*fatigue + 0.6*angle
    return(diffsA, diffA)
    
## MORAL


def calcul_stress(df, ni, name_A, name_B):  # différence entre stress et moral
    """ définir une fonction stress :
    - Lorsqu’un joueur est proche de gagner (balle de match), il est stressé, et d’autant plus si l’autre joueur est proche d’égaliser
    - Plus un échange est long, plus celui qui le perd sera stressé pour l’échange suivant
    - A chaque faute, le joueur est un peu plus stressé
    - Si un joueur échoue une offensive, il stresse un peu plus
    """
    
    calcul_scores(df, ni)   # pour accèder au score
    Stress = []
    stressA = 1
    stressB = 1
    compteur_duree_echange = 0
    faute_conseq_A = 0
    faute_conseq_B = 0
    pt_gagne_conseq_A = 0 
    pt_gagne_conseq_B = 0 
    time_mem = 0
    for i, row in df.iterrows():
        time = row['debut']
        scoreA = row['scoreA']
        scoreB = row['scoreB']
        faute = row['faute']
        joueur = row['nom']
        type_coup = row['type_coup']
        
        if time < time_mem :    # on change de match
            break
        
        if scoreA > scoreB :
            if scoreA != 11 :
                stressA += 1/(scoreA-scoreB)/(11-scoreA)
            else :
                stressA += 1/(scoreA-scoreB)
        elif scoreB > scoreA :
            if scoreB != 11 :
                stressB += 1/(scoreB-scoreA)/(11-scoreB)
            else :
                stressB += 1/(scoreB-scoreA)
        if faute == 'out' or faute == 'filet' :
            if joueur == name_A :
                if scoreB != 11 :
                    stressA += compteur_duree_echange/(11-scoreB)
                else :
                    stressA += compteur_duree_echange/11
                faute_conseq_A += 1
                pt_gagne_conseq_A = 0
                
            else :
                if scoreA != 11 :
                    stressB += compteur_duree_echange/(11-scoreA)
                else :
                    stressB += compteur_duree_echange/11
                faute_conseq_B += 1
                pt_gagne_conseq_B = 0
            compteur_duree_echange = 0
                
        elif faute == 'pt_gagne':
            if joueur == name_A :
                if scoreA == 11 :
                    stressB += compteur_duree_echange/11
                else :
                    stressB += compteur_duree_echange/(11-scoreA)
                pt_gagne_conseq_A += 1
                faute_conseq_A = 0
            else :
                if scoreB == 11 :
                    stressA += compteur_duree_echange/11
                else :
                    stressA += compteur_duree_echange/(11-scoreB)
                pt_gagne_conseq_B += 1
                faute_conseq_B = 0
            compteur_duree_echange = 0
        else :
            compteur_duree_echange += 1
                
        stressB += faute_conseq_B - pt_gagne_conseq_B
        if stressB < 1 :
            # stressA += 1-stressB
            stressB = 1
        stressA += faute_conseq_A - pt_gagne_conseq_A
        if stressA < 1 :
            # stressB += 1 - stressA
            stressA = 1
            
        Stress.append((stressB-stressA)/(stressA + stressB))   # entre -1 et 1 (1 si B stressé donc A en confiance)
        time_mem = time
    last_stress = (stressB-stressA)/(stressA + stressB)
    return Stress, last_stress

def display_score_phys_domination(df, ni):
    calcul_scores(df)
    diffsA, Fatig, Aggre, Angle = np.array(calcul_diff_position(df))
    
    fig, axs = plt.subplots(4)
    fig.suptitle('Evolution de la domination (au score et au physique) sur un set')
    
    coups = np.arange(0,101,1)
    avantage_scoreA = np.array(df['proba_gagne'])
    avantage_scoreB = - avantage_scoreA
    
    avantage_score_A_smooth = splrep(coups, avantage_scoreA, s=1)
    avantage_score_B_smooth = splrep(coups, avantage_scoreB, s=1)
    
    avantage_physique_A_smooth = splrep(coups, diffsA, s=0)
    avantage_physique_B_smooth = splrep(coups, -diffsA, s=0)
    
    
    axs[0].plot(coups, df['scoreA'], label = df['joueurA'][ni])
    axs[0].plot(coups, df['scoreB'], label = df['joueurB'][ni])
    axs[0].legend(loc="lower right")
    axs[0].set_xlim([0, 100])
    axs[0].set_ylabel('Score')
    
    axs[1].plot(coups, BSpline(*avantage_score_A_smooth)(coups))
    axs[1].plot(coups, BSpline(*avantage_score_B_smooth)(coups))
    axs[1].set_ylim([-1, 1])
    axs[1].set_xlim([0, 100])
    axs[1].set_ylabel('Winning chances')
    
    axs[2].plot(coups,BSpline(*avantage_physique_A_smooth)(coups))
    axs[2].plot(coups,BSpline(*avantage_physique_B_smooth)(coups))
    axs[2].set_ylim([-1, 1])
    axs[2].set_xlim([0, 100])
    axs[2].set_ylabel('Physical domination')
    
    axs[3].plot(coups,0.5*BSpline(*avantage_physique_A_smooth)(coups) + 0.5*BSpline(*avantage_score_A_smooth)(coups))
    axs[3].plot(coups,0.5*BSpline(*avantage_physique_B_smooth)(coups) + 0.5*BSpline(*avantage_score_B_smooth)(coups))
    axs[3].set_ylim([-1, 1])
    axs[3].set_xlim([0, 100])
    axs[3].set_ylabel('Domination')
    
    fig.supxlabel("Number of strokes")
    
def display_detail_phys_domination(df, ni):
    diffsA, Fatig, Aggre, Angle = np.array(calcul_diff_position(df))
    coups = np.arange(0,101,1)
    
    fig, axs = plt.subplots(4)
    fig.suptitle('Evolution de la domination physique sur un set')
    
    axs[0].plot(coups, Fatig, label = df['joueurA'][ni])
    axs[0].set_xlim([0, 100])
    axs[0].set_ylabel('Fatigue')
    
    axs[1].plot(coups, Aggre)
    axs[1].set_ylim([-1, 1])
    axs[1].set_xlim([0, 100])
    axs[1].set_ylabel('Agressivity')
    
    axs[2].plot(coups,Angle)
    axs[2].set_ylim([-1, 1])
    axs[2].set_xlim([0, 100])
    axs[2].set_ylabel('Angular Difficulty')
    
    axs[3].plot(coups, diffsA)
    axs[3].set_ylim([-1, 1])
    axs[3].set_xlim([0, 100])
    axs[3].set_ylabel('Domination')

def display_stress_domination(df, ni):
    Stress = np.array(calcul_stress(df))
    coups = np.arange(0,101,1)
    
    fig, axs = plt.subplots(2)
    fig.suptitle('Evolution de la domination mentale sur un set')
    
    axs[0].plot(coups, df['scoreA'], label = df['joueurA'][ni])
    axs[0].plot(coups, df['scoreB'], label = df['joueurB'][ni])
    axs[0].set_xlim([0, 100])
    axs[0].legend(loc = 'lower right')
    axs[0].set_ylabel('Score')
    
    axs[1].plot(coups, Stress)
    axs[1].set_ylim([-1.1, 1.1])
    axs[1].set_xlim([0, 100])
    axs[1].set_ylabel('Stress remontada')
    
def display_all_domination(df, ni):
    N = df.shape[0]
    calcul_scores(df)
    diffsA, Fatig, Aggre, Angle = np.array(calcul_diff_position(df))
    Stress = np.array(calcul_stress(df))
    
    fig, axs = plt.subplots(5)
    fig.suptitle('Evolution de la domination sur un set')
    
    coups = np.arange(0,N,1)
    avantage_scoreA = np.array(df['proba_gagne'])
    avantage_scoreB = - avantage_scoreA
    
    avantage_score_A_smooth = splrep(coups, avantage_scoreA, s=1)
    avantage_score_B_smooth = splrep(coups, avantage_scoreB, s=1)
    
    avantage_physique_A_smooth = splrep(coups, diffsA, s=1)
    avantage_physique_B_smooth = splrep(coups, -diffsA, s=1)
    
    avantage_stress_A_smooth = splrep(coups, Stress, s=1)
    avantage_stress_B_smooth = splrep(coups, -Stress, s=1)
    
    
    axs[0].plot(coups, df['scoreA'], label = df['joueurA'][ni])
    axs[0].plot(coups, df['scoreB'], label = df['joueurB'][ni])
    axs[0].legend(loc="lower right")
    axs[0].set_xlim([0, N])
    axs[0].set_ylabel('Score')
    
    axs[1].plot(coups, BSpline(*avantage_score_A_smooth)(coups))
    axs[1].plot(coups, BSpline(*avantage_score_B_smooth)(coups))
    axs[1].set_ylim([-1, 1])
    axs[1].set_xlim([0, N])
    axs[1].set_ylabel('Winning chances')
    
    axs[2].plot(coups,BSpline(*avantage_physique_A_smooth)(coups))
    axs[2].plot(coups,BSpline(*avantage_physique_B_smooth)(coups))
    axs[2].set_ylim([-1, 1])
    axs[2].set_xlim([0, N])
    axs[2].set_ylabel('Physical domination')
    
    axs[3].plot(coups,BSpline(*avantage_stress_A_smooth)(coups))
    axs[3].plot(coups,BSpline(*avantage_stress_B_smooth)(coups))
    axs[3].set_ylim([-1, 1])
    axs[3].set_xlim([0, N])
    axs[3].set_ylabel('Stress Domination')
    
    axs[4].plot(coups,0.4*BSpline(*avantage_score_A_smooth)(coups)+0.3*BSpline(*avantage_physique_A_smooth)(coups)+0.3*BSpline(*avantage_stress_A_smooth)(coups))
    axs[4].plot(coups,0.4*BSpline(*avantage_score_B_smooth)(coups)+0.3*BSpline(*avantage_physique_B_smooth)(coups)+0.3*BSpline(*avantage_stress_B_smooth)(coups))
    axs[4].set_ylim([-1, 1])
    axs[4].set_xlim([0, N])
    axs[4].set_ylabel('Global Domination')
    
    fig.supxlabel("Number of strokes")    
    
def display_domination(df, ni):
    N = df.shape[0]
    calcul_scores(df)
    diffsA, Fatig, Aggre, Angle = np.array(calcul_diff_position(df))
    Stress = np.array(calcul_stress(df))
    
    fig, axs = plt.subplots(2, figsize=(8,12))
    fig.suptitle('Evolution de la domination sur un set')
    
    coups = np.arange(0,N,1)
    avantage_scoreA = np.array(df['proba_gagne'])
    avantage_scoreB = - avantage_scoreA
    
    avantage_score_A_smooth = splrep(coups, avantage_scoreA, s=1)
    avantage_score_B_smooth = splrep(coups, avantage_scoreB, s=1)
    
    avantage_physique_A_smooth = splrep(coups, diffsA, s=1)
    avantage_physique_B_smooth = splrep(coups, -diffsA, s=1)
    
    avantage_stress_A_smooth = splrep(coups, Stress, s=1)
    avantage_stress_B_smooth = splrep(coups, -Stress, s=1)
    
    
    axs[0].plot(coups, df['scoreA'], label = df['joueurA'][ni])
    axs[0].plot(coups, df['scoreB'], label = df['joueurB'][ni])
    axs[0].legend(loc="lower right")
    axs[0].set_xlim([0, N])
    axs[0].set_ylabel('Score', rotation=0, labelpad=50)
    axs[0].yaxis.set_label_coords(-0.075, 0.5)
    
    
    axs[1].plot(coups,0.4*BSpline(*avantage_score_A_smooth)(coups)+0.3*BSpline(*avantage_physique_A_smooth)(coups)+0.3*BSpline(*avantage_stress_A_smooth)(coups))
    axs[1].plot(coups,0.4*BSpline(*avantage_score_B_smooth)(coups)+0.3*BSpline(*avantage_physique_B_smooth)(coups)+0.3*BSpline(*avantage_stress_B_smooth)(coups))
    axs[1].set_ylim([-1, 1])
    axs[1].set_xlim([0, N])
    axs[1].set_ylabel('Domination', rotation=0, labelpad=50)
    axs[1].yaxis.set_label_coords(-0.15, 0.5)
    
    fig.supxlabel("Number of strokes")    
    
# match LIANG LEBRUN
def liang_lebrun():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2022_macao_china_annotation_all.csv")
    display_domination(df, 0)

# match LEBRUN DRINKHALL
def lebrun_drinkhall():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2023_France_Q_ChE_annotation_all.csv")[100:]  
    display_domination(df, 100)

# match JARVIS GAUZY
def jarvis_gauzy():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2023_France_Q_ChE_annotation_all.csv")[31:100]
    display_domination(df, 31)
    
if __name__ == '__main__':
    liang_lebrun()
