from abc import ABC, abstractmethod
from Detector import *
import cv2
from cv2 import cuda
import sys


# print("Python interpreter path: ", sys.executable)
# print("cv2 version", cv2.__version__)

import inspect
#for testing purposes for scripting below
import json

import datetime

# os.chdir(r"C:\CSCE482\systemDev\RescueTrek")

class Model(ABC):
    @abstractmethod
    def loadModel(self):
        pass

    #to determine the type of feed the model will use
    #using 'sensorType' to describe feed. Can be changed later if not matching
    @abstractmethod
    def defineSensorType(self, sensorType):
        pass

    @abstractmethod
    def setName(self, name):
        pass

    @abstractmethod
    def predict(self):
        pass


class imageDetector(Model):
    #
#model path is the path to the specific model used to instantiate an instance of 'imageDetector'
#modelFolder is the filepath to the folder 'pretrained_models'
    def __init__(self, modelPath, modelFolder, labelPath, threshold, name="UnnamedImageDetector"):
        self.threshold = threshold
        self.detector = Detector()
        self.setLabels(labelPath)
        self.defineSensorType("Camera")
        self.setName(name)
        self.loadModel(modelPath, modelFolder)


    def defineSensorType(self, sensorType):
        self.sensorType = sensorType

    def loadModel(self, modelPath, modelFolder):
        print(modelPath)
        self.detector.loadModel(modelPath, modelFolder)

    def setName(self, name):
        print(name)
        self.name = name

    def predict(self, feed): # feed is nos array
        # if image:
        return self.detector.createBoundingBox(feed, self.threshold) # Adjust this later

    def setLabels(self, labelPath):
        self.detector.readClasses(labelPath)


# f = open('config.json')
# models = (json.load(f))["SensorData"]["Camera"]["Models"]

# model = None
# for a in models:
#     model = a
# print(model)

# print("C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\pretrained_models\\checkpoints\\my_mobilenet_v12_model", model['Data']['ModelPath'], model['Data']['LabelPath'], model['Threshold'], model['Name'])
   
# model = None
# for a in models:
#     model = a

# from tensorflow.python.client import device_lib
# print(device_lib.list_local_devices())
    
# exampleGunModel = imageDetector("C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\pretrained_models\\checkpoints\\my_mobilenet_v12_model", model['Data']['ModelPath'], model['Data']['LabelPath'], model['Threshold'], model['Name'])

# exampleGunModel.predict([0,'C:\\CSCE482\\systemDev\\RescueTrek\\videos\\scene2.mp4', 'C:\\CSCE482\\systemDev\\RescueTrek\\videos\\woman_tommy_slow.mp4'], False)  


# listOfImages = []
# for filename in os.listdir('images'):
#     listOfImages.append(filename)

# os.chdir('C:\\CSCE482\\systemDev\\RescueTrek\\images')

# for image in listOfImages:
#     exampleGunModel.predict(image, True)
# exampleGunModel.predict('C:\\CSCE482\\systemDev\\RescueTrek\\images\\gunmanSill.jpg', True)  