import cv2 
import csv
import os

def affichage_exemple(repertory, img):
    """This function allow to show image"""
    
    # Lecture du fichier CSV
    file_csv = f"./dataset/{repertory}_data.csv"
    with open(file_csv, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            # Récupération des valeurs de la ligne 
            image,label = row
            image = image.split('/')[-1]
            
            if image == img: 
                img_path = f'./dataset/{repertory}/{label}/{image}'
          
                if (os.path.isfile(img_path)):
                    # Ouverture d'une fenêtre pour afficher l'image
                    window = cv2.imread(img_path)
                    
                    window_name = f'{img_path}, Label: {label}'
                    cv2.imshow(window_name, window)
    
                    # Attend que l'utilisateur appuie sur une touche pour fermer la fenêtre
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    
if __name__ == "__main__":
    affichage_exemple("test","3.png")
    affichage_exemple("test","134.png")
    affichage_exemple("test","1555.png")
    affichage_exemple("test","1984.png")