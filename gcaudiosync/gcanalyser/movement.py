import numpy as np
import copy
import math

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

from gcaudiosync.gcanalyser.arcinformation import ArcInformation
from gcaudiosync.gcanalyser.linearaxes import LinearAxes
from gcaudiosync.gcanalyser.rotationaxes import RotationAxes

class Movement:
    """
    A class to represent a movement in CNC machining.

    Attributes:
    -----------
    line_index : int
        The line index of the G-code corresponding to this movement.
    movement_type : int
        The type of movement (e.g., linear, circular).
    start_position_linear_axes : LinearAxes
        The start position for linear axes.
    end_position_linear_axes : LinearAxes
        The end position for linear axes.
    start_position_rotation_axes : RotationAxes
        The start position for rotation axes.
    end_position_rotation_axes : RotationAxes
        The end position for rotation axes.
    arc_information : ArcInformation
        Information about the arc, if applicable.
    feed_rate : float
        The feed rate for the movement.
    start_time : int
        Time when the movement starts.
    time : int
        Time duration for this movement.
    start_time_is_adjustable : bool
        Indicates if the start time of this movement is adjustable.
    time_is_adjustable : bool
        Indicates if the time of this movement is adjustable.
    """ 

    # Constructor
    def __init__(self,
                 g_code_line_index: int,
                 movement_type: int,
                 start_position_linear_axes: LinearAxes, 
                 end_position_linear_axes: LinearAxes,
                 start_position_rotation_axes: RotationAxes,
                 end_position_rotation_axes: RotationAxes,
                 arc_information: ArcInformation,
                 feed_rate: float,
                 active_plane: int):
        """
        Initializes the Movement instance with the provided parameters.

        Parameters:
        -----------
        g_code_line_index : int
            The line index of the G-code corresponding to this movement.
        movement_type : int
            The type of movement (e.g., linear, circular).
        start_position_linear_axes : LinearAxes
            The start position for linear axes.
        end_position_linear_axes : LinearAxes
            The end position for linear axes.
        start_position_rotation_axes : RotationAxes
            The start position for rotation axes.
        end_position_rotation_axes : RotationAxes
            The end position for rotation axes.
        arc_information : ArcInformation
            Information about the arc, if applicable.
        feed_rate : float
            The feed rate for the movement.
        active_plane: int
            Plane in which the movement takes place
        start_vector_linear_axes : np.array
            The start vector for linear axes.
        end_vector_linear_axes : np.array
            The end vector for linear axes.
        start_vector_rotation_axes : np.array
            The start vector for rotation axes.
        end_vector_rotation_axes : np.array
            The end vector for rotation axes.
        """

        # Save all parameters
        self.g_code_line_index              = g_code_line_index
        self.movement_type                  = movement_type
        self.start_position_linear_axes     = copy.deepcopy(start_position_linear_axes)
        self.end_position_linear_axes       = copy.deepcopy(end_position_linear_axes)
        self.start_position_rotation_axes   = copy.deepcopy(start_position_rotation_axes)
        self.end_position_rotation_axes     = copy.deepcopy(end_position_rotation_axes)
        self.arc_information                = copy.deepcopy(arc_information)
        self.feed_rate                      = feed_rate
        self.active_plane                   = active_plane

        # Create all the vectors
        self.start_vector_linear_axes    = np.array([0.0, 0.0, 0.0])  
        self.end_vector_linear_axes      = np.array([0.0, 0.0, 0.0])  
        self.start_vector_rotation_axes  = np.array([0.0, 0.0, 0.0]) 
        self.end_vector_rotation_axes    = np.array([0.0, 0.0, 0.0]) 

        # Set initial values for time and adjustability
        self.start_time: int = 0                      
        self.time: int = 0
        self.start_time_is_adjustable: bool = True
        self.time_is_adjustable: bool = True 

        # Check if movement is valid: compute optimal vectors and expected time
        if movement_type != -1:
            self.compute_optimal_start_vector_linear_axes() 
            self.compute_optimal_start_vector_rotation()        # Not implemented
            self.compute_optimal_end_vector_linear_axes()
            self.compute_optimal_end_vector_rotation()          # Not implemented
        else:
            self.time_is_adjustable = False

    #################################################################################################
    # Methods

    def compute_optimal_start_vector_linear_axes(self) -> None: 
        """
        Compute the optimal start vector for linear axes.

        This method calculates the optimal start vector for linear axes based on the difference
        between the start and end positions.

        For linear movements (movement types 0 and 1), the start vector is calculated as the unit vector
        pointing from the start to the end position, scaled by the feed rate.

        For circular movements (movement types 2 and 3), the start vector is calculated as the unit vector
        perpendicular to the vector from the arc center to the start position, scaled by the feed rate,
        with the direction determined by the movement type.

        Returns:
        --------
        None
        """

        # Get start and end position
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        if self.movement_type in [0, 1]:    # Linear movement
            # Compute start vector 
            start_vector_linear = end_position_linear_axes - start_position_linear_axes
            vector_length = np.linalg.norm(start_vector_linear)
            if vector_length > 0:
                self.start_vector_linear_axes = start_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:                               # Arc movement
            # Check plane and compute start vector
            match self.active_plane:
                case 17:
                    XY_normal_vector = np.array([0.0, 0.0, 1.0])
                    arc_center = self.arc_information.get_arc_center_as_array()
                    arc_center_2_start = start_position_linear_axes - arc_center
                    
                    if self.movement_type == 2:
                        self.start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "right") * self.feed_rate
                    else: 
                        self.start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "left") * self.feed_rate
                case 18:
                    raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
                case 19:
                    raise Exception(f"G02 and G03 are only available in plane 19")   # TODO

    # TODO
    def compute_optimal_start_vector_rotation(self) -> None:
        pass

    def compute_optimal_end_vector_linear_axes(self) -> None:
        """
        Compute the optimal end vector for linear axes.

        This method calculates the optimal end vector for linear axes based on the difference
        between the start and end positions.

        For linear movements (movement types 0 and 1), the end vector is calculated as the unit vector
        pointing from the start to the end position, scaled by the feed rate.

        For circular movements (movement types 2 and 3), the end vector is calculated as the unit vector
        perpendicular to the vector from the arc center to the end position, scaled by the feed rate,
        with the direction determined by the movement type.

        Returns:
        --------
        None
        """
        
        # Get start and end position
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        if self.movement_type in [0, 1]:        # Linear movement    
            # Compute start vector 
            end_vector_linear = end_position_linear_axes - start_position_linear_axes
            vector_length = np.linalg.norm(end_vector_linear)
            if vector_length > 0:
                self.end_vector_linear_axes = end_vector_linear / vector_length * self.feed_rate
            else:
                pass
        else:
            # Check plane and compute start vector
            match self.active_plane:
                case 17:
                    XY_normal_vector = np.array([0.0, 0.0, 1.0])
                    arc_center = self.arc_information.get_arc_center_as_array()
                    arc_center_2_end = end_position_linear_axes - arc_center
                    
                    if self.movement_type == 2:
                        self.end_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_end, XY_normal_vector, "right") * self.feed_rate
                    else: 
                        self.end_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_end, XY_normal_vector, "left") * self.feed_rate
                case 18:
                    raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
                case 19:
                    raise Exception(f"G02 and G03 are only available in plane 19")   # TODO
                
    # TODO
    def compute_optimal_end_vector_rotation(self) -> None:
        pass

    def do_exact_stop(self) -> None:
        """
        Perform an exact stop for the movement.

        This method sets the end vectors for both linear and rotation axes to zero,
        effectively stopping the movement.

        Returns:
        --------
        None
        """

        # Set vectors to 0
        self.end_vector_linear_axes = np.array([0.0, 0.0, 0.0])
        self.end_vector_rotation_axes = np.array([0.0, 0.0, 0.0])

    def compute_expected_time(self) -> None:
        """
        Compute the expected time for the movement.

        This method calculates the expected time required for the movement based on the movement type,
        start and end positions, and feed rate.

        For linear movements (movement types 0 and 1), the distance between start and end positions is used
        to calculate the time.

        For circular movements (movement types 2 and 3), the arc length is computed based on the radius and angle
        between start and end positions, along with the linear distance in the Z-axis, if applicable.

        Raises:
        -------
        Exception:
            If the target velocity is 0.

        Returns:
        --------
        None
        """

        if self.movement_type == -1:
            # No movement at all
            return
        
        # Get start and end position
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        # Get and check target velocity
        target_velocity = self.feed_rate
        if target_velocity == 0:
            raise Exception(f"F value is 0 in line {self.g_code_line_index+1}.")
        
        # Compute distance
        distance = 0

        if self.movement_type in [0, 1]:    # Linear movement
            distance = np.linalg.norm(end_position_linear_axes - start_position_linear_axes)
        else:                               # Arc movement
            arc_center = self.arc_information.get_arc_center_as_array()
            distance_Z = 0

            # Check plane
            match self.active_plane:
                case 17:
                    # Get Z distance
                    distance_Z = end_position_linear_axes[2] - start_position_linear_axes[2]

                    # Handle Z coordinate
                    start_position_linear_axes[2] = 0.0
                    end_position_linear_axes[2] = 0.0
                    arc_center [2] = 0.0

                case 18:
                    raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
                case 19:
                    raise Exception(f"G02 and G03 are only available in plane 19")   # TODO

            center_2_start = start_position_linear_axes - arc_center
            center_2_end = end_position_linear_axes - arc_center

            radius = abs(self.arc_information.radius)

            # Check if smaller or bigger angle is used
            smaller_angle = True
            if self.arc_information.radius >= 0:
                pass
            else:
                smaller_angle = False

            angle: float = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)
            circumference: float = 2.0*math.pi*radius
            arc_distance: float = angle / 360.0 * circumference 
            distance = math.sqrt(math.pow(arc_distance, 2) + math.pow(distance_Z, 2))

        # Compute time
        self.time = int(distance / target_velocity)

    def get_position_linear_axes_in_movement(self, 
                                             time_in_movement: int) -> np.ndarray:
        """
        Get the position of linear axes at a given time during the movement.

        This method computes the position of linear axes at a specified time during the movement
        based on the linear interpolation between start and end positions.

        Parameters:
        -----------
        time_in_movement : int
            The time at which to compute the position during the movement.

        Returns:
        --------
        np.ndarray:
            The position of linear axes at the specified time during the movement.
        """

        position = np.array([0.0, 0.0, 0.0])

        portion = time_in_movement / self.time

        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()
        
        if self.movement_type == -1:        # No movement at all
            position = start_position_linear_axes
        elif self.movement_type in [0, 1]:  # Linear movement
            # Interpolate Position
            position = start_position_linear_axes + (end_position_linear_axes - start_position_linear_axes) * portion
        else:                               # Arc movement
            # Get positions of arc
            start_point_linear: LinearAxes = copy.deepcopy(start_position_linear_axes)
            end_point_linear: LinearAxes = copy.deepcopy(end_position_linear_axes)
            arc_center = self.arc_information.get_arc_center_as_array()

            # Compute vectors
            center_2_start = start_point_linear - arc_center
            center_2_end = end_point_linear - arc_center

            match self.active_plane:
                case 17: 
                    # Handle Z coordinate
                    start_point_linear[2] = 0
                    end_point_linear[2] = 0
                    arc_center[2] = 0
                case 18:
                    raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
                case 19:
                    raise Exception(f"G02 and G03 are only available in plane 19")   # TODO
                
            # Check angle
            smaller_angle = True
            if self.arc_information.radius >= 0:
                pass
            else:
                smaller_angle = False

            # Compute angele
            angle = vecfunc.compute_angle(center_2_start, center_2_end, smaller_angle)
            current_angle = portion * angle
            if self.movement_type == 2:
                current_angle *= -1

            # Check plane
            match self.active_plane:
                case 17: 
                    # Handle Z coordinate
                    center_2_start = center_2_start[0:2]
                    arc_center = arc_center[0:2]
                    XY_position = vecfunc.rotate_2D_vector(center_2_start, arc_center, current_angle)
                    
                    position[0] = XY_position[0]
                    position[1] = XY_position[1]

                    distance_Z = self.end_position_linear_axes.Z - self.start_position_linear_axes.Z
                    current_Z = self.start_position_linear_axes.Z + portion * distance_Z
                    position[2] = current_Z
                case 18:
                    raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
                case 19:
                    raise Exception(f"G02 and G03 are only available in plane 19")   # TODO

        return np.round(position, 3)

    def print_info(self) -> None:
        """
        Print information about the movement.

        This method prints various details about the movement, including line index,
        movement type, start and end points, start and end vectors, arc information (if applicable),
        feed rate, and expected time.
        """
        print(f"Expected time: {self.time} ms")
        print(f"Movement in line {self.g_code_line_index+1}")
        print(f"g_code_line_index: {self.g_code_line_index}")
        print(f"Movement: {self.movement_type}")
        print(f"Start point: {self.start_position_linear_axes.get_as_array()}")
        print(f"End point: {self.end_position_linear_axes.get_as_array()}")
        print(f"Start vector: {self.start_vector_linear_axes}")
        print(f"End vector: {self.end_vector_linear_axes}")

        if self.movement_type in [2, 3]:    # Arc movement
            print(f"Arc info: {self.arc_information.print()}")
        
        print(f"feed rate [mm/ms]: {self.feed_rate}")

# End of class
#####################################################################################################
