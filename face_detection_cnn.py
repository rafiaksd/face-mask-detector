# -*- coding: utf-8 -*-
"""face_detection_CNN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1f1Hcoo1qPNe5HpMt1BNWRB6nORyZoJUe
"""

# Install Kaggle API package to fetch datasets
!pip install kaggle

# Create the necessary directory for Kaggle API credentials
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# Use Kaggle API to download the face mask dataset
!kaggle datasets download -d omkargurav/face-mask-dataset

from zipfile import ZipFile
dataset = '/content/face-mask-dataset.zip'

# Extract the downloaded dataset
with ZipFile(dataset, 'r') as zip:
  zip.extractall()
  print('The dataset is extracted')

# List all files in the current directory (to check the extraction)
!ls

# Import necessary libraries
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
from google.colab.patches import cv2_imshow
from PIL import Image
from sklearn.model_selection import train_test_split

# Get list of image files with and without masks
with_mask_files = os.listdir('/content/data/with_mask')
print(with_mask_files[0:5])  # Display first 5 filenames
print(with_mask_files[-5:])  # Display last 5 filenames

without_mask_files = os.listdir('/content/data/without_mask')
print(without_mask_files[0:5])  # Display first 5 filenames
print(without_mask_files[-5:])  # Display last 5 filenames

# Print number of images in both categories
print('Number of with mask images:', len(with_mask_files))
print('Number of without mask images:', len(without_mask_files))

"""# **Creating Labels for the two classes of Images**"""

# Create labels: 1 for 'with mask' and 0 for 'without mask'
with_mask_labels = [1]*3725  # All 'with mask' images get label 1
without_mask_labels = [0]*3828  # All 'without mask' images get label 0

# Print first few labels to confirm
print(with_mask_labels[0:5])
print(without_mask_labels[0:5])

# Combine the labels for both classes
labels = with_mask_labels + without_mask_labels
print(len(labels))  # Total number of labels
print(labels[0:5])  # Check first few labels
print(labels[-5:])  # Check last few labels

# Display a 'with mask' image
img = mpimg.imread('/content/data/with_mask/with_mask_1545.jpg')
imgplot = plt.imshow(img)
plt.show()

# Display a 'without mask' image
img = mpimg.imread('/content/data/without_mask/without_mask_2931.jpg')
imgplot = plt.imshow(img)
plt.show()

# Preprocessing images: Resizing and converting to RGB
with_mask_path = '/content/data/with_mask/'
data = []
for img_file in with_mask_files:
  image = Image.open(with_mask_path + img_file)
  image = image.resize((128,128))  # Resize to 128x128
  image = image.convert('RGB')  # Convert to RGB
  image = np.array(image)  # Convert image to numpy array
  data.append(image)

without_mask_path = '/content/data/without_mask/'
for img_file in without_mask_files:
  image = Image.open(without_mask_path + img_file)
  image = image.resize((128,128))  # Resize to 128x128
  image = image.convert('RGB')  # Convert to RGB
  image = np.array(image)  # Convert image to numpy array
  data.append(image)

# Convert the image list and label list to numpy arrays
X = np.array(data)
Y = np.array(labels)

# Split the data into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=2)

# Normalize the pixel values to range [0,1]
X_train_scaled = X_train / 255
X_test_scaled = X_test / 255

import tensorflow as tf
from tensorflow import keras

num_of_classes = 2  # Binary classification: with mask or without mask

# Build the CNN model using Keras Sequential API
model = keras.Sequential()

# Add first convolutional layer with 32 filters, 3x3 kernel, ReLU activation, and input shape
model.add(keras.layers.Conv2D(32, kernel_size=(3,3), activation='relu', input_shape=(128,128,3)))
model.add(keras.layers.MaxPooling2D(pool_size=(2,2)))  # Max pooling to reduce dimensions

# Add second convolutional layer with 64 filters, 3x3 kernel, and ReLU activation
model.add(keras.layers.Conv2D(64, kernel_size=(3,3), activation='relu'))
model.add(keras.layers.MaxPooling2D(pool_size=(2,2)))  # Max pooling to reduce dimensions

# Flatten the feature map to a 1D array for input to dense layers
model.add(keras.layers.Flatten())

# Fully connected dense layers with ReLU activations and dropout to prevent overfitting
model.add(keras.layers.Dense(128, activation='relu'))
model.add(keras.layers.Dropout(0.5))

model.add(keras.layers.Dense(64, activation='relu'))
model.add(keras.layers.Dropout(0.5))

# Final dense layer with 2 output classes (with mask or without mask), using sigmoid activation
model.add(keras.layers.Dense(num_of_classes, activation='sigmoid'))

# Compile the model with the Adam optimizer, sparse categorical crossentropy loss, and accuracy metric
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['acc'])

# Train the model on the training data with validation split
history = model.fit(X_train_scaled, Y_train, validation_split=0.1, epochs=5)

# Evaluate the model on the test data
loss, accuracy = model.evaluate(X_test_scaled, Y_test)
print('Test Accuracy =', accuracy)

# Plot training and validation loss over epochs
plt.plot(history.history['loss'], label='train loss')
plt.plot(history.history['val_loss'], label='validation loss')
plt.legend()
plt.show()

# Plot training and validation accuracy over epochs
plt.plot(history.history['acc'], label='train accuracy')
plt.plot(history.history['val_acc'], label='validation accuracy')
plt.legend()
plt.show()

# Load a specific input image for prediction
input_image_path = '/content/data/with_mask/with_mask_1005.jpg'

# Read and display the input image
input_image = cv2.imread(input_image_path)
cv2_imshow(input_image)

# Preprocess the image: resize, scale, and reshape it for the model
input_image_resized = cv2.resize(input_image, (128,128))
input_image_scaled = input_image_resized / 255
input_image_reshaped = np.reshape(input_image_scaled, [1,128,128,3])

# Make a prediction with the trained model
input_prediction = model.predict(input_image_reshaped)

# Print the prediction results
print(input_prediction)

# Get the predicted class label (0 or 1)
input_pred_label = np.argmax(input_prediction)
print(input_pred_label)

# Output result based on the prediction (with or without mask)
if input_pred_label == 1:
  print('The person in the image is wearing a mask')
else:
  print('The person in the image is not wearing a mask')
