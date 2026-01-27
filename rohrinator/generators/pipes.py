"""
Parameterized Pipe Section Generator

Creates pipe sections using CadQuery based on ASME B36.10 dimensions.
Pipes can have weld preparation chamfers at the ends.
"""

import cadquery as cq
from typing import Optional
from ..data.asme_b36_10 import get_pipe_dimensions, get_available_schedules, PIPE_OD


def create_pipe_section(
    nps: str = "2",
    schedule: str = "STD",
    length: float = 500.0,
    od_override: Optional[float] = None,
    id_override: Optional[float] = None,
    weld_prep: bool = True,
    weld_prep_angle: float = 37.5,
    weld_prep_land: float = 1.6,
) -> cq.Workplane:
    """
    Create a pipe section.

    Args:
        nps: Nominal pipe size as string (e.g., "2", "1/2", "1-1/4")
        schedule: Pipe schedule (e.g., "STD", "40", "80", "XS")
        length: Pipe length in mm
        od_override: Override outer diameter (mm), uses standard if None
        id_override: Override inner diameter (mm), uses standard if None
        weld_prep: Add weld preparation chamfer at ends
        weld_prep_angle: Chamfer angle for weld prep (degrees)
        weld_prep_land: Root face land width (mm)

    Returns:
        CadQuery Workplane containing the pipe solid

    Raises:
        ValueError: If NPS or schedule not available
    """
    # Get dimensions from data module
    dims = get_pipe_dimensions(nps, schedule)

    od = od_override if od_override is not None else dims["od"]
    id_ = id_override if id_override is not None else dims["id"]
    wall = (od - id_) / 2

    # Create basic pipe (hollow cylinder)
    pipe = (
        cq.Workplane("XY")
        .circle(od / 2)
        .circle(id_ / 2)
        .extrude(length)
    )

    # Add weld preparation chamfer at both ends
    if weld_prep and wall > weld_prep_land:
        chamfer_depth = wall - weld_prep_land

        # Bottom end chamfer (Z=0)
        try:
            pipe = (
                pipe.faces("<Z")
                .edges("%Circle")
                .edges(cq.selectors.RadiusNthSelector(0))  # Inner edge
                .chamfer(chamfer_depth * 0.8, chamfer_depth)
            )
        except Exception:
            pass

        # Top end chamfer (Z=length)
        try:
            pipe = (
                pipe.faces(">Z")
                .edges("%Circle")
                .edges(cq.selectors.RadiusNthSelector(0))  # Inner edge
                .chamfer(chamfer_depth * 0.8, chamfer_depth)
            )
        except Exception:
            pass

    return pipe


def create_pipe_section_simple(
    od: float,
    id_: float,
    length: float,
) -> cq.Workplane:
    """
    Create a simple pipe section with explicit dimensions.

    Args:
        od: Outer diameter (mm)
        id_: Inner diameter (mm)
        length: Pipe length (mm)

    Returns:
        CadQuery Workplane containing the pipe solid
    """
    pipe = (
        cq.Workplane("XY")
        .circle(od / 2)
        .circle(id_ / 2)
        .extrude(length)
    )
    return pipe


def get_pipe_metadata(
    nps: str = "2",
    schedule: str = "STD",
    length: float = 500.0,
    od_override: Optional[float] = None,
    id_override: Optional[float] = None,
) -> dict:
    """
    Get metadata for a pipe section configuration.

    Returns a dictionary with all dimensions and calculated values
    suitable for BOM generation.
    """
    dims = get_pipe_dimensions(nps, schedule)

    od = od_override if od_override is not None else dims["od"]
    id_ = id_override if id_override is not None else dims["id"]
    wall = (od - id_) / 2

    # Calculate approximate weight (steel density ~7850 kg/m³)
    import math
    volume_mm3 = math.pi * ((od/2)**2 - (id_/2)**2) * length
    volume_m3 = volume_mm3 * 1e-9
    weight_kg = volume_m3 * 7850

    return {
        "type": "pipe_section",
        "standard": "ASME B36.10",
        "nps": nps,
        "schedule": schedule,
        "dimensions": {
            "od": od,
            "id": id_,
            "wall_thickness": round(wall, 2),
            "length": length,
        },
        "weight_kg": round(weight_kg, 3),
        "unit": "mm",
    }


def list_available_pipes() -> dict:
    """List all available pipe configurations."""
    return {
        "standard": "ASME B36.10",
        "sizes": list(PIPE_OD.keys()),
        "schedules_by_size": {
            nps: get_available_schedules(nps)
            for nps in PIPE_OD.keys()
        },
    }
