#!/usr/bin/env python3
"""
Generate example STEP files to verify the generators work correctly.

Run from the rohrinator directory:
    python generate_examples.py
"""

import os
import sys
import math

# Setup path for direct execution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import cadquery as cq

# Import data directly (avoiding relative imports)
from data.asme_b16_5 import get_flange_dimensions, PRESSURE_CLASSES, AVAILABLE_SIZES
from data.asme_b36_10 import get_pipe_dimensions, get_available_schedules

# Create output directories
PARTS_DIR = os.path.join(SCRIPT_DIR, "parts")
EXAMPLES_DIR = os.path.join(SCRIPT_DIR, "examples")

os.makedirs(PARTS_DIR, exist_ok=True)
os.makedirs(EXAMPLES_DIR, exist_ok=True)


# ============================================================
# Flange Generator (inline to avoid import issues)
# ============================================================

def create_weld_neck_flange(pressure_class=150, nps="2", bore_override=None, welding_gap=0.0):
    """Create an ASME B16.5 weld neck flange."""
    dims = get_flange_dimensions(pressure_class, nps)

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
    fillet_radius = min(3.0, flange_thickness * 0.1)

    # Flange body
    flange = cq.Workplane("XY").circle(flange_od / 2).extrude(flange_thickness)

    # Raised face
    raised_face = (
        cq.Workplane("XY")
        .workplane(offset=flange_thickness)
        .circle(raised_face_od / 2)
        .extrude(raised_face_height)
    )
    flange = flange.union(raised_face)

    # Tapered neck
    neck_profile = (
        cq.Workplane("XZ")
        .moveTo(hub_od / 2, 0)
        .lineTo(hub_od / 2, -5)
        .lineTo(pipe_od / 2, -(neck_length - 10))
        .lineTo(pipe_od / 2, -neck_length + welding_gap)
        .lineTo(bore / 2, -neck_length + welding_gap)
        .lineTo(bore / 2, 0)
        .close()
    )
    neck = neck_profile.revolve(360, (0, 0, 0), (0, 1, 0))
    flange = flange.union(neck)

    # Through bore
    bore_depth = neck_length + flange_thickness + raised_face_height + 2
    bore_cut = (
        cq.Workplane("XY")
        .workplane(offset=-neck_length - 1)
        .circle(bore / 2)
        .extrude(bore_depth)
    )
    flange = flange.cut(bore_cut)

    # Bolt holes
    bolt_holes = (
        cq.Workplane("XY")
        .workplane(offset=-1)
        .polarArray(bolt_circle / 2, 0, 360, num_bolts)
        .circle(bolt_hole_dia / 2)
        .extrude(flange_thickness + 2)
    )
    flange = flange.cut(bolt_holes)

    return flange


def get_flange_metadata(pressure_class=150, nps="2", bore_override=None):
    """Get metadata for a flange configuration."""
    dims = get_flange_dimensions(pressure_class, nps)
    bore = bore_override if bore_override is not None else dims["bore"]
    return {
        "type": "weld_neck_flange",
        "standard": "ASME B16.5",
        "pressure_class": pressure_class,
        "nps": nps,
        "dn": dims["dn"],
        "dimensions": {**dims, "bore": bore},
        "unit": "mm",
    }


# ============================================================
# Pipe Generator (inline)
# ============================================================

def create_pipe_section(nps="2", schedule="STD", length=500.0, od_override=None, id_override=None):
    """Create a pipe section."""
    dims = get_pipe_dimensions(nps, schedule)
    od = od_override if od_override is not None else dims["od"]
    id_ = id_override if id_override is not None else dims["id"]

    pipe = cq.Workplane("XY").circle(od / 2).circle(id_ / 2).extrude(length)
    return pipe


def get_pipe_metadata(nps="2", schedule="STD", length=500.0, od_override=None, id_override=None):
    """Get metadata for a pipe section."""
    dims = get_pipe_dimensions(nps, schedule)
    od = od_override if od_override is not None else dims["od"]
    id_ = id_override if id_override is not None else dims["id"]
    wall = (od - id_) / 2

    volume_mm3 = math.pi * ((od/2)**2 - (id_/2)**2) * length
    volume_m3 = volume_mm3 * 1e-9
    weight_kg = volume_m3 * 7850

    return {
        "type": "pipe_section",
        "standard": "ASME B36.10",
        "nps": nps,
        "schedule": schedule,
        "dimensions": {"od": od, "id": id_, "wall_thickness": round(wall, 2), "length": length},
        "weight_kg": round(weight_kg, 3),
        "unit": "mm",
    }


# ============================================================
# Straight Assembly Generator (inline)
# ============================================================

