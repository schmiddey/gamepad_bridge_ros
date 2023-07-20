import rclpy 
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

from gamepad_bridge.gamepad_rcv import GamepadReceiver
from gamepad_bridge.joy import Joy as BridgeJoy



class JoyBridgeNode(Node):
  def __init__(self):
    super().__init__('joy_bridge_node')
    #parameters
    self.declare_parameter('host', '69.69.69.88')
    self.declare_parameter('port', 1336)
    self.declare_parameter('rate', 50.0)
    # self.declare_parameter('max_linear_vel', 2.0)
    # self.declare_parameter('max_angular_vel', 3.0)

    host = self.get_parameter('host').get_parameter_value().string_value
    port = self.get_parameter('port').get_parameter_value().integer_value
    rate = self.get_parameter('rate').get_parameter_value().double_value
    # self.max_linear_vel = self.get_parameter('max_linear_vel').get_parameter_value().double_value
    # self.max_angular_vel = self.get_parameter('max_angular_vel').get_parameter_value().double_value

    #print params
    self.get_logger().info('---------------------------------')
    self.get_logger().info('-- Parameters --')
    self.get_logger().info('host: {}'.format(host))
    self.get_logger().info('port: {}'.format(port))
    self.get_logger().info('rate: {}'.format(rate))
    # self.get_logger().info('max_linear_vel: {}'.format(self.max_linear_vel))
    # self.get_logger().info('max_angular_vel: {}'.format(self.max_angular_vel))

    self.get_logger().info('---------------------------------')


    # self.pub_vel = self.create_publisher(Twist, 'joy_vel/cmd_vel', 10)
    self.pub_joy = self.create_publisher(Joy, 'joy', 10)
    self.timer = self.create_timer(1/rate, self.timer_callback)
    self.gamepad_rcv = GamepadReceiver(host=host, port=port, callback=self.bridge_joy_callback)


  def connect(self):
    self.gamepad_rcv.connect()

  def close(self):
    self.gamepad_rcv.close()

  def bridge_joy_callback(self, joy_msg: BridgeJoy):
    # twist_msg = Twist()
    # twist_msg.linear.x = (joy_msg.trigger_r - joy_msg.trigger_l) * self.max_linear_vel
    # twist_msg.linear.y = joy_msg.stick_r_x * self.max_linear_vel
    # twist_msg.angular.z = joy_msg.stick_l_x * self.max_angular_vel * -1
    # self.pub_vel.publish(twist_msg)

    axis_6 = 0.0 #cross btn left right
    if joy_msg.btn_left:
      axis_6 = 1.0
    elif joy_msg.btn_right:
      axis_6 = -1.0

    axis_7 = 0.0 #cross btn up down
    if joy_msg.btn_up:
      axis_7 = 1.0
    elif joy_msg.btn_down:
      axis_7 = -1.0

    ros_joy = Joy()
    ros_joy.header.stamp = self.get_clock().now().to_msg()
    ros_joy.header.frame_id = 'gamepad'

    axis_5 = (1.0 - (joy_msg.trigger_r * 2))  #forward
    axis_2 = (1.0 - (joy_msg.trigger_l * 2))  #backward


    ros_joy.axes = [
                    joy_msg.stick_l_x,  #0 
                    joy_msg.stick_l_y,  #1 
                    axis_2,  #2 
                    joy_msg.stick_r_x * -1,  #3 
                    joy_msg.stick_r_y * -1,  #4 
                    axis_5,  #5
                    axis_6,  #6
                    axis_7,  #7
                    0.0,  #8
                    0.0,  #9
                    0.0   #10
                    ]


    ros_joy.buttons = [joy_msg.btn_a,
                      joy_msg.btn_b,
                      joy_msg.btn_x,
                      joy_msg.btn_y,
                      joy_msg.btn_l1,
                      joy_msg.btn_r1,
                      0, #6,
                      0, #7,
                      0, #8,
                      0, #10,
                      joy_msg.btn_stick_l,
                      joy_msg.btn_stick_r,
                      0 #13
                      ]
    self.pub_joy.publish(ros_joy)


  def timer_callback(self):
    self.gamepad_rcv.tick()




def main(args=None):
  rclpy.init(args=args)

  node = JoyBridgeNode()
  node.connect()
  #fix exception
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass

  node.close()

  node.destroy_node()
  # rclpy.shutdown()


if __name__ == '__main__':
    main()
