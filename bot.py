import cv2
import numpy as np
import keyboard
import pyautogui
from PIL import ImageGrab
import ctypes
from ctypes import wintypes
import time
import os

class MaErreurPersonnalisee(Exception):
    pass

# --- CONSTANTES ---
OUTPUT_FILE ="screenshot.png"
DIR_CELLULE ="dossier_cellule_3"
OUTPUT_CELL_TEMPLATE =f"{DIR_CELLULE}/cellule_temp&&&.png"
TIMER =0.001

# Couleurs utilisées dans le jeu
COLOR_BORDER = (31, 32, 35)
COLOR_INTERIEUR = (198, 198, 196)
COLOR_EXTERIEUR = (48, 52, 55)
# Cadre final : (142, 303, 1192, 768)

# Définir les structures et les constantes nécessaires
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

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



def get_position_mouse_pressed_enter():
    """Attend un clic sur 'Enter' pour récupérer la position actuelle du curseur."""
    # attendre que la touche "enter" soit pressée
    keyboard.wait("enter")
    # recuperer la position du curseur
    x, y = pyautogui.position()

    return x, y



# Fonction pour créer et ajuster un cadre basé sur deux clics
def select_frame():
    """
    Permet à l'utilisateur de sélectionner un cadre en cliquant sur deux coins opposés.
    Ajuste automatiquement les limites pour exclure les bordures inutiles.
    """
    print("Cliquez sur le premier coin du cadre.")
    x1, y1 = get_position_mouse_pressed_enter()
    print(f"Premier point sélectionné : ({x1}, {y1})")

    print("Cliquez sur le deuxième coin du cadre.")
    x2, y2 = get_position_mouse_pressed_enter()
    print(f"Deuxième point sélectionné : ({x2}, {y2})")

    # Réordonner pour s'assurer que (x1, y1) est le coin supérieur gauche
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))

    # Ajuster automatiquement le cadre pour inclure uniquement la grille
    x1, y1 = refine_frame_start(x1, y1, x2, y2)
    x2, y2 = refine_frame_end(x1, y1, x2, y2)

    frame = (x1, y1, x2, y2)
    print(f"Cadre final : {frame}")
    return frame

def refine_frame_start(x1, y1, x2, y2):
    """Affiner le coin supérieur gauche pour éviter les bordures."""
    for x in range(x1, x2 + 1):
        for y in range(y1, y1 + ((y2 - y1) // 50)):
            print(f"Pixel bd ({x}, {y}) : {pyautogui.pixel(x, y)}")
            if pyautogui.pixel(x, y) == COLOR_BORDER:
                return x, y
    return x1, y1


def refine_frame_end(x1, y1, x2, y2):
    """Affiner le coin inférieur droit pour éviter les bordures."""
    for x in range(x2, x1 - 1, -1):
        for y in range(y2, y2 - ((y2 - y1) // 50), -1):
            print(f"Pixel bd ({x}, {y}) : {pyautogui.pixel(x, y)}")
            if pyautogui.pixel(x, y) == COLOR_BORDER:
                return x, y
    return x2, y2





def calculate_grid_step(frame):
    """
    Calcule la taille des cellules (pas de la grille).
    """
    x, y = frame[0] + 1, frame[1] + 1
    while pyautogui.pixel(x, y) != COLOR_BORDER:
        x += 1
    step = x - frame[0]
    print(f"Pas de la grille : {step} pixels.")
    return step


def capture_screen(frame):
    """Capture une image de la région spécifiée par le cadre."""
    screenshot = ImageGrab.grab(frame)
    screenshot.save(OUTPUT_FILE)
    print(f"Capture enregistrée : {OUTPUT_FILE}")


def extract_cellule(grid_step):
    """
    Divise l'image capturée en cellules uniques et les enregistre.
    """

    image = cv2.imread(OUTPUT_FILE)
    height, width, _ = image.shape
    cells = []
    cell_count = 0
    grid_step_bis = grid_step

    for y in range(0, height, grid_step_bis):
        if y != 0:
            y+=1
        for x in range(0, width, grid_step_bis):
            if x != 0:
                x+=1
            if y + grid_step_bis > height or x + grid_step_bis > width:
                continue
            cell = image[y:y + grid_step_bis, x:x + grid_step_bis]
            if not any(np.array_equal(cell, existing) for existing in cells):
                cell_count += 1
                cells.append(cell)
                cell_path = OUTPUT_CELL_TEMPLATE.replace("&&&", str(cell_count))
                cv2.imwrite(cell_path, cell)
                print(f"Cellule sauvegardée : {cell_path}")

            if cell_count >= 50:
                raise MaErreurPersonnalisee("Trop de cellule")

    return cell_count

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



def find_pict(pict):
    # recuperer la position de l'image

    try:
        # trouver via la couleur
        position = pyautogui.locateOnScreen(pict, confidence=0.99, grayscale=True, region=(0, 0, 1920, 1080))
        x, y = position.left, position.top
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

    if x == -1 or y == -1:
        return False


    color = pyautogui.pixel(x, y)

    while True:

        click(x+(pas//2), y+(pas//2))
        declick()

        time.sleep(0.01)

        if color != pyautogui.pixel(x, y):
            return True
        else:
            change_color()






def color():
    while True:
        x, y = pyautogui.position()
        color = pyautogui.pixel(x, y)
        print(f'couleur : {color}')

def pos_souris():
    while True:
        x, y = pyautogui.position()
        print(f'position de la souris : {x}, {y}')


def supprimer_fichiers_dossier():
    for fichier in os.listdir(DIR_CELLULE):
        chemin = os.path.join(DIR_CELLULE, fichier)
        if os.path.isfile(chemin):  # Vérifie si c'est un fichier
            os.remove(chemin)       # Supprime le fichier



def process_cells(grid_step):
    """
    Parcourt toutes les cellules extraites, les localise sur la grille et les clique.
    """
    for image_file in os.listdir(DIR_CELLULE):

        cell_path = os.path.join(DIR_CELLULE, image_file)

        check_color_val = check_color(cell_path, grid_step)
        print(f"check_color_val : {str(check_color_val)}")
        if not check_color_val:
            continue

        print(f"image : {cell_path}")
        position_all_pict = find_all_pict(cell_path)

        for position in position_all_pict:

            x, y = position.left, position.top
            y = int(y + (grid_step // 2))
            x = int(x + (grid_step // 2))
            click(x, y)
            time.sleep(TIMER)

            if x == -1 or y == -1:
                break

            if keyboard.is_pressed('q'):
                break

            time.sleep(TIMER)

        declick()


def main():
    supprimer_fichiers_dossier()
    cadre = select_frame()
    grid_step = calculate_grid_step(cadre)
    print(f"Le pas de la grille est de {grid_step} pixels.")
    capture_screen(cadre)
    extract_cellule(grid_step)
    process_cells(grid_step)


if __name__ == "__main__":
    main()