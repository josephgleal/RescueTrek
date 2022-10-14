import cv2 as cv
import numpy as np
# import matplotlib.pyplot as plt
from tensorflow.keras import datasets, layers, models
# import datetime
import os
import random
import gc
#
# (training_images, training_labels), (testing_images, testing_labels) = datasets.cifar10.load_data()
# print(type(training_images))
# print(type(training_labels))
# training_images, testing_images = training_images/255, testing_images/255
# # this is to normalize the pixel values from 0 to 255 as being from 0 to 1
#
# a = 0
labels = ['Gun', 'Other']
training_images = []
testing_images = []
gun_test = os.listdir(r'C:\CSCE482\gun\test')
other_test = os.listdir(r'C:\CSCE482\other\test')
gun_train = os.listdir(r'C:\CSCE482\gun\train')
other_train = os.listdir(r'C:\CSCE482\other\train\other')
gun_train_file_path = r'C:\CSCE482\gun\train'
other_train_file_path = r'C:\CSCE482\other\train\other'
gun_test_file_path = r'C:\CSCE482\gun\test'
other_test_file_path = r'C:\CSCE482\other\test'


training_labels = []
testing_labels = []
a = 0
for img in gun_train:
    try:
        file_path = os.path.join(gun_train_file_path, img)
        a += 1
        # print(a)
        img = cv.imread(file_path)
        # cv.imshow('img', img)
        img = cv.resize(img, (64,64))

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB )
        training_images.append(img)
        # print("Show if successfully append")
        training_labels.append([0])
        if a % 1000 == 0:
            print(a/1000)
        if a == 30000:
            break
    except Exception as e:
        print(e)
#     # if a == 1000:
#     #     break
a = 0
print("Finished Guns")
for img in other_train:
    try:
        file_path = os.path.join(other_train_file_path, img)
        a += 1
        img = cv.imread(file_path)
        # cv.imshow('img', img)
        img = cv.resize(img, (64,64))

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        training_images.append(img)
        # print("Show if successfully append")
        training_labels.append([1])
        # if a % 1000 == 0:
        #     print(a/1000)
        if a == 30000:
            break
        # print(img.shape)

    except Exception as e:
        print(e)
    # if a == 1000:
    #     break
print("finished others")

a = 0
for img in other_test:
    try:
        file_path = os.path.join(other_test_file_path, img)
        a += 1
        img = cv.imread(file_path)
        # cv.imshow('img', img)
        img = cv.resize(img, (64,64))

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        testing_images.append(img)
        # print("Show if successfully append")
        testing_labels.append([1])
        # if a % 1000 == 0:
        #     print(a/1000)
        if a == 900:
            break
        # print(img.shape)

    except Exception as e:
        print(e)

print("finished other test")
a = 0
for img in gun_test:
    try:
        file_path = os.path.join(gun_test_file_path, img)
        a += 1
        img = cv.imread(file_path)
        # cv.imshow('img', img)
        img = cv.resize(img, (64,64))

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        testing_images.append(img)
        # print("Show if successfully append")
        testing_labels.append([1])
        if a % 1000 == 0:
            print(a/1000)
        if a == 900:
            break
        # print(img.shape)

    except Exception as e:
        print(e)

print("finished gun test")
# model = models.load_model('generic_classifier.model')

# print("time: " + str(datetime.datetime.now()))
# img = cv.imread('horse.jpg')
# img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
# img_scale_down = cv.resize(img, (32, 32))
# print("time: " + str(datetime.datetime.now()))

# plt.imshow(img, cmp=plt.cm.binary)
#
# prediction = model.predict(np.array([img_scale_down]) / 255)
# index = np.argmax(prediction)
# print('Prediction is ' + str(class_names[index]))
# print("time: " + str(datetime.datetime.now()))

training_set = list(zip(training_images, training_labels))
random.shuffle(training_set)
training_images, training_labels = zip(*training_set)

testing_set = list(zip(testing_images, testing_labels))
random.shuffle(testing_set)
testing_images, testing_labels = zip(*testing_set)


training_images1 = np.array(training_images)
training_labels1 = np.array(training_labels)
testing_images1 = np.array(testing_images)
testing_labels1 = np.array(testing_labels)


del training_images
print("Cleared testing unformatted training images")
del training_labels
print("Cleared testing unformatted training labels")
del testing_images
print("Cleared testing unformatted testing images")
del testing_labels
print("Cleared testing unformatted testing labels")


training_images1, testing_images1 = training_images1/255, testing_images1/255


model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)))
model.add(layers.MaxPooling2D((2,2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2,2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.Flatten())
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
print("Fitting models now\n")
model.fit(training_images1, training_labels1, epochs=10, validation_data=(testing_images1, testing_labels1))

model.save("initial_gun1.model")