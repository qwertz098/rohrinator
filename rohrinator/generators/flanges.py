"""
Parameterized Weld Neck Flange Generator

Creates ASME B16.5 weld neck flanges using CadQuery based on
standard dimensions from the data module.
"""

import sys
from pathlib import Path

# Setup path for imports
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cadquery as cq
from typing import Optional
from data.asme_b16_5 import get_flange_dimensions, PRESSURE_CLASSES, AVAILABLE_SIZES


def create_weld_neck_flange(
    pressure_class: int = 150,
    nps: str = "2",
    bore_override: Optional[float] = None,
    welding_gap: float = 0.0,
) -> cq.Workplane:
    """
    Create an ASME B16.5 weld neck flange.

    Args:
        pressure_class: ASME pressure class (150, 300, 600, 900, 1500, 2500)
        nps: Nominal pipe size as string (e.g., "2", "1/2", "1-1/4")
        bore_override: Override bore diameter (mm), uses standard if None
        welding_gap: Gap at weld end for welding preparation (mm)

    Returns:
        CadQuery Workplane containing the flange solid

    Raises:
        ValueError: If pressure class or size not available
    """
    # Get dimensions from data module
    dims = get_flange_dimensions(pressure_class, nps)

    # Extract dimensions
    flange_od = dims["flange_od"]
    flange_thickness = dims["flange_thickness"]
    raised_face_od = dims["raised_face_od"]
    raised_face_height = dims["raised_face_height"]
    bolt_circle = dims["bolt_circle"]
    num_bolts = dims["num_bolts"]
    bolt_hole_dia = dims["bolt_hole_dia"]
    hub_od = dims["hub_od"]
    neck_length = dims["neck_length"]
    pipe_od = dims["pipe_od"]
    bore = bore_override if bore_override is not None else dims["bore"]

    # Fillet radius (proportional to size)
    fillet_radius = min(3.0, flange_thickness * 0.1)

    # 1. Flange body (base plate)
    flange = (
        cq.Workplane("XY")
        .circle(flange_od / 2)
        .extrude(flange_thickness)
    )

    # 2. Raised face (sealing surface)
    raised_face = (
        cq.Workplane("XY")
        .workplane(offset=flange_thickness)
        .circle(raised_face_od / 2)
        .extrude(raised_face_height)
    )
    flange = flange.union(raised_face)

    # 3. Tapered neck (weld neck)
    # The neck tapers from hub diameter to pipe OD
    # Profile is revolved around Y axis
    neck_profile = (
        cq.Workplane("XZ")
        .moveTo(hub_od / 2, 0)                              # Start at hub
        .lineTo(hub_od / 2, -5)                             # Short straight section
        .lineTo(pipe_od / 2, -(neck_length - 10))          # Tapered transition
        .lineTo(pipe_od / 2, -neck_length + welding_gap)   # Pipe connection
        .lineTo(bore / 2, -neck_length + welding_gap)      # Inner edge at bottom
        .lineTo(bore / 2, 0)                                # Inner wall to flange
        .close()
    )

    neck = neck_profile.revolve(360, (0, 0, 0), (0, 1, 0))
    flange = flange.union(neck)

    # 4. Through bore (pipe bore through entire flange)
    bore_depth = neck_length + flange_thickness + raised_face_height + 2
    bore_cut = (
        cq.Workplane("XY")
        .workplane(offset=-neck_length - 1)
        .circle(bore / 2)
        .extrude(bore_depth)
    )
    flange = flange.cut(bore_cut)

    # 5. Bolt holes
    bolt_holes = (
        cq.Workplane("XY")
        .workplane(offset=-1)
        .polarArray(bolt_circle / 2, 0, 360, num_bolts)
        .circle(bolt_hole_dia / 2)
        .extrude(flange_thickness + 2)
    )
    flange = flange.cut(bolt_holes)

    # 6. Edge fillets (optional, may fail on some geometries)
    try:
        flange = (
            flange.edges("|Z")
            .edges(cq.selectors.RadiusNthSelector(-1))
            .fillet(fillet_radius)
        )
    except Exception:
        # Skip fillet if geometry doesn't support it
        pass

    return flange


def get_flange_metadata(
    pressure_class: int = 150,
    nps: str = "2",
    bore_override: Optional[float] = None,
) -> dict:
    """
    Get metadata for a flange configuration.

    Returns a dictionary with all dimensions and calculated values
    suitable for BOM generation.
    """
    dims = get_flange_dimensions(pressure_class, nps)
    bore = bore_override if bore_override is not None else dims["bore"]

    return {
        "type": "weld_neck_flange",
        "standard": "ASME B16.5",
        "pressure_class": pressure_class,
        "nps": nps,
        "dn": dims["dn"],
        "dimensions": {
            "flange_od": dims["flange_od"],
            "flange_thickness": dims["flange_thickness"],
            "raised_face_od": dims["raised_face_od"],
            "raised_face_height": dims["raised_face_height"],
            "bolt_circle": dims["bolt_circle"],
            "num_bolts": dims["num_bolts"],
            "bolt_hole_dia": dims["bolt_hole_dia"],
            "hub_od": dims["hub_od"],
            "neck_length": dims["neck_length"],
            "pipe_od": dims["pipe_od"],
            "bore": bore,
        },
        "unit": "mm",
    }


def list_available_flanges() -> dict:
    """List all available flange configurations."""
    return {
        "standard": "ASME B16.5",
        "pressure_classes": PRESSURE_CLASSES,
        "sizes_by_class": AVAILABLE_SIZES,
    }