def create_straight_assembly(pressure_class=150, nps="2", pipe_schedule="STD",
                             face_to_face=500.0, welding_gap=3.0):
    """Create a straight pipe assembly with two flanges."""
    dims = get_flange_dimensions(pressure_class, nps)
    pipe_dims = get_pipe_dimensions(nps, pipe_schedule)

    flange_rf_height = dims["raised_face_height"]
    flange_thickness = dims["flange_thickness"]
    flange_neck_length = dims["neck_length"]

    # Calculate pipe length
    # Face-to-face minus full flange lengths (RF + thickness + neck) and weld gaps
    flange_total = flange_rf_height + flange_thickness + flange_neck_length
    pipe_length = face_to_face - 2 * flange_total - 2 * welding_gap
    if pipe_length < 0:
        raise ValueError(f"Face-to-face {face_to_face}mm too short (min: {2 * flange_total + 2 * welding_gap + 50}mm)")

    # Create Flange A (rotated so RF faces +Z)
    flange_a = create_weld_neck_flange(pressure_class, nps, pipe_dims["id"], welding_gap)
    flange_a = flange_a.rotate((0, 0, 0), (1, 0, 0), 180)
    flange_a = flange_a.translate((0, 0, flange_thickness + flange_rf_height))

    # Create Flange B (RF faces -Z)
    flange_b = create_weld_neck_flange(pressure_class, nps, pipe_dims["id"], welding_gap)
    flange_b_z = face_to_face - flange_rf_height - flange_thickness
    flange_b = flange_b.translate((0, 0, flange_b_z))

    # Create pipe section - starts after flange A neck end + weld gap
    pipe_z_start = flange_thickness + flange_rf_height + flange_neck_length + welding_gap
    pipe = create_pipe_section(nps, pipe_schedule, pipe_length, pipe_dims["od"], pipe_dims["id"])
    pipe = pipe.translate((0, 0, pipe_z_start))

    # Combine
    assembly = flange_a.union(pipe).union(flange_b)
    return assembly


def get_assembly_metadata(pressure_class=150, nps="2", pipe_schedule="STD",
                          face_to_face=500.0, welding_gap=3.0):
    """Get metadata for an assembly."""
    dims = get_flange_dimensions(pressure_class, nps)
    pipe_dims = get_pipe_dimensions(nps, pipe_schedule)
    flange_total = dims["raised_face_height"] + dims["flange_thickness"] + dims["neck_length"]
    pipe_length = face_to_face - 2 * flange_total - 2 * welding_gap

    return {
        "type": "straight_assembly",
        "face_to_face": face_to_face,
        "components": [
            {"item": 1, "description": f"Flange A - Class {pressure_class} NPS {nps}"},
            {"item": 2, "description": f"Pipe - NPS {nps} Sch {pipe_schedule} L={pipe_length:.0f}mm"},
            {"item": 3, "description": f"Flange B - Class {pressure_class} NPS {nps}"},
        ],
    }


# ============================================================
# Example Generators
# ============================================================

def generate_flange_examples():
    """Generate example flanges in various sizes."""
    print("\n=== Generating Flange Examples ===")
    sizes = ["1/2", "1", "2", "4", "6", "8"]

    for nps in sizes:
        print(f"\nGenerating Class 150 NPS {nps} flange...")
        try:
            flange = create_weld_neck_flange(pressure_class=150, nps=nps)
            metadata = get_flange_metadata(pressure_class=150, nps=nps)

            filename = f"flange_class150_nps{nps.replace('/', '-')}.step"
            filepath = os.path.join(PARTS_DIR, filename)
            cq.exporters.export(flange, filepath, exportType="STEP")

            print(f"  Created: {filename}")
            print(f"  DN: {metadata['dn']}")
            print(f"  Flange OD: {metadata['dimensions']['flange_od']} mm")
            print(f"  Bolt holes: {metadata['dimensions']['num_bolts']}x Ø{metadata['dimensions']['bolt_hole_dia']} mm")
        except Exception as e:
            print(f"  ERROR: {e}")

    return True


def generate_pipe_examples():
    """Generate example pipe sections."""
    print("\n=== Generating Pipe Section Examples ===")
    configs = [("2", "STD", 300), ("2", "80", 300), ("4", "STD", 500), ("6", "40", 500)]

    for nps, schedule, length in configs:
        print(f"\nGenerating NPS {nps} Sch {schedule} pipe (L={length}mm)...")
        try:
            pipe = create_pipe_section(nps=nps, schedule=schedule, length=length)
            metadata = get_pipe_metadata(nps=nps, schedule=schedule, length=length)

            filename = f"pipe_nps{nps}_sch{schedule}_L{length}.step"
            filepath = os.path.join(PARTS_DIR, filename)
            cq.exporters.export(pipe, filepath, exportType="STEP")

            print(f"  Created: {filename}")
            print(f"  OD: {metadata['dimensions']['od']} mm, Wall: {metadata['dimensions']['wall_thickness']} mm")
            print(f"  Weight: {metadata['weight_kg']} kg")
        except Exception as e:
            print(f"  ERROR: {e}")

    return True


