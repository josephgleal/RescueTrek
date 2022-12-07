from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QPushButton, QVBoxLayout, QWidget, QGridLayout,QLayoutItem, QLabel, QSizePolicy, \
    QLineEdit, QFormLayout
from PyQt6.QtCore import QTimer, Qt
# from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QImage, QDoubleValidator
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
import numpy as np

import constant as const

pyqtgraph.setConfigOptions(imageAxisOrder = 'row-major')


# itemDetector = imageDetector("/Users/joey/Downloads/modelsCorrectDirectoryLayout/pretrained_models/checkpoints/my_mobilenet_v12_model", "/Users/joey/Downloads/modelsCorrectDirectoryLayout/pretrained_models", "/Users/joey/Downloads/modelsCorrectDirectoryLayout/coco.names", 0.5)
itemDetector = imageDetector("/Users/joey/Downloads/modelsCorrectDirectoryLayout/pretrained_models/checkpoints/my_mobilenet_v12_model", "/Users/joey/Downloads/modelsCorrectDirectoryLayout/pretrained_models", "/Users/joey/Downloads/modelsCorrectDirectoryLayout/coco_v2.names", 0.5)


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
        self.setStyleSheet(open('css/stylesheet.css').read())
        self.confidenceLevels = []
        self.cameras = []
        self.cameraWindows = []
        self.colorList = np.random.uniform(low=0, high=255, size =(len(cameras), 3))
        self.priorityWindow = None
        self.oldPriorityWindow = None
        #Here to keep feed with most recent gun detected in the priority feed if no further guns are detected in other feeds
        self.central_widget = QLabel("Null Threat")
        self.main_layout = QGridLayout()        
        self.setWindowTitle("Null Threat")
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.showMaximized()
        self.button_start = QPushButton('start')
        self.button_start.setStyleSheet(open('css/buttons.css').read())
        self.main_layout.addWidget(self.button_start,1,0,2,1)
        self.button_start.clicked.connect(self.run)
        
        self.priority_view = QLabel(
            pixmap=QPixmap("imgs/null_threat_discord.png")
        )
        self.priority_view.setFixedHeight(900)
        self.priority_view.setFixedWidth(900)
        self.priority_view.setScaledContents(True)
        self.priority_view.setStyleSheet('margin-bottom: 150%; margin-top: 150%;')

        # self.priority_view = RawImageWidget(scaled=True) # change to Qlabel, add background to each camera, play with
        
        self.priority_label = QLabel(text="Priority Cam: ")
        # self.priority_label.setFixedHeight(100)
        self.priority_label.setFixedWidth(900)
        self.priority_label.setStyleSheet('background-color:black; color: white; margin-bottom: 150%; margin-top: 150%; magin-left: -350%')

        self.priority_num = 0
        # self.main_layout.setRowMinimumHeight( 0, 3)
        self.button_start.setFixedHeight(100)
        self.button_start.setFixedWidth(300)

        self.label = QLabel("Null Threat", self.central_widget)
        # self.main_layout.addWidget(self.label,0,0)
        self.central_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap('imgs/null_threat_grey.png')
        self.central_widget.setPixmap(pixmap)
        self.central_widget.setScaledContents(True)
       
        self.main_layout.addWidget(self.priority_view, 0, 0, 3, 1)
        self.main_layout.addWidget(self.priority_label, 0, 0, 3, 1, Qt.AlignmentFlag.AlignTop)
        self.priority_view.hide()
        self.priority_label.hide()
        

############
# have a widget over another widget to give each one it's own background
        # priority_cam = QLabel(
        #     pixmap=QPixmap("/Users/sgrac/Documents/FALL 2022/CSCE-482/Deep-Learning/scripts/test/gun.jpg")
        # )#image
        # priority_text = QLabel(text="Priority")
        # # priority_widget = QWidget()
        # priority_widget = self.central_widget#flip?
        # self.setCentralWidget(priority_widget)
        # priority_layout = QVBoxLayout(priority_widget)
        

        # priority_layout.addWidget(priority_cam, alignment=Qt.AlignmentFlag.AlignLeft)
        # priority_layout.addWidget(priority_text, alignment=Qt.AlignmentFlag.AlignLeft)
        # # priority_layout.addWidget(priority_cam, 0, 0, 3, 1)
        # # priority_layout.addWidget(priority_text, 0, 0, 3, 1)
