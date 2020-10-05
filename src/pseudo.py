
"""
Path Planning
Station Keeping
Waypoint Following
Course and Speed to Waypoint
Course PID Controller
Heading Fusion of Gyro, Magetometer, GPS Heading
Speed Fusion of Accelerometer and GPS Speed
Gyro
Accelerometer
Magnetomoeter
GPS Position, Heading, Speed, Accuracy
Differential Thruster Mixer
Thruster Driver
Brushless Motors
https://www.youtube.com/watch?v=2et2Q3v6XPg&feature=youtu.be
"""

def followwaypoints( waypoints ):
    """
    strategy to follow one or more waypoints    
    """
    # uses gps
    # uses course to set a new course
    pass

def keepstation():
    """
    strategy to keep the current position
    """
    # uses positionFusion to get a fast and accurate position
    # uses course to keep the station
    pass

def positionFustion():
    """
    fustion of the gps Position (slow but accurate)
    with accelerometer ( fast but with integral drift )
    """
    # uses gps
    # uses accermeter
    # returns a fast and accurate position

def headingFusion():
    """
    fusion of the gps Heading(slow but accurate),
    with Magnetometer( faster but inaccurate)
    with Gyro ( very fast with drift )
    """
    # uses gps
    # uses magnetometer
    # uses gyro
    # return an accurate and fast low drift heading
    pass

def speedFusion():
    """
    fusion of the gps speed (slow but accrate )
    with Acceleroeter ( very fast but with drift)
    """
    # uses gps
    # uses accelerometer
    # return an accurate and fast speed 
    pass


def headingPID( heading ):
    """
    keeps the desired heading in radians
    """
    # uses headingFusion for actual heading
    pass

def speedPID( speed ):
    """
    keeps the desired speed -1..0..1
    """
    # ses speedFusion for actual speed
    pass


def waypoint( lat, long ):
    """
    sets the desired waypoint to go to
    """
    # uses gps position
    # uses course
    pass

def course( heading, speed ):
    """
    sets the desired course
    heading in radians
    speed in meters per second
    """
    #uses headingPID
    #uses speedPID
    #uses thrustermixer
    pass

def thrusterMixer( rudder, power )
    """
    controls the left and right thruster speeds
    rudder angle in radians
    power -1 .. 0 .. 1
    """
    #uses thrusterLeft
    #uses thrusterRight
    pass

def thrusterLeft( power ):
    """
    controls the speed and direction for the left thruster motor
    power -1 .. 0 .. 1
    """
    # uses pwmLeft
    pass


def thrusterRight( power ):
    """
    controls the speed and direction for the right thruster motor
    power -1 .. 0 .. 1
    """
    # usespwmRight
    pass