def generate_elbow_examples():
    """Generate example elbow assemblies."""
    print("\n=== Generating Elbow Assembly Examples ===")

    from data.asme_b36_10 import PIPE_OD

    def create_pipe_elbow(nps="2", schedule="STD", angle=90.0, bend_radius_factor="3D", od_override=None, id_override=None, welding_gap=3.0):
        """Create a pipe elbow with 37.5° weld prep chamfers."""
        dims = get_pipe_dimensions(nps, schedule)
        od = od_override if od_override is not None else dims["od"]
        id_ = id_override if id_override is not None else dims["id"]

        r_pipe = od / 2
        r_inner = id_ / 2
        wall = r_pipe - r_inner

        nominal_od = PIPE_OD[nps]
        factor_map = {"2D": 2.0, "3D": 3.0, "5D": 5.0}
        factor = factor_map.get(bend_radius_factor, 3.0)
        r_bend = nominal_od * factor

        # Chamfer parameters: 37.5° bevel with root face
        chamfer_angle = 37.5
        root_face = min(1.6, wall * 0.2)
        chamfer_depth = wall - root_face
        chamfer_height = chamfer_depth * math.tan(math.radians(chamfer_angle))

        # Create arc path
        if angle == 90.0:
            path = cq.Workplane("XZ").radiusArc((r_bend, r_bend), r_bend)
        else:
            end_x = r_bend * math.sin(math.radians(angle))
            end_z = r_bend * (1 - math.cos(math.radians(angle)))
            path = cq.Workplane("XZ").radiusArc((end_x, end_z), r_bend)

        # Sweep profiles
        outer = cq.Workplane("XY").circle(r_pipe).sweep(path, isFrenet=True)
        inner = cq.Workplane("XY").circle(r_inner).sweep(path, isFrenet=True)
        elbow = outer.cut(inner)

        # Inlet chamfer (at origin)
        chamfer_inlet = (
            cq.Workplane("XY")
            .circle(r_pipe + 1)
            .circle(r_inner + root_face)
            .extrude(-chamfer_height - welding_gap / 2)
        )
        bevel_inlet = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -welding_gap / 2))
            .circle(r_pipe)
            .workplane(offset=-chamfer_height)
            .circle(r_inner + root_face)
            .loft()
        )
        elbow = elbow.cut(chamfer_inlet).union(bevel_inlet)

        # Outlet chamfer (at r_bend, 0, r_bend for 90°)
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
            elbow = elbow.cut(chamfer_outlet).union(bevel_outlet)

        return elbow

    def get_elbow_dimensions(nps, schedule, angle, bend_radius_factor):
        dims = get_pipe_dimensions(nps, schedule)
        nominal_od = PIPE_OD[nps]
        factor_map = {"2D": 2.0, "3D": 3.0, "5D": 5.0}
        factor = factor_map.get(bend_radius_factor, 3.0)
        bend_radius = nominal_od * factor  # Centerline bend radius = factor × nominal diameter
        arc_length = 2 * math.pi * bend_radius * (angle / 360)
        return {"od": dims["od"], "id": dims["id"], "bend_radius": bend_radius, "arc_length": arc_length}

    def create_pipe_section_simple(od, id_, length):
        return cq.Workplane("XY").circle(od / 2).circle(id_ / 2).extrude(length)

    def create_elbow_assembly(pressure_class=150, nps="2", pipe_schedule="STD",
                              leg_a_length=300.0, leg_b_length=300.0,
                              bend_radius_factor="3D", welding_gap=3.0):
        """Create an L-shaped pipe assembly with 90° elbow."""
        from cadquery import Compound

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

        if pipe_a_length < 0 or pipe_b_length < 0:
            raise ValueError(f"Leg lengths too short for this configuration")

        od = pipe_dims["od"]
        id_ = pipe_dims["id"]

        # Flange A
        flange_a = create_weld_neck_flange(pressure_class, nps, id_, welding_gap)
        flange_a = flange_a.rotate((0, 0, 0), (1, 0, 0), 180)
        flange_a = flange_a.translate((0, 0, flange_thickness + rf_height))

        # Pipe A
        pipe_a_start = flange_total + welding_gap
        pipe_a = create_pipe_section_simple(od, id_, pipe_a_length)
        pipe_a = pipe_a.translate((0, 0, pipe_a_start))

        # Elbow with 37.5° chamfers
        elbow = create_pipe_elbow(nps, pipe_schedule, 90.0, bend_radius_factor, od, id_, welding_gap)
        elbow = elbow.rotate((0, 0, 0), (0, 1, 0), 90)
        elbow_inlet_z = pipe_a_start + pipe_a_length + welding_gap
        elbow = elbow.translate((0, 0, elbow_inlet_z - bend_radius))

        # Pipe B
        pipe_b_start_x = bend_radius + welding_gap
        pipe_b = create_pipe_section_simple(od, id_, pipe_b_length)
        pipe_b = pipe_b.rotate((0, 0, 0), (0, 1, 0), 90)
        pipe_b = pipe_b.translate((pipe_b_start_x, 0, elbow_inlet_z))

        # Flange B
        flange_b = create_weld_neck_flange(pressure_class, nps, id_, welding_gap)
        flange_b = flange_b.rotate((0, 0, 0), (0, 1, 0), 90)
        flange_b_x = pipe_b_start_x + pipe_b_length + welding_gap
        flange_b = flange_b.translate((flange_b_x, 0, elbow_inlet_z))

        parts = [flange_a, pipe_a, elbow, pipe_b, flange_b]
        solids = []
        for p in parts:
            for s in p.solids().vals():
                solids.append(s)
        assembly = cq.Workplane("XY").add(Compound.makeCompound(solids))
        return assembly

    configs = [
        {"nps": "2", "pressure_class": 150, "leg_a": 500, "leg_b": 500, "bend_radius_factor": "3D"},
        {"nps": "4", "pressure_class": 150, "leg_a": 700, "leg_b": 800, "bend_radius_factor": "3D"},
        {"nps": "2", "pressure_class": 150, "leg_a": 600, "leg_b": 600, "bend_radius_factor": "5D"},
    ]

    for i, cfg in enumerate(configs, 1):
        nps, pc = cfg["nps"], cfg["pressure_class"]
        leg_a, leg_b = cfg["leg_a"], cfg["leg_b"]
        brf = cfg["bend_radius_factor"]
        print(f"\nGenerating Elbow Assembly {i}: NPS {nps} Class {pc} {brf}...")
        try:
            assembly = create_elbow_assembly(pc, nps, "STD", leg_a, leg_b, brf)

            filename = f"elbow_nps{nps}_class{pc}_{brf.lower()}.step"
            filepath = os.path.join(EXAMPLES_DIR, filename)
            cq.exporters.export(assembly, filepath, exportType="STEP")

            stl_filepath = os.path.join(EXAMPLES_DIR, f"elbow_nps{nps}_class{pc}_{brf.lower()}.stl")
            cq.exporters.export(assembly, stl_filepath, exportType="STL")

            print(f"  Created: {filename}")
            print(f"  Leg A: {leg_a}mm, Leg B: {leg_b}mm, Bend radius: {brf}")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    return True


