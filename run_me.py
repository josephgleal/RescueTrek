from Detector import *

# modelURL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
# modelURL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/centernet_resnet50_v1_fpn_512x512_kpts_coco17_tpu-8.tar.gz"
# modelURL = "http://download.tensorflow.org/models/object_detection/tf2/20210210/centernet_mobilenetv2fpn_512x512_coco17_od.tar.gz"
# modelURL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz"
# modelURL = "http://download.tensorflow.org/models/object_detection/tf2/20200711/efficientdet_d0_coco17_tpu-32.tar.gz"

# classFile = "coco.names"
classFile = "coco_v2.names"
# imagePath = "test/1.jpg"
imagePath = "test/guns2.jpg"
videoPath = 0
threshold = 0.2

def reference(a,b):
    a = 5
    b = 2


detector = Detector()
detector.readClasses(classFile)
# detector.downloadModel(modelURL)
# detector.loadModel()
# detector.loadModel("my_ssd_resnet50_v1_fpn_640x640_coco17_tpu-8", "./pre-trained_models")
# detector.loadModel("my_model", "./pre-trained_models")
detector.loadModel("my_resnet50_v2_model", "./pre-trained_models")
# detector.loadModel("my_model1017", "./pre-trained_models")
# detector.loadModel("my_mobilenet_v3_model", "./pre-trained_models")

detector.predictImage(imagePath, threshold)
# detector.predictVideo(videoPath, threshold)