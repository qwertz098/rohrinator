"""
Rohrinator FastAPI Application

REST API for generating 3D pipe assembly models.
"""

import os
import sys
import uuid
import tempfile
from pathlib import Path
from typing import Optional
from datetime import datetime

# Setup path for imports
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

import cadquery as cq

# Import generators (using absolute imports from rohrinator package)
from models.straight import create_straight_assembly, get_straight_assembly_metadata
from models.elbow import create_elbow_assembly, get_elbow_assembly_metadata
from generators.flanges import list_available_flanges
from generators.pipes import list_available_pipes

# Create FastAPI app
app = FastAPI(
    title="Rohrinator API",
    description="REST API for generating 3D pipe assembly models (flanges, pipes, fittings)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Storage for generated assemblies (in production, use proper storage)
STORAGE_DIR = Path(tempfile.gettempdir()) / "rohrinator"
STORAGE_DIR.mkdir(exist_ok=True)

# In-memory cache for assembly metadata
assembly_cache: dict = {}


# ============================================================
# Pydantic Models
# ============================================================

class StraightAssemblyRequest(BaseModel):
    """Request model for creating a straight pipe assembly."""

    # Project info
    project: Optional[str] = Field(None, description="Project name/number")
    designation: Optional[str] = Field(None, description="Assembly designation")
    description: Optional[str] = Field(None, description="Assembly description")

    # Flange parameters
    pressure_class: int = Field(150, description="ASME pressure class (150, 300, 600, 900, 1500, 2500)")
    nps: str = Field("2", description="Nominal pipe size (e.g., '2', '1/2', '1-1/4')")

    # Pipe parameters
    pipe_schedule: str = Field("STD", description="Pipe schedule (e.g., 'STD', '40', '80', 'XS')")
    face_to_face: float = Field(500.0, ge=100, le=10000, description="Face-to-face distance in mm")

    # Options
    welding_gap: float = Field(3.0, ge=0, le=10, description="Welding gap in mm")
    flange_a_class: Optional[int] = Field(None, description="Override pressure class for flange A")
    flange_b_class: Optional[int] = Field(None, description="Override pressure class for flange B")

    class Config:
        json_schema_extra = {
            "example": {
                "project": "Project-001",
                "designation": "SP-001",
                "description": "Straight pipe spool NPS 2 Class 150",
                "pressure_class": 150,
                "nps": "2",
                "pipe_schedule": "STD",
                "face_to_face": 500.0,
                "welding_gap": 3.0,
            }
        }


class ElbowAssemblyRequest(BaseModel):
    """Request model for creating an elbow (90°) pipe assembly."""

    # Project info
    project: Optional[str] = Field(None, description="Project name/number")
    designation: Optional[str] = Field(None, description="Assembly designation")
    description: Optional[str] = Field(None, description="Assembly description")

    # Flange parameters
    pressure_class: int = Field(150, description="ASME pressure class (150, 300, 600, 900, 1500, 2500)")
    nps: str = Field("2", description="Nominal pipe size (e.g., '2', '1/2', '1-1/4')")

    # Pipe parameters
    pipe_schedule: str = Field("STD", description="Pipe schedule (e.g., 'STD', '40', '80', 'XS')")

    # Dimensions
    leg_a_length: float = Field(400.0, ge=200, le=5000, description="Length of leg A (flange face to elbow center) in mm")
    leg_b_length: float = Field(400.0, ge=200, le=5000, description="Length of leg B (elbow center to flange face) in mm")

    # Elbow parameters
    bend_radius_factor: str = Field("3D", description="Elbow bend radius factor ('2D', '3D', '5D')")

    # Options
    welding_gap: float = Field(3.0, ge=0, le=10, description="Welding gap in mm")

    class Config:
        json_schema_extra = {
            "example": {
                "project": "Project-001",
                "designation": "EL-001",
                "description": "90° elbow spool NPS 2 Class 150",
                "pressure_class": 150,
                "nps": "2",
                "pipe_schedule": "STD",
                "leg_a_length": 400.0,
                "leg_b_length": 400.0,
                "bend_radius_factor": "3D",
                "welding_gap": 3.0,
            }
        }


class AssemblyResponse(BaseModel):
    """Response model for assembly creation."""

    id: str = Field(..., description="Unique assembly ID")
    created_at: str = Field(..., description="Creation timestamp")
    project: Optional[str] = None
    designation: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = Field(..., description="Assembly metadata including BOM")
    download_urls: dict = Field(..., description="URLs to download files")


class AvailableOptionsResponse(BaseModel):
    """Response model for available configuration options."""

    flanges: dict
    pipes: dict


# ============================================================
# API Endpoints
# ============================================================

@app.get("/", tags=["Info"])
async def root():
    """API root - basic info."""
    return {
        "name": "Rohrinator API",
        "version": "0.1.0",
        "description": "REST API for generating 3D pipe assembly models",
        "docs": "/docs",
    }


@app.get("/api/v1/options", response_model=AvailableOptionsResponse, tags=["Options"])
async def get_available_options():
    """Get available configuration options for flanges and pipes."""
    return {
        "flanges": list_available_flanges(),
        "pipes": list_available_pipes(),
    }


@app.post("/api/v1/assembly/straight", response_model=AssemblyResponse, tags=["Assembly"])
async def create_assembly_straight(request: StraightAssemblyRequest):
    """
    Create a straight pipe assembly.

    Generates a 3D model of a straight pipe with flanges at both ends.
    Returns assembly ID and metadata. Use the download endpoints to get
    STEP, STL, or BOM files.
    """
    # Generate unique ID
    assembly_id = str(uuid.uuid4())[:8]
    created_at = datetime.utcnow().isoformat() + "Z"

    try:
        # Generate the 3D model
        assembly = create_straight_assembly(
            pressure_class=request.pressure_class,
            nps=request.nps,
            pipe_schedule=request.pipe_schedule,
            face_to_face=request.face_to_face,
            welding_gap=request.welding_gap,
            flange_a_class=request.flange_a_class,
            flange_b_class=request.flange_b_class,
        )

        # Get metadata
        metadata = get_straight_assembly_metadata(
            pressure_class=request.pressure_class,
            nps=request.nps,
            pipe_schedule=request.pipe_schedule,
            face_to_face=request.face_to_face,
            welding_gap=request.welding_gap,
            flange_a_class=request.flange_a_class,
            flange_b_class=request.flange_b_class,
        )

        # Create storage directory for this assembly
        assembly_dir = STORAGE_DIR / assembly_id
        assembly_dir.mkdir(exist_ok=True)

        # Export STEP file
        step_path = assembly_dir / "assembly.step"
        cq.exporters.export(assembly, str(step_path), exportType="STEP")

        # Export STL file
        stl_path = assembly_dir / "assembly.stl"
        cq.exporters.export(assembly, str(stl_path), exportType="STL")

        # Store metadata in cache
        assembly_cache[assembly_id] = {
            "created_at": created_at,
            "project": request.project,
            "designation": request.designation,
            "description": request.description,
            "metadata": metadata,
            "step_path": str(step_path),
            "stl_path": str(stl_path),
        }

        return AssemblyResponse(
            id=assembly_id,
            created_at=created_at,
            project=request.project,
            designation=request.designation,
            description=request.description,
            metadata=metadata,
            download_urls={
                "step": f"/api/v1/assembly/{assembly_id}/step",
                "stl": f"/api/v1/assembly/{assembly_id}/stl",
                "bom": f"/api/v1/assembly/{assembly_id}/bom",
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate assembly: {str(e)}")


@app.post("/api/v1/assembly/elbow", response_model=AssemblyResponse, tags=["Assembly"])
async def create_assembly_elbow(request: ElbowAssemblyRequest):
    """
    Create an elbow (90°) pipe assembly.

    Generates a 3D model of an L-shaped pipe with flanges at both ends
    and a 90° elbow in the middle. Returns assembly ID and metadata.
    Use the download endpoints to get STEP, STL, or BOM files.
    """
    # Generate unique ID
    assembly_id = str(uuid.uuid4())[:8]
    created_at = datetime.utcnow().isoformat() + "Z"

    try:
        # Generate the 3D model
        assembly = create_elbow_assembly(
            pressure_class=request.pressure_class,
            nps=request.nps,
            pipe_schedule=request.pipe_schedule,
            leg_a_length=request.leg_a_length,
            leg_b_length=request.leg_b_length,
            bend_radius_factor=request.bend_radius_factor,
            welding_gap=request.welding_gap,
        )

        # Get metadata
        metadata = get_elbow_assembly_metadata(
            pressure_class=request.pressure_class,
            nps=request.nps,
            pipe_schedule=request.pipe_schedule,
            leg_a_length=request.leg_a_length,
            leg_b_length=request.leg_b_length,
            bend_radius_factor=request.bend_radius_factor,
            welding_gap=request.welding_gap,
        )

        # Create storage directory for this assembly
        assembly_dir = STORAGE_DIR / assembly_id
        assembly_dir.mkdir(exist_ok=True)

        # Export STEP file
        step_path = assembly_dir / "assembly.step"
        cq.exporters.export(assembly, str(step_path), exportType="STEP")

        # Export STL file
        stl_path = assembly_dir / "assembly.stl"
        cq.exporters.export(assembly, str(stl_path), exportType="STL")

        # Store metadata in cache
        assembly_cache[assembly_id] = {
            "created_at": created_at,
            "project": request.project,
            "designation": request.designation,
            "description": request.description,
            "metadata": metadata,
            "step_path": str(step_path),
            "stl_path": str(stl_path),
        }

        return AssemblyResponse(
            id=assembly_id,
            created_at=created_at,
            project=request.project,
            designation=request.designation,
            description=request.description,
            metadata=metadata,
            download_urls={
                "step": f"/api/v1/assembly/{assembly_id}/step",
                "stl": f"/api/v1/assembly/{assembly_id}/stl",
                "bom": f"/api/v1/assembly/{assembly_id}/bom",
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate elbow assembly: {str(e)}")


@app.get("/api/v1/assembly/{assembly_id}/step", tags=["Download"])
async def download_step(assembly_id: str):
    """Download STEP file for an assembly."""
    if assembly_id not in assembly_cache:
        raise HTTPException(status_code=404, detail=f"Assembly {assembly_id} not found")

    step_path = assembly_cache[assembly_id]["step_path"]
    if not os.path.exists(step_path):
        raise HTTPException(status_code=404, detail="STEP file not found")

    designation = assembly_cache[assembly_id].get("designation") or assembly_id
    filename = f"{designation}.step"

    return FileResponse(
        path=step_path,
        filename=filename,
        media_type="application/step",
    )


@app.get("/api/v1/assembly/{assembly_id}/stl", tags=["Download"])
async def download_stl(assembly_id: str):
    """Download STL file for an assembly (for 3D preview)."""
    if assembly_id not in assembly_cache:
        raise HTTPException(status_code=404, detail=f"Assembly {assembly_id} not found")

    stl_path = assembly_cache[assembly_id]["stl_path"]
    if not os.path.exists(stl_path):
        raise HTTPException(status_code=404, detail="STL file not found")

    return FileResponse(
        path=stl_path,
        filename=f"{assembly_id}.stl",
        media_type="model/stl",
    )


@app.get("/api/v1/assembly/{assembly_id}/bom", tags=["Download"])
async def get_bom(assembly_id: str):
    """Get Bill of Materials for an assembly."""
    if assembly_id not in assembly_cache:
        raise HTTPException(status_code=404, detail=f"Assembly {assembly_id} not found")

    cached = assembly_cache[assembly_id]

    return JSONResponse({
        "assembly_id": assembly_id,
        "project": cached.get("project"),
        "designation": cached.get("designation"),
        "description": cached.get("description"),
        "created_at": cached["created_at"],
        "bom": cached["metadata"]["components"],
        "total_weight_kg": cached["metadata"]["total_weight_kg"],
    })


@app.get("/api/v1/assembly/{assembly_id}", tags=["Assembly"])
async def get_assembly_info(assembly_id: str):
    """Get information about an existing assembly."""
    if assembly_id not in assembly_cache:
        raise HTTPException(status_code=404, detail=f"Assembly {assembly_id} not found")

    cached = assembly_cache[assembly_id]

    return AssemblyResponse(
        id=assembly_id,
        created_at=cached["created_at"],
        project=cached.get("project"),
        designation=cached.get("designation"),
        description=cached.get("description"),
        metadata=cached["metadata"],
        download_urls={
            "step": f"/api/v1/assembly/{assembly_id}/step",
            "stl": f"/api/v1/assembly/{assembly_id}/stl",
            "bom": f"/api/v1/assembly/{assembly_id}/bom",
        },
    )


# ============================================================
# Health Check
# ============================================================

@app.get("/health", tags=["Info"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "cadquery_available": True}
