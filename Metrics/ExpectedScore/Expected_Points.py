#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:48:55 2023

@author: gab
"""
# A partir des trois premiers échanges : 
    # service, remise de l'adversaire et réponse du serveur
# determiner le expected score


import pandas as pd
import matplotlib.pyplot as plt


import sys
sys.path.append('..')
import Analyse_Simu as AS
#from ExpectedScore import Analyse_Simu as AS

# match LIANG LEBRUN
def liang_lebrun():
    df = pd.read_csv("Data/AnnotatedData/WithTracking/2022_macao_china_annotation_all.csv")
    return(df,0)

# match LEBRUN DRINKHALL
def lebrun_drinkhall():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2023_France_Q_ChE_annotation_all.csv")[100:]  
    return(df,100)

# match JARVIS GAUZY
def jarvis_gauzy():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2023_France_Q_ChE_annotation_all.csv")[31:100]
    return(df,31)

def lebrun_qiu():
    df = pd.read_csv("../../Data/AnnotatedData/WithoutTracking/FELIX-LEBRUN_vs_DANG-QIU_annotation.csv")
    return(df,0)
    

def evaluer_stroke(A, chemin, profondeur, serveur, nom_A, nom_B):
    p = 3*profondeur +1
    # A.afficher_chemin(chemin)
    chemin_utile = chemin[1:p]
    # print(chemin_utile)
    noeud = A.racine
    for i,n in enumerate(chemin_utile) :
        if noeud.fils_existe(n) :
            noeud = noeud.fils_donne(n)
            # print(i, n)
        else : 
            # print('le noeud qu on va voir est ',noeud.nom)
            # print(i)
            if not ((i-1)//3)%2 : # si c'est au serveur de jouer à l'instant i : if (i//3)%2
                # print("not serveur")
                if serveur == nom_A :
                    return(noeud.proba_gain, 1-noeud.proba_gain)
                else :
                    return(1-noeud.proba_gain,noeud.proba_gain)
            else :
                # print("serveur")
                if serveur == nom_B :
                    return(noeud.proba_gain, 1-noeud.proba_gain)
                else :
                    return(1-noeud.proba_gain,noeud.proba_gain)
           
    if serveur == nom_A :
        return (noeud.proba_gain, 1-noeud.proba_gain)
    return(1-noeud.proba_gain,noeud.proba_gain)
        

def evaluer_match(A, df, ni):
    nom_A = df['joueurA'][ni]
    nom_B = df['joueurB'][ni]
    
    X_scoresA, X_scoresB, scoresA, scoresB = [0], [0], [0], [0]
    X_scoreA,  X_scoreB,  scoreA, scoreB = 0, 0, 0, 0
    chemin = ['racine']
    num_set = 1
    for i,row in df.iterrows():
        if row["set"] != num_set:
            num_set = num_set = row["set"]
            X_scoreA,  X_scoreB,  scoreA, scoreB = 0, 0, 0, 0
            


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
        

        # DETERMINATION DES SCORES
        # Si le point est terminé : ça veut dire qu'un nouveau point va commencer
        if faute in ['out', 'filet', 'pt_gagne'] :     
            chemin.append(lateralite)
            chemin.append(type_stroke)
                
            if row.faute == 'pt_gagne' :
                chemin.append(zone + ' pt_gagne')
            else :
                chemin.append('faute')
            add_XscoreA, add_XscoreB = evaluer_stroke(A, chemin, 3, serveur, nom_A, nom_B)
            X_scoreA += add_XscoreA
            X_scoreB += add_XscoreB
            chemin = ['racine']
        else :
            chemin.append(lateralite)
            chemin.append(type_stroke)
            chemin.append(zone)
                
        scoresA.append(scoreA)
        scoresB.append(scoreB)
        X_scoresA.append(X_scoreA)
        X_scoresB.append(X_scoreB)
                
    fig, axs = plt.subplots(2)
    fig.suptitle('Real Score and Expected Score')
    
    coups = list(range(len(df)+1))
    
    axs[0].plot(coups, scoresA, label = 'score Fan Zhendong')
    axs[0].plot(coups, scoresB, label = 'score Truls Moregardh')
    axs[0].set_xlim([0, len(df)+1])
    axs[0].set_ylim([0, 11])
    axs[0].legend(loc = 'lower right')
    axs[0].set_ylabel('Real Score')
    
    axs[1].plot(coups, X_scoresA, label = 'X_score Fan Zhendong')
    axs[1].plot(coups, X_scoresB, label = 'X_score Truls Moregardh')
    axs[1].set_xlim([0, len(df)+1])
    axs[1].legend(loc = 'lower right')
    axs[1].set_ylabel('Expected Score')
    axs[1].set_xlabel('Strokes')

    plt.show()


if __name__ == '__main__':
    A = AS.Arbre()
    #AS.give_match(A)
    #df,ni = liang_lebrun()
    df = pd.read_csv("Data/AnnotatedData/WithTracking/FAN-ZHENDONG_vs_TRULS-MOREGARD_annotation_metrics.csv")
    ni = 0

    evaluer_match(A, df, ni)
