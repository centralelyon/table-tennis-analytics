#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 09:17:45 2023

@author: gab
"""
import sys
sys.path.append('..')

from plotly.figure_factory import create_dendrogram
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

import numpy as np
from ExpectedScore import Analyse_Simu as AS
# import Expected_Points as EP
import pandas as pd
import matplotlib.pyplot as plt

def liang_lebrun():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2022_macao_china_annotation_all.csv")
    return(df,0)

# match LEBRUN DRINKHALL
def lebrun_drinkhall():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2023_France_Q_ChE_annotation_all.csv")[100:]  
    return(df,100)

# match JARVIS GAUZY
def jarvis_gauzy():
    df = pd.read_csv("../../Data/AnnotatedData/WithTracking/2023_France_Q_ChE_annotation_all.csv")[31:100]
    return(df,31)

choices = ['0_type', '0_lat', '0_zone', '1_type', '1_lat', '1_zone', '2_type', '2_lat', '2_zone']

def create_dendro(noeud, choices, u):
    for f in noeud.fils :
        u.append()
        create_dendro(f, choices, u)
        
def extract_match(df, nom_A, nom_B):
    
    chemin = ['racine']
    openings_A = []
    openings_B = []
    #nom_A = df['joueurA'][0]
    #nom_B = df['joueurB'][0]
    
    for i,row in df.iterrows():
        if row.type_service in ['lat_droit','lat_gauche'] :
            serveur = row.nom
            type_stroke = row.type_service
        else :
            type_stroke = row.type_coup

        zone = row.zone_jeu
        lateralite = row.lateralite
        faute = row.faute

        # Si le point est terminé : ça veut dire qu'un nouveau point va commencer
        if faute in ['out', 'filet', 'pt_gagne'] :     
            chemin.append(lateralite)
            chemin.append(type_stroke)
            if row.faute == 'pt_gagne' :
                chemin.append(zone)
            else :
                chemin.append('faute')
                
            if serveur == nom_A :
                openings_A.append(chemin)
            else :
                openings_B.append(chemin)
                
            chemin = ['racine']
        else :
            chemin.append(lateralite)
            chemin.append(type_stroke)
            chemin.append(zone)
            
	#return nom_A, nom_B, scoresA, scoresB, server_names, winner_names, exchanges
    return(openings_A, openings_B)
    
"""def extract_match_2(df, ni):
    
    chemin = ['racine']
    openings_A = []
    openings_B = []
    nom_A = df['joueurA'][ni]
    nom_B = df['joueurB'][ni]
    
    for i,row in df.iterrows():
        if row.type_service in ['lat_droit','lat_gauche'] :
            serveur = row.nom
            type_stroke = row.type_service
        else :
            type_stroke = row.type_coup

        zone = row.zone_jeu
        lateralite = row.lateralite
        faute = row.faute

        # Si le point est terminé : ça veut dire qu'un nouveau point va commencer
        if faute in ['out', 'filet', 'pt_gagne'] :     
            chemin.append(lateralite)
            chemin.append(type_stroke)
            if row.faute == 'pt_gagne' :
                chemin.append(zone)
            else :
                chemin.append('faute')
                
            if serveur == nom_A :
                openings_A.append(chemin)
            else :
                openings_B.append(chemin)
                
            chemin = ['racine']
        else :
            chemin.append(lateralite)
            chemin.append(type_stroke)
            chemin.append(zone)
		return nom_A, nom_B, scoresA, scoresB, server_names, winner_names, exchanges"""

zones_to_index = {'faute' : 0, 'd1' : 1, 'd2' : 2, 'd3' : 3, 'm1' : 4, 'm2' : 5, 'm3' : 6, 'g1' : 7, 'g2' : 8, 'g3' : 9, 'vide' : 10}
distances_zones = [
    [0, 1, 2, 1, 2, 3, 2, 1, 2, 1, 0],
    [1, 0, 1, 2, 1, 2, 3, 2, 3, 4, 0],
    [2, 1, 0, 1, 2, 1, 2, 3, 2, 3, 0],
    [1, 2, 1, 0, 3, 2, 1, 4, 3, 2, 0],
    [2, 1, 2, 3, 0, 1, 2, 1, 2, 3, 0],
    [3, 2, 1, 2, 1, 0, 1, 2, 1, 2, 0],
    [2, 3, 2, 1, 2, 1, 0, 3, 2, 1, 0],
    [1, 2, 3, 4, 1, 2, 3, 0, 1, 2, 0],
    [2, 3, 2, 3, 2, 1, 2, 1, 0, 1, 0],
    [1, 4, 3, 2, 3, 2, 1, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


def distance(L1, L2):
    if L1 == L2:
        return 0
    size = len(L1)
    dist = 0
    for i in range(size):
        if L1[i] == 'vide' and L2[i] == 'vide' :
            dist += size - i
        elif  L1[i] == 'vide' or L2[i] == 'vide' :
            return dist/10
        elif L1[i] in ['racine', 'revers', 'coup_droit', 'lat_gauche', 'lat_droit', 'offensif', 'defensif', 'poussette'] :
            if L1[i] != L2[i] :
                dist += size - i  # Pénalité proportionnelle à la position de l'élément différent
        elif L1[i] in ['d1', 'd2', 'd3', 'm1', 'm2', 'm3', 'g1' ,'g2', 'g3', 'faute'] :
            i1 = zones_to_index[L1[i]]
            i2 = zones_to_index[L2[i]]
            dist_zone = distances_zones[i1][i2]/4
            dist += dist_zone * (size - i)
    return dist/10


def convert_to_number(exchanges) :
    matrice = []
    for chemin in exchanges:
        ligne = []
        for chemin_bis in exchanges :
            ligne.append(distance(chemin, chemin_bis))
        matrice.append(ligne)
    return(matrice)
        
if __name__ == '__main__':
    A = AS.Arbre()
    AS.give_match(A)
    
    """
    df,ni = jarvis_gauzy()
    nom_A, nom_B, scoresA, scoresB, server_names, winner_names, exchanges = extract_match_2(df, ni)
    labels_points = []
    three_first_strokes = []
    for j,chemin in enumerate(exchanges) :
        for i in range(10):
            chemin.append('vide')
        three_first_strokes.append(chemin[:10])
        labels_points.append(server_names[j] + ' sert, ' +  winner_names[j] + ' gagne sur ' + str(chemin[:10]))
        print(chemin[:10])


    
    matrice = np.array(convert_to_number(three_first_strokes))
    plt.imshow(matrice)
    numpoints = [str(i) for i in range(len(matrice))]
    
    dendro = create_dendrogram(matrice, orientation='right', labels=numpoints)
    dendro.update_layout({'width':700, 'height':500}) 


    labels = list(dendro['layout']['yaxis']['ticktext'])
    hauteurs = list(dendro['layout']['yaxis']['tickvals'])
    hauteurs_triees = labels.copy()
    for i,l in enumerate(labels) :
        hauteurs_triees[int(l)] = hauteurs[i]
    
    points = go.Scatter(
            x= list(range(len(matrice))),  # La timeline est située à x = 0
            y=hauteurs_triees,  # Hauteurs des noeuds du dendrogramme
            mode='markers',
            marker=dict(
                size=5,
                color=['red' if winner == nom_A else 'blue' for winner in winner_names],
                symbol='circle',
                ),
            xaxis='x2',
            yaxis='y2',
            name='Timeline', 
            text = labels_points)
            
    fig = go.Figure(dendro['data'])
    fig.add_trace(points)
    fig.add_trace(go.Heatmap(z=matrice,
                         colorscale='Viridis',
                         xaxis='x3',
                         yaxis='y3',
                         showlegend=False))
    fig.update_layout(xaxis={'side': 'top', 'domain': [0, 40], 'showticklabels': False},
                  yaxis={'side': 'right', 'showticklabels': False},
                  xaxis2={'side': 'top', 'domain': [0, 160]},
                  yaxis2={'side': 'left', 'showticklabels': False},
                  xaxis3={'anchor': 'y3', 'showticklabels': False},
                  yaxis3={'anchor': 'x3', 'showticklabels': False})
    
    
    fig.show()"""
