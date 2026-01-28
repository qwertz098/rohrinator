"""
Elbow Pipe Assembly Generator

Creates an L-shaped pipe assembly consisting of:
- Flange A (start, horizontal)
- Pipe section A (horizontal)
- 90° elbow
- Pipe section B (vertical)
- Flange B (end, vertical)

The assembly is oriented with:
- Flange A at origin, facing +Z (horizontal leg along +Z)
- Elbow turns from +Z to +Y direction
- Flange B facing +Y (vertical leg along +Y)
"""

import sys
import math
from pathlib import Path
from typing import Optional, Literal

# Setup path for imports
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cadquery as cq
from generators.flanges import create_weld_neck_flange
from generators.pipes import create_pipe_section_simple
from generators.elbows import create_pipe_elbow, get_elbow_dimensions
from data.asme_b16_5 import get_flange_dimensions
from data.asme_b36_10 import get_pipe_dimensions


def create_elbow_assembly(
    # Flange parameters
    pressure_class: int = 150,
    nps: str = "2",
    # Pipe parameters
    pipe_schedule: str = "STD",
    # Dimensions
    leg_a_length: float = 300.0,  # Length of horizontal leg (flange face to elbow center)
    leg_b_length: float = 300.0,  # Length of vertical leg (elbow center to flange face)
    # Elbow parameters
    bend_radius_factor: Literal["2D", "3D", "5D"] = "3D",
    # Options
    welding_gap: float = 3.0,
) -> cq.Workplane:
    """
    Create an L-shaped pipe assembly with 90° elbow.

    The assembly is oriented with:
    - Flange A at Z=0, raised face pointing toward +Z
    - Horizontal pipe section along +Z axis
    - 90° elbow turning from +Z to +Y direction
    - Vertical pipe section along +Y axis
    - Flange B at top, raised face pointing toward +Y

    Args:
        pressure_class: ASME pressure class for flanges
        nps: Nominal pipe size
        pipe_schedule: Pipe schedule
        leg_a_length: Distance from Flange A face to elbow centerline (mm)
        leg_b_length: Distance from elbow centerline to Flange B face (mm)
        bend_radius_factor: Elbow bend radius ("2D", "3D", "5D")
        welding_gap: Gap between parts for welding (mm)

    Returns:
        CadQuery Workplane containing the complete assembly
    """
    # Get dimensions
    flange_dims = get_flange_dimensions(pressure_class, nps)
    pipe_dims = get_pipe_dimensions(nps, pipe_schedule)
    elbow_dims = get_elbow_dimensions(nps, pipe_schedule, 90.0, bend_radius_factor)

    # Flange dimensions
    rf_height = flange_dims["raised_face_height"]
    flange_thickness = flange_dims["flange_thickness"]
    neck_length = flange_dims["neck_length"]
    flange_total = rf_height + flange_thickness + neck_length

    # Elbow dimensions
    bend_radius = elbow_dims["bend_radius"]

    # Calculate pipe section lengths
    # Leg A: from flange A neck end to elbow inlet
    pipe_a_length = leg_a_length - flange_total - bend_radius - welding_gap
    # Leg B: from elbow outlet to flange B neck end
    pipe_b_length = leg_b_length - flange_total - bend_radius - welding_gap

    if pipe_a_length < 0:
        min_leg_a = flange_total + bend_radius + 2 * welding_gap + 50
        raise ValueError(f"Leg A length {leg_a_length}mm too short. Minimum: {min_leg_a}mm")
    if pipe_b_length < 0:
        min_leg_b = flange_total + bend_radius + 2 * welding_gap + 50
        raise ValueError(f"Leg B length {leg_b_length}mm too short. Minimum: {min_leg_b}mm")

    od = pipe_dims["od"]
    id_ = pipe_dims["id"]

    # =========================================
    # Create components
    # =========================================

    # 1. Flange A - at origin, RF pointing toward +Z
    flange_a = create_weld_neck_flange(
        pressure_class=pressure_class,
        nps=nps,
        bore_override=id_,
        welding_gap=welding_gap,
    )
    # Rotate so RF faces +Z and neck extends toward -Z
    # Default: RF at top (+Z side), neck at bottom (-Z)
    # We want: RF at Z=0 pointing +Z, neck extending -Z
    # Then flip so RF points +Z, neck goes toward +Z (into assembly)
    flange_a = flange_a.rotate((0, 0, 0), (1, 0, 0), 180)
    flange_a = flange_a.translate((0, 0, flange_thickness + rf_height))

    # 2. Pipe section A - horizontal, along +Z
    pipe_a_start = flange_total #+ welding_gap
    pipe_a = create_pipe_section_simple(od, id_, pipe_a_length)
    pipe_a = pipe_a.translate((0, 0, pipe_a_start))

    # 3. Elbow - at the bend point
    # Default elbow geometry (from elbows.py, revolved around Z):
    # - Inlet at (bend_radius, 0, 0) with pipe axis along X
    # - Outlet at (0, bend_radius, 0) with pipe axis along Y

    elbow = create_pipe_elbow(nps, pipe_schedule, 90.0, bend_radius_factor, od, id_)

    # We want elbow to connect:
    # - Inlet from pipe A coming along +Z axis
    # - Outlet to pipe B going along +Y axis

    # Rotate elbow so inlet aligns with +Z axis:
    # Rotate 90° around Y axis: inlet moves from +X to +Z
    #elbow = elbow.rotate((0, 0, 0), (0, 1, 0), 90)

    # Position elbow so inlet connects to pipe A end
    # After rotation: inlet is at (0, 0, bend_radius), outlet at (bend_radius, 0, 0)
    # We need inlet at Z = pipe_a_start + pipe_a_length + welding_gap
    elbow_inlet_z = pipe_a_start + pipe_a_length + welding_gap
    #elbow = elbow.translate((0, 0, elbow_inlet_z - bend_radius))
    elbow = elbow.translate((0, 0, leg_a_length - bend_radius))
    # 4. Pipe section B - along +X axis (after elbow rotation, outlet points toward +X)
    # Elbow outlet is at X = bend_radius after rotation
    elbow_outlet_x = bend_radius
    pipe_b_start_x = elbow_outlet_x + welding_gap
    pipe_b_start_z = leg_a_length
    pipe_b = create_pipe_section_simple(od, id_, pipe_b_length)
    # Rotate to align with X axis
    pipe_b = pipe_b.rotate((0, 0, 0), (0, 1, 0), 90)
    pipe_b = pipe_b.translate((pipe_b_start_x, 0, pipe_b_start_z))

    # 5. Flange B - at end, RF pointing toward +X
    flange_b = create_weld_neck_flange(
        pressure_class=pressure_class,
        nps=nps,
        bore_override=id_,
        welding_gap=welding_gap,
    )
    # Default flange has RF at top (+Z), neck at bottom
    # Rotate 90° around Y to point along +X
    flange_b = flange_b.rotate((0, 0, 0), (0, 1, 0), 90)
    flange_b_x = leg_b_length - flange_thickness - rf_height
    flange_b = flange_b.translate((flange_b_x, 0, pipe_b_start_z))

    # =========================================
    # Combine all parts using fuse (avoids clean issues)
    # =========================================
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from cadquery import Compound

    parts = [flange_a, pipe_a, elbow, pipe_b, flange_b]
    solids = []
    for p in parts:
        for s in p.solids().vals():
            solids.append(s)

    assembly = cq.Workplane("XY").add(Compound.makeCompound(solids))

    return assembly


