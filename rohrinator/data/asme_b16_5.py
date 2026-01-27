"""
ASME B16.5 Weld Neck Flange Dimensions
All dimensions in mm

Classes: 150, 300, 600, 900, 1500, 2500
Sizes: NPS 1/2" to 24"

Key parameters:
- flange_od: Flange outside diameter
- flange_thickness: Flange thickness at bolt line
- raised_face_od: Raised face diameter
- raised_face_height: Height of raised face
- bolt_circle: Bolt circle diameter
- num_bolts: Number of bolt holes
- bolt_hole_dia: Diameter of bolt holes
- hub_od: Hub diameter at flange junction
- neck_length: Length of tapered neck
- pipe_od: Pipe outside diameter (standard)
- bore: Default bore diameter (standard weight)
"""

# ASME B16.5 Class 150 Weld Neck Flanges - Complete data
CLASS_150 = {
    "1/2": {
        "nps": "1/2",
        "dn": 15,
        "flange_od": 88.9,
        "flange_thickness": 11.2,
        "raised_face_od": 34.9,
        "raised_face_height": 1.6,
        "bolt_circle": 60.3,
        "num_bolts": 4,
        "bolt_hole_dia": 15.9,
        "hub_od": 38.1,
        "neck_length": 47.8,
        "pipe_od": 21.3,
        "bore": 15.8,
    },
    "3/4": {
        "nps": "3/4",
        "dn": 20,
        "flange_od": 98.4,
        "flange_thickness": 12.7,
        "raised_face_od": 42.9,
        "raised_face_height": 1.6,
        "bolt_circle": 69.8,
        "num_bolts": 4,
        "bolt_hole_dia": 15.9,
        "hub_od": 47.6,
        "neck_length": 50.8,
        "pipe_od": 26.7,
        "bore": 20.9,
    },
    "1": {
        "nps": "1",
        "dn": 25,
        "flange_od": 107.9,
        "flange_thickness": 14.3,
        "raised_face_od": 50.8,
        "raised_face_height": 1.6,
        "bolt_circle": 79.4,
        "num_bolts": 4,
        "bolt_hole_dia": 15.9,
        "hub_od": 54.0,
        "neck_length": 53.8,
        "pipe_od": 33.4,
        "bore": 26.6,
    },
    "1-1/4": {
        "nps": "1-1/4",
        "dn": 32,
        "flange_od": 117.5,
        "flange_thickness": 15.9,
        "raised_face_od": 63.5,
        "raised_face_height": 1.6,
        "bolt_circle": 88.9,
        "num_bolts": 4,
        "bolt_hole_dia": 15.9,
        "hub_od": 63.5,
        "neck_length": 55.6,
        "pipe_od": 42.2,
        "bore": 35.1,
    },
    "1-1/2": {
        "nps": "1-1/2",
        "dn": 40,
        "flange_od": 127.0,
        "flange_thickness": 17.5,
        "raised_face_od": 73.0,
        "raised_face_height": 1.6,
        "bolt_circle": 98.4,
        "num_bolts": 4,
        "bolt_hole_dia": 15.9,
        "hub_od": 69.8,
        "neck_length": 57.2,
        "pipe_od": 48.3,
        "bore": 40.9,
    },
    "2": {
        "nps": "2",
        "dn": 50,
        "flange_od": 152.4,
        "flange_thickness": 19.1,
        "raised_face_od": 92.1,
        "raised_face_height": 1.6,
        "bolt_circle": 120.6,
        "num_bolts": 4,
        "bolt_hole_dia": 19.1,
        "hub_od": 84.1,
        "neck_length": 61.9,
        "pipe_od": 60.3,
        "bore": 52.5,
    },
    "2-1/2": {
        "nps": "2-1/2",
        "dn": 65,
        "flange_od": 177.8,
        "flange_thickness": 22.2,
        "raised_face_od": 104.8,
        "raised_face_height": 1.6,
        "bolt_circle": 139.7,
        "num_bolts": 4,
        "bolt_hole_dia": 19.1,
        "hub_od": 100.1,
        "neck_length": 66.5,
        "pipe_od": 73.0,
        "bore": 62.7,
    },
    "3": {
        "nps": "3",
        "dn": 80,
        "flange_od": 190.5,
        "flange_thickness": 23.8,
        "raised_face_od": 127.0,
        "raised_face_height": 1.6,
        "bolt_circle": 152.4,
        "num_bolts": 4,
        "bolt_hole_dia": 19.1,
        "hub_od": 117.5,
        "neck_length": 69.9,
        "pipe_od": 88.9,
        "bore": 77.9,
    },
    "3-1/2": {
        "nps": "3-1/2",
        "dn": 90,
        "flange_od": 215.9,
        "flange_thickness": 23.8,
        "raised_face_od": 139.7,
        "raised_face_height": 1.6,
        "bolt_circle": 177.8,
        "num_bolts": 8,
        "bolt_hole_dia": 19.1,
        "hub_od": 130.2,
        "neck_length": 73.2,
        "pipe_od": 101.6,
        "bore": 90.1,
    },
    "4": {
        "nps": "4",
        "dn": 100,
        "flange_od": 228.6,
        "flange_thickness": 23.8,
        "raised_face_od": 157.2,
        "raised_face_height": 1.6,
        "bolt_circle": 190.5,
        "num_bolts": 8,
        "bolt_hole_dia": 19.1,
        "hub_od": 142.9,
        "neck_length": 76.2,
        "pipe_od": 114.3,
        "bore": 102.3,
    },
    "5": {
        "nps": "5",
        "dn": 125,
        "flange_od": 254.0,
        "flange_thickness": 23.8,
        "raised_face_od": 185.7,
        "raised_face_height": 1.6,
        "bolt_circle": 215.9,
        "num_bolts": 8,
        "bolt_hole_dia": 22.2,
        "hub_od": 163.6,
        "neck_length": 82.6,
        "pipe_od": 141.3,
        "bore": 128.2,
    },
    "6": {
        "nps": "6",
        "dn": 150,
        "flange_od": 279.4,
        "flange_thickness": 25.4,
        "raised_face_od": 215.9,
        "raised_face_height": 1.6,
        "bolt_circle": 241.3,
        "num_bolts": 8,
        "bolt_hole_dia": 22.2,
        "hub_od": 177.8,
        "neck_length": 88.9,
        "pipe_od": 168.3,
        "bore": 154.1,
    },
    "8": {
        "nps": "8",
        "dn": 200,
        "flange_od": 342.9,
        "flange_thickness": 28.6,
        "raised_face_od": 269.9,
        "raised_face_height": 1.6,
        "bolt_circle": 298.4,
        "num_bolts": 8,
        "bolt_hole_dia": 22.2,
        "hub_od": 219.1,
        "neck_length": 101.6,
        "pipe_od": 219.1,
        "bore": 202.7,
    },
    "10": {
        "nps": "10",
        "dn": 250,
        "flange_od": 406.4,
        "flange_thickness": 30.2,
        "raised_face_od": 323.8,
        "raised_face_height": 1.6,
        "bolt_circle": 361.9,
        "num_bolts": 12,
        "bolt_hole_dia": 25.4,
        "hub_od": 273.0,
        "neck_length": 114.3,
        "pipe_od": 273.0,
        "bore": 254.5,
    },
    "12": {
        "nps": "12",
        "dn": 300,
        "flange_od": 482.6,
        "flange_thickness": 31.8,
        "raised_face_od": 381.0,
        "raised_face_height": 1.6,
        "bolt_circle": 431.8,
        "num_bolts": 12,
        "bolt_hole_dia": 25.4,
        "hub_od": 323.8,
        "neck_length": 127.0,
        "pipe_od": 323.8,
        "bore": 304.8,
    },
    "14": {
        "nps": "14",
        "dn": 350,
        "flange_od": 533.4,
        "flange_thickness": 35.0,
        "raised_face_od": 412.8,
        "raised_face_height": 1.6,
        "bolt_circle": 476.2,
        "num_bolts": 12,
        "bolt_hole_dia": 28.6,
        "hub_od": 355.6,
        "neck_length": 139.7,
        "pipe_od": 355.6,
        "bore": 336.5,
    },
    "16": {
        "nps": "16",
        "dn": 400,
        "flange_od": 596.9,
        "flange_thickness": 36.6,
        "raised_face_od": 469.9,
        "raised_face_height": 1.6,
        "bolt_circle": 539.8,
        "num_bolts": 16,
        "bolt_hole_dia": 28.6,
        "hub_od": 406.4,
        "neck_length": 152.4,
        "pipe_od": 406.4,
        "bore": 387.4,
    },
    "18": {
        "nps": "18",
        "dn": 450,
        "flange_od": 635.0,
        "flange_thickness": 39.7,
        "raised_face_od": 533.4,
        "raised_face_height": 1.6,
        "bolt_circle": 577.8,
        "num_bolts": 16,
        "bolt_hole_dia": 31.8,
        "hub_od": 457.2,
        "neck_length": 165.1,
        "pipe_od": 457.0,
        "bore": 438.2,
    },
    "20": {
        "nps": "20",
        "dn": 500,
        "flange_od": 698.5,
        "flange_thickness": 42.9,
        "raised_face_od": 584.2,
        "raised_face_height": 1.6,
        "bolt_circle": 635.0,
        "num_bolts": 20,
        "bolt_hole_dia": 31.8,
        "hub_od": 508.0,
        "neck_length": 177.8,
        "pipe_od": 508.0,
        "bore": 488.9,
    },
    "24": {
        "nps": "24",
        "dn": 600,
        "flange_od": 812.8,
        "flange_thickness": 47.6,
        "raised_face_od": 692.2,
        "raised_face_height": 1.6,
        "bolt_circle": 749.3,
        "num_bolts": 20,
        "bolt_hole_dia": 35.0,
        "hub_od": 609.6,
        "neck_length": 203.2,
        "pipe_od": 610.0,
        "bore": 590.6,
    },
}

