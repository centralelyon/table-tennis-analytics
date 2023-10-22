#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 08:31:31 2023

@author: gab
"""
import sys
sys.path.append('..')

# faire un figure canon qui résume le match avec toutes les métriques

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import splrep, BSpline

from Domination import Calcul_Domination_Match as CDM
from ExpectedScore import Analyse_Simu as AS
from ExpectedScore import Expected_Points as EP
from Creativity import Creativity as C

def detect_sets(df, nom_A, nom_B):
    sets_stroke = {}
    sets_points = {}
    num_set = 1
    debut_stroke = 0
    # Initialiser les scores des deux joueurs à zéro
    scoreA = 0
    scoreB = 0
    setA = 0
    setB = 0
    # Créer des listes vides pour stocker les scores des deux joueurs
    proba_gagne = []
    scoresA = []
    scoresB = []
    
    # Parcourir le DataFrame
    for i, row in df.iterrows():
        proba_gagne.append(proba_gagne_match(scoreA, scoreB, setA, setB))
        scoresA.append(scoreA)
        scoresB.append(scoreB)
        if (scoreA >= 11 and scoreB < scoreA - 1) or (scoreB >= 11 and scoreA < scoreB - 1):
            if scoreA > scoreB :
                setA += 1
            else :
                setB += 1
            sets_stroke[num_set] = (debut_stroke, i+2)
            num_set += 1
            debut_stroke = i+2
            scoreA = 0
            scoreB = 0
        joueur = row['nom']
        
        # Si le point est en faute (derniere touche de balle = perdant)
        if row['faute'] == 'out' or row['faute'] == 'filet' :
            if nom_A == joueur :
                scoreB += 1
            else :
                scoreA += 1
        # Si le point est gagnant (derniere touche de balle = gagnant)
        elif row['faute'] == 'pt_gagne':
            if nom_B == joueur :
                scoreB += 1
            else :
                scoreA += 1
    df['scoreA'] = scoresA
    df['scoreB'] = scoresB
    sets_stroke[num_set] = (debut_stroke, i+2)
    scoresA.append(scoreA)
    scoresB.append(scoreB)
    proba_gagne.append(proba_gagne_match(scoreA, scoreB, setA, setB))
    return(sets_points, sets_stroke, scoresA, scoresB, np.array(proba_gagne))

def proba_gagne_match(scoreA, scoreB, setA, setB):
    proba_gagne_set_actuel = CDM.proba_A_gagne(scoreA, scoreB)
    
    if setA == 3 :
        return 1
    elif setB == 3 :
        return 0
    else :
        return(proba_gagne_set_actuel*proba_gagne_match(0, 0, setA+1, setB) + (1-proba_gagne_set_actuel)*proba_gagne_match(0, 0, setA, setB+1) )
    
def calcul_stress_match(match, nom_A, nom_B):
    Stress = []
    for set_i in match :
        debut, fin = match[set_i]
        S, lS = CDM.calcul_stress(df[debut:fin], debut, nom_A, nom_B)
        Stress += S
    Stress.append(lS)
    return Stress

    
def calcul_physique_match(match, nom_A, nom_B):
    physique = []
    for set_i in match :
        debut, fin = match[set_i]
        P, lP = CDM.calcul_diff_position(df[debut:fin], nom_A, nom_B)
        physique += P
    physique.append(lP)
    # plt.plot(physique)
    return physique
        
        
def evaluer_match(A, df, sets, nom_A, nom_B):
    n = 1
    X_scoresA, X_scoresB, scoresA, scoresB = [0], [0], [0], [0]
    X_scoreA,  X_scoreB,  scoreA, scoreB = 0, 0, 0, 0
    chemin = ['racine']
    
    for i,row in df.iterrows():
        if row.type_service in ['lat_droit','lat_gauche'] :
            type_stroke = row.type_service
            serveur = row.nom
        else :
            type_stroke = row.type_coup
        
        joueur = row.nom
        zone = row.zone_jeu
        lateralite = row.lateralite
        faute = row.faute
        
        if faute == 'out' or faute == 'filet' :
            if nom_A == joueur :
                scoreB += 1
            else :
                scoreA += 1

        # Si le point est gagnant (derniere touche de balle = gagnant)
        elif faute == 'pt_gagne':
            if nom_B == joueur :
                scoreB += 1
            else :
                scoreA += 1

            
        if (scoreA >= 11 and scoreB < scoreA -1) or (scoreB >= 11 and scoreA < scoreB -1) :
            scoresA.append(scoreA)
            scoresB.append(scoreB)
            X_scoresA.append(X_scoreA)
            X_scoresB.append(X_scoreB)
            scoreA = 0
            scoreB = 0
            X_scoreA = 0
            X_scoreB = 0     
        else :
            scoresA.append(scoreA)
            scoresB.append(scoreB)
            X_scoresA.append(X_scoreA)
            X_scoresB.append(X_scoreB)
            
        # DETERMINATION DES SCORES
        # Si le point est terminé : ça veut dire qu'un nouveau point va commencer
        if faute in ['out', 'filet', 'pt_gagne'] :     
            chemin.append(lateralite)
            if type_stroke == 'defensif' :
                chemin.append('poussette')
            elif type_stroke == 'intermediaire' :
                chemin.append('defensif')
            else :
                chemin.append(type_stroke)
            if row.faute == 'pt_gagne' :
                chemin.append(zone + ' pt_gagne')
            else :
                chemin.append('faute')
            # print('Point ', n , ' : ',serveur, chemin)
            n+= 1
            add_XscoreA, add_XscoreB = EP.evaluer_stroke(A, chemin, 3, serveur, nom_A, nom_B)

            # print(serveur, add_XscoreA, add_XscoreB)
            # print(add_XscoreA)
            # print(add_XscoreB)
            
            X_scoreA += add_XscoreA
            X_scoreB += add_XscoreB
            
            chemin = ['racine']
        else :
            chemin.append(lateralite)
            if type_stroke == 'defensif' :
                chemin.append('poussette')
            elif type_stroke == 'intermediaire' :
                chemin.append('defensif')
            else :
                chemin.append(type_stroke)
            chemin.append(zone)

    return X_scoresA, X_scoresB, scoresA, scoresB
        
def display_score_domination(proba_gagne, scoresA, scoresB, nom_A, nom_B):
    fig, axs = plt.subplots(2, figsize=(8,12))
    fig.suptitle('Evolution de la domination sur un match complet')
    N = df.shape[0]
    coups = np.arange(0,N+1,1)
    
    avantage_score_A_smooth = splrep(coups, 2*proba_gagne-1, s=1)
    avantage_score_B_smooth = splrep(coups, 1-2*proba_gagne, s=1)
    
    axs[0].plot(coups, scoresA, label = nom_A)
    axs[0].plot(coups, scoresB, label = nom_B)
    axs[0].legend(loc="lower right")
    axs[0].set_xlim([0, N])
    axs[0].set_ylabel('Score', rotation=90, labelpad=20)
    axs[0].yaxis.set_label_coords(-0.075, 0.5)
    
    
    axs[1].plot(coups, BSpline(*avantage_score_A_smooth)(coups))
    axs[1].plot(coups, BSpline(*avantage_score_B_smooth)(coups))
    axs[1].set_ylim([-1, 1])
    axs[1].set_xlim([0, N])
    axs[1].set_ylabel('Domination', rotation=90, labelpad=20)
    axs[1].yaxis.set_label_coords(-0.075, 0.5) 

def display_expected_score(X_scoresA, X_scoresB, scoresA, scoresB, nom_A, nom_B):
    fig, axs = plt.subplots(2, figsize=(8,12))
    fig.suptitle('Evolution de la domination sur un match complet')
    
    axs[0].plot(scoresA, label = nom_A)
    axs[0].plot(scoresB, label = nom_B)
    axs[0].legend(loc="lower right")
    axs[0].set_ylabel('Score', rotation=90, labelpad=20)
    axs[0].yaxis.set_label_coords(-0.075, 0.5)
    
    
    axs[1].plot(X_scoresA, label = nom_A)
    axs[1].plot(X_scoresB, label = nom_B)
    axs[1].set_ylabel('Expected Score', rotation=90, labelpad=20)
    axs[1].yaxis.set_label_coords(-0.075, 0.5)
    
    
def display_alldom_Xscore(proba_gagne, Stress, physique, X_scoresA, X_scoresB, scoresA, scoresB, nom_A, nom_B):
    fig, axs = plt.subplots(6, figsize=(8,16))
    fig.suptitle('Evolution de la domination sur un match complet')
    
    N = df.shape[0]
    coups = np.arange(0,N+1,1)
    
    avantage_score_A =  2*proba_gagne-1
    avantage_score_B =  1-2*proba_gagne
    
    Stroke_domination_A = 0.4*np.array(avantage_score_A)+0.3*np.array(Stress)+0.3*np.array(physique)
    Stroke_domination_B = -1* Stroke_domination_A
    
    Stroke_domination_A_smooth = splrep(coups, Stroke_domination_A, s=1)
    Stroke_domination_B_smooth = splrep(coups, Stroke_domination_B, s=1)
    
    axs[0].plot(coups, scoresA, label = nom_A)
    axs[0].plot(coups, scoresB, label = nom_B)
    # axs[0].legend(loc="lower right")
    axs[0].set_xlim([0, N])
    axs[0].set_ylabel('Real Score', rotation=0, labelpad=20)
    axs[0].yaxis.set_label_coords(-0.075, 0.5)
    axs[0].set_xticks([])
    axs[0].set_yticks([])
    
    axs[1].plot(coups, X_scoresA)
    axs[1].plot(coups, X_scoresB)
    axs[1].set_xlim([0, N])
    axs[1].set_ylabel('Xscore', rotation=0, labelpad=20)
    axs[1].yaxis.set_label_coords(-0.075, 0.5)
    axs[1].set_xticks([])
    axs[1].set_yticks([])
    
    axs[2].plot(coups,  BSpline(*Stroke_domination_A_smooth)(coups))
    axs[2].plot(coups,  BSpline(*Stroke_domination_B_smooth)(coups))
    axs[2].set_ylabel('Domination', rotation=0, labelpad=20)
    axs[2].set_xlim([0, N])
    axs[2].set_ylim([-1,1])
    axs[2].yaxis.set_label_coords(-0.075, 0.5)
    axs[2].set_xticks([])
    axs[2].set_yticks([])
    
    axs[3].plot(coups,  avantage_score_A)
    axs[3].plot(coups,  avantage_score_B)
    axs[3].set_ylabel('Score dom', rotation=0, labelpad=20)
    axs[3].set_xlim([0, N])
    axs[3].set_ylim([-1,1])
    axs[3].yaxis.set_label_coords(-0.075, 0.5)
    axs[3].set_xticks([])
    axs[3].set_yticks([])
    
    axs[4].plot(coups,  physique)
    axs[4].plot(coups,  -physique)
    axs[4].set_ylabel('physical dom', rotation=0, labelpad=20)
    axs[4].set_xlim([0, N])
    axs[4].set_ylim([-1,1])
    axs[4].yaxis.set_label_coords(-0.075, 0.5)
    axs[4].set_xticks([])
    axs[4].set_yticks([])
    
    axs[5].plot(coups,  Stress)
    axs[5].plot(coups,  -Stress)
    axs[5].set_ylabel('Mental dom', rotation=0, labelpad=20)
    axs[5].set_xlim([0, N])
    axs[5].set_ylim([-1,1])
    axs[5].yaxis.set_label_coords(-0.075, 0.5)
    axs[5].set_xticks([])
    axs[5].set_yticks([])
    
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, mode='expand')
    
    
    
def distance_matrix(df, nom_A, nom_B):
    chemins_A, chemins_B = C.extract_match(df, nom_A, nom_B)
    
    three_first_strokes_A = []
    three_first_strokes_B = []
    for j,chemin in enumerate(chemins_A) :
        for i in range(10):
            chemin.append('vide')
        three_first_strokes_A.append(chemin[:10])
        
    for j,chemin in enumerate(chemins_B) :
        for i in range(10):
            chemin.append('vide')
        three_first_strokes_B.append(chemin[:10])
    
    matrice_A = C.convert_to_number(three_first_strokes_A)
    matrice_B = C.convert_to_number(three_first_strokes_B)
    
    fig = plt.figure(figsize=(10, 6))
    grid = fig.add_gridspec(2, 2, width_ratios=[4, 4], height_ratios=[6, 0.6])
    
    # Sous-graphique pour image A
    ax1 = fig.add_subplot(grid[0, 0])
    im1 = ax1.imshow(matrice_A, cmap='Reds')
    ax1.set_title(nom_A)
    ax1.set_xlabel('Opening number')
    ax1.set_ylabel('Opening number')

    # Sous-graphique pour image B
    ax2 = fig.add_subplot(grid[0, 1])
    im2 = ax2.imshow(matrice_B, cmap='Reds')
    ax2.set_title(nom_B)
    ax2.set_xlabel('Opening number')
    ax2.set_ylabel('Opening number')
    
    # Colorbar
    cbar_ax = fig.add_subplot(grid[1, :])
    cbar = plt.colorbar(im2, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Distance between openings')
    

    # Afficher la figure
    plt.show()

    
if __name__ == '__main__':
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/ALEXIS-LEBRUN_vs_FAN-ZHENDONG_annotation_2.csv")
    nom_A = df['joueur_frappe'][0]
    nom_B = df['joueur_sur'][0]
    
    A = AS.Arbre()
    AS.give_match(A)
    # A.afficher(3)         # pour afficher l'arbre dans le terminal (attention ça prend de la place), 3 est la profondeur d'affichage
    
    sets_points, sets_stroke, scoresA, scoresB, proba_gagne = detect_sets(df, nom_A, nom_B)
    X_scoresA, X_scoresB, scoresA, scoresB = evaluer_match(A, df, sets_stroke, nom_A, nom_B)
    diffA = np.array(calcul_physique_match(sets_stroke, nom_A, nom_B))
    Stress = np.array(calcul_stress_match(sets_stroke, nom_A, nom_B))
    
    display_alldom_Xscore(proba_gagne, Stress, diffA, X_scoresA, X_scoresB, scoresA, scoresB, nom_A, nom_B)
    display_score_domination(proba_gagne, scoresA, scoresB, nom_A, nom_B)
    display_expected_score(X_scoresA, X_scoresB, scoresA, scoresB, nom_A, nom_B)
    distance_matrix(df, nom_A, nom_B)
