"""
Straight Pipe Assembly Generator

Creates a straight pipe assembly consisting of:
- Flange A (start)
- Pipe section A (if different sizes, before reducer)
- Concentric reducer (if different flange sizes)
- Pipe section B (if different sizes, after reducer)
- Flange B (end)

The assembly is oriented along the Z axis with Flange A at Z=0
(raised face pointing in +Z direction).
"""

import os
import sys
import math
from pathlib import Path

# Setup path for imports
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cadquery as cq
from typing import Optional
from cadquery import Compound
from generators.flanges import create_weld_neck_flange, get_flange_metadata
from generators.pipes import create_pipe_section_simple, get_pipe_metadata
from generators.reducers import create_concentric_reducer, get_reducer_metadata
from data.asme_b16_5 import get_flange_dimensions
from data.asme_b36_10 import get_pipe_dimensions
from data.asme_b16_9 import get_reducer_dimensions, get_reducer_length


def create_straight_assembly(
    # Flange parameters
    pressure_class: int = 150,
    nps: str = "2",
    # Different flange sizes (optional)
    nps_a: Optional[str] = None,
    nps_b: Optional[str] = None,
    # Pipe parameters
    pipe_schedule: str = "STD",
    face_to_face: float = 500.0,
    # Reducer position (0.0 = at flange A, 1.0 = at flange B, 0.5 = middle)
    reducer_position: float = 0.5,
    # Options
    welding_gap: float = 3.0,
    flange_a_class: Optional[int] = None,
    flange_b_class: Optional[int] = None,
) -> cq.Workplane:
    """
    Create a straight pipe assembly with two flanges.

    If nps_a and nps_b are different, a concentric reducer is included.

    Args:
        pressure_class: Default ASME pressure class for both flanges
        nps: Default nominal pipe size (used if nps_a/nps_b not specified)
        nps_a: Nominal pipe size for flange A (e.g., "4")
        nps_b: Nominal pipe size for flange B (e.g., "2")
        pipe_schedule: Pipe schedule (e.g., "STD", "40", "80")
        face_to_face: Distance between flange faces (mm)
        reducer_position: Position of reducer (0.0-1.0), relative to pipe length
        welding_gap: Gap between parts for welding (mm)
        flange_a_class: Override pressure class for flange A
        flange_b_class: Override pressure class for flange B

    Returns:
        CadQuery Workplane containing the complete assembly
    """
    # Resolve NPS for each flange
    size_a = nps_a if nps_a is not None else nps
    size_b = nps_b if nps_b is not None else nps

    # Resolve pressure classes
    class_a = flange_a_class if flange_a_class is not None else pressure_class
    class_b = flange_b_class if flange_b_class is not None else pressure_class

    # Check if reducer is needed
    needs_reducer = size_a != size_b

    # Get flange dimensions
    dims_a = get_flange_dimensions(class_a, size_a)
    dims_b = get_flange_dimensions(class_b, size_b)

    # Get pipe dimensions
    pipe_dims_a = get_pipe_dimensions(size_a, pipe_schedule)
    pipe_dims_b = get_pipe_dimensions(size_b, pipe_schedule)

    # Flange measurements
    flange_a_rf = dims_a["raised_face_height"]
    flange_a_thick = dims_a["flange_thickness"]
    flange_a_neck = dims_a["neck_length"]
    flange_a_total = flange_a_rf + flange_a_thick + flange_a_neck

    flange_b_rf = dims_b["raised_face_height"]
    flange_b_thick = dims_b["flange_thickness"]
    flange_b_neck = dims_b["neck_length"]
    flange_b_total = flange_b_rf + flange_b_thick + flange_b_neck

    # Get reducer dimensions if needed
    reducer_length = 0
    if needs_reducer:
        # Determine large and small ends
        if pipe_dims_a["od"] > pipe_dims_b["od"]:
            large_nps, small_nps = size_a, size_b
        else:
            large_nps, small_nps = size_b, size_a
        reducer_length = get_reducer_length(large_nps, small_nps)

    # Calculate available pipe space
    total_flange_space = flange_a_total + flange_b_total
    if needs_reducer:
        # Space for reducer plus 2 more welding gaps (4 total)
        min_required = total_flange_space + reducer_length + 4 * welding_gap + 50
        available_pipe_space = face_to_face - total_flange_space - reducer_length - 4 * welding_gap
    else:
        # Simple case: 2 welding gaps
        min_required = total_flange_space + 2 * welding_gap + 50
        available_pipe_space = face_to_face - total_flange_space - 2 * welding_gap

    if available_pipe_space < 0:
        raise ValueError(
            f"Face-to-face distance {face_to_face}mm is too short. "
            f"Minimum required: {min_required}mm"
        )

    # =========================================
    # Create components
    # =========================================
    parts = []

    # 1. Flange A at Z=0
    flange_a = create_weld_neck_flange(
        pressure_class=class_a,
        nps=size_a,
        bore_override=pipe_dims_a["id"],
        welding_gap=welding_gap,
    )
    flange_a = (
        flange_a
        .rotate((0, 0, 0), (1, 0, 0), 180)
        .translate((0, 0, flange_a_thick + flange_a_rf))
    )
    parts.append(flange_a)

    if needs_reducer:
        # Calculate pipe lengths based on reducer position
        # reducer_position: 0 = right after flange A, 1 = right before flange B
        pipe_a_length = available_pipe_space * reducer_position
        pipe_b_length = available_pipe_space * (1 - reducer_position)

        # Ensure minimum pipe lengths
        min_pipe_len = 20
        if pipe_a_length < min_pipe_len:
            pipe_a_length = min_pipe_len
            pipe_b_length = available_pipe_space - min_pipe_len
        if pipe_b_length < min_pipe_len:
            pipe_b_length = min_pipe_len
            pipe_a_length = available_pipe_space - min_pipe_len

        # 2. Pipe A (large diameter side)
        pipe_a_start = flange_a_total + welding_gap
        if pipe_a_length > 0:
            pipe_a = create_pipe_section_simple(
                od=pipe_dims_a["od"],
                id_=pipe_dims_a["id"],
                length=pipe_a_length,
            )
            pipe_a = pipe_a.translate((0, 0, pipe_a_start))
            parts.append(pipe_a)

        # 3. Reducer
        # Determine orientation based on which end is larger
        if pipe_dims_a["od"] > pipe_dims_b["od"]:
            # A is larger, reducer large end at flange A side
            reducer = create_concentric_reducer(
                large_nps=size_a,
                small_nps=size_b,
                large_schedule=pipe_schedule,
                small_schedule=pipe_schedule,
                welding_gap=welding_gap,
            )
            # Reducer: large at Z=0, small at Z=H
            # Position so large end connects to pipe A
            reducer_z = pipe_a_start + pipe_a_length + welding_gap
        else:
            # B is larger, need to flip reducer
            reducer = create_concentric_reducer(
                large_nps=size_b,
                small_nps=size_a,
                large_schedule=pipe_schedule,
                small_schedule=pipe_schedule,
                welding_gap=welding_gap,
            )
            # Flip reducer so small end is at flange A side
            reducer = reducer.rotate((0, 0, 0), (1, 0, 0), 180)
            reducer = reducer.translate((0, 0, reducer_length))
            reducer_z = pipe_a_start + pipe_a_length + welding_gap

        reducer = reducer.translate((0, 0, reducer_z))
        parts.append(reducer)

        # 4. Pipe B (small diameter side)
        pipe_b_start = reducer_z + reducer_length + welding_gap
        if pipe_b_length > 0:
            pipe_b = create_pipe_section_simple(
                od=pipe_dims_b["od"],
                id_=pipe_dims_b["id"],
                length=pipe_b_length,
            )
            pipe_b = pipe_b.translate((0, 0, pipe_b_start))
            parts.append(pipe_b)

    else:
        # Simple case: single pipe
        pipe_length = available_pipe_space
        pipe_z_start = flange_a_total + welding_gap
        pipe = create_pipe_section_simple(
            od=pipe_dims_a["od"],
            id_=pipe_dims_a["id"],
            length=pipe_length,
        )
        pipe = pipe.translate((0, 0, pipe_z_start))
        parts.append(pipe)

    # 5. Flange B at end
    flange_b = create_weld_neck_flange(
        pressure_class=class_b,
        nps=size_b,
        bore_override=pipe_dims_b["id"],
        welding_gap=welding_gap,
    )
    flange_b_z = face_to_face - flange_b_rf - flange_b_thick
    flange_b = flange_b.translate((0, 0, flange_b_z))
    parts.append(flange_b)

    # Combine all parts using Compound to avoid union issues
    solids = []
    for p in parts:
        for s in p.solids().vals():
            solids.append(s)

    assembly = cq.Workplane("XY").add(Compound.makeCompound(solids))

    return assembly


