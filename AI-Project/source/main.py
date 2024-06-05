from model import load_model
import numpy as np
import cv2
from tensorflow import keras
import os
import matplotlib.pyplot as plt
from seaborn import heatmap
from pandas import DataFrame 


def main():
    # Importation du modele
    model = load_model()
    # Formatage de la base de données
    train_ds = keras.utils.image_dataset_from_directory(
        directory='./dataset/train/',
        labels='inferred',
        label_mode='categorical',
        batch_size=32,
        image_size=(28, 28))
    validation_ds = keras.utils.image_dataset_from_directory(
        directory='./dataset/test/',
        labels='inferred',
        label_mode='categorical',
        batch_size=32,
        image_size=(28, 28))
    # Compilation et entrainement du modele // metrics=['accuracy'] pour connaitre sa precision
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy',metrics=['accuracy'])
    model.fit(train_ds, epochs=5, validation_data=validation_ds)
    
    # Initialisation de la matrice
    predict_tab = {
        "0": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "1": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "2": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "3": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "4": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "5": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "6": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "7": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "8": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0},
        "9": {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0}
    }
    
    # Phase de test du modele
    for repertory in os.listdir("./dataset/test/"):
        path = f"./dataset/test/{repertory}"
        for img in os.listdir(path) :
            img_path = f"{path}/{img}"  
            img = cv2.imread(img_path)
            img_batch = np.expand_dims(img, axis=0)
            img_batch = np.expand_dims(img_batch, axis=-1)
            # Prediction de la valeur sur l'image
            predictions = model.predict(img_batch, verbose=0)[0]
            predict_max_position = np.argmax(predictions)
            # Incrementation de la valeur predite dans la matrice
            predict_tab[f"{repertory}"][f"{predict_max_position}"] += 1 
            #print(img_path, predictions, predict_max_position)
    #print(predict_tab)
    
    # Construction du graphe
    df = DataFrame.from_dict(predict_tab, orient='index')
    # Créer le heatmap avec seaborn
    plt.figure(figsize=(10, 8))
    heatmap(df, annot=True, cmap='Blues', fmt='d', cbar_kws={'label': 'Nombre de prédictions'})
    plt.gca().invert_yaxis()
    plt.title('Matrice de Prédictions')
    plt.xlabel('Chiffre Prédit')
    plt.ylabel('Chiffre Réel')
    # Affichage du graphe
    plt.show()
    
if __name__ == "__main__":
    main()