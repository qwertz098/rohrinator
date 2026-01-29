"""
2D Drawing Generator

Creates 2D engineering drawings from 3D assemblies.
Outputs DXF format for CAD software and SVG for web preview.
"""

import sys
import math
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime

# Setup path for imports
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import ezdxf
from ezdxf import units
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import cadquery as cq


def get_assembly_bounds(assembly: cq.Workplane) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """Get bounding box of assembly."""
    bb = assembly.val().BoundingBox()
    return (bb.xmin, bb.ymin, bb.zmin), (bb.xmax, bb.ymax, bb.zmax)


def project_to_2d(assembly: cq.Workplane, direction: str = "front") -> List[dict]:
    """
    Project 3D assembly to 2D edges for a given view direction.

    Args:
        assembly: CadQuery workplane with the assembly
        direction: View direction - "front" (XZ), "top" (XY), "side" (YZ)

    Returns:
        List of edge dictionaries with start/end points
    """
    edges = []

    # Get bounding box
    bb = assembly.val().BoundingBox()

    # For simplified drawing, we'll create outline based on bounding box
    # and key features

    if direction == "front":
        # Front view - looking along Y axis (XZ plane)
        # Assembly is along Z axis, so front view shows length
        edges.append({
            "type": "line",
            "start": (bb.xmin, bb.zmin),
            "end": (bb.xmax, bb.zmin)
        })
        edges.append({
            "type": "line",
            "start": (bb.xmax, bb.zmin),
            "end": (bb.xmax, bb.zmax)
        })
        edges.append({
            "type": "line",
            "start": (bb.xmax, bb.zmax),
            "end": (bb.xmin, bb.zmax)
        })
        edges.append({
            "type": "line",
            "start": (bb.xmin, bb.zmax),
            "end": (bb.xmin, bb.zmin)
        })
        # Center line
        cx = (bb.xmin + bb.xmax) / 2
        edges.append({
            "type": "centerline",
            "start": (cx, bb.zmin - 10),
            "end": (cx, bb.zmax + 10)
        })

    elif direction == "top":
        # Top view - looking along Z axis (XY plane)
        edges.append({
            "type": "line",
            "start": (bb.xmin, bb.ymin),
            "end": (bb.xmax, bb.ymin)
        })
        edges.append({
            "type": "line",
            "start": (bb.xmax, bb.ymin),
            "end": (bb.xmax, bb.ymax)
        })
        edges.append({
            "type": "line",
            "start": (bb.xmax, bb.ymax),
            "end": (bb.xmin, bb.ymax)
        })
        edges.append({
            "type": "line",
            "start": (bb.xmin, bb.ymax),
            "end": (bb.xmin, bb.ymin)
        })
        # Center line
        cy = (bb.ymin + bb.ymax) / 2
        edges.append({
            "type": "centerline",
            "start": (bb.xmin - 10, cy),
            "end": (bb.xmax + 10, cy)
        })

    elif direction == "side":
        # Side view - looking along X axis (YZ plane)
        edges.append({
            "type": "line",
            "start": (bb.ymin, bb.zmin),
            "end": (bb.ymax, bb.zmin)
        })
        edges.append({
            "type": "line",
            "start": (bb.ymax, bb.zmin),
            "end": (bb.ymax, bb.zmax)
        })
        edges.append({
            "type": "line",
            "start": (bb.ymax, bb.zmax),
            "end": (bb.ymin, bb.zmax)
        })
        edges.append({
            "type": "line",
            "start": (bb.ymin, bb.zmax),
            "end": (bb.ymin, bb.zmin)
        })

    return edges


