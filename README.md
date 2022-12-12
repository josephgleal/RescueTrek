# RescueTrek
To run the system, ensure the appropriate environment is open and run the command:
>Python3 main.py

You should see the model load. This can take up to 20 seconds.

Once the model loads, you will see the GUI appear. It is recommended to maximize the window for the best viewing appearance.

Press the start button to initialize connections.


The GUI will appear with a prioritized window that is larger to the left and a speicifed amount of input feeds to the right that are smaller than the prioritized feeds. Any cameras that were not able to be initialized will display as a black “NULL THREAT” image.

Once the camera connections are successfully established, any camera feed where the model detects a weapon will be replicated on the left side of the GUI while its original source will have a red border on the right side. In this screenshot the middle camera feed has a weapon detected and is being replicated on the left.

The camera feed displayed on the left side priority window will be the feed with the current highest probability of there being a weapon detected. When the priority window switches feed sources, the last feed source that was prioritized will have a yellow border. 

UPDATING THRESHOLD

In the bottom right corner of the GUI, there is an update threshold button.

Pressing this button brings up a dialogue that allows the user to set a new threshold without restarting the system.

The threshold value must be between 0 and 1 and corresponds to the percent confidence that must be met for a bounding box to be drawn over an item. A lower threshold may cause the model to detect false positives more often. A high threshold will likely cause more false negatives.

The password to change the threshold is specified in the constant.py file.


