"""
Marketplace controller for IriusRisk Content Manager API
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class FileData(BaseModel):
    """File data model for saving release notes"""
    filePath: str
    data: Dict[str, Any]


class SaveReleaseNotesRequest(BaseModel):
    """Request model for saving release notes"""
    files: List[FileData]
    basePath: str = None  # Optional base path where files should be saved


@router.post("/marketplace/save-release-notes")
async def save_release_notes(request: SaveReleaseNotesRequest) -> Dict[str, Any]:
    """
    Save release notes to JSON files.
    
    This endpoint receives file paths and their updated JSON data,
    and saves them back to the filesystem. Since we're working with
    relative paths from a folder selection, we need a base path.
    
    For now, this will save files relative to a configured export folder,
    or you can provide a basePath in the request.
    """
    try:
        saved_count = 0
        errors = []
        
        # If basePath is provided, use it; otherwise use OUTPUT_FOLDER
        from isra.src.ile.backend.app.configuration.constants import ILEConstants
        
        base_path = Path(request.basePath) if request.basePath else Path(ILEConstants.OUTPUT_FOLDER) / "release_notes"
        base_path.mkdir(parents=True, exist_ok=True)
        
        for file_data in request.files:
            try:
                # Reconstruct the file path
                file_path = base_path / file_data.filePath
                
                # Create parent directories if they don't exist
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the JSON data
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(file_data.data, f, indent=2, ensure_ascii=False)
                
                saved_count += 1
                logger.info(f"Saved release notes to {file_path}")
            except Exception as e:
                error_msg = f"Error saving {file_data.filePath}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        if errors:
            raise HTTPException(
                status_code=500,
                detail=f"Some files failed to save. Saved: {saved_count}/{len(request.files)}. Errors: {errors}"
            )
        
        return {
            "status": "success",
            "message": f"Successfully saved {saved_count} file(s)",
            "saved_count": saved_count
        }
        
    except Exception as e:
        logger.error(f"Error saving release notes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving release notes: {str(e)}")