def create_drawing_dxf(
    assembly: cq.Workplane,
    metadata: dict,
    output_path: str,
    title: str = "Assembly Drawing",
    scale: float = 1.0,
) -> str:
    """
    Create a DXF drawing with orthographic views.

    Args:
        assembly: CadQuery workplane with the assembly
        metadata: Assembly metadata dict with components
        output_path: Path to save DXF file
        title: Drawing title
        scale: Drawing scale (1.0 = 1:1)

    Returns:
        Path to created DXF file
    """
    # Create DXF document
    doc = ezdxf.new('R2018', setup=True)
    doc.units = units.MM

    msp = doc.modelspace()

    # Get assembly bounds
    bb = assembly.val().BoundingBox()
    length = bb.zmax - bb.zmin  # Assembly along Z
    width = bb.xmax - bb.xmin
    height = bb.ymax - bb.ymin

    # Layout configuration
    margin = 50
    view_spacing = 80

    # Create layers
    doc.layers.add("OUTLINE", color=7)  # White
    doc.layers.add("CENTERLINE", color=1, linetype="CENTER")  # Red, center
    doc.layers.add("DIMENSION", color=3)  # Green
    doc.layers.add("TEXT", color=7)  # White
    doc.layers.add("TITLEBLOCK", color=5)  # Blue

    # =============================================
    # Front View (main view) - XZ projection
    # Looking along Y axis, shows length (Z) horizontal
    # =============================================
    front_origin = (margin, margin + height + view_spacing)

    # Draw outline rectangle (simplified)
    # Bottom
    msp.add_line(
        (front_origin[0], front_origin[1]),
        (front_origin[0] + length, front_origin[1]),
        dxfattribs={"layer": "OUTLINE"}
    )
    # Right
    msp.add_line(
        (front_origin[0] + length, front_origin[1]),
        (front_origin[0] + length, front_origin[1] + width),
        dxfattribs={"layer": "OUTLINE"}
    )
    # Top
    msp.add_line(
        (front_origin[0] + length, front_origin[1] + width),
        (front_origin[0], front_origin[1] + width),
        dxfattribs={"layer": "OUTLINE"}
    )
    # Left
    msp.add_line(
        (front_origin[0], front_origin[1] + width),
        (front_origin[0], front_origin[1]),
        dxfattribs={"layer": "OUTLINE"}
    )

    # Center line (horizontal through middle)
    cy = front_origin[1] + width / 2
    msp.add_line(
        (front_origin[0] - 15, cy),
        (front_origin[0] + length + 15, cy),
        dxfattribs={"layer": "CENTERLINE"}
    )

    # Add dimension - overall length
    dim = msp.add_linear_dim(
        base=(front_origin[0], front_origin[1] - 20),
        p1=(front_origin[0], front_origin[1]),
        p2=(front_origin[0] + length, front_origin[1]),
        dimstyle="EZDXF",
        dxfattribs={"layer": "DIMENSION"}
    )
    dim.render()

    # View label
    msp.add_text(
        "FRONT VIEW",
        height=5,
        dxfattribs={"layer": "TEXT"}
    ).set_placement((front_origin[0] + length/2, front_origin[1] - 40), align=ezdxf.enums.TextEntityAlignment.CENTER)

    # =============================================
    # Top View - XY projection (below front view)
    # =============================================
    top_origin = (margin, margin)

    # Draw circle (end view of pipe)
    center_x = top_origin[0] + height / 2
    center_y = top_origin[1] + height / 2

    # Outer circle (flange OD approximation)
    msp.add_circle(
        (center_x, center_y),
        radius=width / 2,
        dxfattribs={"layer": "OUTLINE"}
    )

    # Inner circle (bore)
    msp.add_circle(
        (center_x, center_y),
        radius=width / 4,
        dxfattribs={"layer": "OUTLINE"}
    )

    # Center lines
    msp.add_line(
        (center_x - width/2 - 10, center_y),
        (center_x + width/2 + 10, center_y),
        dxfattribs={"layer": "CENTERLINE"}
    )
    msp.add_line(
        (center_x, center_y - width/2 - 10),
        (center_x, center_y + width/2 + 10),
        dxfattribs={"layer": "CENTERLINE"}
    )

    # View label
    msp.add_text(
        "END VIEW",
        height=5,
        dxfattribs={"layer": "TEXT"}
    ).set_placement((center_x, top_origin[1] - 15), align=ezdxf.enums.TextEntityAlignment.CENTER)

    # =============================================
    # Title Block
    # =============================================
    tb_x = front_origin[0] + length + 40
    tb_y = margin
    tb_width = 120
    tb_height = 80

    # Title block outline
    msp.add_lwpolyline(
        [(tb_x, tb_y), (tb_x + tb_width, tb_y),
         (tb_x + tb_width, tb_y + tb_height), (tb_x, tb_y + tb_height), (tb_x, tb_y)],
        close=True,
        dxfattribs={"layer": "TITLEBLOCK"}
    )

    # Horizontal dividers
    msp.add_line((tb_x, tb_y + 20), (tb_x + tb_width, tb_y + 20), dxfattribs={"layer": "TITLEBLOCK"})
    msp.add_line((tb_x, tb_y + 40), (tb_x + tb_width, tb_y + 40), dxfattribs={"layer": "TITLEBLOCK"})
    msp.add_line((tb_x, tb_y + 60), (tb_x + tb_width, tb_y + 60), dxfattribs={"layer": "TITLEBLOCK"})

    # Title block text
    text_height = 3
    msp.add_text("ROHRINATOR", height=4, dxfattribs={"layer": "TEXT"}).set_placement(
        (tb_x + tb_width/2, tb_y + 70), align=ezdxf.enums.TextEntityAlignment.CENTER)

    msp.add_text(title, height=text_height, dxfattribs={"layer": "TEXT"}).set_placement(
        (tb_x + 5, tb_y + 50), align=ezdxf.enums.TextEntityAlignment.LEFT)

    config = metadata.get("configuration", {})
    msp.add_text(f"NPS: {config.get('nps_a', 'N/A')} x {config.get('nps_b', 'N/A')}",
                 height=text_height, dxfattribs={"layer": "TEXT"}).set_placement(
        (tb_x + 5, tb_y + 30), align=ezdxf.enums.TextEntityAlignment.LEFT)

    msp.add_text(f"Face-to-Face: {config.get('face_to_face', 'N/A')} mm",
                 height=text_height, dxfattribs={"layer": "TEXT"}).set_placement(
        (tb_x + 5, tb_y + 10), align=ezdxf.enums.TextEntityAlignment.LEFT)

    msp.add_text(f"Date: {datetime.now().strftime('%Y-%m-%d')}",
                 height=text_height, dxfattribs={"layer": "TEXT"}).set_placement(
        (tb_x + 5, tb_y + 2), align=ezdxf.enums.TextEntityAlignment.LEFT)

    # Save DXF
    doc.saveas(output_path)
    return output_path


