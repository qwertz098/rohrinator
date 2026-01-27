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
    chamfer_angle: float = 37.5,
    welding_gap: float = 3.0,
) -> cq.Workplane:
    """
    Create a pipe elbow by sweeping pipe profile along a curved path.

    Args:
        nps: Nominal pipe size as string (e.g., "2", "1/2", "1-1/4")
        schedule: Pipe schedule (e.g., "STD", "40", "80", "XS")
        angle: Bend angle in degrees (typically 90 or 45)
        bend_radius_factor: Bend radius as multiple of nominal diameter ("2D", "3D", "5D")
        od_override: Override outer diameter (mm)
        id_override: Override inner diameter (mm)
        chamfer_angle: Weld prep bevel angle in degrees (default 37.5°)
        welding_gap: Root gap for welding (mm)

    Returns:
        CadQuery Workplane containing the elbow solid
    """
    # Get pipe dimensions
    dims = get_pipe_dimensions(nps, schedule)
    od = od_override if od_override is not None else dims["od"]
    id_ = id_override if id_override is not None else dims["id"]

    r_pipe = od / 2  # Outer radius
    r_inner = id_ / 2  # Inner radius
    wall = r_pipe - r_inner

    # Calculate bend radius (center line radius)
    # Factor is based on nominal pipe OD: 2D = 2×D, 3D = 3×D, 5D = 5×D
    nominal_od = PIPE_OD[nps]
    factor_map = {"2D": 2.0, "3D": 3.0, "5D": 5.0}
    factor = factor_map.get(bend_radius_factor, 3.0)
    r_bend = nominal_od * factor  # Centerline bend radius = factor × nominal diameter

    # Calculate chamfer depth based on wall thickness and angle
    # Chamfer goes from OD down toward ID at 37.5°
    # Leave a small land (root face) at the ID for welding
    root_face = min(1.6, wall * 0.2)  # ~1.6mm or 20% of wall, whichever is smaller
    chamfer_depth = wall - root_face
    chamfer_height = chamfer_depth * math.tan(math.radians(chamfer_angle))

    # Create path: arc for the bend
    # For 90° elbow: quarter circle from (0,0) to (r_bend, r_bend)
    if angle == 90.0:
        path = cq.Workplane("XZ").radiusArc((r_bend, r_bend), r_bend)
    else:
        # General angle: end point calculation
        end_x = r_bend * math.sin(math.radians(angle))
        end_z = r_bend * (1 - math.cos(math.radians(angle)))
        path = cq.Workplane("XZ").radiusArc((end_x, end_z), r_bend)

    # Sweep outer circle profile along path
    outer = cq.Workplane("XY").circle(r_pipe).sweep(path, isFrenet=True)

    # Sweep inner circle and subtract to make hollow pipe
    inner = cq.Workplane("XY").circle(r_inner).sweep(path, isFrenet=True)
    elbow = outer.cut(inner)

    # Add 37.5° chamfer at inlet end (at origin, facing -X direction)
    # Create a cone-shaped cut for the bevel
    chamfer_inlet = (
        cq.Workplane("XY")
        .circle(r_pipe + 1)  # Slightly larger to ensure clean cut
        .circle(r_inner + root_face)  # Leave root face
        .extrude(-chamfer_height - welding_gap / 2)
    )
    # Create the angled bevel using a cone
    bevel_inlet = (
        cq.Workplane("XY")
        .transformed(offset=(0, 0, -welding_gap / 2))
        .circle(r_pipe)
        .workplane(offset=-chamfer_height)
        .circle(r_inner + root_face)
        .loft()
    )
    # Cut flat end and add bevel
    elbow = elbow.cut(chamfer_inlet)
    elbow = elbow.union(bevel_inlet)

    # Add 37.5° chamfer at outlet end
    # For 90° elbow, outlet is at (r_bend, 0, r_bend) facing +Z direction
    if angle == 90.0:
        chamfer_outlet = (
            cq.Workplane("XY")
            .transformed(offset=(r_bend, 0, r_bend))
            .circle(r_pipe + 1)
            .circle(r_inner + root_face)
            .extrude(chamfer_height + welding_gap / 2)
        )
        bevel_outlet = (
            cq.Workplane("XY")
            .transformed(offset=(r_bend, 0, r_bend + welding_gap / 2))
            .circle(r_pipe)
            .workplane(offset=chamfer_height)
            .circle(r_inner + root_face)
            .loft()
        )
        elbow = elbow.cut(chamfer_outlet)
        elbow = elbow.union(bevel_outlet)
    else:
        # General angle outlet position
        end_x = r_bend * math.sin(math.radians(angle))
        end_z = r_bend * (1 - math.cos(math.radians(angle)))
        # Rotate chamfer to match outlet angle
        chamfer_outlet = (
            cq.Workplane("XY")
            .transformed(offset=(end_x, 0, end_z), rotate=(0, -angle, 0))
            .circle(r_pipe + 1)
            .circle(r_inner + root_face)
            .extrude(chamfer_height + welding_gap / 2)
        )
        bevel_outlet = (
            cq.Workplane("XY")
            .transformed(offset=(end_x, 0, end_z), rotate=(0, -angle, 0))
            .transformed(offset=(0, 0, welding_gap / 2))
            .circle(r_pipe)
            .workplane(offset=chamfer_height)
            .circle(r_inner + root_face)
            .loft()
        )
        elbow = elbow.cut(chamfer_outlet)
        elbow = elbow.union(bevel_outlet)

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
    bend_radius = nominal_od * factor  # Centerline bend radius = factor × nominal diameter

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
    bend_radius = nominal_od * factor  # Centerline bend radius = factor × nominal diameter

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
