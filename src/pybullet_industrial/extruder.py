from typing import Dict

import numpy as np

from pybullet_industrial.material import Plastic
from pybullet_industrial.raycaster import RayCaster
from pybullet_industrial import RobotBase


class Extruder(RayCaster):

    def __init__(self, urdf_model: str, start_position: np.array, start_orientation: np.array,
                 extruder_properties: Dict, coupled_robot: RobotBase = None,
                 tcp_frame: str = None, connector_frame: str = None):
        """Special Endeffector Tool which can extrude material from its tcp.

        Args:
            urdf_model (str): A valid path to a urdf file describint the tool geometry
            start_position (np.array): the position at which the tool should be spawned
            start_orientation (np.array): the orientation at which the tool should be spawned
            extruder_properties(Dict): A dictionary containing the properties of the extrusion head.
                                       During initialization only 'material' has to be set.
                                       Default Values are:
                                       'opening angle':0,'number of rays':1,
                                       'material properties': {'particle size':0.03,
                                                               'color' : [1, 0, 0, 1]},
                                       'maximum distance':1,'material':Particle,
            coupled_robot (RobotBase, optional): A pybullet_industrial.RobotBase object if
                                                 the robot is coupled from the start.
                                                 Defaults to None.
            tcp_frame (str, optional): The name of the urdf_link
                                       describing the tool center point.
                                       Defaults to None in which case the last link is used.
            connector_frame (str, optional): The name of the urdf_link
                                             at which a robot connects.
                                             Defaults to None in which case the base link is used.

        Raises:
            ValueError: If no material is provided during initialization.
        """

        super().__init__(urdf_model, start_position, start_orientation,
                         coupled_robot, tcp_frame, connector_frame)

        self.properties['material'] = Plastic
        self.properties['material properties'] = {
            'particle size': 0.03, 'color': [1, 0, 0, 1]}

        self.change_properties(extruder_properties)

    def extrude(self, tcp_frame: str = None):
        """Extrudes material from the specified tcp_frame.

        Args:
            tcp_frame (str, optional): the name of the link from which to extrude the material.
                                       Defaults to None in which case the default tcp is used
        """
        position, orientation = self.get_tool_pose(tcp_frame)
        ray_cast_results = self.cast_rays(position, orientation)

        particle_list = []
        for ray_intersection in ray_cast_results:
            if ray_intersection[0] != -1:
                particle = self.properties['material'](ray_intersection,
                                                       self.properties['material properties'])
                particle_list.append(particle)
        return particle_list
