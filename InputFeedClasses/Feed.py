from pkgutil import get_data
from threading import Thread
from abc import ABC, abstractmethod
# from Model import GunDetection


    
class Feed(ABC):
    # def __init__(self, models = None) -> None:
    #     super().__init__()
    #     #array of models
    #     self.models = models

    @abstractmethod
    def __init__(self, locations = None):
        pass
    #Initiliaze feed object. Inlcudes any setup not involved in initial __init__
    @abstractmethod
    def initialize(self):
        pass
    
    #Release feed object resource
    @abstractmethod
    def close(self):
        pass
    
    # Verify that the feed can be accessed
    @abstractmethod
    def verify_feed(self, source):
        pass

    # Retrieve data from sensor
    @abstractmethod
    def get_data(self):
        pass
    
    # Return string indicating sensor type
    @abstractmethod
    def get_sensor_type(self):
        pass
    
    # Run individual model associated with sensor (i.e. camera can run GunDetection Model)
    @abstractmethod
    def run_model(self, source):
        pass
    
    # Run all models
    def run_models(self):
        pass