# ASME B16.5 Class 300 Weld Neck Flanges - Placeholder structure
CLASS_300 = {
    "1/2": {"nps": "1/2", "dn": 15, "flange_od": 95.2, "flange_thickness": 14.3, "raised_face_od": 34.9, "raised_face_height": 1.6, "bolt_circle": 66.7, "num_bolts": 4, "bolt_hole_dia": 15.9, "hub_od": 38.1, "neck_length": 47.8, "pipe_od": 21.3, "bore": 15.8},
    "3/4": {"nps": "3/4", "dn": 20, "flange_od": 117.5, "flange_thickness": 15.9, "raised_face_od": 42.9, "raised_face_height": 1.6, "bolt_circle": 82.5, "num_bolts": 4, "bolt_hole_dia": 19.1, "hub_od": 47.6, "neck_length": 50.8, "pipe_od": 26.7, "bore": 20.9},
    "1": {"nps": "1", "dn": 25, "flange_od": 123.8, "flange_thickness": 17.5, "raised_face_od": 50.8, "raised_face_height": 1.6, "bolt_circle": 88.9, "num_bolts": 4, "bolt_hole_dia": 19.1, "hub_od": 54.0, "neck_length": 53.8, "pipe_od": 33.4, "bore": 26.6},
    # TODO: Add remaining sizes
}

