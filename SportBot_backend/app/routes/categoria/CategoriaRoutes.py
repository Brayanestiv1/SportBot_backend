from fastapi import APIRouter, HTTPException, status
from typing import List
from app.controllers.categoria.CategoriaController import CategoriaController
from app.models.categoria.CategoriaModel import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def create_categoria(categoria: CategoriaCreate):
    """Create a new categoria"""
    try:
        return CategoriaController.create_categoria(categoria)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[CategoriaResponse])
def get_all_categorias():
    """Get all categorias"""
    return CategoriaController.get_all_categorias()

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def get_categoria(categoria_id: int):
    """Get categoria by ID"""
    categoria = CategoriaController.get_categoria_by_id(categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria not found")
    return categoria

@router.put("/{categoria_id}", response_model=CategoriaResponse)
def update_categoria(categoria_id: int, categoria: CategoriaUpdate):
    """Update categoria"""
    updated_categoria = CategoriaController.update_categoria(categoria_id, categoria)
    if not updated_categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria not found")
    return updated_categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(categoria_id: int):
    """Delete categoria"""
    if not CategoriaController.delete_categoria(categoria_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria not found")
