import os
import pybullet as p
import pybullet_data
import pybullet_industrial as pi
import numpy as np



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
    p.loadURDF("cube.urdf", [1.7, 0, 0.5],p.getQuaternionFromEuler([np.pi/2, 0, np.pi/2]), useFixedBase=True)

    start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    robot = pi.RobotBase(urdf_file1, [0, 0, 0], start_orientation)

    paint = pi.Paint(0.015,[0, 0, 1])

    extruder_properties = {'maximum distance':0.7,'opening angle':np.pi/2,'material':paint,'number of rays':6}
    extruder = pi.Extruder(
        urdf_file2, [1.9, 0, 1.2], start_orientation,extruder_properties)
    extruder.couple(robot, 'link6')



    target_position = np.array([1.9, 0])
    target_orientation = p.getQuaternionFromEuler([0, 0, 0])
    steps = 500
    base_height = 1.20
    path_x = np.linspace(target_position[0]-0.5,target_position[0]+0.5,steps)
    path_y = np.zeros(steps)-target_position[1]-0.5
    path_z = np.ones(steps)*base_height
    test_path = np.array([path_x,path_y,path_z])

    for i in range(20):
        extruder.set_tool_pose(test_path[:, 0], target_orientation)
        for _ in range(100):
                p.stepSimulation()

    while True:
        for i in range(steps):
            extruder.set_tool_pose(test_path[:, i], target_orientation)
            position, orientation = extruder.get_tool_pose()
            print(extruder.extrude())
            p.stepSimulation()

        test_path[1,:] += 0.25
        extruder.set_tool_pose(test_path[:, 0], target_orientation)
        for _ in range(20):
            p.stepSimulation()

