from abc import ABC, abstractmethod
from Detector import *

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

class imageDetector(Model):
    #
#model path is the path to the specific model used to instantiate an instance of 'imageDetector'
#modelFolder is the filepath to the folder 'pretrained_models'
    def __init__(self, modelPath, modelFolder, labelPath, name="UnnamedImageDetector"):
        self.defineSensorType("Camera")
        self.setName(name)
        self.loadModel(modelPath, modelFolder)
        self.setLabels(labelPath)

    def defineSensorType(self, sensorType):
        self.sensorType = sensorType

    def loadModel(self, modelPath, modelFolder):
        print(modelPath)
        self.detector = Detector()
        self.detector.loadModel(modelPath, modelFolder)

    def setName(self, name):
        print(name)
        self.name = name

    def startMonitoring(self, videoPath):
        self.detector.predictVideo(videoPath)

    def setLabels(self, labelPath):
        self.detector.readClasses(labelPath)


exampleGunModel = imageDetector("10_22_2_model", r"C:\Users\bceup\PycharmProjects\modelTryingOut\pretrained_models",
            r'C:\Users\bceup\PycharmProjects\modelTryingOut\coco_v2.names', "GUNDETECTOR")

exampleGunModel.startMonitoring(r'C:\Users\bceup\PycharmProjects\modelTryingOut\images\dog-running.mp4')           