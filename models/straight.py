"""
Straight Pipe Assembly Generator

Creates a straight pipe assembly consisting of:
- Flange A (start)
- Pipe section
- Flange B (end)

The assembly is oriented along the Z axis with Flange A at Z=0
(raised face pointing in +Z direction).
"""

import os
import sys
from pathlib import Path

# Setup path for imports
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cadquery as cq
from typing import Optional
from generators.flanges import create_weld_neck_flange, get_flange_metadata
from generators.pipes import create_pipe_section_simple, get_pipe_metadata
from data.asme_b16_5 import get_flange_dimensions
from data.asme_b36_10 import get_pipe_dimensions


def create_straight_assembly(
    # Flange parameters
    pressure_class: int = 150,
    nps: str = "2",
    # Pipe parameters
    pipe_schedule: str = "STD",
    face_to_face: float = 500.0,
    # Options
    welding_gap: float = 3.0,
    flange_a_class: Optional[int] = None,
    flange_b_class: Optional[int] = None,
) -> cq.Workplane:
    """
    Create a straight pipe assembly with two flanges.

    The assembly is oriented with:
    - Flange A at Z=0, raised face pointing toward +Z (into the pipe)
    - Flange B at Z=face_to_face, raised face pointing toward -Z (into the pipe)
    - Pipe section connecting the two flanges

    Args:
        pressure_class: Default ASME pressure class for both flanges
        nps: Nominal pipe size as string (e.g., "2", "1/2")
        pipe_schedule: Pipe schedule (e.g., "STD", "40", "80")
        face_to_face: Distance between flange faces (mm)
        welding_gap: Gap between parts for welding (mm)
        flange_a_class: Override pressure class for flange A
        flange_b_class: Override pressure class for flange B

    Returns:
        CadQuery Workplane containing the complete assembly

    Raises:
        ValueError: If configuration is invalid
    """
    # Resolve flange classes
    class_a = flange_a_class if flange_a_class is not None else pressure_class
    class_b = flange_b_class if flange_b_class is not None else pressure_class

    # Get flange dimensions
    dims_a = get_flange_dimensions(class_a, nps)
    dims_b = get_flange_dimensions(class_b, nps)

    # Get pipe dimensions
    pipe_dims = get_pipe_dimensions(nps, pipe_schedule)

    # Calculate positions
    # Flange A: neck extends in -Z, raised face at Z=0
    flange_a_rf_height = dims_a["raised_face_height"]
    flange_a_thickness = dims_a["flange_thickness"]
    flange_a_neck_length = dims_a["neck_length"]

    # Flange B: positioned at face_to_face distance
    flange_b_rf_height = dims_b["raised_face_height"]
    flange_b_thickness = dims_b["flange_thickness"]
    flange_b_neck_length = dims_b["neck_length"]

    # Pipe length calculation
    # Face to face is measured from raised face to raised face
    # Each flange occupies: RF_height + flange_thickness + neck_length
    # Pipe connects between the neck ends with welding gaps
    flange_a_total = flange_a_rf_height + flange_a_thickness + flange_a_neck_length
    flange_b_total = flange_b_rf_height + flange_b_thickness + flange_b_neck_length

    pipe_length = (
        face_to_face
        - flange_a_total      # Full length of flange A
        - flange_b_total      # Full length of flange B
        - 2 * welding_gap     # Welding gaps at both ends
    )

    if pipe_length < 0:
        min_required = flange_a_total + flange_b_total + 2 * welding_gap + 50
        raise ValueError(
            f"Face-to-face distance {face_to_face}mm is too short for this configuration. "
            f"Minimum required: {min_required}mm"
        )

    # Create Flange A
    # The flange generator creates flanges with:
    # - Raised face on top (Z = flange_thickness + rf_height)
    # - Neck extending downward (Z < 0)
    flange_a = create_weld_neck_flange(
        pressure_class=class_a,
        nps=nps,
        bore_override=pipe_dims["id"],
        welding_gap=welding_gap,
    )

    # Rotate flange A so raised face points toward +Z (into assembly)
    # and translate so raised face is at Z=0
    # Current orientation: RF at top, neck at bottom
    # Flip 180° around X axis so RF points down, neck points up
    # Then translate
    flange_a = (
        flange_a
        .rotate((0, 0, 0), (1, 0, 0), 180)
        .translate((0, 0, flange_a_thickness + flange_a_rf_height))
    )

    # Create Flange B
    flange_b = create_weld_neck_flange(
        pressure_class=class_b,
        nps=nps,
        bore_override=pipe_dims["id"],
        welding_gap=welding_gap,
    )

    # Position Flange B: raised face at Z=face_to_face, pointing toward -Z
    # Current orientation is correct (RF on top pointing away from assembly)
    # Just need to translate to correct position
    flange_b_z_offset = face_to_face - flange_b_rf_height - flange_b_thickness
    flange_b = flange_b.translate((0, 0, flange_b_z_offset))

    # Create pipe section
    # Position: starts after flange A neck, ends before flange B neck
    pipe_z_start = flange_a_total + welding_gap
    pipe = create_pipe_section_simple(
        od=pipe_dims["od"],
        id_=pipe_dims["id"],
        length=pipe_length,
    )
    pipe = pipe.translate((0, 0, pipe_z_start))

    # Combine all parts
    assembly = flange_a.union(pipe).union(flange_b)

    return assembly


