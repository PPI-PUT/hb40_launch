# Copyright 2024 Maciej Krupka
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, FindExecutable, Command, PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.descriptions import ParameterValue
import xacro
from os.path import join


def launch_setup(context, *args, **kwargs):
    robot = LaunchConfiguration("robot_model").perform(context)
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare("hb40_commons"),
                    "models",
                    "urdf",
                    f"{robot}.urdf",
                ]
            ),
        ]
    )
    robot_description = {"robot_description": ParameterValue(
        robot_description_content, value_type=str)}
    robot_state_publisher_node = Node(
        name=f"{robot}",
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
        remappings=[
            ("joint_states", LaunchConfiguration('input_states')),
        ],
        condition=IfCondition(LaunchConfiguration("gui")),
    )
    # Initialize Arguments
    gui = LaunchConfiguration("gui")
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("hb40_launch"), "rviz", "default.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )

    joint_state_publisher_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        condition=IfCondition(gui),
    )
    return [
        robot_state_publisher_node,
        rviz_node,
        joint_state_publisher_node,
    ]


def generate_launch_description():
    declared_arguments = []

    def add_launch_arg(name: str, default_value: str = None):
        declared_arguments.append(
            DeclareLaunchArgument(name, default_value=default_value)
        )

    add_launch_arg('robot_model', 'intention')
    add_launch_arg('gui', 'False')
    add_launch_arg('input_states', '/hb40/joint_states')
    return LaunchDescription([
        *declared_arguments,
        OpaqueFunction(function=launch_setup)
    ])