def get_straight_assembly_metadata(
    pressure_class: int = 150,
    nps: str = "2",
    nps_a: Optional[str] = None,
    nps_b: Optional[str] = None,
    pipe_schedule: str = "STD",
    face_to_face: float = 500.0,
    reducer_position: float = 0.5,
    welding_gap: float = 3.0,
    flange_a_class: Optional[int] = None,
    flange_b_class: Optional[int] = None,
) -> dict:
    """
    Get metadata for a straight assembly configuration.
    """
    # Resolve sizes and classes
    size_a = nps_a if nps_a is not None else nps
    size_b = nps_b if nps_b is not None else nps
    class_a = flange_a_class if flange_a_class is not None else pressure_class
    class_b = flange_b_class if flange_b_class is not None else pressure_class

    needs_reducer = size_a != size_b

    dims_a = get_flange_dimensions(class_a, size_a)
    dims_b = get_flange_dimensions(class_b, size_b)
    pipe_dims_a = get_pipe_dimensions(size_a, pipe_schedule)
    pipe_dims_b = get_pipe_dimensions(size_b, pipe_schedule)

    flange_a_total = dims_a["raised_face_height"] + dims_a["flange_thickness"] + dims_a["neck_length"]
    flange_b_total = dims_b["raised_face_height"] + dims_b["flange_thickness"] + dims_b["neck_length"]

    # Weight calculation helper
    def flange_weight(dims):
        vol = math.pi * ((dims["flange_od"]/2)**2 - (dims["bore"]/2)**2) * dims["flange_thickness"]
        vol += math.pi * ((dims["hub_od"]/2)**2 - (dims["bore"]/2)**2) * dims["neck_length"] * 0.7
        return vol * 7.85e-9

    def pipe_weight(od, id_, length):
        vol = math.pi * ((od/2)**2 - (id_/2)**2) * length
        return vol * 7.85e-9

    components = []
    total_weight = 0
    item = 1

    # Flange A
    weight_a = flange_weight(dims_a)
    total_weight += weight_a
    components.append({
        "item": item,
        "type": "weld_neck_flange",
        "description": f"Flange A - ASME B16.5 Class {class_a} NPS {size_a}",
        "standard": "ASME B16.5",
        "pressure_class": class_a,
        "nps": size_a,
        "dn": dims_a["dn"],
        "quantity": 1,
        "weight_kg": round(weight_a, 2),
    })
    item += 1

    if needs_reducer:
        # Determine large/small
        if pipe_dims_a["od"] > pipe_dims_b["od"]:
            large_nps, small_nps = size_a, size_b
        else:
            large_nps, small_nps = size_b, size_a

        reducer_len = get_reducer_length(large_nps, small_nps)
        available = face_to_face - flange_a_total - flange_b_total - reducer_len - 4 * welding_gap

        pipe_a_length = max(20, available * reducer_position)
        pipe_b_length = max(20, available * (1 - reducer_position))

        # Adjust if needed
        if pipe_a_length + pipe_b_length > available:
            pipe_a_length = available * reducer_position
            pipe_b_length = available - pipe_a_length

        # Pipe A
        weight_pa = pipe_weight(pipe_dims_a["od"], pipe_dims_a["id"], pipe_a_length)
        total_weight += weight_pa
        components.append({
            "item": item,
            "type": "pipe_section",
            "description": f"Pipe A - ASME B36.10 NPS {size_a} Sch {pipe_schedule}",
            "standard": "ASME B36.10",
            "nps": size_a,
            "schedule": pipe_schedule,
            "length_mm": round(pipe_a_length, 1),
            "quantity": 1,
            "weight_kg": round(weight_pa, 2),
        })
        item += 1

        # Reducer
        reducer_meta = get_reducer_metadata(large_nps, small_nps, pipe_schedule, pipe_schedule)
        total_weight += reducer_meta["weight_kg"]
        components.append({
            "item": item,
            "type": "concentric_reducer",
            "description": f"Reducer - ASME B16.9 NPS {large_nps} x {small_nps}",
            "standard": "ASME B16.9",
            "large_nps": large_nps,
            "small_nps": small_nps,
            "length_mm": reducer_len,
            "quantity": 1,
            "weight_kg": round(reducer_meta["weight_kg"], 2),
        })
        item += 1

        # Pipe B
        weight_pb = pipe_weight(pipe_dims_b["od"], pipe_dims_b["id"], pipe_b_length)
        total_weight += weight_pb
        components.append({
            "item": item,
            "type": "pipe_section",
            "description": f"Pipe B - ASME B36.10 NPS {size_b} Sch {pipe_schedule}",
            "standard": "ASME B36.10",
            "nps": size_b,
            "schedule": pipe_schedule,
            "length_mm": round(pipe_b_length, 1),
            "quantity": 1,
            "weight_kg": round(weight_pb, 2),
        })
        item += 1

    else:
        # Single pipe
        pipe_length = face_to_face - flange_a_total - flange_b_total - 2 * welding_gap
        weight_p = pipe_weight(pipe_dims_a["od"], pipe_dims_a["id"], pipe_length)
        total_weight += weight_p
        components.append({
            "item": item,
            "type": "pipe_section",
            "description": f"Pipe - ASME B36.10 NPS {size_a} Sch {pipe_schedule}",
            "standard": "ASME B36.10",
            "nps": size_a,
            "schedule": pipe_schedule,
            "length_mm": round(pipe_length, 1),
            "quantity": 1,
            "weight_kg": round(weight_p, 2),
        })
        item += 1

    # Flange B
    weight_b = flange_weight(dims_b)
    total_weight += weight_b
    components.append({
        "item": item,
        "type": "weld_neck_flange",
        "description": f"Flange B - ASME B16.5 Class {class_b} NPS {size_b}",
        "standard": "ASME B16.5",
        "pressure_class": class_b,
        "nps": size_b,
        "dn": dims_b["dn"],
        "quantity": 1,
        "weight_kg": round(weight_b, 2),
    })

    return {
        "type": "straight_assembly",
        "configuration": {
            "face_to_face": face_to_face,
            "nps_a": size_a,
            "nps_b": size_b,
            "has_reducer": needs_reducer,
            "reducer_position": reducer_position if needs_reducer else None,
            "welding_gap": welding_gap,
        },
        "components": components,
        "total_weight_kg": round(total_weight, 2),
        "unit": "mm",
    }
