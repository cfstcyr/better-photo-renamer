def convert_gps_to_decimal(gps_tuple) -> float:
    """
    Converts GPS coordinates from degrees, minutes, and seconds format to decimal format.
    Args:
        gps_tuple (tuple): A tuple containing three tuples, each representing degrees, minutes, and seconds.
                           Each inner tuple contains two integers, the numerator and denominator of a fraction.
                           Example: `((41, 1), (56, 1), (2910, 100))`
    Returns:
        float: The GPS coordinates in decimal format.
    """

    degrees = gps_tuple[0][0] / gps_tuple[0][1]
    minutes = gps_tuple[1][0] / gps_tuple[1][1]
    seconds = gps_tuple[2][0] / gps_tuple[2][1]

    return degrees + (minutes / 60) + (seconds / 3600)
