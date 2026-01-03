wget https://s3.ap-northeast-1.wasabisys.com/download-raw/dpkg/ros2-desktop/debian/bookworm/ros-jazzy-desktop-0.3.2_20240525_arm64.deb
sudo apt install ./ros-jazzy-desktop-0.3.2_20240525_arm64.deb
pip install --break-system-packages empy==3.3.4
sudo pip install --break-system-packages vcstool colcon-common-extensions

echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

source /opt/ros/jazzy/setup.bash

sudo apt install hailo-all -y