# ASME B16.5 Class 600 Weld Neck Flanges - Placeholder
CLASS_600 = {
    # TODO: Populate with actual data
}

# ASME B16.5 Class 900 Weld Neck Flanges - Placeholder
CLASS_900 = {
    # TODO: Populate with actual data
}

# ASME B16.5 Class 1500 Weld Neck Flanges - Placeholder
CLASS_1500 = {
    # TODO: Populate with actual data
}

# ASME B16.5 Class 2500 Weld Neck Flanges - Placeholder
CLASS_2500 = {
    # TODO: Populate with actual data
}

# Main lookup dictionary
ASME_B16_5_FLANGES = {
    150: CLASS_150,
    300: CLASS_300,
    600: CLASS_600,
    900: CLASS_900,
    1500: CLASS_1500,
    2500: CLASS_2500,
}

# Available sizes per class
AVAILABLE_SIZES = {
    150: list(CLASS_150.keys()),
    300: list(CLASS_300.keys()),
    600: [],  # TODO
    900: [],  # TODO
    1500: [],  # TODO
    2500: [],  # TODO
}

PRESSURE_CLASSES = [150, 300, 600, 900, 1500, 2500]


def get_flange_dimensions(pressure_class: int, nps: str) -> dict:
    """
    Get flange dimensions for a given pressure class and nominal pipe size.

    Args:
        pressure_class: ASME pressure class (150, 300, 600, 900, 1500, 2500)
        nps: Nominal pipe size as string (e.g., "2", "1/2", "1-1/4")

    Returns:
        Dictionary with flange dimensions in mm

    Raises:
        ValueError: If pressure class or size not available
    """
    if pressure_class not in ASME_B16_5_FLANGES:
        raise ValueError(f"Invalid pressure class: {pressure_class}. Available: {PRESSURE_CLASSES}")

    class_data = ASME_B16_5_FLANGES[pressure_class]

    if nps not in class_data:
        available = list(class_data.keys())
        raise ValueError(f"Size {nps} not available for Class {pressure_class}. Available: {available}")

    return class_data[nps]
