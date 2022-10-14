from fileinput import filename
import cv2, time, os, tensorflow as tf
import numpy as np

from tensorflow.python.keras.utils.data_utils import get_file

np.random.seed(123)

class Detector:
    def __init__(self):
        pass

    def readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classesList = f.read().splitlines()

            # Colors list
            self.colorList = np.random.uniform(low=0, high=255, size =(len(self.classesList), 3))

            print(len(self.classesList), len(self.colorList))

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

    def loadModel(self):
        print("Loading Model " + self.modelName)
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(os.path.join(self.cacheDir, "checkpoints", self.modelName, "saved_model"))

        print("Model " + self.modelName + " loaded successfully...")

    def createBoundingBox(self, image, threshold=0.5):
        inputTensor = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
        inputTensor = tf.convert_to_tensor(inputTensor,dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis,...]

        detections = self.model(inputTensor)

        boundingBoxes = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()

        imH, imW, imC = image.shape

        boundingBoxIndex = tf.image.non_max_suppression(boundingBoxes, classScores, max_output_size=50,
        iou_threshold=threshold, score_threshold=threshold)

        print(boundingBoxIndex)
        
        if len(boundingBoxes) != 0:
            for i in boundingBoxIndex:
                boundingBox = tuple(boundingBoxes[i].tolist())
                classConfidence = round(100*classScores[i])
                classIndex = classIndexes[i]

                classLabelText = self.classesList[classIndex].upper()
                classColor = self.colorList[classIndex]
                
                displayText = '{}: {}%'.format(classLabelText, classConfidence)

                ymin, xmin, ymax, xmax = boundingBox

                
                xmin, xmax, ymin, ymax = (int(xmin * imW), int(xmax * imW), int(ymin * imH), int(ymax * imH))

                cv2.rectangle(image,(xmin, ymin), (xmax, ymax), color=classColor, thickness=1)
                cv2.putText(image, displayText, (xmin, ymin-10), cv2.FONT_HERSHEY_PLAIN, 1, classColor, 2)

                ########### BOUNDING BOXES' CORNERS ############
                lineWidth = min(int((xmax - xmin) * 0.2), int((ymax - ymin) * 0.2))
                # top left, top and then left
                cv2.line(image, (xmin, ymin), (xmin + lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmin, ymin), (xmin, ymin + lineWidth), classColor, thickness=5)

                #top right, top and then right
                cv2.line(image, (xmax, ymin), (xmax - lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmax, ymin), (xmax, ymin + lineWidth), classColor, thickness=5)


                ##########################################################
                #bottom left, bottom and then left
                cv2.line(image, (xmin, ymax), (xmin + lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmin, ymax), (xmin, ymax - lineWidth), classColor, thickness=5)
                
                #bottom right, bottom and then right
                cv2.line(image, (xmax, ymax), (xmax - lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmax, ymax), (xmax, ymax - lineWidth), classColor, thickness=5)



            return image



    def predictImage(self, imagePath, threshold=0.5):
        image = cv2.imread(imagePath,1)
        image = cv2.resize(image, (960, 540)) 

        boundingBoxImage = self.createBoundingBox(image, threshold)
        # self.createBoundingBox(image)

        cv2.imwrite(self.modelName + ".jpg", boundingBoxImage)
        cv2.imshow("Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def predictVideo(self, videoPath, threshold=0.5):
        cap = cv2.VideoCapture(videoPath)

        if not cap.isOpened():
            print("Error opening video...")
            return

        success, image = cap.read()

        startTime = 0

        while success:
            currentTime = time.time()

            fps = 1/(currentTime - startTime)
            startTime = currentTime

            boundingBoxImage = self.createBoundingBox(image, threshold)

            cv2.putText(boundingBoxImage, "FPS: " + str(int(fps)), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
            cv2.imshow("Result", boundingBoxImage)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            success, image = cap.read()

        cv2.destoryAllWindows()