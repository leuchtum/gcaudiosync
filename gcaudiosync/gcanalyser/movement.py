import numpy as np
import copy
import math

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc
import gcaudiosync.gcanalyser.numericalmethods as nummet

from gcaudiosync.gcanalyser.arcinformation import ArcInformation
from gcaudiosync.gcanalyser.cncparameter import CNCParameter
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
    start_time : float
        Time when the movement starts.
    time : float
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
                 active_plane: int,
                 CNC_Parameter: CNCParameter):
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
        self.g_code_line_index: int                         = g_code_line_index
        self.movement_type: int                             = movement_type
        self.start_position_linear_axes: LinearAxes         = copy.deepcopy(start_position_linear_axes)
        self.end_position_linear_axes: LinearAxes           = copy.deepcopy(end_position_linear_axes)
        self.start_position_rotation_axes: RotationAxes     = copy.deepcopy(start_position_rotation_axes)
        self.end_position_rotation_axes: RotationAxes       = copy.deepcopy(end_position_rotation_axes)
        self.arc_information: ArcInformation                = copy.deepcopy(arc_information)
        self.feed_rate: float                               = feed_rate
        self.active_plane: int                              = active_plane

        # Create all the vectors
        self.start_vector_linear_axes: np.array     = np.array([0.0, 0.0, 0.0])  
        self.end_vector_linear_axes: np.array       = np.array([0.0, 0.0, 0.0])  
        self.start_vector_rotation_axes: np.array   = np.array([0.0, 0.0, 0.0]) 
        self.end_vector_rotation_axes: np.array     = np.array([0.0, 0.0, 0.0]) 

        # Set initial values for time and adjustability
        self.start_time: float              = 0.0                   
        self.time: float                    = 0.0
        self.start_time_is_adjustable: bool = True
        self.time_is_adjustable: bool       = True 

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

        # Initialize start vector
        start_vector_linear_axes = np.zeros(3)

        if self.movement_type in [0, 1]:    # Linear movement
            # Compute start vector 
            start_vector_linear = end_position_linear_axes - start_position_linear_axes
            vector_length = np.linalg.norm(start_vector_linear)
            if vector_length > 0:
                start_vector_linear_axes = start_vector_linear / vector_length * self.feed_rate
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
                        start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "right") * self.feed_rate
                    else: 
                        start_vector_linear_axes = vecfunc.compute_normal_vector(arc_center_2_start, XY_normal_vector, "left") * self.feed_rate
                case 18:
                    raise Exception(f"G02 and G03 are not available in plane 18")    # TODO
                case 19:
                    raise Exception(f"G02 and G03 are not available in plane 19")   # TODO

        self.start_vector_linear_axes = start_vector_linear_axes

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
                    raise Exception(f"G02 and G03 are not available in plane 19")   # TODO
                
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

    # TODO: comment
    def compute_expected_time(self,
                              max_acceleration: np.array,
                              max_deceleration: np.array) -> None:

        if self.movement_type == -1:
            # No movement at all
            pass
        elif self.movement_type in [0, 1]:
            self.compute_expected_time_linear_movement_type(max_acceleration, max_deceleration)
        elif self.movement_type in [2, 3]:
            self.compute_expected_time_arc_movement_type(max_acceleration, max_deceleration)
        else:
            Exception(f"Unknown movement type: {self.movement_type}")

    # TODO: comment
    def compute_expected_time_linear_movement_type(self,
                                                   max_acceleration: np.array,
                                                   max_deceleration: np.array) -> None:

        # Get start and end position
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        # Get start and end vector
        start_velocity_vector_linear_axes = np.absolute(copy.copy(self.start_vector_linear_axes))
        end_velocity_vector_linear_axes = np.absolute(copy.copy(self.end_vector_linear_axes))

        # Get and check target velocity
        target_velocity = self.feed_rate
        if target_velocity == 0:
            raise Exception(f"F value is 0 in line {self.g_code_line_index+1}.")
        
        # Compute distance vector and distance
        distance_vector_linear_axes = np.absolute(end_position_linear_axes - start_position_linear_axes)
        distance = np.linalg.norm(end_position_linear_axes - start_position_linear_axes)

        # Check if distance > 0
        if not distance > 0:
            self.time = 0
            return

        target_velocity_vector_linear_axes = distance_vector_linear_axes / distance * target_velocity

        # Copmute delta velocity from start to target
        delta_velocity_start = target_velocity_vector_linear_axes - start_velocity_vector_linear_axes
        delta_velocity_start = np.absolute(delta_velocity_start)

        # Compute acceleration time and distance
        acceleration_times = np.divide(delta_velocity_start, max_acceleration)
        acceleration_time = max(acceleration_times)
        important_axe_acceleration = np.argmax(acceleration_times)
        distance_acceleration = 0.5*max_acceleration[important_axe_acceleration]*acceleration_time**2 + start_velocity_vector_linear_axes[important_axe_acceleration]*acceleration_time
        
        # Check distance acceleration
        if distance_acceleration > distance:
            pass
        
        # Copmute delta velocity from target to end
        delta_velocity_end = target_velocity_vector_linear_axes - end_velocity_vector_linear_axes
        delta_velocity_end = np.absolute(delta_velocity_end)

        # Compute acceleration time and distance
        deceleration_times = np.divide(delta_velocity_end, max_deceleration)
        deceleration_time = max(deceleration_times)
        important_axe_deceleration = np.argmax(deceleration_times)
        distance_deceleration = 0.5*max_deceleration[important_axe_deceleration]*deceleration_time**2 + end_velocity_vector_linear_axes[important_axe_deceleration]*deceleration_time
        
        # Check distance deceleration
        if distance_deceleration > distance:
            pass
        
        # Compute and check distance with target velocity
        distance_target_velocity = distance - distance_acceleration - distance_deceleration
        if distance_target_velocity < 0:
            distance_target_velocity = 0
        
        # Compute time with target velocity
        target_velocity_time = distance_target_velocity / target_velocity

        # Compute time
        self.time = acceleration_time + target_velocity_time + deceleration_time
    
    # TODO: comment
    def compute_expected_time_arc_movement_type(self,
                                                max_acceleration: np.array,
                                                max_deceleration: np.array) -> int:
        # Simplified computation: Acceleration or deceleration linear until the start or end velocity for the velocity of the arc movement is reached.
        # Does not check if acceleration is enought for the arc movement

        # Get start and end position
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()

        # Get arc center
        arc_center = self.arc_information.get_arc_center_as_array()

        # Shift start and end position into the center, happens in active plane (does not matter for the computation of the time)
        start_position_linear_axes = start_position_linear_axes - arc_center
        end_position_linear_axes = end_position_linear_axes - arc_center
        # From here on: X = 0 and Y = 0 is the center of the arc!

        # Get start and end vector
        start_velocity_vector_linear_axes = copy.copy(self.start_vector_linear_axes)
        end_velocity_vector_linear_axes = copy.copy(self.end_vector_linear_axes)

        # Get and check target velocity
        target_velocity = self.feed_rate
        if target_velocity == 0:
            raise Exception(f"F value is 0 in line {self.g_code_line_index+1}.")
        
        # Get the radius
        radius = abs(self.arc_information.radius)
            
        # Check if smaller or bigger angle is used
        smaller_angle = True
        if self.arc_information.radius > 0:
            pass
        elif self.arc_information.radius < 0:
            smaller_angle = False
        else:
            raise Exception(f"Radius of arc movement is 0.")
        
        # Initialize time
        time = 0

        # Match the active plane
        match self.active_plane:
            case 17:
                # Save stuff for Z Axis
                distance_vector_Z = end_position_linear_axes[2] - start_position_linear_axes[2]
                start_velocity_Z = start_velocity_vector_linear_axes[2]
                end_velocity_Z = end_velocity_vector_linear_axes[2]

                # Compute start and end velocity for the arc movement
                start_velocity_arc_movement = np.linalg.norm(start_velocity_vector_linear_axes[0:2])
                end_velocity_arc_movement = np.linalg.norm(end_velocity_vector_linear_axes[0:2])

                # Create 2D arrays for further computation of the arc
                start_position_linear_axes = start_position_linear_axes[0:2]
                end_position_linear_axes = end_position_linear_axes[0:2]

                # Compute angle of movement
                angle = 0.0
                if (start_position_linear_axes == end_position_linear_axes).all():
                    angle = 360.0
                else:
                    angle: float = vecfunc.compute_small_or_big_angle_in_degree(start_position_linear_axes, 
                                                                                end_position_linear_axes, 
                                                                                smaller_angle)

                # Compute distances
                circumference: float = 2.0*math.pi*radius
                arc_distance: float = angle / 360.0 * circumference 
                distance_Z = abs(distance_vector_Z)
                distance = math.sqrt(math.pow(arc_distance, 2) + math.pow(distance_Z, 2))

                # Compute target velocities
                target_velocity_Z = target_velocity * distance_Z / distance
                target_velocity_arc_movement = target_velocity * arc_distance / distance

                # Compute start times for the arc movement
                start_time_X_Y = 0.0
                delta_velocity_start_arc_movement = target_velocity_arc_movement - start_velocity_arc_movement
                acceleration_start_arc_movement = min(max_acceleration[0:2])
                if delta_velocity_start_arc_movement > 0:
                    start_time_X_Y = delta_velocity_start_arc_movement / acceleration_start_arc_movement

                # Compute start time for the Z axis
                start_time_Z = 0.0
                delta_velocity_start_Z = abs(target_velocity_Z -  start_velocity_Z)
                if delta_velocity_start_Z > 0:
                    start_time_Z = delta_velocity_start_Z / max_acceleration[2]

                # Compute start time
                start_time = max(start_time_X_Y, start_time_Z)

                # Compute and check start distance
                start_distance_percentage = 0
                if start_time > 0:
                    if start_time_Z >= start_time_X_Y:
                        start_distance_Z = acceleration_start_arc_movement * start_time**2 + start_velocity_vector_linear_axes[2] * start_time
                        start_distance_percentage = start_distance_Z / distance_vector_Z
                    else:
                        start_distance_X_Y = acceleration_start_arc_movement * start_time**2 + start_velocity_arc_movement * start_time
                        start_distance_percentage = start_distance_X_Y / arc_distance
                
                    # Check start_distance_percentage
                    if start_distance_percentage > 1:
                        pass

                # Compute end times for the arc movement
                end_time_X_Y = 0.0
                delta_velocity_end_arc_movement = target_velocity_arc_movement - end_velocity_arc_movement
                deceleration_end_arc_movement = min(max_deceleration[0:2])
                if delta_velocity_end_arc_movement > 0:
                    end_time_X_Y = delta_velocity_end_arc_movement / deceleration_end_arc_movement

                # Compute end time for the Z axis
                end_time_Z = 0.0
                delta_velocity_end_Z = abs(target_velocity_Z -  end_velocity_Z)
                if delta_velocity_end_Z > 0:
                    end_time_Z = delta_velocity_end_Z / max_deceleration[2]
                
                # Compute end time
                end_time = max(end_time_X_Y, end_time_Z)

                # Compute and check end distance
                end_distance_percentage = 0
                if end_time > 0:
                    if end_time_Z >= end_time_X_Y:
                        end_distance_Z = deceleration_end_arc_movement * end_time**2 + end_velocity_vector_linear_axes[2] * end_time
                        end_distance_percentage = end_distance_Z / distance_vector_Z
                    else:
                        end_distance_X_Y = deceleration_end_arc_movement * end_time**2 + end_velocity_arc_movement * end_time
                        end_distance_percentage = end_distance_X_Y / arc_distance
                
                    # Check end_distance_percentage
                    if end_distance_percentage > 1:
                        pass

                # Check start and end distance percentage
                distance_target_velocity = 0
                if start_distance_percentage + end_distance_percentage <= 1:
                    distance_target_velocity = distance * (1 - start_distance_percentage - end_distance_percentage)

                # Compute time with target velocity
                target_velocity_time = distance_target_velocity / target_velocity

                # Compute total time
                time = target_velocity_time + start_time + end_time

            case 18:
                raise Exception(f"G02 and G03 are not available in plane 18")   # TODO
            case 19:
                raise Exception(f"G02 and G03 are not available in plane 19")   # TODO


        self.time = time

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
            arc_center = self.arc_information.get_arc_center_as_array()

            # Compute vectors
            center_2_start = start_position_linear_axes - arc_center
            center_2_end = end_position_linear_axes - arc_center

            match self.active_plane:
                case 17: 
                    # Handle Z coordinate
                    start_position_linear_axes[2] = 0
                    end_position_linear_axes[2] = 0
                    arc_center[2] = 0

                    # Check angle
                    smaller_angle = True
                    if self.arc_information.radius >= 0:
                        pass
                    else:
                        smaller_angle = False

                    # Compute angele
                    angle = 0.0
                    if (start_position_linear_axes == end_position_linear_axes).all():
                        angle = 360.0
                    else:
                        angle = vecfunc.compute_small_or_big_angle_in_degree(center_2_start, center_2_end, smaller_angle)
                    current_angle = portion * angle
                    if self.movement_type == 2:
                        current_angle *= -1

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
                    raise Exception(f"G02 and G03 are not available in plane 19")   # TODO

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
