from InputFeedClasses.Feed import Feed
import cv2
from collections import deque
import constant as const
class IPCamera(Feed):
    def __init__(self, ip, username = "", password = "", location = "", models = None):
        super().__init__(models)
        self.models = models
        self.cap = None
        self.frame = None
        self.ip = ip
        self.location = location
        # self.deque = deque(maxlen = 20)
        self.priorities = {}

        #not secure 
        self.username = username
        self.password = password

        #maybe more effecient way to do this
        self.link = ""
        
    #starts the camera stream and initialized the self.cap variable
    def initialize(self):
        try:
            cam_string = "rtsp://"+self.username+":"+self.password+"@"+self.ip+"/1"
            self.link = cam_string
            if self.ip == "0" or self.ip == "1":
                self.cap = cv2.VideoCapture(int(self.ip)) #cam_string goes here
            else:
                self.cap = cv2.VideoCapture(cam_string)
            if self.models != None:
                self.priorities = {model: {0:0} for model in self.models}
        except Exception as Argument:
            print("error with camera with ip", self.ip, "\n", "Error:", Argument)
    
    # attempts to connect to camera feed. Returns True if succesful
    def verify_feed(self, source):
        ret, cap = cv2.VideoCapture(source)  
        if not cap.isOpened():
            return False
        else:
            cap.release()
        return True

    #Attempt to Re-establish connection with the feed
    def reconnect(self, source):
        cap = cv2.VideoCapture(source)  
        if not cap.isOpened():
            return False
        else:
            self.cap = cap
        return True

    #Releases camera capture
    def close(self):
        self.cap.release()

    #Retrieves an individual frame
    def get_data(self):
        """Retrieves an individual frame"""
        try:
            ret, frame = self.cap.read()
            # frame = cv2.resize(frame, (400, 400))
            return frame
        except AttributeError as err:
            print(err)
            print("did you initilize the camera?")
    
    # gets new frame from camera and sets it as attribute
    def update_frame(self):
        frame = self.get_data()
        self.frame = frame

    # Runs model to detect threat
    # Might need to be in the model class
    def run_model(self, source):
        pass
        # self.model.assess(self.frame)
        # self.model.assess(get_data())

    #primative solution to run all models
    def run_models(self):
        for model in self.models:
            self.run_model(model)
    
    def list_priorities(self):
        for model in self.priorities:
            # print(model.name)
            print(self.priorities.get(model))
        
    #Returns sensor type
    def get_sensor_type(self):
        return const.CAMERA
    def show(self):
        while(True):
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            # resizing for faster detection
            frame = cv2.resize(frame, (400, 400))
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break