sudo cp ./src/ROS2_Nodes/sllidarROS2.service /etc/systemd/system/
#复制系统服务配置文件

sudo systemctl enable sllidarROS2
sudo systemctl start sllidarROS2
