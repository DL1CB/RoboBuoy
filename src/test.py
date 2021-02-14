from pseudo import bearing

def test_bearing(  ):
    assert(bearing( (49, 10) , (59, 10)) == 0)
    assert(bearing( (49, 10) , (39, 10)) == 180)
    assert(bearing( (49, 10) , (49, 11)) == 89.62264108690965)
    assert(bearing( (49, 10) , (49, 9))  == 270.37735891309035)