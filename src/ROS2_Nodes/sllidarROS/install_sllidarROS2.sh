git clone https://github.com/Slamtec/sllidar_ros2.git

source /opt/ros/jazzy/setup.bash
pip install catkin_pkg
colcon build --symlink-install

echo "source ~/Xelerator-Soccer-OpenSource/src/ROS2_Nodes/sllidarROS/install/setup.bash" >> ~/.bashrc

source ~/.bashrc