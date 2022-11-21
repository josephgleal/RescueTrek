#These values will be used for string comparison with values from the config file
#They should match values found in the config file
CAMERA = "Camera"
GUN_DETECTION = "Gun Detection"

#This value can be changed at the start of the GUI when threshold value is being read in
ITEM_DETECTOR_THRESHOLD = 0.5
ADMINISTRATOR_PASSWORD = "Password"

#may be necessary since changing the value of the above constants does not persist in other python files when run
class adjustable_values():
    def __init__(self):
        self.item_detector_threshold = 0.5
    
    def change_threshold_value(self, value):
        self.item_detector_threshold = value
    
    def return_threshold_value(self):
        return self.item_detector_threshold

list_of_values = adjustable_values()