import json
import maya.cmds as cmds
import maya.mel as mel

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QCheckBox
 
class OutlinerOrganizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("outliner organiser")
        self.resize(500, 100)
        self.create_ui()

    def create_ui(self):

        #cree les different elements necessaire pour le UI
        layout = QVBoxLayout(self)
        label = QLabel("enter json rule path")
        self.boite_texte = QLineEdit()
        bouton = QPushButton("organise outliner")
        bouton.clicked.connect(self.on_click)
        self.selection_only_box = QCheckBox("apply on selection only")
        self.apply_color_box = QCheckBox("apply colors")
        self.apply_reorder_box = QCheckBox("apply reorder")

        #ajoute tout au layout
        layout.addWidget(label)
        layout.addWidget(self.boite_texte)
        layout.addWidget(self.selection_only_box)
        layout.addWidget(self.apply_color_box)
        layout.addWidget(self.apply_reorder_box)
        layout.addWidget(bouton)


    def message_erreur(self, texte):

        message_erreur = QMessageBox()
        message_erreur.setText(texte)
        message_erreur.setIcon(QMessageBox.Critical)
        message_erreur.exec()

    def on_click(self):

        #mets dans une variable le path du json regle 
        regle_path = self.boite_texte.text()

        try:
            #ouvre le json et save ces données dans data
            with open(regle_path, encoding='utf-8') as f:
                data = json.load(f)

        #message d'erreur si jamais le fichier n'est pas trouver ou s'il le champ est vide
        except FileNotFoundError:
            self.message_erreur("Fichier non trouver")
            return

        #message d'erreur si jamais le fichier json est brisé
        except json.JSONDecodeError:
            self.message_erreur("Fichier non valide")
            return

        #si la case selection only est cocher, crée un liste avec seulement les objet selectionné
        if self.selection_only_box.isChecked():
            liste_objet = cmds.ls(selection=True)

        #sinon mets tout les objets dans la liste
        else:
            liste_objet = cmds.ls()

        #ouvre le chunk pour le ctrlZ
        cmds.undoInfo(openChunk=True)

        #crée un liste vide pour ensuite y mettre les objets a trier
        liste_objet_a_trier = []

        #parcours tout les items de la liste_objet
        for nom_objet in (liste_objet):
            #parcours tout les keys du json
            for prefixe_objet in (data.keys()):

               #si le nom de l'objet commence avec l'un des prefixes dit dans le json
               if nom_objet.startswith(prefixe_objet) :

                    #ajoute l'objet dans la liste a trier
                    liste_objet_a_trier.append(nom_objet)

                    #si la case pour appliquer les couleurs est coché
                    if self.apply_color_box.isChecked():

                        #récupérer la couleur en fonction du préfixe de l'objet
                        couleur = data[prefixe_objet]

                        #active l'option des couleurs
                        cmds.setAttr(nom_objet + '.useOutlinerColor', True) 
                        #applique les couleurs rgb, *couleur permet d'extraire chaque chiffre
                        #du code de couleur et double3 indique a maya que c'est un groupe de 3 chiffre
                        cmds.setAttr(nom_objet + '.outlinerColor', *couleur, type="double3")
        

        #trie la liste d'objet a trier
        liste_objet_a_trier.sort()

        #pour tout les objets dans la lister a trier
        for objet in liste_objet_a_trier:
            #si la case apply reorder est cocher
            if self.apply_reorder_box.isChecked():
                #comme ma liste est déja trier en ordre croissant, je commence par le premier item
                #et ensuite j'envoie les autres 1 par 1 sous celui-ci
                cmds.reorder(objet, back=True)

        #ferme le chunk pour le ctrlZ
        cmds.undoInfo(closeChunk=True)

        #refresh l'outliner
        mel.eval("AEdagNodeCommonRefreshOutliners;")
               

def main():
    global widget
    try:
        widget.close()
    except Exception:
        pass
    widget = OutlinerOrganizer()
    widget.show()
 
main()