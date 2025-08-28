from fastapi import APIRouter, HTTPException, status
from typing import List
from app.controllers.promocion.PromocionController import PromocionController
from app.models.promocion.PromocionModel import PromocionCreate, PromocionUpdate, PromocionResponse

router = APIRouter(prefix="/promociones", tags=["promociones"])

@router.post("/", response_model=PromocionResponse, status_code=status.HTTP_201_CREATED)
def create_promocion(promocion: PromocionCreate):
    """Create a new promocion"""
    try:
        return PromocionController.create_promocion(promocion)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[PromocionResponse])
def get_all_promociones():
    """Get all promociones"""
    return PromocionController.get_all_promociones()

@router.get("/{promocion_id}", response_model=PromocionResponse)
def get_promocion(promocion_id: int):
    """Get promocion by ID"""
    promocion = PromocionController.get_promocion_by_id(promocion_id)
    if not promocion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion not found")
    return promocion

@router.put("/{promocion_id}", response_model=PromocionResponse)
def update_promocion(promocion_id: int, promocion: PromocionUpdate):
    """Update promocion"""
    updated_promocion = PromocionController.update_promocion(promocion_id, promocion)
    if not updated_promocion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion not found")
    return updated_promocion

@router.delete("/{promocion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promocion(promocion_id: int):
    """Delete promocion"""
    if not PromocionController.delete_promocion(promocion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promocion not found")
