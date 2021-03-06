#!/usr/bin/env python

import rospy
import numpy as np
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger

class ControlLane():
    def __init__(self):
        self.sub_lane = rospy.Subscriber('lane_center', Float64, self.cbFollowLane, queue_size = 1)
        #self.sub_max_vel = rospy.Subscriber('/control/max_vel', Float64, self.cbGetMaxVel, queue_size = 1)
        self.pub_cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        self.lastError = 0
        self.MAX_VEL = 0.06
        rospy.Service('lane_follow/turn_off', Trigger, self.svc_turn_off)

        rospy.on_shutdown(self.fnShutDown)

    #def cbGetMaxVel(self, max_vel_msg):
        #self.MAX_VEL = max_vel_msg.data
    def svc_turn_off(self, data):
        self.sub_lane.unregister()
        self.fnShutDown()
        return (True,'lane_follow node has been turned off!')

    def cbFollowLane(self, desired_center):
        center = desired_center.data

        error = center - 500

        Kp = 0.0030  # before was 0.0028
        Kd = 0.006
        angular_z = Kp * error + Kd * (error - self.lastError)
        self.lastError = error
        twist = Twist()
        twist.linear.x = min(self.MAX_VEL * ((1 - abs(error) / 500) ** 2.2), 0.2)
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = -max(angular_z, -1.3) if angular_z < 0 else -min(angular_z, 1.3)
        self.pub_cmd_vel.publish(twist)

    def fnShutDown(self):
        rospy.loginfo("Shutting down. cmd_vel will be 0")

        twist = Twist()
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        self.pub_cmd_vel.publish(twist)

    def main(self):
        rospy.spin()

if __name__ == '__main__':
    rospy.init_node('lane_follow')
    node = ControlLane()
    node.main()
