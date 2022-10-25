from abc import ABC, abstractmethod
from Detector import *

#for testing purposes for scripting below
import json

import datetime

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
    def predidct(self):
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

    def predict(self, feed,image=True):
        if image:
            self.detector.predictImage(feed, self.threshold)
        else:
            self.detector.predictVideo(feed, self.threshold)

    def setLabels(self, labelPath):
        self.detector.readClasses(labelPath)


# f = open('config.json')
# models = (json.load(f))["SensorData"]["Camera"]["Models"]
# modelList = []
# for model in models:
#     modelList.append(imageDetector(model['Data']['ModelName'], model['Data']['ModelPath'], model['Data']['LabelPath'], model['Data']["Feed"], model['Name']))

# exampleGunModel = imageDetector("10_22_2_model", r"C:\Users\bceup\PycharmProjects\modelTryingOut\pretrained_models",
#             r'C:\Users\bceup\PycharmProjects\modelTryingOut\coco_v2.names', "GUNDETECTOR")

# exampleGunModel.startMonitoring(r'C:\Users\bceup\PycharmProjects\modelTryingOut\images\dog-running.mp4')     
# model = None
# for a in models:
#     model = a
    
# exampleGunModel = imageDetector(model['Data']['ModelName'], model['Data']['ModelPath'], model['Data']['LabelPath'], model['Data']['Threshold'], model['Name'])

# for model in modelList:
#     model.startMonitoring()      


# before = datetime.datetime.now()
# model.predict()


# after = datetime.datetime.now()