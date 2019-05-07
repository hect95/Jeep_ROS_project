#include <ros/ros.h>|
#include <std_msgs/Float32.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <math.h>
#include <std_msgs/String.h>
#include <jeep_msgs/yolov3_msg.h>
#include <std_msgs/Float32MultiArray.h>
#include <vector>

#define stop 80


float factor_steer = 16.3636

static ros::Publisher pub;
static std_msgs::Float32MultiArray array;
	
void callback_receive_yolov3(const jeep_msgs::yolov3_msg& msg){
	
	//array.data.clear();		
	//if (msg.name == "person"){			
		//array.data.push_back()
		//array.data[0] = 0;
		array.data[1] = 100*exp(-(pow(0.25*msg.depth,2))); //y = 80*e^(-(0.1*x)^2) GAUSSIAN FUNCTION
		array.data[2] = array.data[1];
		array.data[0] = array.data[1];
		pub.publish(array);
	//}
			
}
void callback_receive_steer_angle(const jeep_msgs::yolov3_msg& msg){
	array.data[0] = msg.data*factor_steer;
	pub.publish(array);	
	}


int main ( int argc, char **argv)
{
	array.data = std::vector<float>(3,0);
	ros::init(argc, argv, "navigation_control_node");
	ros::NodeHandle nh;

	pub = nh.advertise<std_msgs::Float32MultiArray>("/I2C/nxp_communication",10);
	ros::Subscriber sub = nh.subscribe("/yolo_detections_topic",1000,callback_receive_yolov3);
	ros::Subscriber sub = nh.subscribe("/lane_detector/steer_angle",1000,callback_receive_steer_angle);


  	ros::spin();
	


}

