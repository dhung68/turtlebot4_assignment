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
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(navigation_dir / "launch" / "localization.launch.py")
        ),
        launch_arguments={
            "map": str(repo_dir / "maps" / "map.yaml"),
            "use_sim_time": "true",
        }.items(),
    )
    return LaunchDescription([localization])
