from fastapi import APIRouter, HTTPException, status
from typing import List
from app.controllers.usuario.UsuarioController import UsuarioController
from app.models.usuario.UsuarioModel import UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario: UsuarioCreate):
    """Create a new usuario"""
    try:
        return UsuarioController.create_usuario(usuario)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[UsuarioResponse])
def get_all_usuarios():
    """Get all usuarios"""
    return UsuarioController.get_all_usuarios()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def get_usuario(usuario_id: int):
    """Get usuario by ID"""
    usuario = UsuarioController.get_usuario_by_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(usuario_id: int, usuario: UsuarioUpdate):
    """Update usuario"""
    updated_usuario = UsuarioController.update_usuario(usuario_id, usuario)
    if not updated_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
    return updated_usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(usuario_id: int):
    """Delete usuario"""
    if not UsuarioController.delete_usuario(usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
