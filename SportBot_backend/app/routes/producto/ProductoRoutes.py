from fastapi import APIRouter, HTTPException, status
from typing import List
from app.controllers.producto.ProductoController import ProductoController
from app.models.producto.ProductoModel import ProductoCreate, ProductoUpdate, ProductoResponse

router = APIRouter(prefix="/productos", tags=["productos"])

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def create_producto(producto: ProductoCreate):
    """Create a new producto"""
    try:
        return ProductoController.create_producto(producto)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[ProductoResponse])
def get_all_productos():
    """Get all productos"""
    return ProductoController.get_all_productos()

@router.get("/{producto_id}", response_model=ProductoResponse)
def get_producto(producto_id: int):
    """Get producto by ID"""
    producto = ProductoController.get_producto_by_id(producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto not found")
    return producto

@router.get("/categoria/{categoria_id}", response_model=List[ProductoResponse])
def get_productos_by_categoria(categoria_id: int):
    """Get productos by categoria"""
    return ProductoController.get_productos_by_categoria(categoria_id)

@router.put("/{producto_id}", response_model=ProductoResponse)
def update_producto(producto_id: int, producto: ProductoUpdate):
    """Update producto"""
    updated_producto = ProductoController.update_producto(producto_id, producto)
    if not updated_producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto not found")
    return updated_producto

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(producto_id: int):
    """Delete producto"""
    if not ProductoController.delete_producto(producto_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto not found")
