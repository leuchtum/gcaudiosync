import numpy as np
import copy
import math

import gcaudiosync.gcanalyser.vectorfunctions as vecfunc

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
        self.max_acceleration: np.array             = CNC_Parameter.get_acceleration_as_array()
        self.max_deceleration: np.array             = CNC_Parameter.get_deceleration_as_array()

        # Create all the scalars
        self.start_time: float              = 0.0                   
        self.duration: float                = 0.0
        self.start_time_is_adjustable: bool = True
        self.time_is_adjustable: bool       = True 
        self.duration_acceleration: float   = 0.0
        self.duration_constant_speed: float = 0.0
        self.duration_deceleration: float   = 0.0
        self.distance_acceleration: float   = 0.0
        self.distance_constant_speed: float = 0.0
        self.distance_deceleration: float   = 0.0
        self.total_distance: float          = 0.0
        self.acceleration: float            = 0.0
        self.deceleration: float            = 0.0
        self.max_feed_rate: float           = CNC_Parameter.F_MAX / 60000
        self.dynamic_is_ok: bool            = True

        # Check if movement is valid: compute optimal vectors and expected time
        if self.movement_type != -1:
            if self.movement_type in [2, 3]:
                self.adjust_arc_movement_feed_rate()

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

    def compute_expected_time(self) -> None:
        '''
        Method to compute the expected time for a movement.
        '''

        if self.movement_type == -1:
            # No movement at all
            pass
        elif self.movement_type in [0, 1]:
            self.compute_expected_time_linear_movement_type()
        elif self.movement_type in [2, 3]:
            self.compute_expected_time_arc_movement_type()
        else:
            Exception(f"Unknown movement type: {self.movement_type}")

    def compute_expected_time_linear_movement_type(self) -> None:
        '''
        Method to compute the expected time for a linear movement.
        '''

        # Assumption: the distance of the movement is long enought to accelerate or decelerate from the start position to the end position
        # If this is not the case, the start or end velocity must be adjusted. This is not implemented jet. So the computet time would be not computed correct.

        self.dynamic_is_ok = True

        # Get start and end position
        start_position_linear_axes = self.start_position_linear_axes.get_as_array()     # [mm]
        end_position_linear_axes = self.end_position_linear_axes.get_as_array()         # [mm]

        # Get start and end vector
        start_velocity_vector_linear_axes = np.absolute(copy.copy(self.start_vector_linear_axes))   # [mm/ms]
        end_velocity_vector_linear_axes = np.absolute(copy.copy(self.end_vector_linear_axes))       # [mm/ms]

        # Get target velocity
        target_velocity = self.feed_rate        # [mm/ms]
        
        # Compute distance vector and distance
        distance_vector_linear_axes = np.absolute(end_position_linear_axes - start_position_linear_axes)
        self.distance = np.linalg.norm(end_position_linear_axes - start_position_linear_axes)
        
        # Check if distance > 0
        if not self.distance > 0:
            self.duration = 0

        # Compute target velocity for linear axes
        target_velocity_vector_linear_axes = vecfunc.normalize(distance_vector_linear_axes) * target_velocity

        # Acceleration phase #####################################################
        # Compute max acceleration for this movement -> proportional to the feed rate
        max_acceleration = self.max_acceleration * target_velocity / self.max_feed_rate

        # Copmute delta velocity from start to target
        delta_velocity_start = target_velocity_vector_linear_axes - start_velocity_vector_linear_axes

        # Compute acceleration time and distance
        durations_acceleration = np.divide(delta_velocity_start, max_acceleration)
        self.duration_acceleration = max(durations_acceleration)

        if self.duration_acceleration < 0:
            raise Exception(f"Something went wrong: acceleration time is negative.")
        elif self.duration_acceleration == 0:
            pass
        else:
            important_axis_acceleration = np.argmax(durations_acceleration)
            distance_acceleration_important_axis = 0.5 * max_acceleration[important_axis_acceleration] * self.duration_acceleration**2 + start_velocity_vector_linear_axes[important_axis_acceleration] * self.duration_acceleration
            distance_vector_acceleration_linear_axes = vecfunc.normalize(distance_vector_linear_axes) / distance_vector_linear_axes[important_axis_acceleration] * distance_acceleration_important_axis
            self.distance_acceleration = np.linalg.norm(distance_vector_acceleration_linear_axes)
            start_velocity_linear_axes = np.linalg.norm(start_velocity_vector_linear_axes)
            self.acceleration = 2 * (self.distance_acceleration - start_velocity_linear_axes * self.duration_acceleration) / self.duration_acceleration**2
            
            # Check distance acceleration
            if self.distance_acceleration > self.distance:
                # TODO: In this case the target feed rate is not reachable in time. -> Adjust target feed rate. Careful: could affect end velocity vector.
                self.dynamic_is_ok = False
        
        # Deceleration phase #####################################################
        # Compute max deceleration for this movement -> proportional to the feed rate
        max_deceleration = self.max_deceleration * target_velocity / self.max_feed_rate

        # Copmute delta velocity from target to end
        delta_velocity_end = target_velocity_vector_linear_axes - end_velocity_vector_linear_axes

        # Compute acceleration time and distance
        duration_deceleration = np.divide(delta_velocity_end, max_deceleration)
        self.duration_deceleration = max(duration_deceleration)

        if self.duration_deceleration < 0:
            raise Exception(f"Something went wrong: deceleration time is negative.")
        elif self.duration_deceleration == 0:
            pass
        else:
            important_axis_deceleration = np.argmax(duration_deceleration)
            distance_deceleration_important_axis = 0.5 * max_deceleration[important_axis_deceleration] * self.duration_deceleration**2 + end_velocity_vector_linear_axes[important_axis_deceleration] * self.duration_deceleration
            distance_vector_deceleration_linear_axes = vecfunc.normalize(distance_vector_linear_axes) / distance_vector_linear_axes[important_axis_deceleration] * distance_deceleration_important_axis
            self.distance_deceleration = np.linalg.norm(distance_vector_deceleration_linear_axes)
            end_velocity_linear_axes = np.linalg.norm(end_velocity_vector_linear_axes)
            self.deceleration = 2 * (self.distance_deceleration - end_velocity_linear_axes * self.duration_deceleration) / self.duration_deceleration**2
            
            # Check distance acceleration
            if self.distance_deceleration > self.distance:
                # TODO: In this case the end feed rate is not reachable in time. -> Adjust target feed rate. Careful: could affect start velocity vector.
                self.dynamic_is_ok = False
        
        # Phase with target feed rate #####################################################
        self.distance_constant_speed = self.distance - self.distance_acceleration - self.distance_deceleration
        if self.distance_constant_speed < 0:
            # TODO: In this case the end feed rate is not reachable in time. -> Adjust target feed rate and/or start and end velocities
            self.distance_constant_speed = 0
            self.dynamic_is_ok = False
        
        # Compute time with target velocity
        self.duration_constant_speed = self.distance_constant_speed / target_velocity

        # Compute time
        self.duration = self.duration_acceleration + self.duration_constant_speed + self.duration_deceleration
    
    def compute_expected_time_arc_movement_type(self) -> int:
        '''
        Method to compute the expected time for a arc movement.
        '''

        # Assumption: the distance of the movement is long enought to accelerate or decelerate from the start position to the end position
        # If this is not the case, the start or end velocity must be adjusted. This is not implemented jet. So the computet time would be not computed correct.

        self.dynamic_is_ok = True

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

        # Match the active plane
        match self.active_plane:
            case 17:
                # Save stuff for Z Axis
                distance_Z = abs(end_position_linear_axes[2] - start_position_linear_axes[2])
                start_velocity_Z = abs(start_velocity_vector_linear_axes[2])
                end_velocity_Z = abs(end_velocity_vector_linear_axes[2])

                # Compute start and end velocity for the arc movement
                start_velocity_arc_movement = np.linalg.norm(start_velocity_vector_linear_axes[0:2])
                end_velocity_arc_movement = np.linalg.norm(end_velocity_vector_linear_axes[0:2])

                # Create 2D arrays for further computation of the arc
                start_position_arc_linear_axes = start_position_linear_axes[0:2]
                end_position_arc_linear_axes = end_position_linear_axes[0:2]

                # Compute angle of movement
                angle: float = 0.0
                if (start_position_arc_linear_axes == end_position_arc_linear_axes).all():
                    angle = 360.0
                else:
                    angle = vecfunc.compute_small_or_big_angle_in_degree(start_position_arc_linear_axes, 
                                                                         end_position_arc_linear_axes, 
                                                                         smaller_angle)

                # Compute distances
                circumference: float = 2.0*math.pi*radius
                distance_arc: float = angle / 360.0 * circumference 
                self.distance = math.sqrt(math.pow(distance_arc, 2) + math.pow(distance_Z, 2))

                # Compute target velocities
                target_velocity_Z = target_velocity * distance_Z / self.distance
                target_velocity_arc_movement = target_velocity * distance_arc / self.distance

                # Acceleration phase #####################################################
                # Compute max acceleration for this movement -> proportional to the feed rate

                min_acceleration_deceleration_arc = min(np.min(self.max_acceleration[0:2]), min(self.max_deceleration[0:2]))  # Min acceleration or deceleration
                max_tangential_acceleration = math.sqrt(min_acceleration_deceleration_arc**2 + target_velocity_arc_movement**2 / radius)
                max_acceleration_arc = max_tangential_acceleration * target_velocity / self.max_feed_rate
                max_acceleration_Z = self.max_acceleration[2] * target_velocity / self.max_feed_rate

                # Compute delta velocities start
                delta_velocity_start_arc_movement = target_velocity_arc_movement - start_velocity_arc_movement
                delta_velocity_start_Z = target_velocity_Z -  start_velocity_Z
                
                # Compute acceleration time and distance
                duration_acceleration_arc = delta_velocity_start_arc_movement / max_acceleration_arc
                duration_acceleration_Z = delta_velocity_start_Z / max_acceleration_Z
                self.duration_acceleration = max(duration_acceleration_arc, duration_acceleration_Z)

                if self.duration_acceleration < 0:
                    raise Exception(f"Something went wrong: acceleration time is negative.")
                elif self.duration_acceleration == 0:
                    pass
                elif duration_acceleration_Z > duration_acceleration_arc:
                    distance_acceleration_Z = 0.5 * max_acceleration_Z * self.duration_acceleration**2 + start_velocity_Z * self.duration_acceleration
                    factor_start = distance_acceleration_Z / distance_Z
                    distance_acceleration_arc = factor_start * distance_arc
                    self.distance_acceleration = math.sqrt(distance_acceleration_Z**2 + distance_acceleration_arc**2)
                    start_velocity_linear_axes = np.linalg.norm(start_velocity_vector_linear_axes)
                    self.acceleration = 2 * (self.distance_acceleration - start_velocity_linear_axes * self.duration_acceleration) / self.duration_acceleration**2
                else:
                    distance_acceleration_arc = 0.5 * max_acceleration_arc * self.duration_acceleration**2 + start_velocity_arc_movement * self.duration_acceleration
                    factor_start = distance_acceleration_arc / distance_arc
                    distance_acceleration_Z = factor_start * distance_Z
                    self.distance_acceleration = math.sqrt(distance_acceleration_Z**2 + distance_acceleration_arc**2)
                    start_velocity_linear_axes = np.linalg.norm(start_velocity_vector_linear_axes)
                    self.acceleration = 2 * (self.distance_acceleration - start_velocity_linear_axes * self.duration_acceleration) / self.duration_acceleration**2

                    # Check distance acceleration
                    if self.distance_acceleration > self.distance:
                        # TODO: In this case the target feed rate is not reachable in time. -> Adjust target feed rate. Careful: could affect end velocity vector.
                        self.dynamic_is_ok = False
        
                # Deceleration phase #####################################################
                # Compute max deceleration for this movement -> proportional to the feed rate

                min_acceleration_deceleration_arc = min(np.min(self.max_acceleration[0:2]), min(self.max_deceleration[0:2]))  # Min acceleration or deceleration
                max_tangential_deceleration = math.sqrt(min_acceleration_deceleration_arc**2 + target_velocity_arc_movement**2 / radius)
                max_deceleration_arc = max_tangential_deceleration * target_velocity / self.max_feed_rate
                max_deceleration_Z = self.max_deceleration[2] * target_velocity / self.max_feed_rate        
                
                # Compute delta velocities end
                delta_velocity_end_arc_movement = target_velocity_arc_movement - end_velocity_arc_movement
                delta_velocity_end_Z = target_velocity_Z -  end_velocity_Z

                # Compute acceleration time and distance
                duration_deceleration_arc = delta_velocity_end_arc_movement / max_deceleration_arc
                duration_deceleration_Z = delta_velocity_end_Z / max_deceleration_Z
                self.duration_deceleration = max(duration_deceleration_arc, duration_deceleration_Z)
                
                if self.duration_deceleration < 0:
                    raise Exception(f"Something went wrong: deceleration time is negative.")
                elif self.duration_deceleration == 0:
                    pass
                elif duration_deceleration_Z > duration_deceleration_arc:
                    distance_deceleration_Z = 0.5 * max_deceleration_Z * self.duration_deceleration**2 + end_velocity_Z * self.duration_deceleration
                    factor_end = distance_deceleration_Z / distance_Z
                    distance_deceleration_arc = factor_end * distance_arc
                    self.distance_deceleration = math.sqrt(distance_deceleration_Z**2 + distance_deceleration_arc**2)
                    end_velocity_linear_axes = np.linalg.norm(end_velocity_vector_linear_axes)
                    self.deceleration = 2 * (self.distance_deceleration - end_velocity_linear_axes * self.duration_deceleration) / self.duration_deceleration**2
                else:
                    distance_deceleration_arc = 0.5 * max_deceleration_arc * self.duration_deceleration**2 + end_velocity_arc_movement * self.duration_deceleration
                    factor_end = distance_deceleration_arc / distance_arc
                    distance_deceleration_Z = factor_end * distance_Z
                    self.distance_deceleration = math.sqrt(distance_deceleration_Z**2 + distance_deceleration_arc**2)
                    end_velocity_linear_axes = np.linalg.norm(end_velocity_vector_linear_axes)
                    self.deceleration = 2 * (self.distance_deceleration - end_velocity_linear_axes * self.duration_deceleration) / self.duration_deceleration**2

                    # Check distance deceleration
                    if self.distance_deceleration > self.distance:
                        # TODO: In this case the target feed rate is not reachable in time. -> Adjust target feed rate. Careful: could affect end velocity vector.
                        self.dynamic_is_ok = False

                # Phase with target feed rate #####################################################
                self.distance_constant_speed = self.distance - self.distance_acceleration - self.distance_deceleration
                if self.distance_constant_speed < 0:
                    # TODO: In this case the end feed rate is not reachable in time. -> Adjust target feed rate and/or start and end velocities
                    self.distance_constant_speed = 0
                    self.dynamic_is_ok = False
                
                # Compute time with target velocity
                self.duration_constant_speed = self.distance_constant_speed / target_velocity

                # Compute time
                self.duration = self.duration_acceleration + self.duration_constant_speed + self.duration_deceleration

            case 18:
                raise Exception(f"G02 and G03 are not available in plane 18")   # TODO
            case 19:
                raise Exception(f"G02 and G03 are not available in plane 19")   # TODO
    
    def get_position_linear_axes_in_movement_as_array(self, 
                                                      time_in_movement: float) -> np.array:
        """
        Get the position of linear axes at a given time during the movement.

        This method computes the position of linear axes at a specified time during the movement
        based on the linear interpolation between start and end positions.

        Parameters:
        -----------
        time_in_movement : float
            The time at which to compute the position during the movement.

        Returns:
        --------
        np.ndarray:
            The position of linear axes at the specified time during the movement.
        """

        position = np.array([0.0, 0.0, 0.0])

        portion = time_in_movement / self.duration

        if portion < 0 or portion > 1:
            raise Exception(f"Something wrong here")

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
                    angle: float = 0.0
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

        position = np.round(position, 3)

        return position

    def print_info(self) -> None:
        """
        Print information about the movement.

        This method prints various details about the movement, including line index,
        movement type, start and end points, start and end vectors, arc information (if applicable),
        feed rate, and expected time.
        """
        print(f"Expected duration: {self.duration} ms")
        print(f"Movement in line {self.g_code_line_index+1}")
        print(f"g_code_line_index: {self.g_code_line_index}")
        print(f"Movement: {self.movement_type}")
        print(f"Start point: {self.start_position_linear_axes.get_as_array()}")
        print(f"End point: {self.end_position_linear_axes.get_as_array()}")
        print(f"Start vector: {self.start_vector_linear_axes}")
        print(f"End vector: {self.end_vector_linear_axes}")

        if self.movement_type in [2, 3]:    # Arc movement
            self.arc_information.print()
        
        print(f"feed rate [mm/ms]: {self.feed_rate}")

    def adjust_arc_movement_feed_rate(self):
        '''
        Method to adjust the feed rate of a arc movement
        '''
        
        radius = self.arc_information.radius    # [mm]
        feed_rate = self.feed_rate              # [mm/ms]

        acceleration_normal = feed_rate**2 / radius # Normal acceleration [mm/ms^2]

        min_acceleration_deceleration = min(np.min(self.max_acceleration), min(self.max_deceleration))  # Min acceleration or deceleration

        acceleration_factor = 0.8   # Safety factor for acceleration

        # Check acceleration
        if acceleration_normal > min_acceleration_deceleration*acceleration_factor:
            # Compute new feed rate
            new_feed_rate = math.sqrt(min_acceleration_deceleration*acceleration_factor*radius)
            self.feed_rate = new_feed_rate

# End of class
#####################################################################################################