def generate_assembly_examples():
    """Generate example straight assemblies."""
    print("\n=== Generating Straight Assembly Examples ===")
    configs = [
        {"nps": "2", "pressure_class": 150, "face_to_face": 500, "pipe_schedule": "STD"},
        {"nps": "2", "pressure_class": 150, "face_to_face": 1000, "pipe_schedule": "STD"},
        {"nps": "4", "pressure_class": 150, "face_to_face": 800, "pipe_schedule": "40"},
        {"nps": "6", "pressure_class": 150, "face_to_face": 1200, "pipe_schedule": "STD"},
    ]

    for i, cfg in enumerate(configs, 1):
        nps, pc, ftf, sch = cfg["nps"], cfg["pressure_class"], cfg["face_to_face"], cfg["pipe_schedule"]
        print(f"\nGenerating Assembly {i}: NPS {nps} Class {pc} FTF={ftf}mm...")
        try:
            assembly = create_straight_assembly(pc, nps, sch, ftf)
            metadata = get_assembly_metadata(pc, nps, sch, ftf)

            filename = f"straight_nps{nps}_class{pc}_ftf{ftf}.step"
            filepath = os.path.join(EXAMPLES_DIR, filename)
            cq.exporters.export(assembly, filepath, exportType="STEP")

            stl_filepath = os.path.join(EXAMPLES_DIR, f"straight_nps{nps}_class{pc}_ftf{ftf}.stl")
            cq.exporters.export(assembly, stl_filepath, exportType="STL")

            print(f"  Created: {filename}")
            for comp in metadata['components']:
                print(f"    - {comp['description']}")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    return True


def main():
    print("=" * 60)
    print("ROHRINATOR - Example Generator")
    print("=" * 60)

    generate_flange_examples()
    generate_pipe_examples()
    generate_assembly_examples()
    generate_elbow_examples()

    print("\n" + "=" * 60)
    print("Examples generated!")
    print(f"\nParts: {PARTS_DIR}")
    print(f"Assemblies: {EXAMPLES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
