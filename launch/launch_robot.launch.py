import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

from launch_ros.actions import Node



def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='johnny_two' #<--- CHANGE ME

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false'}.items()
    )


    

    #Commmand substitution that will manually use the robot state publisher info as controller manager does not do this automatically like Gazebo
    #robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])
    #Dont need the command substitution, control manager "automatically" gets the robot description from the ros2 topic (/robot_descrition)
    
    controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[controller_params_file]
        #parameters=[{'robot_description': robot_description},    #don't need this, above works
        #                controller_params_file]
    )

    #may need to delay controller manager until eveything above has a chamce to start
    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])


    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    #Tell it to not start the spawners below until starting the controller manager
    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    #Tell it to not start the spawners below until starting the controller manager
    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )


    # Launch them all!
    return LaunchDescription([
        rsp,
        delayed_controller_manager
        #delayed_diff_drive_spawner,
        #delayed_joint_broad_spawner
    ])