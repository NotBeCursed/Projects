from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, MaxPooling2D, InputLayer


def load_model():
    # Initialiser le modèle séquentiel
    model = Sequential()
    model.add(InputLayer(input_shape=(28, 28, 3)))
    # Ajouter la première couche de convolution
    # 32 est le nombre de filtres (kernels), (3, 3) est la taille de chaque filtre
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
    # Ajouter une couche de MaxPooling pour réduire la dimension spatiale
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # Ajouter la deuxième couche de convolution avec 64 filtres pour extraire davantage de caractéristiques
    model.add(Conv2D(64, (3, 3), activation='relu'))
    # Ajouter une autre couche de MaxPooling
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # Ajouter la troisième couche de convolution avec 128 filtres pour une complexité accrue
    model.add(Conv2D(128, (3, 3), activation='relu'))
    # Aplatir les données pour la transition vers les couches fully-connected
    model.add(Flatten())
    # Ajouter une couche fully-connected
    model.add(Dense(128, activation='relu'))
    # Ajouter la couche de sortie avec 10 unités pour les 10 classes de chiffres et une activation 'softmax' pour la classification
    model.add(Dense(10, activation='softmax'))
    # Compiler le modèle avec l'optimiseur 'adam' et la fonction de perte 'categorical_crossentropy' pour un problème de classification multiclasse
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    return model

