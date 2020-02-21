# Jeep ROS project

This respository was developed as the capstone project of Mechantronics Engineering 2019 at Tecnologico de Monterrey, Guadalajara, Mexico.

The objective of the project was to make a 2001 Jeep Cherokee sport follow a simulated street lane autonomously. Besides, stopping when a nearby object is detected.

This project was implemented and tested on NVIDIA JetsonTX2 running Ubuntu 16.04.
## MCU Software 
The development of the MCU (NXP S32k148) sofware layer could be found on [Farid Izar] repository.

## YOLOV3 and ZED camera
We implement the well-known YOLOV3 algorithm to recognize objects as well as its distances with a ZED camera from StereoLabs.
- [YoloV3] repository
- [Zed Ros Wrapper] 

######  Author(s): Hector Cruz (Main developer), Ander Plascencia (lane_detector node), [Farid Izar] (Low-level Control) 


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
[Zed Ros Wrapper]: <https://github.com/stereolabs/zed-ros-wrapper>
[YoloV3]: <https://github.com/AlexeyAB/darknet/blob/master/src/yolo_v2_class.hpp>
[Farid Izar]: <https://github.com/FaridIz/cartec-mcu>