############

        self.start = 0
        self.current = 0
        self.counter = 0
        
        self.p = False

        self.timer = QTimer()
        self.ptimer = QTimer()

        self.ptimer.timeout.connect(self.setP)
        self.ptimer.start(1500)

        # update priority / time every second

        #make these variables as self.variables, test it?        
        self.confidenceVal, self.priorityCameraWindow, self.maxConfidence, self.currPriorityCamera, self.currOldPriorityCamera = None, None, 0, 0, 0
        # self.timer.timeout.connect(self.update_priority)

        self.timer.timeout.connect(self.update_priority)
        self.timer.timeout.connect(self.update_time)
        # self.timer.timeout.connect(self.update_counter)
        self.timer.start(10)
    

        #make system provide cameras, put this in a function and remove parameter
        for camera in cameras:
            self.cameras.append(camera)
        
    #modify this to check from list of priorities
    def setP(self):
        self.p = True
    def update_priority(self):
        # if self.priority_num < (len(self.cameraWindows) - 1):
        #     self.priority_num = self.priority_num + 1
        # else:
        #     self.priority_num = 0
        # self.priority_view.setImage(self.cameraWindows[self.priority_num].frame) #= self.cameraWindows[0].return_frame()
        # print(self.counter)
        confidenceVal = None
        priorityCameraWindow = self.priorityWindow
        maxConfidence = self.maxConfidence
        cameraName = "Priority Cam: "
        currPriorityCamera = self.currPriorityCamera
        currOldPriorityCamera = self.currOldPriorityCamera
        index = 0
        if self.p == True:
        # iterating over camera windows to get one with highest priority level
            
            for cameraWindow in self.cameraWindows:
                if not confidenceVal:
                    # for i in range(len(self.cameraWindows)):
                    #     self.cameraWindows[i].update_border(False,False)
                    confidenceVal = cameraWindow.confidenceLevel
                    priorityCameraWindow = cameraWindow
                    maxConfidence = cameraWindow.confidenceLevel
                    cameraName = "Priority Cam: " + priorityCameraWindow.camera.ip
                    
                    currPriorityCamera = index
                    # priorityCameraWindow.update_border(True, False)
                elif confidenceVal < cameraWindow.confidenceLevel and currPriorityCamera != index:
                    # print(index, "camera was decreased")
                    # priorityCameraWindow.update_border(False, True)
                    # if currOldPriorityCamera != index:
                    #     self.cameraWindows[currOldPriorityCamera].update_border(False, False)
                    currOldPriorityCamera = currPriorityCamera
                    
                    confidenceVal = cameraWindow.confidenceLevel
                    priorityCameraWindow = cameraWindow
                    maxConfidence = cameraWindow.confidenceLevel
                    
                    # priorityCameraWindow.update_border(True, False)
                    currPriorityCamera = index
                    # do if statement that checks for old priority camera and changes based on that
                    # if index == 0:
                    #     print(len(self.cameraWindows)-1, "camera was increased")
                    # else:
                    #     print(index-1, "camera was increased")
                # elif cameraWindow != priorityCameraWindow: 
                #     # print(index, "camera was decreased")
                #     cameraWindow.update_border(False, False)
                # print("type of camerawindow:", type(cameraWindow))
                
                index += 1
            
            #This should be a value that's less than the threshold we set, but for now the value can be 0
            if (self.priorityWindow == None):
                self.priorityWindow = priorityCameraWindow
                self.priorityWindow.update_border(True,False)
            elif maxConfidence == 0:
                self.priorityWindow = self.priorityWindow
            elif priorityCameraWindow == self.oldPriorityWindow and priorityCameraWindow != None:
                self.oldPriorityWindow = self.priorityWindow
                self.priorityWindow = priorityCameraWindow
                self.priorityWindow.update_border(True,False)
                self.oldPriorityWindow.update_border(False,True)
            elif self.oldPriorityWindow == None and self.priorityWindow != priorityCameraWindow and self.priorityWindow != None:
                self.oldPriorityWindow = self.priorityWindow
                self.priorityWindow = priorityCameraWindow
                self.oldPriorityWindow.update_border(False,True)
                self.priorityWindow.update_border(True,False)
            elif priorityCameraWindow != self.oldPriorityWindow and priorityCameraWindow != self.priorityWindow and self.priorityWindow != None and self.oldPriorityWindow != None:
                self.oldPriorityWindow.update_border(False,False)
                self.oldPriorityWindow = self.priorityWindow
                self.priorityWindow = priorityCameraWindow
                self.oldPriorityWindow.update_border(False,True)
                self.priorityWindow.update_border(True,False)
        self.p = False
        priorityCameraWindow = self.priorityWindow
        self.confidenceVal = confidenceVal
        cameraName = "Priority Cam: " + priorityCameraWindow.camera.locations
        # self.priority_view.setImage(priorityCameraWindow.frame) #= self.cameraWindows[0].return_frame()
        frame = priorityCameraWindow.boundingBoxFrame
        image = QImage(frame, frame.shape[1], frame.shape[0], 
                    frame.strides[0], QImage.Format.Format_RGB888)

        image = image.rgbSwapped()
        # self.image_label.setPixmap(QPixmap.fromImage(image))
        
        # self.image_view.setImage(frame)
        
        # print(cameraName, type(cameraName))
        self.priority_view.setPixmap(QPixmap.fromImage(image))
        self.priority_label.setText(cameraName)
        self.priority_view.setScaledContents(True)


        return (confidenceVal, priorityCameraWindow, maxConfidence, currPriorityCamera, currOldPriorityCamera)

        # print("attempted to update priority")

    def update_time(self):
        self.current = time.time()

    # def update_counter(self):
    #     self.counter += 1

        
    def startup():
        """call system startup and get the number of feeds so the GUI can organize itself"""
        pass
    def run(self):
        self.button_start.hide()
        self.priority_view.show()
        self.priority_label.show()
        # Replace self.cameras with location of cameras from system produced by startup()
        i = 0
        for camera in self.cameras:
            cam = CameraWindow(camera)

            self.main_layout.addWidget(cam.return_frame(),i,1,1,1)
            
            self.cameraWindows.append(cam)
            i += 1
        for camera in self.cameraWindows:
            camera.startCamera()

        self.button_update_threshold = QPushButton('Update Threshold')
        self.button_update_threshold.clicked.connect(self.open_threshold_menu)
        self.button_update_threshold.setStyleSheet('background-color: black; color: white; margin-right:50%; margin-left: 250%')

        self.main_layout.addWidget(self.button_update_threshold,i, 1, 1, 1)
    
    def open_threshold_menu(self):
        # print("This will open the additional window to update threshold\n\n\n")
        try:
            self.threshold_window = ThresholdWindow()
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
    def __init__(self):
        super().__init__()
        self.password = ""
        self.threshold_value = const.ITEM_DETECTOR_THRESHOLD
        self.status_text = QLabel()
        
        self.status_text.setText("Enter Password and Threshold Values")

        password_text_input = QLineEdit()
        password_text_input.textChanged.connect(self.passwordTextChanged)
        password_text_input.setEchoMode(QLineEdit.EchoMode.Password)

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
        self.setStyleSheet(open('css/cameraWindow.css').read())
        self.deque = deque(maxlen=100)

        self.camera = camera
        # self.layout = QVBoxLayout()
        self.layout = QGridLayout()

        # self.image_view = RawImageWidget(scaled=True)
        # self.image_view = QLabel()
        self.frame = None
        self.boundingBoxFrame = None
        self.frame_updated = False
        
        
        self.image_view = QLabel(
            pixmap=QPixmap("imgs/null_threat_discord.png")
        )
        self.image_view.setScaledContents(True)
        self.image_view.setStyleSheet('margin-right:50%; margin-left: 250%;')
        # self.image_pri_border = QLabel()
        # self.image_old_pri_border = QLabel()
        # self.image_pri_border.setStyleSheet('margin-right:50%; margin-left: 250%; border: 20px solid red;')
        # self.image_old_pri_border.setStyleSheet('margin-right:50%; margin-left: 250%; border: 15px solid yellow;')
        self.is_pri = False
        self.is_old_pri = False

        # self.layout.addWidget(self.image_pri_border)
        # self.layout.addWidget(self.image_old_pri_border)
        # self.layout.addWidget(self.image_view)

        # self.image_pri_border.hide()
        # self.image_old_pri_border.hide()

        self.start = 0
        self.current = 0
        # self.video_frame = QtGui.QLabel()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image_no_deque)
        # self.timer.timeout.connect(self.update_time)
        self.timer.start(.05)

        #thread to pull in images in a loop
        self.get_frame_thread = Thread(target=self.get_frame)
        self.get_frame_thread.daemon = True
        self.get_frame_thread.start()
        # self.update_image()

    def update_border(self, is_pri = False, is_old_pri = False):

        if is_pri:
            self.image_view.setStyleSheet('margin-right:50%; margin-left: 250%; border: 10px solid rgb(139, 0, 0);')
            # self.image_old_pri_border.hide()
            # self.image_pri_border.show()
            # print("Showing priority...")
        elif is_old_pri :
            self.image_view.setStyleSheet('margin-right:50%; margin-left: 250%; border: 10px solid rgb(255, 195, 0);')
            # self.image_pri_border.hide()
            # self.image_old_pri_border.show()
            # print("Hiding priority... Showing Old Priority...")
        else:
            self.image_view.setStyleSheet('margin-right:50%; margin-left: 250%; border: 10px solid black;')
            # self.image_pri_border.hide()
            # self.image_old_pri_border.hide()
            # print("Hiding priority... Hiding priority...")
        
        self.is_pri = is_pri
        self.is_old_pri = is_old_pri

    def get_priority(self):
        return (self.is_pri, self.is_old_pri)


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
                # print(type(frame))
                # print(str(int(fps)) + " cam " + str(self.camera.ip))
                cv2.putText(frame, "FPS: " + str(int(fps)) + " cam " + str(self.camera.ip), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                # self.image_view.setImage(frame)
                # frame = 
                image = QImage(frame, frame.shape[1], frame.shape[0], 
                       frame.strides[0], QImage.Format.Format_RGB888)

                image = image.rgbSwapped()
                # self.image_label.setPixmap(QPixmap.fromImage(image))
                
                # self.image_view.setImage(frame)
                self.image_view.setPixmap(QPixmap.fromImage(image))
                self.image_view.setScaledContents(True)
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

                self.start = self.current

                
                # print("type: ", type(frame))
                # print(str(int(fps)) + " cam " + str(self.camera.ip))
                cv2.putText(frame, "FPS: " + str(int(fps)) + " cam " + str(self.camera.ip), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                
                image = QImage(frame, frame.shape[1], frame.shape[0], 
                       frame.strides[0], QImage.Format.Format_RGB888)

                image = image.rgbSwapped()

                # print("type: ", type(image), " vs ", type(frame))
                # self.image_label.setPixmap(QPixmap.fromImage(image))
                
                # self.image_view.setImage(frame)
                
                self.image_view.setPixmap(QPixmap.fromImage(image))
                self.image_view.setScaledContents(True)
                
                self.boundingBoxFrame = frame
                self.frame_updated = False
                # print("update_image_no_deque worked")
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
                # print("get_frame worked")
            except Exception as err:
                print(err)
                print("deque error probably full")
    
    def get_frame_detector(self):
        pass

    def return_frame(self):
        # return (self.image_view, self.image_pri_border, self.image_old_pri_border)
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