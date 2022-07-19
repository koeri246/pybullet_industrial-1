import pybullet as p
import pybullet_industrial as pi
import numpy as np


class ToolPath:

    def __init__(self, positions, orientations=None, tool_acivations=None):
        """A Base object for representing an manipulating toolpaths.

        Args:
            positions (numpy.array(3,n)): A 3 dimensional array whith each dimension containing
                                          subsequent positions.
            orientations (numpy.array(4,n), optional): A 4 dimensional array where each dimension
                                                       describes a subsequent quaternion.
                                                       Defaults to None in which case the orientation
                                                       of the world coordinate system is assumed.
            tool_acivations ([type], optional): A 1 dimensional array with boolean values describing
                                                wheter a tool is active at a given path pose.
                                                Defaults to None in which case the tool is always
                                                inactive.

        Raises:
            ValueError: If all given input arrays are different lengths.
        """
        self.positions = positions
        if orientations == None:
            self.orientations = np.zeros((4, len(self.positions[0])))
            self.orientations[3] = 1
        else:
            if len(orientations[0]) != len(positions[0]):
                raise ValueError(
                    "The position and orientation paths need to have the same length")
            self.orientations = orientations
        if tool_acivations == None:
            self.tool_activations = np.zeros(len(self.positions[0]))
        else:
            if len(tool_acivations[0]) != len(positions[0]):
                raise ValueError(
                    "The position and tool activation paths need to have the same length")
            self.tool_activations = tool_acivations

    def translate(self, vector):
        """Translates the whole path by a given vector

        Args:
            vector ([type]): A 3D vector describing the path translation
        """
        self.positions[0] += vector[0]
        self.positions[1] += vector[1]
        self.positions[2] += vector[2]

    def rotate(self, quaternion):
        """Rotates the vector by a given quaternion.
           Can be combined with pybullet.getQuaternionFromEuler() for easier usage.

        Args:
            quaternion ([type]): A 4 dimensional quaternion as a list or numpy array
        """
        path_positions = np.transpose(self.positions)
        path_orientations = np.transpose(self.orientations)

        rot_matrix = p.getMatrixFromQuaternion(quaternion)
        rot_matrix = np.array(rot_matrix).reshape(3, 3)
        for i in range(len(self)):
            path_positions[i] = rot_matrix@path_positions[i]
            path_orientations[i] = pi.quaternion_multiply(
                path_orientations[i], quaternion)

        self.positions = np.transpose(path_positions)
        self.orientations = np.transpose(path_orientations)

    def draw(self, pose=False, color=[0, 0, 1]):
        """Function which draws the path into the Debugin GUI.
           The path can either be a line representing the positions or a series of coordinate systems
           representing the whole pose

        Args:
            orientation (bool, optional): Flag which determins if only the path position is shown
                                          or the full pose. Defaults to False.
            color (list, optional): The color of the line used for position only drawing.
                                    Defaults to [0, 0, 1].
        """
        if pose == False:
            pi.draw_path(self.positions, color)
        else:
            path_positions = np.transpose(self.positions)
            path_orientations = np.transpose(self.orientations)
            for i in range(len(self)):
                pi.draw_coordinate_system(
                    path_positions[i], path_orientations[i])

    def append(self, tool_path):
        """Appends a given ToolPath object to the end of this tool path.

        Args:
            tool_path (ToolPath): Another ToolPath object.
        """
        self.positions = np.append(self.positions, tool_path.positions, axis=1)
        self.orientations = np.append(
            self.orientations, tool_path.orientations, axis=1)
        self.tool_activations = np.append(
            self.tool_activations, tool_path.tool_activations)

    def prepend(self, tool_path):
        """Prepends a given ToolPath object to the start of this tool path.

        Args:
            tool_path (ToolPath): Another ToolPath object.
        """
        self.positions = np.append(tool_path.positions, self.positions, axis=1)
        self.orientations = np.append(
            tool_path.orientations, self.orientations, axis=1)
        self.tool_activations = np.append(
            tool_path.tool_activations, self.tool_activations)

    def __len__(self):
        return len(self.positions[0])

    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index <= len(self)-1:
            i = self.current_index
            self.current_index += 1
            return self.positions[:, i], self.orientations[:, i], self.tool_activations[i]
        else:
            raise StopIteration
