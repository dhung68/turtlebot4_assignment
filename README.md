# Bài thực hành 04 - TurtleBot 4 Simulation

Xây dựng bản đồ bằng SLAM Toolbox, lưu bản đồ, localization bằng
AMCL và autonomous navigation bằng Nav2 trong môi trường depot.

## Chạy nhanh

- Chưa cài môi trường/dependency: xem mục 3.
- Chạy navigation với bản đồ đã nộp: xem mục 4–5, 9–10.
- Xây dựng lại bản đồ: xem mục 4–8.

## 1. Môi trường

- Ubuntu 22.04.
- ROS 2 Humble Desktop.
- Gazebo Fortress.
- TurtleBot 4 Simulator.
- SLAM Toolbox và Nav2.

Máy thực nghiệm: Dell Precision 7560, NVIDIA RTX A2000 Laptop 4 GB.

## 2. Cấu trúc repository

- `launch/mapping.launch.py`: gọi launch SLAM có sẵn, dùng cấu hình của bài.
- `launch/localization.launch.py`: gọi launch localization, nạp bản đồ của bài.
- `config/slam.yaml`: cấu hình SLAM đã điều chỉnh.
- `maps/map.yaml`: thông tin bản đồ.
- `maps/map.pgm`: ảnh bản đồ.
- `README.md`: hướng dẫn cài đặt và chạy.

Sử dụng simulator, mô hình robot và controller từ các package có sẵn.
Hai launch tự viết chỉ đóng vai trò gọi lại launch của TurtleBot 4
với đường dẫn cấu hình và bản đồ nằm trong repository.

Không cần tạo workspace hoặc chạy colcon build.
ROS 2 hỗ trợ chạy trực tiếp launch file bằng đường dẫn.

## 3. Cài đặt

Cài ROS 2 Humble Desktop theo tài liệu chính thức:

https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html

Sau khi đã có ROS 2 Humble và Gazebo Fortress:

```bash
sudo apt update

sudo apt install \
  ros-humble-turtlebot4-simulator \
  ros-humble-irobot-create-nodes \
  ros-humble-turtlebot4-navigation \
  ros-humble-turtlebot4-viz \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-teleop-twist-keyboard
```

Cập nhật TF2 và kiểm tra phiên bản:

```bash
sudo apt install --only-upgrade ros-humble-tf2 ros-humble-tf2-ros
apt-cache policy ros-humble-tf2 ros-humble-tf2-ros
```

Phiên thực nghiệm đã cập nhật TF2 từ 0.25.23 lên 0.25.24.
Bản 0.25.24 có sửa lỗi deadlock trong xử lý TF.

Sau khi cập nhật, dừng và mở lại các tiến trình ROS/Gazebo để chúng
sử dụng thư viện mới.

## 4. Chuẩn bị terminal

Mỗi terminal mới cần chạy:

```bash
source /opt/ros/humble/setup.bash
```

Các lệnh dùng `./launch/...` hoặc `./maps/...` phải chạy từ
thư mục gốc của repository.

Có thể clone repository vào bất kỳ thư mục nào; các launch tự tìm
bản đồ và cấu hình dựa trên vị trí của chúng.

## 5. Khởi chạy Gazebo

Terminal 1:

```bash
ros2 launch turtlebot4_ignition_bringup \
  turtlebot4_ignition.launch.py world:=depot rviz:=false
```

Trên máy có Intel và NVIDIA ở chế độ on-demand, phiên thực nghiệm dùng:

```bash
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia \
ros2 launch turtlebot4_ignition_bringup \
  turtlebot4_ignition.launch.py world:=depot rviz:=false
```

Lệnh NVIDIA chỉ áp dụng trên máy đã cài driver NVIDIA phù hợp.
Gazebo có thể tải tài nguyên world từ Gazebo Fuel trong lần chạy đầu.

## 6. Kiểm tra topic

Trong terminal khác:

