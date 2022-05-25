import os
import pybullet as p
import pybullet_data
import pybullet_industrial as pi
import numpy as np
from lemniscate import build_lemniscate_path


def draw_sphere(center,radius,steps=3,color=[0.0, 1.0, 0.0]):
    width = radius*500
    theta2              = np.linspace(-np.pi,  0, steps)
    phi2                = np.linspace( 0 ,  5 * 2*np.pi , steps)


    x_coord           = radius * np.sin(theta2) * np.cos(phi2) + center[0]
    y_coord           = radius * np.sin(theta2) * np.sin(phi2) + center[1]
    z_coord           = radius * np.cos(theta2)+ center[2]

    path = np.array([x_coord,y_coord,z_coord])
    pi.draw_path(path,color,width)


class Material:
    def __init__(self):
        pass

    def spawn_particle(self,position):
        pass


class Paint(Material):

    def __init__(self,particle_size,color):
        self.particle_size = particle_size
        self.color = color

        self.visualShapeId = p.createVisualShape(shapeType=p.GEOM_SPHERE, rgbaColor=self.color, radius=self.particle_size)

    def spawn_particle(self,ray_cast_result):
        particle_ids = []
        target_id = ray_cast_result[0]
        if target_id != -1:
            target_link_id = ray_cast_result[1]
            if target_link_id == -1:
                target_position,target_orientation = p.getBasePositionAndOrientation(target_id)
            else:
                target_link_state = p.getLinkState(target_id,target_link_id)
                target_position = np.array(target_link_state[0])
                target_orientation = np.array(target_link_state[1])
            adj_target_position = np.array(ray_cast_result[3])-target_position
            
            steps = 3
            width = self.particle_size*500
            theta2              = np.linspace(-np.pi,  0, steps)
            phi2                = np.linspace( 0 ,  5 * 2*np.pi , steps)


            x_coord           = self.particle_size * np.sin(theta2) * np.cos(phi2) + adj_target_position[0]
            y_coord           = self.particle_size * np.sin(theta2) * np.sin(phi2) + adj_target_position[1]
            z_coord           = self.particle_size * np.cos(theta2)+ adj_target_position[2]

            path = np.array([x_coord,y_coord,z_coord])
            path_steps = len(path[0])
            for i in range(1, path_steps):
                current_point = path[:, i]
                previous_point = path[:, i-1]
                particle_ids.append(p.addUserDebugLine(current_point, previous_point,
                                lineColorRGB=self.color, lineWidth=width,lifeTime=0,parentObjectUniqueId=target_id,parentLinkIndex=target_link_id))
        return particle_ids


if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    urdf_file1 = os.path.join(dirname,
                              'robot_descriptions', 'comau_NJ290_3-0_m.urdf')
    urdf_file2 = os.path.join(dirname,
                              'robot_descriptions', 'milling_head.urdf')

    physics_client = p.connect(p.GUI)
    p.setGravity(0,0,-10)
    p.setPhysicsEngineParameter(numSolverIterations=5000)

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    monastryId =p.createCollisionShape(p.GEOM_MESH,
                            fileName="samurai_monastry.obj",
                            flags=p.GEOM_FORCE_CONCAVE_TRIMESH)
    orn = p.getQuaternionFromEuler([1.5707963, 0, 0])
    p.createMultiBody(0, monastryId, baseOrientation=orn)
    p.loadURDF("cube.urdf", [1.7, 0, 0.5], useFixedBase=False)

    start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    robot = pi.RobotBase(urdf_file1, [0, 0, 0], start_orientation)

    paint = Paint(0.06,[0, 0, 1])

    extruder_properties = {'maximum distance':0.5,'opening angle':np.pi/3,'material':paint,'number of rays':40}
    extruder = pi.Extruder(
        urdf_file2, [1.9, 0, 1.2], start_orientation,extruder_properties)
    extruder.couple(robot, 'link6')



    target_position = np.array([1.9, 0])
    target_orientation = p.getQuaternionFromEuler([0, 0, 0])
    steps = 100
    base_height = 1.03
    test_path = build_lemniscate_path(target_position, steps, base_height, 0.3)
    for i in range(20):
        extruder.set_tool_pose(test_path[:, 0], target_orientation)
        for _ in range(50):
                p.stepSimulation()

    pi.draw_path(test_path)
    while True:
        for i in range(steps):
            extruder.set_tool_pose(test_path[:, i], target_orientation)
            position, orientation = extruder.get_tool_pose()
            extruder.extrude()

            for _ in range(30):
                p.stepSimulation()


