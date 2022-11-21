from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QPushButton, QVBoxLayout, QWidget, QGridLayout,QLayoutItem, QLabel, \
    QLineEdit, QFormLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QDoubleValidator
# import pyqt
import pyqtgraph
from pyqtgraph import ImageView, RawImageWidget, ImageItem
import cv2
from threading import Thread
from collections import deque
import InputFeedClasses.IPCamera
import queue
import threading
import time
from system import System
from modelclass import *

#Temporary for testing purposes
import sys

import constant as const
pyqtgraph.setConfigOptions(imageAxisOrder = 'row-major')


itemDetector = imageDetector("C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\pretrained_models\\checkpoints\\my_mobilenet_v12_model", "C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\pretrained_models", "C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\coco_v2.names", 0.5)



class GUI():
    def __init__(self, configFile) -> None:
        #start system here
        # self.itemDetector = imageDetector("C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\pretrained_models\\checkpoints\\my_mobilenet_v12_model", "C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\pretrained_models", "C:\\Users\\bceup\\PycharmProjects\\modelTryingOut\\coco_v2.names", 0.5)
        self.system = System(configFile)
        self.cameras = self.system.GetCameras()
        self.app = QApplication([])
        self.window = MainWindow(self.cameras)
        self.itemDetectorThreshold = 0.5
        
        self.window.show()
        self.app.exit(self.app.exec())

    def run(self):
        # self.window.run()
        pass
        
        


class MainWindow(QMainWindow):
    def __init__(self,cameras):
        super().__init__()
        self.confidenceLevels = []
        self.cameras = []
        self.cameraWindows = []

        self.testWindowString = "Here to show that the main window can be accessed"
        
        self.priorityWindow = None 
        #Here to keep feed with most recent gun detected in the priority feed if no further guns are detected in other feeds
        self.central_widget = QWidget()
        self.main_layout = QGridLayout()
        self.setWindowTitle("Null Threat")
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        
        # Starting off fullscreen
        # self.showMaximized()
        self.button_start = QPushButton('start', self.central_widget)
        self.main_layout.addWidget(self.button_start,0,1)
        self.button_start.clicked.connect(self.run)
        self.priority_view = RawImageWidget(scaled=True)
        self.priority_num = 0


        
        self.main_layout.addWidget(self.priority_view, 0, 0, 3, 1)
        self.start = 0
        self.current = 0
        
        self.timer = QTimer()

        # update priority / time every second
        self.timer.timeout.connect(self.update_priority)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)


        #make system provide cameras, put this in a function and remove parameter
        for camera in cameras:
            self.cameras.append(camera)
        
        
    #modify this to check from list of priorities
    def update_priority(self):
        # if self.priority_num < (len(self.cameraWindows) - 1):
        #     self.priority_num = self.priority_num + 1
        # else:
        #     self.priority_num = 0
        # self.priority_view.setImage(self.cameraWindows[self.priority_num].frame) #= self.cameraWindows[0].return_frame()

        # iterating over camera windows to get one with highest priority level

        #We can update the fps here / maybe setting the picture here instead of inside the camera windows




        try:
            confidenceVal = None
            priorityCameraWindow = None
            for cameraWindow in self.cameraWindows:
                if not confidenceVal:
                    confidenceVal = cameraWindow.confidenceLevel
                    priorityCameraWindow = cameraWindow
                    maxConfidence = cameraWindow.confidenceLevel
                elif confidenceVal < cameraWindow.confidenceLevel:
                    confidenceVal = cameraWindow.confidenceLevel
                    priorityCameraWindow = cameraWindow
                    maxConfidence = cameraWindow.confidenceLevel
            
            #This should be a value that's less than the threshold we set, but for now the value can be 0
            if (maxConfidence == 0):
                print("This isn't updatin here")
                priorityCameraWindow = self.priorityWindow
            else:
                self.priorityWindow = priorityCameraWindow

            self.priority_view.setImage(priorityCameraWindow.frame) #= self.cameraWindows[0].return_frame()
                
            print("Updated Priorty")
        except Exception as err:
            print(err)
            print("Failed to update the priority")

    def update_time(self):
        self.current = time.time()

        
    def startup():
        """call system startup and get the number of feeds so the GUI can organize itself"""
        pass
    def run(self):
        self.button_start.hide()
        # Replace self.cameras with location of cameras from system produced by startup()
        i = 0
        for camera in self.cameras:
            cam = CameraWindow(camera)
            self.main_layout.addWidget(cam.return_frame(),i,1,1,1)
            self.cameraWindows.append(cam)
            i += 1
        for camera in self.cameraWindows:
            camera.startCamera()

        #Button to update the threshold confidence value for imageDetector Model
        self.button_update_threshold = QPushButton('Update Threshold')
        self.button_update_threshold.clicked.connect(self.open_threshold_menu)
        self.main_layout.addWidget(self.button_update_threshold,i, 1, 1, 1)


    def open_threshold_menu(self):
        print("This will open the additional window to update threshold\n\n\n")
        try:
            self.threshold_window = ThresholdWindow(self)
            self.threshold_window.show()
        except Exception as err:
            print(err)
            print("Unable to initializeWindow")
            sys.exit(0)
        



class ThresholdWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, MainWindow):
        super().__init__()
        self.reference_to_main_window = MainWindow
        self.password = ""
        self.threshold_value = const.ITEM_DETECTOR_THRESHOLD
        self.status_text = QLabel()
        self.status_text.setText("Enter Password and Threshold Values")

        password_text_input = QLineEdit()
        password_text_input.textChanged.connect(self.passwordTextChanged)

        threshold_value_input = QLineEdit()
        threshold_value_input.setValidator(QDoubleValidator(0.99,99.99,2))
        threshold_value_input.textChanged.connect(self.thresholdNumberChanged)

        button_enter = QPushButton('Enter')
        button_enter.clicked.connect(self.enteredValues)

        layout = QFormLayout()
        layout.addRow(self.status_text)
        layout.addRow("Threshold Value", threshold_value_input)
        layout.addRow("Password", password_text_input)
        layout.addRow(button_enter)

        self.setLayout(layout)
        self.setWindowTitle("Change Threshold Value")

    def passwordTextChanged(self, text):
        self.password = text
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" + self.password + "\n\n\n\n")

    def thresholdNumberChanged(self, text):
        self.threshold_value = float(text)

    
    def enteredValues(self):
        if self.password == const.ADMINISTRATOR_PASSWORD:
            if self.threshold_value >= 1 or self.threshold_value <= 0.2:
                self.status_text.setText("The value you enter must be between 0.2 and 1.")
            else:
                const.list_of_values.change_threshold_value(self.threshold_value)
                self.status_text.setText("The threshold was changed to " + str(const.list_of_values.return_threshold_value()))

        # print("Testing output")
        # print(const.list_of_values.return_threshold_value)
        # sys.exit(0)

        

"""Individual window for a camera feed"""
class CameraWindow(QWidget):
    def __init__(self,camera):
        super().__init__()

        self.deque = deque(maxlen=100)

        self.camera = camera
        self.layout = QVBoxLayout()

        self.image_view = RawImageWidget(scaled=True)
        self.frame = None
        self.frame_updated = False
        
        self.layout.addWidget(self.image_view)

        self.start = 0
        self.current = 0
        # self.video_frame = QtGui.QLabel()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image_no_deque)
        # self.timer.timeout.connect(self.update_time)
        self.timer.start(1)

        #thread to pull in images in a loop
        self.get_frame_thread = Thread(target=self.get_frame)
        self.get_frame_thread.daemon = True
        self.get_frame_thread.start()
        # self.update_image()
        


    def update_time(self):
        self.current = time.time()
    def update_image_fps(self):
        # frame = self.camera.get_data()
        if self.deque:
            try:
                # frame = self.deque[-1]
                frame = self.deque.pop()
                fps = 1 / (self.current - self.start)
                self.start = time.time()
                print(type(frame))
                print(str(int(fps)) + " cam " + str(self.camera.ip))
                cv2.putText(frame, "FPS: " + str(int(fps)) + " cam " + str(self.camera.ip), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                self.image_view.setImage(frame)
                self.frame = frame
            except:
                print("maybe empty")
        else:
            # print("deque empty?")
            pass
    
    def update_image_no_deque(self):
        # self.startCamera()
        global itemDetector

        if self.frame_updated:
            try:
                # frame = self.frame
                # frame = None
                # Creating BoundingBox here
                self.confidenceLevel, frame = itemDetector.detector.createBoundingBox(self.frame, const.list_of_values.return_threshold_value())
                # # Creating boundingBox end
                self.current = time.time()
                fps = 1 / (self.current - self.start)

                #basing the update for fps on the time taken between consecutive self.start declarations

                self.start = self.current 
                print(type(frame))
                print(str(int(fps)) + " cam " + str(self.camera.ip))
                cv2.putText(frame, "FPS: " + str(int(fps)) + " cam " + str(self.camera.ip), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                # Location where the raw image widget is updated
                self.image_view.setImage(frame)
                
                self.frame_updated = False
                print("update_image_no_deque worked")
            except Exception as err:
                print(err)
                print("error in no deque")
    

    def startCamera(self):
        self.camera.initialize()
    
    def get_frame(self):
        # self.startCamera()
        while True:
            try:
                frame = self.camera.get_data()
                # self.deque.append(frame)
                self.frame = frame
                self.frame_updated = True
                # self.deque.append(frame)
                # frame = self.deque[-1]
                # self.image_view.setImage(frame.T)
                print("get_frame worked")
            except Exception as err:
                print(err)
                print("deque error probably full")
    
    def get_frame_detector(self):
        pass

    def return_frame(self):
        return self.image_view

    def return_cv2_frame(self):
        return self.frame
    


    # get_frame(self)
    #   bool, frame = cv2.VideoCapture()
    #   self.frame = frame
    #   self.frame_updated = True

    # update_image_no_deque(self)
    #   frame = self.frame
    #   self.image_view.setImage(frame)
    #   self.frame_updated = False

    # frame = detector.predict(frame)
    # RawImageWidget(frame)