```bash
ros2 topic list

ros2 topic echo /scan --once --qos-reliability best_effort
ros2 topic echo /odom --once --qos-reliability best_effort
ros2 topic info /cmd_vel
```

- `/scan`: dữ liệu khoảng cách LiDAR.
- `/odom`: odometry.
- `/cmd_vel`: lệnh vận tốc; kiểm tra khả năng nhận lệnh bằng teleop.

## 7. Mapping bằng SLAM Toolbox

Terminal 2, từ thư mục gốc repository:

```bash
ros2 launch ./launch/mapping.launch.py
```

Launch sử dụng async SLAM và thời gian mô phỏng.

Các tham số điều chỉnh trong `config/slam.yaml`:

- `minimum_travel_distance: 0.15`
- `minimum_travel_heading: 0.10`
- `map_update_interval: 2.0`
- `enable_interactive_mode: false`
- `scan_queue_size: 1`

Terminal 3 - RViz:

```bash
ros2 launch turtlebot4_viz view_robot.launch.py use_sim_time:=true
```

Có thể thêm hai biến NVIDIA trước lệnh RViz như lệnh Gazebo nếu cần.

Trong RViz:

- Fixed Frame: `map`.
- Map topic: `/map`; Durability: Transient Local.
- LaserScan topic: `/scan`; Reliability: Best Effort.
- LaserScan Decay Time: `0`.
- Bật RobotModel.

Terminal 4 - rời dock:

```bash
ros2 action send_goal /undock irobot_create_msgs/action/Undock \
  "{}" --feedback
```

Đợi kết quả SUCCEEDED, sau đó chạy teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p speed:=0.1 -p turn:=0.2
```

Các phím chính:

- `i`: tiến.
- `,`: lùi.
- `j` / `l`: quay trái / phải.
- `k`: dừng.
- Ctrl+C: thoát.

Terminal cần được focus và không bị bộ gõ tiếng Việt giữ ký tự.
Khảo sát phần lớn khu vực có thể di chuyển; theo dõi bản đồ trên RViz.

## 8. Lưu bản đồ

Khi robot đứng yên và SLAM vẫn chạy, từ thư mục gốc repository:

```bash
ros2 run nav2_map_server map_saver_cli \
  -f ./maps/map --ros-args -p use_sim_time:=true
```

Lệnh ghi `maps/map.yaml` và `maps/map.pgm`.

## 9. Localization trên bản đồ đã lưu

Dừng teleop, SLAM, RViz và Gazebo bằng Ctrl+C.
Khởi động lại Gazebo trong cùng world depot theo mục 5.

Không chạy SLAM đồng thời với AMCL.

Terminal localization, từ thư mục gốc repository:

```bash
ros2 launch ./launch/localization.launch.py
```

Mở lại RViz theo mục 7.

Đặt vị trí ban đầu bằng 2D Pose Estimate:
chọn gần vị trí thật và kéo mũi tên theo hướng đầu robot.

Với robot được khởi động lại tại vị trí xuất phát của phiên mapping,
có thể dùng ước lượng ban đầu x=0, y=0, yaw=0:

```bash
ros2 topic pub --once /initialpose \
  geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}"
```

Đây là ước lượng để AMCL hội tụ, không phải pose ground truth.
Không dùng lại giá trị này sau khi robot đã di chuyển tới khu vực khác.

Undock theo mục 7.
So sánh vị trí robot giữa Gazebo và RViz, kiểm tra laser với các cạnh
tường/vật cản trước khi gửi navigation goal.

## 10. Navigation bằng Nav2

Giữ Gazebo, localization và RViz chạy.
Thoát teleop trước khi dùng Nav2.

Terminal mới:

```bash
ros2 launch turtlebot4_navigation nav2.launch.py use_sim_time:=true
```
Trong RViz:

1. Chọn Nav2 Goal.
2. Chọn điểm đích trong vùng trống.
3. Giữ và kéo chuột để chọn hướng cuối.
4. Thả chuột để gửi goal.
5. Đợi Goal succeeded rồi gửi goal tiếp theo.


