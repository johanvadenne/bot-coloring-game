import cv2
import numpy as np
import mss
import pydirectinput
import keyboard
import pyautogui
from PIL import ImageGrab, Image
import pytesseract
import re
from pynput import mouse
from pynput.mouse import Listener, Button, Controller
import ctypes
from ctypes import wintypes
import time
import os

output_file="screenshot.png"
output_cel_temp="dossier_cellule_3/cellule_temp{&&&}.png"

# Définir les structures et les constantes nécessaires
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# Définir la structure POINT utilisée pour le mouvement de la souris
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

# Charger l'API user32
user32 = ctypes.windll.user32

# Fonction pour déplacer la souris et simuler un clic
def click(x, y):
    # Déplacer la souris
    ctypes.windll.user32.SetCursorPos(x, y)
    # Simuler un clic gauche
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

def declick():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)





def get_click():
    # attendre que la touche "enter" soit pressée
    keyboard.wait("enter")
    # recuperer la position du curseur
    x, y = pyautogui.position()

    return x, y











# Fonction pour créer et ajuster un cadre basé sur deux clics
def make_cadre():
    print("Cliquez pour sélectionner le premier coin du cadre.")
    x1, y1 = get_click()  # Premier clic
    print(f"Premier point sélectionné : ({x1}, {y1})")

    print("Cliquez pour sélectionner le deuxième coin du cadre.")
    x2, y2 = get_click()  # Deuxième clic
    print(f"Deuxième point sélectionné : ({x2}, {y2})")

    # Assurer que (x1, y1) est le coin supérieur gauche et (x2, y2) le coin inférieur droit
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))

    # Parcourir les pixels dans le cadre pour trouver les pixels noirs
    temp_cadre = (x1, y1, x2, y2)

    # Parcourir du coin supérieur gauche vers le bas
    for x in range(x1, x2 + 1):
        for y in range(y1, int(y1 + (y2-y1)/50)):
            print(f"Pixel hg ({x}, {y}) : {pyautogui.pixel(x, y)}")
            if pyautogui.pixel(x, y) == (31, 32, 35):  # Si le pixel est noir
                temp_cadre = (x, y, x2, y2)
                break
        if temp_cadre != (x1, y1, x2, y2):
            break
    x1, y1 = temp_cadre[:2]

    # Parcourir du coin inférieur droit vers le haut
    for x in range(x2, x1 - 1, -1):
        for y in range(y2, int(y2 - (y2-y1)/50), -1):
            print(f"Pixel bd ({x}, {y}) : {pyautogui.pixel(x, y)}")
            if pyautogui.pixel(x, y) == (31, 32, 35):  # Si le pixel est noir
                temp_cadre = (x1, y1, x, y)
                break
        if temp_cadre != (x1, y1, x2, y2):
            break
    x2, y2 = temp_cadre[2:]

    cadre = (x1, y1, x2, y2)
    print(f"Cadre final : {cadre}")

    return cadre





def get_pas(cadre):
    """
    recupere le pas de la grille
    """
    # ajouter 1 pixel pour eviter de tomber sur la bordure
    cadre = (cadre[0] + 1, cadre[1] + 1, cadre[2] - 1, cadre[3] - 1)
    tempx = cadre[0]
    # boucle pour trouver le pas tant que le pixel n'est pas noir
    while True:
        print(f"Pixel ({tempx}, {cadre[1]}) : {pyautogui.pixel(tempx, cadre[1])}")
        # recuperer la couleur du pixel
        couleur = pyautogui.pixel(tempx, cadre[1])
        # si la couleur est noir
        if couleur == (31, 32, 35):
            break
        # sinon on avance de 1 pixel
        tempx += 1
    pas = tempx - cadre[0]

    return pas



# def analyse_number(image_path):
#     text = textract.process(image_path).decode('utf-8')
#     number = extract_number(text)  # Utiliser la fonction d'extraction de numéro définie ci-dessus

#     return number