def create_drawing_svg(
    assembly: cq.Workplane,
    metadata: dict,
    width: int = 800,
    height: int = 400,
) -> str:
    """
    Create an SVG preview of the 2D drawing.

    Args:
        assembly: CadQuery workplane with the assembly
        metadata: Assembly metadata dict
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG string
    """
    # Get assembly bounds
    bb = assembly.val().BoundingBox()
    length = bb.zmax - bb.zmin
    obj_width = bb.xmax - bb.xmin
    obj_height = bb.ymax - bb.ymin

    # Calculate scale to fit
    margin = 60
    available_width = width - 2 * margin - 150  # Space for end view
    available_height = height - 2 * margin

    scale_x = available_width / length if length > 0 else 1
    scale_y = available_height / obj_width if obj_width > 0 else 1
    scale = min(scale_x, scale_y, 1.0)  # Don't scale up

    # Scaled dimensions
    s_length = length * scale
    s_width = obj_width * scale

    # View positions
    front_x = margin
    front_y = margin + 30

    end_x = margin + s_length + 60
    end_y = front_y + s_width / 2
    end_r = min(s_width / 2, 50)

    config = metadata.get("configuration", {})
    face_to_face = config.get("face_to_face", length)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="background: #1a1a2e;">
  <defs>
    <style>
      .outline {{ stroke: #4dabf7; stroke-width: 2; fill: none; }}
      .centerline {{ stroke: #f56565; stroke-width: 1; stroke-dasharray: 10,5,2,5; fill: none; }}
      .dimension {{ stroke: #48bb78; stroke-width: 1; fill: none; }}
      .dim-text {{ fill: #48bb78; font-family: monospace; font-size: 12px; }}
      .label {{ fill: #888; font-family: sans-serif; font-size: 11px; }}
      .title {{ fill: #4dabf7; font-family: sans-serif; font-size: 14px; font-weight: bold; }}
    </style>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#48bb78"/>
    </marker>
  </defs>

  <!-- Front View -->
  <rect x="{front_x}" y="{front_y}" width="{s_length}" height="{s_width}" class="outline"/>

  <!-- Center line -->
  <line x1="{front_x - 15}" y1="{front_y + s_width/2}" x2="{front_x + s_length + 15}" y2="{front_y + s_width/2}" class="centerline"/>

  <!-- Overall dimension -->
  <line x1="{front_x}" y1="{front_y + s_width + 25}" x2="{front_x + s_length}" y2="{front_y + s_width + 25}" class="dimension" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
  <line x1="{front_x}" y1="{front_y + s_width + 5}" x2="{front_x}" y2="{front_y + s_width + 30}" class="dimension"/>
  <line x1="{front_x + s_length}" y1="{front_y + s_width + 5}" x2="{front_x + s_length}" y2="{front_y + s_width + 30}" class="dimension"/>
  <text x="{front_x + s_length/2}" y="{front_y + s_width + 45}" text-anchor="middle" class="dim-text">{face_to_face:.0f}</text>

  <!-- Front view label -->
  <text x="{front_x + s_length/2}" y="{front_y - 10}" text-anchor="middle" class="label">FRONT VIEW</text>

  <!-- End View (circle) -->
  <circle cx="{end_x + end_r}" cy="{end_y}" r="{end_r}" class="outline"/>
  <circle cx="{end_x + end_r}" cy="{end_y}" r="{end_r * 0.4}" class="outline"/>

  <!-- End view center lines -->
  <line x1="{end_x}" y1="{end_y}" x2="{end_x + end_r * 2}" y2="{end_y}" class="centerline"/>
  <line x1="{end_x + end_r}" y1="{end_y - end_r - 10}" x2="{end_x + end_r}" y2="{end_y + end_r + 10}" class="centerline"/>

  <!-- End view label -->
  <text x="{end_x + end_r}" y="{end_y + end_r + 30}" text-anchor="middle" class="label">END VIEW</text>

  <!-- Title -->
  <text x="{width - 10}" y="20" text-anchor="end" class="title">ROHRINATOR</text>
  <text x="{width - 10}" y="38" text-anchor="end" class="label">NPS {config.get('nps_a', '-')} x {config.get('nps_b', '-')}</text>
  <text x="{width - 10}" y="54" text-anchor="end" class="label">Scale: 1:{1/scale:.1f}</text>
</svg>'''

    return svg


# Test
if __name__ == "__main__":
    from models.straight import create_straight_assembly, get_straight_assembly_metadata

    print("Creating test assembly...")
    assembly = create_straight_assembly(nps_a="4", nps_b="2", face_to_face=500, reducer_position=0.5)
    metadata = get_straight_assembly_metadata(nps_a="4", nps_b="2", face_to_face=500, reducer_position=0.5)

    print("Creating DXF drawing...")
    create_drawing_dxf(assembly, metadata, "test_drawing.dxf", title="Test Assembly")
    print("Created test_drawing.dxf")

    print("Creating SVG preview...")
    svg = create_drawing_svg(assembly, metadata)
    with open("test_drawing.svg", "w") as f:
        f.write(svg)
    print("Created test_drawing.svg")
