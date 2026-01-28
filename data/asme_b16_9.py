"""
ASME B16.9 Concentric Reducer Dimensions

Standard dimensions for butt-welding concentric reducers.
All dimensions in millimeters.

Reference: ASME B16.9 - Factory-Made Wrought Buttwelding Fittings
"""

# Concentric Reducer dimensions by size combination
# Key format: "large_nps:small_nps"
# Values: {H: overall length, large_od, small_od}
# Note: OD values are nominal pipe OD from ASME B36.10

CONCENTRIC_REDUCERS = {
    # NPS 2 x 1-1/2
    "2:1-1/2": {"H": 89, "large_od": 60.3, "small_od": 48.3},
    # NPS 2 x 1-1/4
    "2:1-1/4": {"H": 89, "large_od": 60.3, "small_od": 42.2},
    # NPS 2 x 1
    "2:1": {"H": 89, "large_od": 60.3, "small_od": 33.4},
    # NPS 2 x 3/4
    "2:3/4": {"H": 89, "large_od": 60.3, "small_od": 26.7},

    # NPS 2-1/2 x 2
    "2-1/2:2": {"H": 89, "large_od": 73.0, "small_od": 60.3},
    # NPS 2-1/2 x 1-1/2
    "2-1/2:1-1/2": {"H": 89, "large_od": 73.0, "small_od": 48.3},
    # NPS 2-1/2 x 1-1/4
    "2-1/2:1-1/4": {"H": 89, "large_od": 73.0, "small_od": 42.2},
    # NPS 2-1/2 x 1
    "2-1/2:1": {"H": 89, "large_od": 73.0, "small_od": 33.4},

    # NPS 3 x 2-1/2
    "3:2-1/2": {"H": 89, "large_od": 88.9, "small_od": 73.0},
    # NPS 3 x 2
    "3:2": {"H": 89, "large_od": 88.9, "small_od": 60.3},
    # NPS 3 x 1-1/2
    "3:1-1/2": {"H": 89, "large_od": 88.9, "small_od": 48.3},
    # NPS 3 x 1-1/4
    "3:1-1/4": {"H": 89, "large_od": 88.9, "small_od": 42.2},
    # NPS 3 x 1
    "3:1": {"H": 89, "large_od": 88.9, "small_od": 33.4},

    # NPS 4 x 3
    "4:3": {"H": 102, "large_od": 114.3, "small_od": 88.9},
    # NPS 4 x 2-1/2
    "4:2-1/2": {"H": 102, "large_od": 114.3, "small_od": 73.0},
    # NPS 4 x 2
    "4:2": {"H": 102, "large_od": 114.3, "small_od": 60.3},
    # NPS 4 x 1-1/2
    "4:1-1/2": {"H": 102, "large_od": 114.3, "small_od": 48.3},
    # NPS 4 x 1-1/4
    "4:1-1/4": {"H": 102, "large_od": 114.3, "small_od": 42.2},

    # NPS 6 x 5
    "6:5": {"H": 140, "large_od": 168.3, "small_od": 141.3},
    # NPS 6 x 4
    "6:4": {"H": 140, "large_od": 168.3, "small_od": 114.3},
    # NPS 6 x 3
    "6:3": {"H": 140, "large_od": 168.3, "small_od": 88.9},
    # NPS 6 x 2-1/2
    "6:2-1/2": {"H": 140, "large_od": 168.3, "small_od": 73.0},
    # NPS 6 x 2
    "6:2": {"H": 140, "large_od": 168.3, "small_od": 60.3},

    # NPS 8 x 6
    "8:6": {"H": 152, "large_od": 219.1, "small_od": 168.3},
    # NPS 8 x 5
    "8:5": {"H": 152, "large_od": 219.1, "small_od": 141.3},
    # NPS 8 x 4
    "8:4": {"H": 152, "large_od": 219.1, "small_od": 114.3},
    # NPS 8 x 3
    "8:3": {"H": 152, "large_od": 219.1, "small_od": 88.9},

    # NPS 10 x 8
    "10:8": {"H": 178, "large_od": 273.0, "small_od": 219.1},
    # NPS 10 x 6
    "10:6": {"H": 178, "large_od": 273.0, "small_od": 168.3},
    # NPS 10 x 5
    "10:5": {"H": 178, "large_od": 273.0, "small_od": 141.3},
    # NPS 10 x 4
    "10:4": {"H": 178, "large_od": 273.0, "small_od": 114.3},

    # NPS 12 x 10
    "12:10": {"H": 203, "large_od": 323.8, "small_od": 273.0},
    # NPS 12 x 8
    "12:8": {"H": 203, "large_od": 323.8, "small_od": 219.1},
    # NPS 12 x 6
    "12:6": {"H": 203, "large_od": 323.8, "small_od": 168.3},
    # NPS 12 x 5
    "12:5": {"H": 203, "large_od": 323.8, "small_od": 141.3},
}

# Wall thickness schedule mapping for reducers
# Typically matches the larger pipe schedule
REDUCER_SCHEDULES = ["STD", "XS", "40", "80", "160"]


def get_reducer_dimensions(large_nps: str, small_nps: str) -> dict:
    """
    Get concentric reducer dimensions for a given size combination.

    Args:
        large_nps: Large end NPS (e.g., "4")
        small_nps: Small end NPS (e.g., "2")

    Returns:
        Dictionary with H (length), large_od, small_od

    Raises:
        ValueError if combination not found
    """
    key = f"{large_nps}:{small_nps}"

    if key not in CONCENTRIC_REDUCERS:
        # Try reverse order
        reverse_key = f"{small_nps}:{large_nps}"
        if reverse_key in CONCENTRIC_REDUCERS:
            raise ValueError(f"Reducer {key} not found. Did you mean {reverse_key}?")

        available = list(CONCENTRIC_REDUCERS.keys())
        raise ValueError(
            f"Reducer combination {key} not available. "
            f"Available combinations: {available}"
        )

    return CONCENTRIC_REDUCERS[key].copy()


def list_available_reducers() -> dict:
    """List all available reducer combinations."""
    return {
        "combinations": list(CONCENTRIC_REDUCERS.keys()),
        "schedules": REDUCER_SCHEDULES,
    }


def get_reducer_length(large_nps: str, small_nps: str) -> float:
    """Get the overall length (H) of a reducer."""
    dims = get_reducer_dimensions(large_nps, small_nps)
    return dims["H"]
