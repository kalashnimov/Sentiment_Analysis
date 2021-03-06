# -*- coding: utf-8 -*-
"""CNN_MNIST.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11z0qps9blvz4RUUXb8mIQISyhf1rRSJa
"""

import tensorflow as tf
print(tf.__version__)

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

from tensorflow.keras.datasets import mnist
(X_train, y_train), (X_test, y_test) = mnist.load_data()

import numpy as np
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Input, Conv2D, Dense, Activation, Flatten, Dropout, GlobalMaxPooling2D, GlobalAveragePooling2D, MaxPooling2D, AveragePooling2D, BatchNormalization, LeakyReLU, Concatenate
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import regularizers, optimizers
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint

X_train = X_train.astype('float32')/255
X_test = X_test.astype('float32')/255
print("X_train.shape:", X_train.shape)
print("y_train.shape", y_train.shape)

X_train = X_train.reshape(60000, 28, 28, 1)
X_test = X_test.reshape(10000,28,28,1)
print("X_train.shape:", X_train.shape)
print("X_test.shape", X_test.shape)

# number of classes
K = len(set(y_train))
print("number of classes:", K)

y_train_cat = to_categorical(y_train, 10)
y_test_cat = to_categorical(y_test, 10)

#rlr = ReduceLROnPlateau(monitor='val_accuracy', mode = 'max', factor=0.5, min_lr=1e-7, verbose = 1, patience=5)
#es = EarlyStopping(monitor='val_accuracy', mode='max', verbose = 1, patience=50)
#mc = ModelCheckpoint('cnn_best_model.h5', monitor='val_accuracy', mode='max', verbose = 1, save_best_only=True)
rlr = ReduceLROnPlateau(monitor='accuracy', mode = 'max', factor=0.5, min_lr=1e-7, verbose = 1, patience=5)
es = EarlyStopping(monitor='accuracy', mode='max', verbose = 1, patience=50)
mc = ModelCheckpoint('cnn_best_model.h5', monitor='accuracy', mode='max', verbose = 1, save_best_only=True)

def build_model(lr = 0, mt = 0, dr = 0):
    model = Sequential(name = 'cnn_mnist')

    model.add(Conv2D(filters = 32, kernel_size = (3,3), padding = 'Same', activation ='relu', input_shape = (28,28,1)))
    model.add(BatchNormalization())
    model.add(Conv2D(filters = 32, kernel_size = (3,3), padding = 'Same', activation ='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.3))

    model.add(Conv2D(filters = 64, kernel_size = (3,3), padding = 'Same', activation ='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(filters = 64, kernel_size = (3,3), padding = 'Same', activation ='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.4))

    model.add(Flatten())

    model.add(Dense(128, activation = "relu"))
    model.add(Dropout(dr))
    model.add(Dense(10, activation = "softmax"))
    opt = optimizers.SGD(lr = lr, momentum = mt)
    #opt = optimizers.RMSprop(lr = lr, decay = dc)
    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    return model

model = build_model(lr = 0.01, mt = 0.8, dr = 0.5)

model.summary()

#data augmentation
datagen = ImageDataGenerator(
                            rotation_range=15,
                            width_shift_range=0.1,
                            height_shift_range=0.1,
                            zoom_range=0.1,
                            horizontal_flip=False,
                            vertical_flip=False
                            )
datagen.fit(X_train)

# run model
model.fit_generator(datagen.flow(X_train, y_train_cat, batch_size = 64),
                                 validation_data = (X_test, y_test_cat),
                                 steps_per_epoch = X_train.shape[0] // 64, 
                                 epochs = 400, verbose = 2,
                                 callbacks = [rlr, es, mc])

def plot_model(history): 
    fig, axs = plt.subplots(1,2,figsize=(16,5)) 
    # summarize history for accuracy
    axs[0].plot(history.history['accuracy'], 'c') 
    axs[0].plot(history.history['val_accuracy'],'m') 
    axs[0].set_title('Model Accuracy')
    axs[0].set_ylabel('Accuracy') 
    axs[0].set_xlabel('Epoch')
    axs[0].legend(['train', 'validate'], loc='upper left')
    # summarize history for loss
    axs[1].plot(history.history['loss'], 'c') 
    axs[1].plot(history.history['val_loss'], 'm') 
    axs[1].set_title('Model Loss')
    axs[1].set_ylabel('Loss') 
    axs[1].set_xlabel('Epoch')
    axs[1].legend(['train', 'validate'], loc='upper right')
    plt.show()

plot_model(model.history)

saved_model = load_model('cnn_best_model.h5')
train_loss, train_acc = saved_model.evaluate(X_train,  y_train_cat, verbose=2)
test_loss, test_acc = saved_model.evaluate(X_test,  y_test_cat, verbose=2)
print('Train Accuracy:', round(train_acc, 3))
print('Test Accuracy:', round(test_acc, 3))

