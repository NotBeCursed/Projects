# AI Project

---

**How does it work ?**
This project was carried out as part of a study project. The aim of this project is to create a program to recognize handwritten numbers. This project is essentially based on **machine learning**, a method of learning Artificial Intelligence programs.  
The aim of machine learning is to train a **model** on a database so that this model, as in our case, can learn to differentiate between handwritten numbers on images. 
There are several types of **algorithm** capable of learning with this method. In our case, we're going to create a **neural network** (**CNN**). This type of algorithm is made up of several **layers**, each of which gives a probability that the input data corresponds to a result (in our case, the probability that the number on the image corresponds to each of the numbers).

**Developpement**
First, we need to prepare our database so that it can be used to train our algorithm. We have at our disposal a "dataset" directory containing two sub-directories, "test" and "train". There are also two files, "test_data.csv" and "train_data.csv", containing the labels for each of the images in the two sub-directories. This label is the value of the number represented on the associated image. 
These files will be used to reorganize our dataset directory. In the "train" and "test" directories, we'll create sub-directories (from 0 to 9) in which we'll find the corresponding images.

```python
# Scan DB directory
with os.scandir(path_db) as entries:
	for entry in entries:
		new_path = path_db+"/"+entry.name # ./dataset + the directory
		
		# If "new_path" is a directory (= train or test)
		if os.path.isdir(new_path):
			# Create the new directory 
			for i in range (10):
				os.makedirs(new_path+"/"+str(i), exist_ok=True)

			# Read csv file
			file = f'{new_path}_data.csv'
			with open(file, newline='') as csvfile:
				reader = csv.reader(csvfile, delimiter=',')
				for row in reader:
					image,labels = row
					# Move images in repositories
					if (os.path.isfile(f'./{image}')):
						image_name = image.split('/')[2]
						shutil.move(f'./{image}', f'{new_path}/{labels}/{image_name}')
						print(f"{image_name} moved", end="\r")
											
```

For this project, you'll be asked to create a function to display an image with its label. Now that we've reorganized our directories, we can develop this function. To display our image, we need to know its path. By moving them into our subdirectories, we need to use the csv files to find out in which subdirectory the image we wish to display is located. 

```python
# Reading the CSV file
file_csv = f"./dataset/{repertory}_data.csv"
with open(file_csv, newline='') as file:
	reader = csv.reader(file, delimiter=',')
	for row in reader:
		# Retrieving line values 
		image,label = row
		image = image.split('/')[-1]
		
		if image == img: 
			img_path = f'./dataset/{repertory}/{label}/{image}'
	  
			if (os.path.isfile(img_path)):
				# Open a window to display the image
				window = cv2.imread(img_path)
				
				window_name = f'{img_path}, Label: {label}'
				cv2.imshow(window_name, window)

				# Waits for the user to press a key to close the window
				cv2.waitKey(0)
				cv2.destroyAllWindows()
			   
```

We can now move on to building our algorithm. As we've already explained, we're going to create a neural network. To do this, we'll create 3 convolution layers and a "fully-conected" layer.

```python
model = Sequential()
model.add(InputLayer(input_shape=(28, 28, 3)))

model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
# model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
# model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(10, activation='softmax'))
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
```

Now that we've created our algorithm, we can train it on our database. We'll start by describing how to format our database so that our algorithm can be trained.

```python
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
```

Now that our database and algorithm are ready, we can compile and train our model.

```python
model.compile(optimizer='rmsprop', loss='categorical_crossentropy',metrics=['accuracy'])
model.fit(train_ds, epochs=5, validation_data=validation_ds)
```

Finally, to display the performance of our algorithm, we'll test it and generate a graph of the results obtained. We'll test our algorithm at recognizing the handwritten digits on the images and record the result in relation to the actual value. We can also read the accuracy of our algorithm thanks to the argument given at compile time (metrics=['accuracy']). So we can see that our model has an accuracy of over 98%.

```python
for repertory in os.listdir("./dataset/test/"):
	path = f"./dataset/test/{repertory}"
	for img in os.listdir(path) :
		img_path = f"{path}/{img}"  
		img = cv2.imread(img_path)
		img_batch = np.expand_dims(img, axis=0)
		img_batch = np.expand_dims(img_batch, axis=-1)
		predictions = model.predict(img_batch, verbose=0)[0]
		predict_max_position = np.argmax(predictions)
		predict_tab[f"{repertory}"][f"{predict_max_position}"] += 1 

df = DataFrame.from_dict(predict_tab, orient='index')
plt.figure(figsize=(10, 8))
heatmap(df, annot=True, cmap='Blues', fmt='d', cbar_kws={'label': 'Nombre de prédictions'})
plt.gca().invert_yaxis()
plt.title('Matrice de Prédictions')
plt.xlabel('Chiffre Prédit')
plt.ylabel('Chiffre Réel')
plt.show()
```

Our graph allows us to graphically validate the accuracy of our model and to see the few errors in our algorithm.