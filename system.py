from siteclass import Site
import json
import threading
from InputFeedClasses.IPCamera import IPCamera
import constant as const
import sys
from modelclass import *

class System:
    listOfActiveModels = []

    
    def __init__(self, configFile):
        #Read in config file
        f = open(configFile)
        data = json.load(f)
        
        self.listOfActiveModels = []
        self.listOfModelReferences = []
        self.listOfCameras = []
        self.listOfSensors = [] #For MVP this will be the same as listOfCameras
        self.imageDetectorObj = None
        
        self.SetCameras(data)
        self.GetListOfActiveModels(data)
        self.InitializeModels(data)
              
    def InitializeModels(self, configData):
        for sensorSpecificModels in self.listOfActiveModels:
            print(sensorSpecificModels)
            for modelType in sensorSpecificModels:
                print(modelType + " asdf") #Testing what is coming ou8t
                models = sensorSpecificModels[modelType]
                for model in models:
                    print("MODEL: " + str(model))
                    #Function here could be placed with argument to have more generalization on the actual
                    #initialization of the models 
                    if model['Name'] == "GunDetector":
                        data = model['Data']
                        modelPath = data['ModelPath']
                        modelFolder = data['ModelFolder']
                        labelPath = data['LabelPath']
                        threshold = int(data['Threshold'])
                        self.imageDetectorObj = imageDetector(modelPath, modelFolder, labelPath, threshold)
                    
            
    
    def SetCameras(self, configData):
        # siteId = ""
        # location = ""
        # username = ""
        # password = ""
        # ip = ""
        i = 1
        oneCamera = None
        for site in configData['ListOfSites']:
            siteId = ""
            location = ""
            username = ""
            password = ""
            ip = ""
            siteId = site['SiteID']
            location = site['BuildingLocation']
            for sensor in site['ListOfSensors']:
                sensorType = sensor['SensorType']
                if(sensorType not in self.listOfSensors):
                    # print("SensorType here " + sensor['SensorType'])
                    self.listOfSensors.append(sensor['SensorType'])
                    
                if(sensorType == const.CAMERA):
                    print(const.CAMERA)
                    ip = sensor['IP']
                    username = sensor['Username']
                    password = sensor['Password']
                    print(ip)
                    print(username)
                    print(password)
                    print(location)
                    if oneCamera != None:
                        break
                    oneCamera = IPCamera(ip, username, password, location)
                    # print("Camera " + siteId + " is initialized\n")
                    # self.listOfCameras.append(camera)
        self.listOfCameras = [oneCamera, oneCamera, oneCamera]

        
    def GetCameras(self):
        return self.listOfCameras
    
    def GetImageDetector(self):
        return self.imageDetectorObj
                
                    
    def GetListOfActiveModels(self, configData):
        sensorData = configData['SensorData']
        for site in configData['ListOfSites']:
            siteId = site['SiteID']
            print("SITEID HERE " + siteId)
            modelInfo = []
            #Grab a list of all the models that will be used
            for sensor in self.listOfSensors:
                sensorModels = sensorData[sensor]
                modelInfo.append(sensorModels)
            
            #Filter the list of models to unique entires 
            for model in modelInfo:
                if model not in self.listOfActiveModels:
                    self.listOfActiveModels.append(model)
        
    def StartUp(self):
        for i in self.listOfSites:
            thread = threading.Thread(target=i.Run, args=())
            
            thread.start()
            
            self.listOfSiteThreads.append(thread)
            
        #Startup GUI/Display class here, gets it's own thread
        #displayObj = ...
        q = queue.Queue()
        qq = queue.Queue()
        qqq = queue.Queue()
        dequeues = [q, qq, qqq]
        def fillQueues(dequeus):
            while True:
                if not q.full:
                    dequeues[0].put(cv2.imread("photos/images.jpg"))
                    dequeues[0].put(cv2.imread("photos/images2.jpg"))
        fill = threading.Thread(target=fillQueues, args=(dequeues,))
        fill.start()
        
        displayObj = GUI.GUI(dequeues)
        displayObj.start()
        displayObj.join()
            
    def Shutdown(self):
        #displayObj.Shutdown()
        for i in self.listOfSiteThreads:
            i.join()
                
                

