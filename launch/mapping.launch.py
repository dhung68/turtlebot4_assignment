from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    repo_dir = Path(__file__).resolve().parent.parent
    navigation_dir = Path(
        get_package_share_directory("turtlebot4_navigation")
    )
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(navigation_dir / "launch" / "slam.launch.py")
        ),
        launch_arguments={
            "sync": "false",
            "use_sim_time": "true",
            "params": str(repo_dir / "config" / "slam.yaml"),
        }.items(),
    )
    return LaunchDescription([slam])
