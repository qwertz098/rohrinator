"""
Parameterized Concentric Reducer Generator

Creates ASME B16.9 concentric reducers using CadQuery.
Includes 37.5° weld prep chamfers at both ends.
"""

import sys
import math
from pathlib import Path
from typing import Optional

# Setup path for imports
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cadquery as cq
from data.asme_b16_9 import get_reducer_dimensions
from data.asme_b36_10 import get_pipe_dimensions


def create_concentric_reducer(
    large_nps: str = "4",
    small_nps: str = "2",
    large_schedule: str = "STD",
    small_schedule: str = "STD",
    chamfer_angle: float = 37.5,
    welding_gap: float = 3.0,
) -> cq.Workplane:
    """
    Create an ASME B16.9 concentric reducer.

    The reducer transitions from large pipe size to small pipe size.
    Includes 37.5° weld prep chamfers at both ends.

    Args:
        large_nps: Large end nominal pipe size (e.g., "4")
        small_nps: Small end nominal pipe size (e.g., "2")
        large_schedule: Pipe schedule for large end
        small_schedule: Pipe schedule for small end
        chamfer_angle: Weld prep bevel angle (default 37.5°)
        welding_gap: Root gap for welding (mm)

    Returns:
        CadQuery Workplane containing the reducer solid

    Orientation:
        - Large end at Z=0, facing -Z
        - Small end at Z=H, facing +Z
    """
    # Get dimensions
    dims = get_reducer_dimensions(large_nps, small_nps)
    H = dims["H"]  # Overall length

    # Get pipe dimensions for wall thickness
    large_pipe = get_pipe_dimensions(large_nps, large_schedule)
    small_pipe = get_pipe_dimensions(small_nps, small_schedule)

    large_od = large_pipe["od"]
    large_id = large_pipe["id"]
    small_od = small_pipe["od"]
    small_id = small_pipe["id"]

    large_wall = (large_od - large_id) / 2
    small_wall = (small_od - small_id) / 2

    # Chamfer calculations for weld prep
    large_root_face = min(1.6, large_wall * 0.25)
    small_root_face = min(1.6, small_wall * 0.25)
    large_chamfer_depth = large_wall - large_root_face
    small_chamfer_depth = small_wall - small_root_face
    large_chamfer_height = large_chamfer_depth / math.tan(math.radians(chamfer_angle))
    small_chamfer_height = small_chamfer_depth / math.tan(math.radians(chamfer_angle))

    # Create outer tapered body using loft
    outer = (
        cq.Workplane("XY")
        .circle(large_od / 2)
        .workplane(offset=H)
        .circle(small_od / 2)
        .loft()
    )

    # Create inner tapered bore using loft
    inner = (
        cq.Workplane("XY")
        .circle(large_id / 2)
        .workplane(offset=H)
        .circle(small_id / 2)
        .loft()
    )

    # Hollow out the reducer
    reducer = outer.cut(inner)

    # Add weld prep chamfer at large end (Z=0)
    # Create a chamfer by cutting a cone shape from the outside
    if large_chamfer_height > 0.1:
        large_chamfer = (
            cq.Workplane("XY")
            .circle(large_od / 2 + 1)  # Slightly larger to ensure full cut
            .workplane(offset=large_chamfer_height)
            .circle(large_id / 2 + large_root_face)
            .loft()
        )
        reducer = reducer.cut(large_chamfer)

    # Add weld prep chamfer at small end (Z=H)
    if small_chamfer_height > 0.1:
        small_chamfer = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, H))
            .circle(small_od / 2 + 1)  # Slightly larger
            .workplane(offset=-small_chamfer_height)
            .circle(small_id / 2 + small_root_face)
            .loft()
        )
        reducer = reducer.cut(small_chamfer)

    return reducer


def get_reducer_metadata(
    large_nps: str = "4",
    small_nps: str = "2",
    large_schedule: str = "STD",
    small_schedule: str = "STD",
) -> dict:
    """
    Get metadata for a reducer configuration.

    Returns:
        Dictionary with reducer specifications
    """
    dims = get_reducer_dimensions(large_nps, small_nps)
    large_pipe = get_pipe_dimensions(large_nps, large_schedule)
    small_pipe = get_pipe_dimensions(small_nps, small_schedule)

    # Approximate weight calculation
    H = dims["H"]
    large_od = large_pipe["od"]
    large_id = large_pipe["id"]
    small_od = small_pipe["od"]
    small_id = small_pipe["id"]

    # Frustum volume approximation
    avg_od = (large_od + small_od) / 2
    avg_id = (large_id + small_id) / 2
    vol_mm3 = math.pi * ((avg_od / 2) ** 2 - (avg_id / 2) ** 2) * H
    weight_kg = vol_mm3 * 7.85e-9  # Steel density

    return {
        "type": "concentric_reducer",
        "standard": "ASME B16.9",
        "large_nps": large_nps,
        "small_nps": small_nps,
        "large_schedule": large_schedule,
        "small_schedule": small_schedule,
        "dimensions": {
            "length": dims["H"],
            "large_od": large_od,
            "large_id": large_id,
            "small_od": small_od,
            "small_id": small_id,
        },
        "weight_kg": round(weight_kg, 3),
        "unit": "mm",
    }


# Test
if __name__ == "__main__":
    print("Creating test reducer NPS 4 x 2...")
    reducer = create_concentric_reducer("4", "2")
    meta = get_reducer_metadata("4", "2")
    print(f"Dimensions: {meta['dimensions']}")
    print(f"Weight: {meta['weight_kg']} kg")

    # Export
    import os
    out_dir = Path(__file__).parent.parent / "parts"
    os.makedirs(out_dir, exist_ok=True)
    cq.exporters.export(reducer, str(out_dir / "reducer_4x2.step"), exportType="STEP")
    cq.exporters.export(reducer, str(out_dir / "reducer_4x2.stl"), exportType="STL")
    print(f"Exported to {out_dir / 'reducer_4x2.step'}")