def get_straight_assembly_metadata(
    pressure_class: int = 150,
    nps: str = "2",
    pipe_schedule: str = "STD",
    face_to_face: float = 500.0,
    welding_gap: float = 3.0,
    flange_a_class: Optional[int] = None,
    flange_b_class: Optional[int] = None,
) -> dict:
    """
    Get metadata for a straight assembly configuration.

    Returns a dictionary with all components and dimensions
    suitable for BOM generation.
    """
    class_a = flange_a_class if flange_a_class is not None else pressure_class
    class_b = flange_b_class if flange_b_class is not None else pressure_class

    dims_a = get_flange_dimensions(class_a, nps)
    dims_b = get_flange_dimensions(class_b, nps)
    pipe_dims = get_pipe_dimensions(nps, pipe_schedule)

    # Calculate pipe length (must match create_straight_assembly calculation)
    flange_a_total = dims_a["raised_face_height"] + dims_a["flange_thickness"] + dims_a["neck_length"]
    flange_b_total = dims_b["raised_face_height"] + dims_b["flange_thickness"] + dims_b["neck_length"]
    pipe_length = (
        face_to_face
        - flange_a_total
        - flange_b_total
        - 2 * welding_gap
    )

    # Calculate approximate weights
    import math

    # Flange weight (rough approximation)
    def flange_weight(dims):
        # Simplified: treat as cylinder with bore
        vol = math.pi * ((dims["flange_od"]/2)**2 - (dims["bore"]/2)**2) * dims["flange_thickness"]
        vol += math.pi * ((dims["hub_od"]/2)**2 - (dims["bore"]/2)**2) * dims["neck_length"] * 0.7
        return vol * 7.85e-9  # kg

    # Pipe weight
    pipe_vol = math.pi * ((pipe_dims["od"]/2)**2 - (pipe_dims["id"]/2)**2) * pipe_length
    pipe_weight = pipe_vol * 7.85e-9

    return {
        "type": "straight_assembly",
        "configuration": {
            "face_to_face": face_to_face,
            "welding_gap": welding_gap,
        },
        "components": [
            {
                "item": 1,
                "type": "weld_neck_flange",
                "description": f"Flange A - ASME B16.5 Class {class_a} NPS {nps}",
                "standard": "ASME B16.5",
                "pressure_class": class_a,
                "nps": nps,
                "dn": dims_a["dn"],
                "quantity": 1,
                "weight_kg": round(flange_weight(dims_a), 2),
            },
            {
                "item": 2,
                "type": "pipe_section",
                "description": f"Pipe - ASME B36.10 NPS {nps} Sch {pipe_schedule}",
                "standard": "ASME B36.10",
                "nps": nps,
                "schedule": pipe_schedule,
                "length_mm": round(pipe_length, 1),
                "quantity": 1,
                "weight_kg": round(pipe_weight, 2),
            },
            {
                "item": 3,
                "type": "weld_neck_flange",
                "description": f"Flange B - ASME B16.5 Class {class_b} NPS {nps}",
                "standard": "ASME B16.5",
                "pressure_class": class_b,
                "nps": nps,
                "dn": dims_b["dn"],
                "quantity": 1,
                "weight_kg": round(flange_weight(dims_b), 2),
            },
        ],
        "total_weight_kg": round(
            flange_weight(dims_a) + pipe_weight + flange_weight(dims_b), 2
        ),
        "unit": "mm",
    }
