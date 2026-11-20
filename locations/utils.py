import math

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth in kilometers
    using the Haversine formula.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    except (ValueError, TypeError):
        return None

    # Earth radius in kilometers
    R = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    
    # Clip to avoid float precision issues with math.sqrt
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = R * c
    return round(distance, 2)


def calculate_proximity_score(distance_km, max_radius_km=50.0):
    """
    Returns a normalized proximity score between 0.0 and 1.0.
    1.0 means same spot; 0.0 means beyond max_radius_km.
    """
    if distance_km is None:
        return 0.5  # Neutral default when location is not pinpointed
    if distance_km <= 0:
        return 1.0
    if distance_km >= max_radius_km:
        return 0.0
    return round(1.0 - (distance_km / max_radius_km), 4)