def get_elbow_assembly_metadata(
    pressure_class: int = 150,
    nps: str = "2",
    pipe_schedule: str = "STD",
    leg_a_length: float = 300.0,
    leg_b_length: float = 300.0,
    bend_radius_factor: Literal["2D", "3D", "5D"] = "3D",
    welding_gap: float = 3.0,
) -> dict:
    """
    Get metadata for an elbow assembly configuration.
    """
    flange_dims = get_flange_dimensions(pressure_class, nps)
    pipe_dims = get_pipe_dimensions(nps, pipe_schedule)
    elbow_dims = get_elbow_dimensions(nps, pipe_schedule, 90.0, bend_radius_factor)

    rf_height = flange_dims["raised_face_height"]
    flange_thickness = flange_dims["flange_thickness"]
    neck_length = flange_dims["neck_length"]
    flange_total = rf_height + flange_thickness + neck_length
    bend_radius = elbow_dims["bend_radius"]

    pipe_a_length = leg_a_length - flange_total - bend_radius - 2 * welding_gap
    pipe_b_length = leg_b_length - flange_total - bend_radius - 2 * welding_gap

    # Weight calculations
    od = pipe_dims["od"]
    id_ = pipe_dims["id"]

    def pipe_weight(length):
        vol = math.pi * ((od/2)**2 - (id_/2)**2) * length
        return vol * 7.85e-9

    def flange_weight(dims):
        vol = math.pi * ((dims["flange_od"]/2)**2 - (dims["bore"]/2)**2) * dims["flange_thickness"]
        vol += math.pi * ((dims["hub_od"]/2)**2 - (dims["bore"]/2)**2) * dims["neck_length"] * 0.7
        return vol * 7.85e-9

    elbow_weight = pipe_weight(elbow_dims["arc_length"])

    return {
        "type": "elbow_assembly",
        "configuration": {
            "leg_a_length": leg_a_length,
            "leg_b_length": leg_b_length,
            "bend_radius_factor": bend_radius_factor,
            "welding_gap": welding_gap,
        },
        "components": [
            {
                "item": 1,
                "type": "weld_neck_flange",
                "description": f"Flange A - ASME B16.5 Class {pressure_class} NPS {nps}",
                "standard": "ASME B16.5",
                "pressure_class": pressure_class,
                "nps": nps,
                "dn": flange_dims["dn"],
                "quantity": 1,
                "weight_kg": round(flange_weight(flange_dims), 2),
            },
            {
                "item": 2,
                "type": "pipe_section",
                "description": f"Pipe A - ASME B36.10 NPS {nps} Sch {pipe_schedule}",
                "standard": "ASME B36.10",
                "nps": nps,
                "schedule": pipe_schedule,
                "length_mm": round(pipe_a_length, 1),
                "quantity": 1,
                "weight_kg": round(pipe_weight(pipe_a_length), 2),
            },
            {
                "item": 3,
                "type": "pipe_elbow",
                "description": f"90° Elbow {bend_radius_factor} - ASME B16.9 NPS {nps}",
                "standard": "ASME B16.9",
                "nps": nps,
                "angle": 90,
                "bend_radius_factor": bend_radius_factor,
                "quantity": 1,
                "weight_kg": round(elbow_weight, 2),
            },
            {
                "item": 4,
                "type": "pipe_section",
                "description": f"Pipe B - ASME B36.10 NPS {nps} Sch {pipe_schedule}",
                "standard": "ASME B36.10",
                "nps": nps,
                "schedule": pipe_schedule,
                "length_mm": round(pipe_b_length, 1),
                "quantity": 1,
                "weight_kg": round(pipe_weight(pipe_b_length), 2),
            },
            {
                "item": 5,
                "type": "weld_neck_flange",
                "description": f"Flange B - ASME B16.5 Class {pressure_class} NPS {nps}",
                "standard": "ASME B16.5",
                "pressure_class": pressure_class,
                "nps": nps,
                "dn": flange_dims["dn"],
                "quantity": 1,
                "weight_kg": round(flange_weight(flange_dims), 2),
            },
        ],
        "total_weight_kg": round(
            2 * flange_weight(flange_dims) + pipe_weight(pipe_a_length) +
            elbow_weight + pipe_weight(pipe_b_length), 2
        ),
        "unit": "mm",
    }
