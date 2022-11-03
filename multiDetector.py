from configparser import Interpolation
from fileinput import filename
import cv2, time, os
# os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.2/bin")
# os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.2/libnvvp")
# os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.2/include")
# os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.2/extras/CUPTI/lib64")
# os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.2/cuda/bin")
# print("Added directories before te3nsorflow")
import tensorflow as tf
import numpy as np
import sys
from threading import Thread

from tensorflow.python.keras.utils.data_utils import get_file

# import keras
# from keras import backend as K
# print(K.tensorflow_backend._get_available_gpus())

print("Loading in multiDetector Module")

np.random.seed(123)


class Detector:
    def __init__(self):
        pass

    def readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classesList = f.read().splitlines()

            # Colors list
            self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList), 3))

            print(len(self.classesList), len(self.colorList), self.classesList)

    def downloadModel(self, modelURL):
        fileName = os.path.basename(modelURL)
        print(fileName)
        self.modelName = fileName[:fileName.index('.')]
        print(self.modelName)

        self.cacheDir = "./pretrained_models"

        os.makedirs(self.cacheDir, exist_ok=True)

        get_file(fname=fileName, origin=modelURL,
                 cache_dir=self.cacheDir, cache_subdir="checkpoints",
                 extract=True)

    def loadModel(self, modelName="", cacheDir=""):

        if modelName == "":  # or cacheDir == "":
            print("Loading Model " + self.modelName)
            tf.keras.backend.clear_session()
            self.model = tf.saved_model.load(os.path.join(self.cacheDir, "checkpoints", self.modelName, "saved_model"))
            
            # self.model.
            print("Model " + self.modelName + " loaded successfully...")
        else:
            # modelName = "my_ssd_resnet50_v1_fpn_640x640_coco17_tpu-8"
            # cacheDir = ""
            self.modelName = modelName
            self.cacheDir = cacheDir
            print("Loading Model " + modelName)
            tf.keras.backend.clear_session()
            self.model = tf.saved_model.load(os.path.join(cacheDir, "checkpoints", modelName, "saved_model"))

            print("Model " + modelName + " loaded successfully...")

    def createBoundingBox(self, image, threshold=0.5):
        inputTensor = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
        inputTensor = tf.convert_to_tensor(inputTensor, dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis, ...]
        detections = None

        with tf.device('/GPU:0'):
            detections = self.model(inputTensor)

        boundingBoxes = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()

        imH, imW, imC = image.shape

        boundingBoxIndex = tf.image.non_max_suppression(boundingBoxes, classScores, max_output_size=50,
                                                        iou_threshold=threshold, score_threshold=threshold)

        print("amount of bounding boxes:", len(boundingBoxes))

        if len(boundingBoxes) != 0:
            # print("bbIndex:", boundingBoxIndex)
            maxConfidence = 0
            for i in boundingBoxIndex:
                boundingBox = tuple(boundingBoxes[i].tolist())
                classConfidence = round(100 * classScores[i])
                if classConfidence > maxConfidence:
                    maxConfidence = classConfidence # choosing the priority for the gun recognition window

                classIndex = classIndexes[i]
                # print(self.classesList)
                classLabelText = self.classesList[classIndex].upper()
                classColor = self.colorList[classIndex]

                displayText = '{}: {}%'.format(classLabelText, classConfidence)

                ymin, xmin, ymax, xmax = boundingBox

                print("BOUNDING BOX:", boundingBox)
                xmin, xmax, ymin, ymax = (int(xmin * imW), int(xmax * imW), int(ymin * imH), int(ymax * imH))

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color=classColor, thickness=1)
                cv2.putText(image, displayText, (xmin, ymin - 10), cv2.FONT_HERSHEY_PLAIN, 1, classColor, 2)

                ########### BOUNDING BOXES' CORNERS ############
                lineWidth = min(int((xmax - xmin) * 0.2), int((ymax - ymin) * 0.2))
                # top left, top and then left
                cv2.line(image, (xmin, ymin), (xmin + lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmin, ymin), (xmin, ymin + lineWidth), classColor, thickness=5)

                # top right, top and then right
                cv2.line(image, (xmax, ymin), (xmax - lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmax, ymin), (xmax, ymin + lineWidth), classColor, thickness=5)

                ##########################################################
                # bottom left, bottom and then left
                cv2.line(image, (xmin, ymax), (xmin + lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmin, ymax), (xmin, ymax - lineWidth), classColor, thickness=5)

                # bottom right, bottom and then right
                cv2.line(image, (xmax, ymax), (xmax - lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmax, ymax), (xmax, ymax - lineWidth), classColor, thickness=5)
            print("MaxConfidence is : ", maxConfidence)
            return (maxConfidence, image)

    def predictImage(self, imagePath, threshold=0.5):
        image = cv2.imread(imagePath, 1)
        image = cv2.resize(image, (960, 540))

        # boundingBoxImage = self.createBoundingBox(image, threshold)
        boundingBoxImage = self.createBoundingBox(image, threshold)
        # self.createBoundingBox(image)

        cv2.imwrite(self.modelName + ".jpg", boundingBoxImage)
        print("should be written now")
        cv2.imshow("Result", image)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()

    def predictVideo(self, captureList, threshold=0.5, GPU=True):

        captures = []
        for feed in captureList:
            captures.append(cv2.VideoCapture(feed))

        # if not cap1.isOpened():
        #     print("Error opening video...")
        #     return Refer to this error later 

        success = True
        images = []

        for capture in captures:
            captureSuccess, image = capture.read()
            images.append(image)
            success = captureSuccess

        startTime = 0

        while success:
            currentTime = time.time()

            fps = 1 / (currentTime - startTime)
            startTime = currentTime

            #Create the images with bounding boxes, priorities aren't sorted yet
            boundingBoxTuples = []
            for image in images:
                boundingBoxTuples.append(self.createBoundingBox(image, threshold))

            boundingBoxTuples.sort(key = lambda x: x[0], reverse=True)

            priorityFeed = None
            otherFeeds = None
            priorityAssigned = False
            otherAssigned = False #to make sure the priorities and other feeds are assinged in the proper order
            gpu_frame = cv2.cuda_GpuMat()
            for image in boundingBoxTuples:
                if not priorityAssigned:
                    gpu_frame.upload(image[1])
                    priorityFeed = cv2.cuda_GpuMat(1000, 680, gpu_frame.type())
                    priorityFeed = cv2.cuda.resize(gpu_frame, (1000, 680), priorityFeed, interpolation=cv2.INTER_CUBIC)
                    priorityFeed = priorityFeed.download()
                    # print("Size of prirorityFeed is ", priorityFeed.shape)
                    priorityAssigned = True
                    # cv2.imshow('', priorityFeed)
                    # cv2.waitKey(5000)
                elif not otherAssigned:
                    gpu_frame.upload(image[1])
                    otherFeeds = cv2.cuda_GpuMat(1000, 680, gpu_frame.type())
                    otherFeeds = cv2.cuda.resize(gpu_frame, (1000, 680), otherFeeds, interpolation=cv2.INTER_CUBIC)
                    otherFeeds = otherFeeds.download()
                    otherAssigned = True
                    # cv2.imshow('', otherFeeds)
                    # cv2.waitKey(5000)

                else:
                    gpu_frame.upload(image[1])
                    additionalFeed = cv2.cuda_GpuMat(900, 600, gpu_frame.type())
                    additionalFeed = cv2.cuda.resize(gpu_frame, (1000, 680), additionalFeed, interpolation=cv2.INTER_CUBIC)
                    additionalFeed = additionalFeed.download()
                    # cv2.imshow('', additionalFeed)
                    # cv2.waitKey(5000)
                    otherFeeds = np.concatenate((otherFeeds, additionalFeed) , axis=0 )
                    # print("Otherfeedsshape1234: ", str(otherFeeds.shape()))

            gpu_frame.upload(otherFeeds)
            sideFeed = cv2.cuda_GpuMat(500, 680, gpu_frame.type())
            sideFeed = cv2.cuda.resize(gpu_frame, (500, 680), sideFeed, interpolation=cv2.INTER_CUBIC)
            sideFeed = sideFeed.download()
            outputImage = np.concatenate((priorityFeed, sideFeed),axis=1)
            cv2.putText(outputImage, "FPS: " + str(int(fps)), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            cv2.imshow("Result", outputImage)

            # key = cv2.waitKey(1) & 0xFF
            # if key == ord("q"):
            #     break
            cv2.waitKey()
            images.clear()
            for capture in captures:
                captureSuccess, image = capture.read()
                images.append(image)
                success = captureSuccess

        # cv2.destoryAllWindows()