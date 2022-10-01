from robodk import *
from svgpy import svg
from config import CaseConfig
from stock import Stock
from statistics import Statistics
from math import sqrt, pow, fabs
from timer import Timer
from datetime import datetime


class Engrave:
    _APPROACH = 100  # Approach distance in mm
    IMAGE_SIZE_NONE = svg.Point(104, 50)  # size of the image in MM not including edge
    IMAGE_SIZE_EDGE = svg.Point(100, 36)  # size of image in MM not including edge
    IMAGE_SIZE_CURVED = svg.Point(108, 56)  # size of image in MM not including edge
    stock = Stock()
    _PIXEL_SIZE = 1.2  # For calculating the arc length of the images

    def __init__(self, rdk):
        """
        Constructor
        Checks whether an .svg file exist at the given location, if not loads a default .svg file
        and collects information from the config file
        """

        # Check whether the customer has given a valid filepath, if not take the default .svg file
        if os.path.isfile(CaseConfig.file()):
            self.svg = svg.svg_load(CaseConfig.file())
        else:
            self.svg = svg.svg_load(CaseConfig.file('DEFAULT'))

        # Initialize fields of the cover, robodk and statistics
        self.curve = CaseConfig.curve_style()
        self.color = CaseConfig.colour()
        self.RDK = rdk
        self.stat = Statistics()

    @staticmethod
    def point2d_2_pose(point, tangent):
        """
        Translates a point to a point in 3D space
        :param point: Point object containing members x and y
        :param tangent: Tangent object containing method angle
        :return: Returns a 4 x 4 matrix of the point
        """
        return transl(point.x, point.y, 0) * rotz(tangent.angle())

    @staticmethod
    def curved_add_z(x):
        """
        Calculates the z value depending on the x parameter
        Based on the function of the curvature on the curved cover
        :param x: x coordinate
        :return: the corresponding z coordinate
        """
        x = fabs(x+23.3)
        y = pow(57, 2)-pow(x-57, 2)
        z = (8/57)*sqrt(y)
        return z

    def begin_flat(self, time: Timer):
        """
        Engraving for flat covers
        Instructions sent to the robot in RoboDK for engraving the flat cover depending on the file given
        """

        # Initialization of the robot, reference frame, tool and the pixel object and set the speed
        start = datetime.now()
        robot = self.RDK.Item('engraver', 2)
        robot.setSpeed(250)
        robot.setAcceleration(2000)
        item_frame = self.RDK.Item('engrave_flat', 3)
        tool_frame = self.RDK.Item('laser_tool', 4)
        pix_ref = self.RDK.Item('pixel', 5)

        # Move the phone into the environment
        self.move_to_environment()

        # Initialize the cover to engrave upon
        item = self.RDK.Item(f'cover_{self.color}_none_{self.stock.get(f"{self.color}_{self.curve}")+1}', 5)

        # Resize the svg to the engraveable surface on the cover
        self.svg.calc_polygon_fit(self.IMAGE_SIZE_NONE, self._PIXEL_SIZE)

        # Place the image centered on the cover based on the image size
        size_img = self.svg.size_poly()
        placement_var = -19+self.IMAGE_SIZE_NONE.x/2-size_img.x/2

        # For each path in the svg
        for path in self.svg:

            # Align the image with the cover
            path.polygon_move(-25.5, placement_var)

            # Recolour the pixel to black and copy it for simulating engraving
            pix_ref.Recolor([0, 0, 0, 1])
            pix_ref.Copy()

            # Get the first point on the image and switch it coordinates to get the correct rotation
            point_quantity = path.nPoints()
            point_0 = path.getPoint(0)
            point_0.switchXY()

            # Calculate a matrix for orienting the pose to the tool
            orient_frame2tool = invH(item_frame.Pose()) * robot.SolveFK(robot.JointsHome()) * tool_frame.Pose()
            orient_frame2tool[0:3, 3] = Mat([0, 0, 0])

            # Get the first target, and align it with the tool and move the robot there
            target0 = transl(-point_0.x, point_0.y, -299) * orient_frame2tool * Pose(0, 0, 0, -180, 0, 270)
            robot.MoveL(target0)

            # Set the color in RoboDK
            self.RDK.RunProgram('SetColorRGB(%.3f,%.3f,%.3f)' % (
                0, 0, 0))

            # For each point in the given path
            for point in range(point_quantity):

                # Get the point and switch the coordinates for correct rotation
                path_point = path.getPoint(point)
                path_point.switchXY()

                # Calculate the target based on the points, a height and orientation of the tool and move the engraver
                path_target = transl(-path_point.x, path_point.y, -299) * orient_frame2tool * Pose(0, 0, 0, -180, 0, 270)
                robot.MoveL(path_target)

                # create a new pixel object with the calculated pixel pose and add it to the cover
                point_pose = transl(-path_point.x + 5.2, 12, -path_point.y+67.55) * orient_frame2tool * Pose(0, 0, 0, 90, 0, 0)
                item.AddGeometry(pix_ref, point_pose)

            # Move to the end point
            robot.MoveL(path_target)

        # When done engraving move the robot home and move the phone out of the engraving environment
        # Note: the real home position of the engraver is very error prone as is therefore omitted from here
        robot.MoveJ(Pose(0, -23.3, -259, 0, 0, 90))
        self.move_from_environment()

        # Add the engraving to the statistics
        stat_str = self.color + '_' + self.curve + '_engraved'
        self.stat.add(stat_str, 1)
        time.end('average_engraving_time', start)

    def begin_edge(self, time: Timer):
        """
        Engraving for curved edges covers
        Instructions sent to the robot in RoboDK for engraving the curved edges cover depending on the file given
        """

        # Initialization of the robot, reference frame, tool and the pixel object and start the timer
        start = datetime.now()
        robot = self.RDK.Item('engraver', 2)
        robot.setSpeed(250)
        robot.setAcceleration(2000)
        item_frame = self.RDK.Item('engrave_flat', 3)
        tool_frame = self.RDK.Item('laser_tool', 4)
        pix_ref = self.RDK.Item('pixel', 5)

        # Move the phone into the environment
        self.move_to_environment()

        # Initialize the cover to engrave upon
        item = self.RDK.Item(f'cover_{self.color}_edge_{self.stock.get(f"{self.color}_{self.curve}") + 1}', 5)

        # Resize the svg to the engraveable surface on the cover
        self.svg.calc_polygon_fit(self.IMAGE_SIZE_EDGE, self._PIXEL_SIZE)

        # Place the image centered on the cover based on the image size
        size_img = self.svg.size_poly()
        placement_var = -15+self.IMAGE_SIZE_EDGE.x/2-size_img.x/2

        # For each path in the svg
        for path in self.svg:

            # Align the image with the cover
            path.polygon_move(-17, placement_var)

            # Recolour the pixel to black and copy it for simulating engraving
            pix_ref.Recolor([0, 0, 0, 1])
            pix_ref.Copy()

            # Get the first point on the image and switch it coordinates to get the correct rotation
            point_quantity = path.nPoints()
            point_0 = path.getPoint(0)
            point_0.switchXY()

            # Calculate a matrix for orienting the pose to the tool
            orient_frame2tool = invH(item_frame.Pose()) * robot.SolveFK(robot.JointsHome()) * tool_frame.Pose()
            orient_frame2tool[0:3, 3] = Mat([0, 0, 0])

            # Get the first target, and align it with the tool and move the robot there
            target0 = transl(-point_0.x, point_0.y, -296.38) * orient_frame2tool * Pose(0, 0, 0, -180, 0, 270)
            target0_app = target0
            robot.MoveL(target0_app)

            # Set the color in RoboDK
            self.RDK.RunProgram('SetColorRGB(%.3f,%.3f,%.3f)' % (
                0, 0, 0))

            # For each point in the given path
            for point in range(point_quantity):

                # Get the point and switch the coordinates for correct rotation
                path_point = path.getPoint(point)
                path_point.switchXY()

                # Calculate the target based on the points, a height and orientation of the tool and move the engraver
                path_target = transl(-path_point.x, path_point.y, -296.38) * orient_frame2tool * Pose(0, 0, 0, -180, 0, 270)
                robot.MoveL(path_target)

                # create a new pixel object with the calculated pixel pose and add it to the cover
                point_pose = transl(-path_point.x + 5.2, 14.75, -path_point.y + 67.55) * orient_frame2tool * Pose(0, 0, 0, 90, 0, 0)
                item.AddGeometry(pix_ref, point_pose)

            # Move to the end point
            robot.MoveL(path_target)

        # When done engraving move the robot home and move the phone out of the engraving environment
        # Note: the real home position of the engraver is very error prone as is therefore omitted from here
        robot.MoveJ(Pose(0, -23.3, -259, 0, 0, 90))
        self.move_from_environment()

        # Add the engraving to the statistics
        stat_str = self.color + '_' + self.curve + '_engraved'
        self.stat.add(stat_str, 1)

        # End the timer with the engraving time and add it to the average
        time.end('average_engraving_time', start)

    def begin_curved(self, time: Timer):
        """
        Engraving for curved covers
        Instructions sent to the robot in RoboDK for engraving the curved cover depending on the file given
        """

        # Initialization of the robot, reference frame, tool and the pixel object and start the timer
        start = datetime.now()
        robot = self.RDK.Item('engraver', 2)
        robot.setSpeed(250)
        robot.setAcceleration(2000)
        item_frame = self.RDK.Item('engrave_flat', 3)
        tool_frame = self.RDK.Item('laser_tool', 4)
        pix_ref = self.RDK.Item('pixel', 5)

        # Move the phone into the environment
        self.move_to_environment()

        # Initialize the cover to engrave upon
        item = self.RDK.Item(f'cover_{self.color}_curved_{self.stock.get(f"{self.color}_{self.curve}")+1}', 5)

        # Resize the svg to the engraveable surface on the cover
        self.svg.calc_polygon_fit(self.IMAGE_SIZE_CURVED, self._PIXEL_SIZE)

        # Place the image centered on the cover based on the image size
        size_img = self.svg.size_poly()
        placement_var = -21.3+self.IMAGE_SIZE_CURVED.x/2-size_img.x/2

        # For each path in the svg
        for path in self.svg:

            # Align the image with the cover
            path.polygon_move(-27.5, placement_var)

            # Recolour the pixel to black and copy it for simulating engraving
            pix_ref.Recolor([0, 0, 0, 1])
            pix_ref.Copy()

            # Get the first point on the image and switch it coordinates to get the correct rotation
            point_quantity = path.nPoints()
            point_0 = path.getPoint(0)
            point_0.switchXY()

            # Calculate a matrix for orienting the pose to the tool
            orient_frame2tool = invH(item_frame.Pose()) * robot.SolveFK(robot.JointsHome()) * tool_frame.Pose()
            orient_frame2tool[0:3, 3] = Mat([0, 0, 0])

            # Get the first target, and align it with the tool and move the robot there
            target0 = transl(-point_0.x, point_0.y, -302.1+self.curved_add_z(point_0.y)) * orient_frame2tool * Pose(0, 0, 0, -180, 0, 270)
            target0_app = target0
            robot.MoveL(target0_app)

            # Set the color in RoboDK
            self.RDK.RunProgram('SetColorRGB(%.3f,%.3f,%.3f)' % (
                0, 0, 0))

            # For each point in the given path
            for point in range(point_quantity):

                # Get the point and switch the coordinates for correct rotation
                path_point = path.getPoint(point)
                path_point.switchXY()

                # Calculate the target based on the points, a height and orientation of the tool and move the engraver
                path_target = transl(-path_point.x, path_point.y, -302.1 + self.curved_add_z(path_point.y)) * orient_frame2tool * Pose(0, 0, 0, -180, 0, 270)
                robot.MoveL(path_target)

                # create a new pixel object with the calculated pixel pose 20.67
                point_pose = transl(-path_point.x + 5.2, 8.8+self.curved_add_z(path_point.y), -path_point.y +67.55) * orient_frame2tool * Pose(0, 0, 0, 90, 0, 0)

                # create a new pixel object with the calculated pixel pose and add it to the cover
                item.AddGeometry(pix_ref, point_pose)

            # Move to the end point
            robot.MoveL(path_target)

        # When done engraving move the robot home and move the phone out of the engraving environment
        # Note: the real home position of the engraver is very error prone as is therefore omitted from here
        robot.MoveJ(Pose(0, -23.3, -259, 0, 0, 90))
        self.move_from_environment()

        # Add the engraving to the statistics
        stat_str = self.color + '_' + self.curve + '_engraved'
        self.stat.add(stat_str, 1)

        # End the timer with the engraving time and add it to the average
        time.end('average_engraving_time', start)

    def move_to_environment(self):
        """
        Moves the cover into the engraving environment with the engraving plate
        """

        # Initialize the moving_plate and its reference frame and set the speed
        robot = self.RDK.Item('moving_plate')
        plate_ref = self.RDK.Item('engraving_plate_ref', 3)
        robot.setSpeed(300)

        # Set the position of the engraving plate, set the reference frame of the plate and move it to the position
        position_engraving = Pose(318, 0, 16.3, 0, 0, 0)
        robot.setPoseFrame(plate_ref)
        robot.MoveL(position_engraving)

    def move_from_environment(self):
        """
        Moves the cover from the engraving environment with the engraving plate
        """

        # Initialize the moving_plate and its reference frame and set the speed
        robot = self.RDK.Item('moving_plate')
        plate_ref = self.RDK.Item('engraving_plate_ref', 3)
        robot.setSpeed(300)

        # Set the position of the engraving plate, set the reference frame of the plate and move it to the position
        position_engraving_out = Pose(145, 0, 16.3, 0, 0, 0)
        robot.setPoseFrame(plate_ref)
        robot.MoveL(position_engraving_out)