def extract_cellule(pas):
    try:
        image = cv2.imread(output_file)
        height, width, _ = image.shape
        tab_cellule = []
        nbr_img=0

        x1=0
        y1=0
        x2=pas
        y2=pas
        pas+=1
        while True:

            # S'assurer que x2 et y2 ne dépassent pas les dimensions de l'image
            if x2 > width:
                x1 = 0
                x2 = pas  # Limiter x2 à la largeur de l'image
                y1 += pas  # Limiter y2 à la hauteur de l'image
                y2 += pas  # Limiter y2 à la hauteur de l'image
            if y2 > height:
                break

            cell_image = image[y1:y2, x1:x2]

            if not any(np.array_equal(cell_image, existing) for existing in tab_cellule):
                if nbr_img > 100:
                    break
                nbr_img+=1
                tab_cellule.append(cell_image)
                name_img_cell = output_cel_temp.replace("{&&&}", str(nbr_img))
                cv2.imwrite(name_img_cell, cell_image)

            x2 += pas
            x1 += pas
    except:
        return 1




def capture_screen(cadre):
    """
    Capture une image de l'écran entre les coordonnées (x1, y1) et (x2, y2).

    Args:
        x1, y1: Coordonnées du coin supérieur gauche.
        x2, y2: Coordonnées du coin inférieur droit.
        output_file: Chemin où enregistrer l'image capturée.
    """
    # Capture la région de l'écran
    bbox = (cadre[0], cadre[1], cadre[2], cadre[3])
    screenshot = ImageGrab.grab(bbox)

    # Enregistre l'image capturée
    screenshot.save(output_file)
    print(f"Capture enregistrée dans {output_file}")




def find_pict(pict):
    # recuperer la position de l'image

    try:
        # trouver via la couleur
        position = pyautogui.locateOnScreen(pict, confidence=0.99, grayscale=True, region=(0, 0, 1920, 1080))
        x, y = position.left, position.top



        # print(f'position : {x}, {y}')
    except:
        x, y = -1, -1
    return x, y

def find_all_pict(pict):
    # recuperer toutes les positions de l'image
    position = pyautogui.locateAllOnScreen(pict, confidence=0.99, grayscale=True, region=(0, 0, 1920, 1080))

    return position


def change_color():
    # presser la touche "e"
    keyboard.press("e")

def check_color(pic, pas):
    # recuperer la position de l'image
    x, y = find_pict(pic)
    # clicker sur l'image




    x = int(x)
    y = int(y)

    click(x+(pas//2), y+(pas//2))
    declick()
    # attendre 0.01 seconde
    time.sleep(0.008)

    # re recuperer la position de l'image
    x2, y2 = find_pict(pic)

    if x2 == -1 or y2 == -1:
        return False

    x2 = int(x2)
    y2 = int(y2)

    # si les positions les memes
    if x == x2 and y == y2:
        # changer la couleur
        change_color()
        return check_color(pic, pas)


    # sinon
    else:
        return True









def color():
    while True:
        x, y = pyautogui.position()
        color = pyautogui.pixel(x, y)
        print(f'couleur : {color}')

# color()

def pos_souris():
    while True:
        x, y = pyautogui.position()
        print(f'position de la souris : {x}, {y}')

# pos_souris()


def supprimer_fichiers_dossier(dossier):
    for fichier in os.listdir(dossier):
        chemin = os.path.join(dossier, fichier)
        if os.path.isfile(chemin):  # Vérifie si c'est un fichier
            os.remove(chemin)       # Supprime le fichier


# couleur : (48, 52, 55) / exterieure
# couleur : (198, 198, 196) / interieure
# couleur : (31, 32, 35) / bordure
# Cadre final : (142, 303, 1192, 768)

supprimer_fichiers_dossier("dossier_cellule_3")

cadre = make_cadre()

# cadre = (417, 293, 917, 793)

pas = get_pas(cadre)
print(f"Le pas de la grille est de {pas} pixels.")

capture_screen(cadre)
extract_cellule(pas)


# parcourir les images
list_img = os.listdir("dossier_cellule_3")

for img in list_img:

    pic = f"dossier_cellule_3/{img}"
    check_color_val = check_color(pic, pas)
    print(f"check_color_val : {str(check_color_val)}")
    if not check_color_val:
        continue

    path = f"dossier_cellule_3/{img}"
    print(f"image : {path}")
    all = find_all_pict(path)
    print("find all pict : ")
    for pos in all:
        print("pos : " + str(pos))

        x, y = pos.left, pos.top
        print(f"x: {x} y: {y}")

        y = int(y)
        x = int(x)

        x += pas // 2
        y += pas // 2
        click(x, y)
        time.sleep(0.001)

        if x == -1 or y == -1:
            break

        if keyboard.is_pressed('q'):
            break

    declick()