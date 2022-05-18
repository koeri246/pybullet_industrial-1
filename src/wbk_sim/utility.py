import pybullet as p
import numpy as np


def draw_point(point, color=[0.0, 1.0, 0.0], length=0.05, width=2.0):
    """Draws a point in the worldspace as a cross of 3 lines

    Args:
        pnt (array): 3 dimensional point
        color (list, optional): RGB color. Defaults to [0.0,1.0,0.0].
        length (float, optional): The length of the lines.  Defaults to 0.5.
        width (float, optional): The width of the lines. Defaults to 2.0.
    """

    direction = np.array([1, 0, 0])
    p.addUserDebugLine(point + length*direction, point - length*direction,
                       lineColorRGB=color, lineWidth=width, lifeTime=0)

    direction = np.array([0, 1, 0])
    p.addUserDebugLine(point + length*direction, point - length*direction,
                       lineColorRGB=color, lineWidth=width, lifeTime=0)

    direction = np.array([0, 0, 1])
    p.addUserDebugLine(point + length*direction, point - length*direction,
                       lineColorRGB=color, lineWidth=width, lifeTime=0)


def draw_path(path, color=[0.0, 1.0, 0.0], width=2.0):
    """Draws a path in the workspace

    Args:
        path (array(3,n)): Array containing the points in the path
        color (list, optional): RGB color. Defaults to [0.0,1.0,0.0].
        width (float, optional): The width of the lines. Defaults to 2.0.
    """
    path_steps = len(path[0])
    for i in range(1, path_steps):
        current_point = path[:, i]
        previous_point = path[:, i-1]
        p.addUserDebugLine(current_point, previous_point,
                           lineColorRGB=color, lineWidth=width, lifeTime=0)


def draw_coordinate_system(position, orientation, length=0.1, width=2.0, life_time=0):
    """This function draws a coordinate system at a given position

    Args:
        position ([type]): The 3D position of the coordinate system
        orientation ([type]): The quaternion representing the orientation
                              of the coordinate system
        length (float, optional): The length of the lines.  Defaults to 0.5.
        width (float, optional): The width of the lines. Defaults to 2.0.
        life_time (float, optional): How long the coordinate system remains before despawning.
                                     Defaults to 0 in wich case it remains forever.
    """

    euler_angles = p.getEulerFromQuaternion(orientation)
    roll = euler_angles[0]
    pitch = -1*euler_angles[1]
    yaw = euler_angles[2]

    x_direction = np.array([np.cos(yaw)*np.cos(pitch),
                            np.sin(yaw)*np.cos(pitch),
                            np.sin(pitch)])
    y_direction = -1*np.array([-np.cos(yaw)*np.sin(pitch)*np.sin(roll)-np.sin(yaw)*np.cos(roll),
                               -np.sin(yaw)*np.sin(pitch) *
                               np.sin(roll)+np.cos(yaw)*np.cos(roll),
                               np.cos(pitch)*np.sin(roll)])
    z_direction = np.cross(x_direction, y_direction)

    p.addUserDebugLine(position, position+length*x_direction,
                       lineColorRGB=[1, 0, 0], lineWidth=width, lifeTime=life_time)
    p.addUserDebugLine(position, position+length*y_direction,
                       lineColorRGB=[0, 1, 0], lineWidth=width, lifeTime=life_time)
    p.addUserDebugLine(position, position+length*z_direction,
                       lineColorRGB=[0, 0, 1], lineWidth=width, lifeTime=life_time)


def draw_robot_frames(robot, text_size = 1, length=0.1, width=2.0, life_time=0):
    """Visualizes the coordinate Frames of each link of a robot

    Args:
        robot ([type]): a Robot object
        text_size (int, optional): The size at which the text is rendered. Defaults to 1.
        length (float, optional): The length of the lines.  Defaults to 0.1.
        width (float, optional): The width of the lines. Defaults to 2.0.
        life_time (float, optional): How long the coordinate system remains before despawning.
                                     Defaults to 0 in wich case it remains forever.
    """
    for link_name, link_id in robot._link_name_to_index.items():
        link_state  = p.getLinkState(robot.urdf, link_id)
        position = np.array(link_state[0])
        orientation = np.array(link_state[1])
        draw_coordinate_system(position,orientation,length,width,life_time)
        p.addUserDebugText(link_name,position+length,textSize=text_size,lifeTime=life_time)
