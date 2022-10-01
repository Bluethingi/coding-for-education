# The following file contains code written by ROB2 - B223
# 2. Semester AAU 2021.

# Imports for class
import robolink.robolink
from robodk import *
from robolink import *
from robolink.robolink import Robolink
from config import CaseConfig
from stock import Stock
from statistics import Statistics
from datetime import datetime
from timer import Timer


class Cover:
    # Global class variables
    # Distances in mm

    # Offsets for positions of covers in the storage container
    _OFFSETZ_NONE = 50.25
    _OFFSETZ_EDGE = 25
    _OFFSETZ_CURVED = 4.4
    _OFFSETX_COVER_DIST = 70
    _OFFSETY_COVER_DIST = 73
    _APPROACH = 100

    # Cover related offsets for calculations
    _OFFSETZ_COVER_FLAT_DIST = 11.7
    _OFFSETZ_COVER_EDGE_DIST = 14.7
    _OFFSETZ_COVER_CURVED_DIST = 16.7
    _TOP_COVER_INDENT_OFFSET = 5
    _BOTTOM_COVER_HEIGHT = 13

    # Colours for recolouring the bottom cover
    _COLOR_BLACK = [0.1019607843, 0.1019607843, 0.1019607843]
    _COLOR_WHITE = [1, 1, 1]
    _COLOR_BLUE = [0, 0, 0.6078431372]


    def __init__(self, color, curve_type, stock: Stock):
        """
        Constructor:
        Assigns the parameters to the given fields and corrects the position of the cover based on the parameters
        :param color: The color given in the config file
        :param curve_type: The curve type given in the config file
        :param stock: Stock Stock controlling object with type hint Stock
        """

        # Initialization of important object fields
        self.RDK = Robolink()
        self.color = color
        self.curve = curve_type
        self.stock = stock
        self.stat = Statistics()

        # Initial position of the first set of covers
        self.position = Pose(45.5, self._OFFSETY_COVER_DIST, 0, -180, 0, 0)

        # Correct the position of the cover based on colour and curvature
        self.correct_pos(self.stock)

        # Initialize bottom cover as RoboDK Item for recolouring
        bottom = self.RDK.Item('bottom', 5)

        # Based on selection of colour, recolour bottom cover
        if CaseConfig.bottom_colour() == 'black':
            bottom.Recolor(self._COLOR_BLACK)
        if CaseConfig.bottom_colour() == 'white':
            bottom.Recolor(self._COLOR_WHITE)
        if CaseConfig.bottom_colour() == 'blue':
            bottom.Recolor(self._COLOR_BLUE)

    def correct_pos(self, stock: Stock):
        """
        Corrects the position of the cover relative to the stock container, depending on the type of cover.
        Instead of giving each cover a static position
        :param stock: Stock controlling object with type hint Stock
        :return: The position of the specific cover
        """

        # Dicts with identifiers for easier calculation of position
        curve_types = {
            'black_none': 0,
            'black_edge': 3,
            'black_curved': 6,
            'white_none': 1,
            'white_edge': 4,
            'white_curved': 7,
            'blue_none': 2,
            'blue_edge': 5,
            'blue_curved': 8
        }

        case_types = {
            'black_none': 0,
            'black_edge': 1,
            'black_curved': 2,
            'white_none': 3,
            'white_edge': 4,
            'white_curved': 5,
            'blue_none': 6,
            'blue_edge': 7,
            'blue_curved': 8
        }

        case_curve = {
            'curved': 0,
            'edge': 1,
            'none': 2
        }

        # Apply the offset from the bottom of the container to the first cover in the pile
        curvature = case_curve[f'{self.curve}']
        if curvature == 1:
            self.position[2, 3] = self.position[2, 3] + self._OFFSETZ_EDGE
        if curvature == 2:
            self.position[2, 3] = self.position[2, 3] + self._OFFSETZ_NONE
        if curvature == 0:
            self.position[2, 3] = self.position[2, 3] + self._OFFSETZ_CURVED

        # Apply the x-offset based on the type and the colour of the cover
        identifier = case_types[f'{self.color}_{self.curve}']
        self.position[0, 3] = self.position[0, 3] + identifier * self._OFFSETX_COVER_DIST

        # Depending on the remaining stock and type of curve, calculate the Z-offset to compensate for the empty space
        identifier_curve = curve_types[f'{self.color}_{self.curve}']
        if identifier_curve in range(0, 3):
            self.position[2, 3] = self.position[2, 3] + stock.get(
                f'{self.color}_none') * self._OFFSETZ_COVER_FLAT_DIST
        if identifier_curve in range(3, 6):
            self.position[2, 3] = self.position[2, 3] + stock.get(
                f'{self.color}_edge') * self._OFFSETZ_COVER_EDGE_DIST
        if identifier_curve in range(6, 9):
            self.position[2, 3] = self.position[2, 3] + stock.get(
                f'{self.color}_curved') * self._OFFSETZ_COVER_CURVED_DIST

    def __str__(self):
        """
        String representation of the class
        :return: Prints the color, curve type and position of the cover
        """
        print(f'{self.color} curve_{self.curve} cover at {self.position}')

    def get_pos(self):
        """
        Debugging method
        :return:  Returns the position of the cover
        """
        return self.position

    def grab(self, robot):
        """
        Method that sends instructions to the robot in RoboDK to grab the cover from the stock container
        :param robot: Robot object representing the robot in RoboDK
        """

        # Initialize the reference frame as an Item to use in positioning
        frame = self.RDK.Item('storage', 3)

        # Set the reference frame to the newly initialized frame
        robot.setPoseFrame(frame)
        robot.setSpeed(900)

        # Copy the initial position and apply an offset to ensure the same approach each time and move the robot there
        position_copy = self.position
        if self.curve == 'none':
            position_copy[2, 3] = position_copy[2, 3] + self._APPROACH + self.stock.get_init() * self._OFFSETZ_COVER_FLAT_DIST
        elif self.curve == 'edge':
            position_copy[2, 3] = position_copy[2, 3] + self._APPROACH + self.stock.get_init() * self._OFFSETZ_COVER_EDGE_DIST
        elif self.curve == 'curved':
            position_copy[2, 3] = position_copy[2, 3] + self._APPROACH + self.stock.get_init() * self._OFFSETZ_COVER_CURVED_DIST
        robot.MoveJ(position_copy)

        # Reduce the speed and subtract all the height offsets to approach cover and move robot to the given position
        robot.setSpeed(300)
        if self.curve == 'none':
            position_copy[2, 3] = position_copy[2, 3] - self._APPROACH - self.stock.get_init() * self._OFFSETZ_COVER_FLAT_DIST
        elif self.curve == 'edge':
            position_copy[2, 3] = position_copy[2, 3] - self._APPROACH - self.stock.get_init() * self._OFFSETZ_COVER_EDGE_DIST
        elif self.curve == 'curved':
            position_copy[2, 3] = position_copy[2, 3] - self._APPROACH - self.stock.get_init() * self._OFFSETZ_COVER_CURVED_DIST
        robot.MoveL(position_copy)

        # Run RoboDk program to attach cover to tool
        self.RDK.RunProgram('Prog6')

        # Return to the approach position to ensure that the robot doesn't damage anything else and move there
        if self.curve == 'none':
            position_copy[2, 3] = position_copy[2, 3] + self._APPROACH + self.stock.get_init() * self._OFFSETZ_COVER_FLAT_DIST
        elif self.curve == 'edge':
            position_copy[2, 3] = position_copy[2, 3] + self._APPROACH + self.stock.get_init() * self._OFFSETZ_COVER_EDGE_DIST
        elif self.curve == 'curved':
            position_copy[2, 3] = position_copy[2, 3] + self._APPROACH + self.stock.get_init() * self._OFFSETZ_COVER_CURVED_DIST
        robot.MoveL(position_copy)

        # Add the used cover to statistics for later collection of data
        self.stock.sub(f'{self.color}_{self.curve}', 1)

    def give_top(self, time: Timer):
        """
        Sends instructions to RoboDK to grab a cover, place it on top of the bottom cover
        if the cover needs to be engraved, places it on the engraving plate.
        """
        # Start the timer
        start = datetime.now()

        # Carrier positions in relation to it's reference frame
        carrier_offsetx = 88.7  # (Carrier length / 2)
        carrier_offsety = 55.3  # (Carrier width / 2)
        carrier_offsetz = 42.3  # (Carrier depth)

        # Initialization of position of carrier and adding approach distance
        carrier_position_app = Pose(carrier_offsetx, carrier_offsety, carrier_offsetz, -180, 0, -90)
        carrier_position_app[2, 3] = carrier_position_app[2, 3] + self._APPROACH

        # Ensure connections to RoboDK
        self.RDK.Connect()

        # Connect to the robot and initialize pickup procedure
        robot = self.RDK.Item('fanuc', 2)
        self.grab(robot)
        robot.setSpeed(900)

        # Create object frame for usage as reference frame
        carrier_ = self.RDK.Item('carrier', 3)

        # Assign reference frame to robot and move to position
        robot.setPoseFrame(carrier_)
        robot.MoveJ(carrier_position_app)

        # Initialize new position variable with previous position
        position_withoffset = carrier_position_app

        # Check the type of cover again and subtract the approach offset and detail offset,
        # while considering that a cover is attached to the tool
        if self.curve == 'none':
            position_withoffset[2, 3] = position_withoffset[2, 3] - self._APPROACH + self._OFFSETZ_COVER_FLAT_DIST - 1.5
        if self.curve == 'edge':
            position_withoffset[2, 3] = position_withoffset[2, 3] - self._APPROACH + self._OFFSETZ_COVER_EDGE_DIST - 1.77
        if self.curve == 'curved':
            position_withoffset[2, 3] = position_withoffset[
                                            2, 3] - self._APPROACH + self._OFFSETZ_COVER_CURVED_DIST - 2.4

        # Take into account that it is now a whole phone
        position_withoffset[2, 3] = position_withoffset[
                                        2, 3] - self._TOP_COVER_INDENT_OFFSET + self._BOTTOM_COVER_HEIGHT

        # Reduce speed for safety and move to position
        robot.setSpeed(300)
        robot.MoveL(position_withoffset)

        # Run program named Prog7 to attach bottom cover to tool
        self.RDK.RunProgram('Prog7')

        # Add the creation of the phone to statistics
        self.stat.add(f'{self.color}_{self.curve}', 1)

        # If the cover needs engraving
        if CaseConfig.engrave():

            # End the timer and add it to the production time average
            time.end('average_production_time', start)

            # Add approach distance to the position and move the robot there and reset the speed
            carrier_position_app[2, 3] = carrier_position_app[2, 3] + self._APPROACH
            robot.MoveL(carrier_position_app)
            robot.setSpeed(900)

            # Create frame object for reference frame and assign it to the robot
            engrave_plate_ref = self.RDK.Item('engraving_plate_ref', 3)
            robot.setPoseFrame(engrave_plate_ref)

            # Initialize the position of the engraving plate
            engrave_plate_pos_app = Pose(145.29, 0.05, 42.6, -180, 0, 90)

            # Check for type of cover an apply an approach to the z value and move the robot there
            if self.curve == 'none':
                engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH
            if self.curve == 'edge':
                engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH + 3
            if self.curve == 'curved':
                engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH + 5
            robot.MoveJ(engrave_plate_pos_app)

            # Initialize new position variable and check for cover type and subtract the approach while taking into account carrying a phone
            engrave_plate_pos = engrave_plate_pos_app
            robot.setSpeed(300)
            if self.curve == 'none':
                engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] - self._APPROACH
            elif self.curve == 'edge':
                engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] - self._APPROACH - 2
            else:
                engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] - self._APPROACH - 2.5
            robot.MoveL(engrave_plate_pos)

            # Create tool object and detach all children of this object
            tool_suction_ = self.RDK.Item('tool_suction', 4)
            tool_suction_.DetachAll()  # Detach all objects from the robot

            # Check the type of cover and apply approach distance and move the robot there
            if self.curve == 'none':
                engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] + self._APPROACH
            elif self.curve == 'edge':
                engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] + self._APPROACH - 2
            else:
                engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] + self._APPROACH - 2.5
            robot.MoveL(engrave_plate_pos)

            # Move the robot home and attach the phone to the engraving plate by running the program "prog8"
            robot.setSpeed(900)
            robot.MoveJ(robot.JointsHome())
            self.RDK.RunProgram('Prog8')

        # If the cover doesn't need engraving
        else:

            # End the timer and add it to the production time average
            time.end('average_production_time', start)

            # Create a tool object and Detach all children from it
            tool_suction_ = self.RDK.Item('tool_suction', 4)
            tool_suction_.DetachAll()

            # Apply approach distance and move the robot there
            carrier_position_app[2, 3] = carrier_position_app[2, 3] + self._APPROACH
            robot.MoveL(carrier_position_app)

            # Reset speed and move the robot to it's home position
            robot.setSpeed(900)
            robot.MoveJ(robot.JointsHome())



    def retrieve(self):
        """
        Retrieves the cover from the engraving plate and places it on the pallette
        Thereby finishing the production of an engraved cover
        """

        # Initialize moving plate tool object and detach all children of the object.
        move_plate_tool = self.RDK.Item('engraving_plate', 4)
        move_plate_tool.DetachAll()

        # Initialize the reference frame of the engraving plate, the robot and set the robot reference frame to the
        # frame of the engraving plate and set the speed
        engrave_plate_ref = self.RDK.Item('engraving_plate_ref', 3)
        robot = self.RDK.Item('fanuc', 3)
        robot.setPoseFrame(engrave_plate_ref)
        robot.setSpeed(900)

        # Initialize the position of the engraving plate
        engrave_plate_pos_app = Pose(145.29, 0.05, 42.5, -180, 0, 90)

        # Apply approach distance to the position and move the robot there
        if self.curve == 'none':
            engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH
        elif self.curve == 'edge':
            engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH
        else:
            engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH
        robot.MoveJ(engrave_plate_pos_app)

        # Initialize new position variable with the old and subtract the approach distance along with an offset
        robot.setSpeed(300)
        engrave_plate_pos = engrave_plate_pos_app
        if self.curve == 'none':
            engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] - self._APPROACH - 0.25
        elif self.curve == 'edge':
            engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] - self._APPROACH + 1.6
        else:
            engrave_plate_pos[2, 3] = engrave_plate_pos[2, 3] - self._APPROACH + 3.0

        # Move the robot to the new position and attach the phone to it
        robot.MoveL(engrave_plate_pos)
        self.RDK.RunProgram('Prog6')
        self.RDK.RunProgram('Prog7')

        # Apply approach distance to the position and move the robot there
        if self.curve == 'none':
            engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH
        elif self.curve == 'edge':
            engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH
        else:
            engrave_plate_pos_app[2, 3] = engrave_plate_pos_app[2, 3] + self._APPROACH
        robot.MoveJ(engrave_plate_pos_app)

        # Cover position coordinates relative to the carrier reference frame reference frame
        carrier_offsetx = 88.7  # (Carrier length / 2)
        carrier_offsety = 55.3  # (Carrier width / 2)
        carrier_offsetz = 42.3  # (Carrier depth)

        # Initialize position field with position of the carrier
        carrier_position_app = Pose(carrier_offsetx, carrier_offsety, carrier_offsetz, -180, 0, -90)

        # Initialize frame object of the carrier and set the reference frame of the robot to the given frame
        carrier_ = self.RDK.Item('carrier', 3)
        robot.setPoseFrame(carrier_)
        robot.setSpeed(900)

        # Apply the approach distance to the position and move the robot there
        if self.curve == 'none':
            carrier_position_app[2, 3] = carrier_position_app[2, 3] + self._APPROACH
        if self.curve == 'edge':
            carrier_position_app[2, 3] = carrier_position_app[2, 3] + self._APPROACH
        if self.curve == 'curved':
            carrier_position_app[2, 3] = carrier_position_app[2, 3] + self._APPROACH
        robot.MoveJ(carrier_position_app)

        # Initialize new position field
        position_withoffset = carrier_position_app

        # Check the type of cover again and subtract the approach offset,
        # while considering that a cover is attached to the tool
        robot.setSpeed(300)
        if self.curve == 'none':
            position_withoffset[2, 3] = position_withoffset[2, 3] - self._APPROACH + self._OFFSETZ_COVER_FLAT_DIST - 1.85
        if self.curve == 'edge':
            position_withoffset[2, 3] = position_withoffset[2, 3] - self._APPROACH + self._OFFSETZ_COVER_EDGE_DIST - 1.27
        if self.curve == 'curved':
            position_withoffset[2, 3] = position_withoffset[
                                            2, 3] - self._APPROACH + self._OFFSETZ_COVER_CURVED_DIST - 2

        # Take into account that it is now a whole phone and move the robot to the position
        position_withoffset[2, 3] = position_withoffset[
                                        2, 3] - self._TOP_COVER_INDENT_OFFSET + self._BOTTOM_COVER_HEIGHT
        robot.MoveL(position_withoffset)

        # Initialize the tool and detach all children of the tool and move the robot home
        tool_suction_ = self.RDK.Item('tool_suction', 4)
        tool_suction_.DetachAll()
        robot.setSpeed(900)
        robot.MoveJ(robot.JointsHome())

    def new_cover_check(self):
        """
        Checks if any cover is remaining from earlier run-throughs and deletes them
        :return: Deletion of previous covers
        """

        # Dict containing all cover types
        cover_types = {
            0: 'black_none',
            1: 'black_edge',
            2: 'black_curved',
            3: 'white_none',
            4: 'white_edge',
            5: 'white_curved',
            6: 'blue_none',
            7: 'blue_edge',
            8: 'blue_curved'
        }

        # Check all types for previous covers by checking stock
        for key in cover_types:
            item = self.RDK.Item(f'cover_{cover_types[key]}_{self.stock.get(f"{cover_types[key]}") + 1}')
            if item.Valid():
                item.Delete()
