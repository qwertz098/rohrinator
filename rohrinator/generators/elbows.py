"""
Parameterized Pipe Elbow Generator

Creates pipe elbows (90° and 45°) using CadQuery.
Supports different bend radii: 2D, 3D, 5D (where D = nominal pipe diameter).
"""

import sys
import math
from pathlib import Path

# Setup path for imports
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cadquery as cq
from typing import Optional, Literal
from data.asme_b36_10 import get_pipe_dimensions, PIPE_OD


def create_pipe_elbow(
    nps: str = "2",
    schedule: str = "STD",
    angle: float = 90.0,
    bend_radius_factor: Literal["2D", "3D", "5D"] = "3D",
    od_override: Optional[float] = None,
    id_override: Optional[float] = None,
) -> cq.Workplane:
    """
    Create a pipe elbow.

    Args:
        nps: Nominal pipe size as string (e.g., "2", "1/2", "1-1/4")
        schedule: Pipe schedule (e.g., "STD", "40", "80", "XS")
        angle: Bend angle in degrees (typically 90 or 45)
        bend_radius_factor: Bend radius as multiple of nominal diameter ("2D", "3D", "5D")
        od_override: Override outer diameter (mm)
        id_override: Override inner diameter (mm)

    Returns:
        CadQuery Workplane containing the elbow solid
    """
    # Get pipe dimensions
    dims = get_pipe_dimensions(nps, schedule)
    od = od_override if od_override is not None else dims["od"]
    id_ = id_override if id_override is not None else dims["id"]
    wall = (od - id_) / 2

    # Calculate bend radius (center line radius)
    # Factor is based on nominal pipe OD
    nominal_od = PIPE_OD[nps]
    factor_map = {"2D": 2.0, "3D": 3.0, "5D": 5.0}
    factor = factor_map.get(bend_radius_factor, 3.0)
    bend_radius = nominal_od * factor / 2  # Radius to centerline

    # Create elbow by making outer and inner torus sections, then subtracting
    # This approach is more reliable than revolving an annulus

    # Create outer torus section (solid)
    outer = (
        cq.Workplane("XY")
        .center(bend_radius, 0)
        .circle(od / 2)
        .revolve(angle, (0, 0, 0), (0, 0, 1), clean=False)
    )

    # Create inner torus section (to cut out)
    inner = (
        cq.Workplane("XY")
        .center(bend_radius, 0)
        .circle(id_ / 2)
        .revolve(angle, (0, 0, 0), (0, 0, 1), clean=False)
    )

    # Subtract inner from outer to create hollow elbow
    elbow = outer.cut(inner)

    # The elbow is now in XY plane:
    # - Inlet at (bend_radius, 0, 0) pointing in -X direction
    # - Outlet at (0, bend_radius, 0) pointing in +Y direction (for 90° bend)

    return elbow


def create_elbow_with_extensions(
    nps: str = "2",
    schedule: str = "STD",
    angle: float = 90.0,
    bend_radius_factor: Literal["2D", "3D", "5D"] = "3D",
    extension_length: float = 50.0,
    od_override: Optional[float] = None,
    id_override: Optional[float] = None,
) -> cq.Workplane:
    """
    Create a pipe elbow with straight extensions at both ends.

    This makes it easier to position and weld to adjacent pipe sections.

    Args:
        nps: Nominal pipe size
        schedule: Pipe schedule
        angle: Bend angle in degrees
        bend_radius_factor: Bend radius factor ("2D", "3D", "5D")
        extension_length: Length of straight pipe at each end (mm)
        od_override: Override outer diameter (mm)
        id_override: Override inner diameter (mm)

    Returns:
        CadQuery Workplane containing the elbow with extensions
    """
    # Get pipe dimensions
    dims = get_pipe_dimensions(nps, schedule)
    od = od_override if od_override is not None else dims["od"]
    id_ = id_override if id_override is not None else dims["id"]

    # Calculate bend radius
    nominal_od = PIPE_OD[nps]
    factor_map = {"2D": 2.0, "3D": 3.0, "5D": 5.0}
    factor = factor_map.get(bend_radius_factor, 3.0)
    bend_radius = nominal_od * factor / 2

    # Create the main elbow
    elbow = create_pipe_elbow(nps, schedule, angle, bend_radius_factor, od, id_)

    # Add extension at the inlet (along +X axis, before the bend)
    if extension_length > 0:
        inlet_ext = (
            cq.Workplane("YZ")
            .transformed(offset=(bend_radius, 0, 0))
            .circle(od / 2)
            .circle(id_ / 2)
            .extrude(extension_length)
        )
        elbow = elbow.union(inlet_ext)

    # Add extension at the outlet (along +Z axis, after the bend)
    # For 90° bend, outlet is at (0, 0, bend_radius) pointing in +Z
    if extension_length > 0 and angle == 90.0:
        outlet_ext = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, bend_radius))
            .circle(od / 2)
            .circle(id_ / 2)
            .extrude(extension_length)
        )
        elbow = elbow.union(outlet_ext)

    return elbow


def get_elbow_dimensions(
    nps: str = "2",
    schedule: str = "STD",
    angle: float = 90.0,
    bend_radius_factor: Literal["2D", "3D", "5D"] = "3D",
) -> dict:
    """
    Get dimensions for an elbow configuration.

    Returns:
        Dictionary with elbow dimensions
    """
    dims = get_pipe_dimensions(nps, schedule)
    nominal_od = PIPE_OD[nps]

    factor_map = {"2D": 2.0, "3D": 3.0, "5D": 5.0}
    factor = factor_map.get(bend_radius_factor, 3.0)
    bend_radius = nominal_od * factor / 2

    # Arc length along centerline
    arc_length = 2 * math.pi * bend_radius * (angle / 360)

    # Center-to-end dimension (for 90° elbow, this is the bend radius)
    center_to_end = bend_radius

    return {
        "nps": nps,
        "schedule": schedule,
        "angle": angle,
        "bend_radius_factor": bend_radius_factor,
        "od": dims["od"],
        "id": dims["id"],
        "wall_thickness": dims["wall_thickness"],
        "bend_radius": round(bend_radius, 2),
        "arc_length": round(arc_length, 2),
        "center_to_end": round(center_to_end, 2),
    }


def get_elbow_metadata(
    nps: str = "2",
    schedule: str = "STD",
    angle: float = 90.0,
    bend_radius_factor: Literal["2D", "3D", "5D"] = "3D",
) -> dict:
    """
    Get metadata for an elbow configuration suitable for BOM.
    """
    dims = get_elbow_dimensions(nps, schedule, angle, bend_radius_factor)

    # Calculate approximate weight
    arc_length = dims["arc_length"]
    od = dims["od"]
    id_ = dims["id"]
    volume_mm3 = math.pi * ((od/2)**2 - (id_/2)**2) * arc_length
    weight_kg = volume_mm3 * 7.85e-9

    return {
        "type": "pipe_elbow",
        "standard": "ASME B16.9",
        "nps": nps,
        "schedule": schedule,
        "angle": angle,
        "bend_radius_factor": bend_radius_factor,
        "dimensions": dims,
        "weight_kg": round(weight_kg, 3),
        "unit": "mm",
    }
