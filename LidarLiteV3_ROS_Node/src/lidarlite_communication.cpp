#include <ros/ros.h>
#include <std_msgs/Int64.h>
#include <LidarLiteV3Lib.h>  /*Modified version of https://github.com/jetsonhacks/JHLidarLite_V2/blob/master/src/lidarlite.h */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <math.h>

/* Implementation of a LidarLite communication in ROS*/

int main ( int argc, char **argv)
{

	ros::init(argc, argv, "I2C_LidarLite_Communication_node");
	ros::NodeHandle nh;
	ros::Publisher pub = nh.advertise<std_msgs::Int64>("/I2C/LidarLite_data",10);
	ros::Rate rate(10);

    //I2C object for Lidar
    I2C_Device *Lidar = new I2C_Device(0, kLidarLiteI2CAddress);
    std::vector<I2C_Device*> I2C_BUS1;
    I2C_BUS1.push_back(Lidar);
    LidarLite *lidarLite 	= new LidarLite(Lidar);

    int hardwareVersion = lidarLite->getHardwareVersion() ;
    int softwareVersion = lidarLite->getSoftwareVersion() ;
    printf("Hardware Version: %d\n",hardwareVersion) ;
    printf("Software Version: %d\n",softwareVersion) ;

    while (ros::ok(){
        int distance = lidarLite->getDistance();
        if (distance < 0) {
            int llError ;
            llError = lidarLite->getError() ;
            ROS_INFO("Lidar-Lite error: %d\n",llError) ;
        } else {
            int previousDistance = lidarLite->getPreviousDistance();
            int velocity = lidarLite->getVelocity();
            ROS_INFO("Distance: %5d cm  | Previous Distance: %5d cm  | Velocity: % 8d \n",distance,previousDistance,velocity);
        }

	std_msgs::Int64 msg;
	msg.data = distance;
	pub.publish(msg);
	rate.sleep();
	}
	
    delete lidarLite;

}

