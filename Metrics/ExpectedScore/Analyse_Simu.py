#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 08:45:21 2023

@author: gab
"""
# from calcul_domination import *
import pandas as pd
import re
import os
import sys
sys.path.append('..')

def give_match(A):
    path = '../../Data/SimulatedData/'
    file_name = '/test_generation.csv'
    liste_dossier = os.listdir(path)
    for d in liste_dossier :
        df = pd.read_csv(path + d + file_name)
        lire_schema_jeu(df, A)

def lire_schema_jeu(df, A):
    point_en_cours = ['racine']
    for i,row in df.iterrows():
        
        if row.type_service in ['lat_droit','lat_gauche'] :
            type_stroke = row.type_service
        else :
            type_stroke = row.type_coup
            
        if i+1 < len(df) :    # si c'est pas le dernier coup du fichier !
            row_suivante = df.loc[[i+1]]
            if row_suivante['type_service'][i+1] in ['lat_droit','lat_gauche'] :  # si l'échange s'arrete
                point_en_cours.append(row.lateralite)
                point_en_cours.append(type_stroke)
                if row.faute == 'pt_gagne' :
                    point_en_cours.append(row.zone_jeu+ ' pt_gagne')
                else :
                    point_en_cours.append('faute')
                A.ajout_chemin(point_en_cours)
                point_en_cours = ['racine']
            else :
                point_en_cours.append(row.lateralite)
                point_en_cours.append(type_stroke)
                point_en_cours.append(row.zone_jeu)
        else : #si c'est le dernier coup du fichier
            point_en_cours.append(row.lateralite)
            point_en_cours.append(type_stroke)
            if row.faute == 'pt_gagne' :
                point_en_cours.append(row.zone_jeu + ' pt_gagne')
            else :
                point_en_cours.append('faute')
            A.ajout_chemin(point_en_cours)
            

class Noeud :
    def __init__(self, nom, fils):
        self.nom = nom
        self.fils = fils
        self.nb_occurence = 0
        self.nb_branches_gagnantes = 0
        self.proba_gain = 0
        
    def update_proba(self):
        if self.nb_occurence == 0 :
            self.proba_gain = 0
        else :
            self.proba_gain = round(self.nb_branches_gagnantes/self.nb_occurence, 3)
        for f in self.fils :
            f.update_proba()
            
    def afficher(self, niveau, seuil):
        print(self.nom + ' : ' + str(self.nb_branches_gagnantes) + '/' + str(self.nb_occurence))
        if niveau + 1 < seuil :
            for f in self.fils :
                print("\t" * niveau, end = '')
                f.afficher(niveau+1, seuil)
            
    def fils_donne(self, fils_str):
        for f in self.fils :
            if f.nom == fils_str :
                return f
        new_f = Noeud(fils_str, [])
        self.fils.append(new_f)
        return(new_f)
    
    def fils_existe(self, fils_str):
        for f in self.fils :
            if f.nom == fils_str :
                return True
        return False
        
    def afficher_zone_proba(self):
        pass
        
class Arbre :
    def __init__(self):
        self.racine = Noeud('racine', [])
        
    def afficher(self, profondeur):
        p = 3*profondeur + 2
        self.racine.afficher(1, p)
        
    def afficher_chemin(self, chemin):
        noeud_actuel = self.racine
        print(noeud_actuel.nom + " : " + str(noeud_actuel.proba_gain))
        for i,n in enumerate(chemin[1:]):
            if noeud_actuel.fils_existe(n) :
                noeud_actuel = noeud_actuel.fils_donne(n)
                print("\t" * (i+1) + n + " : " + str(noeud_actuel.proba_gain) + ' = ' + str(noeud_actuel.nb_branches_gagnantes) + '/' + str(noeud_actuel.nb_occurence))
            else :
                print("\t" * (i+1) + n + " : aucune occurence")       
        
    def ajout_chemin(self, chemin):
        nb_strokes = (len(chemin)-1)//3
        dernier_joueur_est_serveur = nb_strokes%2
        gagnant_est_serveur = (dernier_joueur_est_serveur and chemin[-1][3:] == 'pt_gagne') or (not dernier_joueur_est_serveur and chemin[-1] == 'faute') 
        joueur_est_serveur = True
        
        self.racine.nb_occurence += 1
        if gagnant_est_serveur :
            self.racine.nb_branches_gagnantes += 1
        
        noeud_actuel = self.racine
            
        for n in chemin[1:] :
            noeud_actuel = noeud_actuel.fils_donne(n)
            noeud_actuel.nb_occurence += 1
            if (gagnant_est_serveur and joueur_est_serveur) or (not gagnant_est_serveur and not joueur_est_serveur)  :
                    noeud_actuel.nb_branches_gagnantes += 1
            if len(noeud_actuel.nom) == 2 : # si c'est une zone alors on change de coup
                joueur_est_serveur = not joueur_est_serveur
        self.racine.update_proba()

if __name__ == '__main__':
    A = Arbre()
    give_match(A)
    A.afficher(3)
    # A.afficher_chemin(['racine','coup_droit', 'lat_droit', 'm3', 'revers', 'offensif', 'm3', 'revers', 'offensif'])
