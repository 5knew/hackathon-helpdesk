"""
Templates router - управление шаблонами ответов
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from database import get_db
from schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse
from models.template import Template
from models.category import Category
from models.user import User

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=List[TemplateResponse])
def list_templates(
    category_id: Optional[UUID] = Query(None, description="Фильтр по категории"),
    category_name: Optional[str] = Query(None, description="Фильтр по названию категории"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    db: Session = Depends(get_db)
):
    """
    Получает список шаблонов с фильтрацией
    """
    query = db.query(Template)
    
    if category_id:
        query = query.filter(Template.category_id == category_id)
    elif category_name:
        category = db.query(Category).filter(Category.name.ilike(f"%{category_name}%")).first()
        if category:
            query = query.filter(Template.category_id == category.id)
        else:
            return []
    
    if is_active is not None:
        query = query.filter(Template.is_active == is_active)
    
    templates = query.order_by(Template.name.asc()).all()
    
    result = []
    for template in templates:
        category_name = None
        if template.category_id:
            category = db.query(Category).filter(Category.id == template.category_id).first()
            if category:
                category_name = category.name
        
        result.append(TemplateResponse(
            id=str(template.id),
            name=template.name,
            category_id=str(template.category_id) if template.category_id else None,
            category_name=category_name,
            content=template.content,
            is_active=template.is_active,
            created_by=str(template.created_by) if template.created_by else None,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat()
        ))
    
    return result


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получает шаблон по ID
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    category_name = None
    if template.category_id:
        category = db.query(Category).filter(Category.id == template.category_id).first()
        if category:
            category_name = category.name
    
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        category_id=str(template.category_id) if template.category_id else None,
        category_name=category_name,
        content=template.content,
        is_active=template.is_active,
        created_by=str(template.created_by) if template.created_by else None,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )


@router.post("", response_model=TemplateResponse)
def create_template(
    template_data: TemplateCreate,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """
    Создает новый шаблон
    """
    # Получаем пользователя из токена (если есть)
    user_id = None
    if authorization:
        try:
            from routers.auth import active_tokens
            if authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
            else:
                token = authorization
            
            token_data = active_tokens.get(token)
            if token_data:
                user_id = token_data["user_id"]
                if isinstance(user_id, str):
                    try:
                        user_id = UUID(user_id)
                    except ValueError:
                        user_id = None
        except Exception as e:
            print(f"Error getting user from token: {e}")
    
    # Проверяем category_id, если указан
    category_id = None
    if template_data.category_id:
        try:
            category_id = UUID(template_data.category_id)
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category_id format")
    
    template = Template(
        name=template_data.name,
        category_id=category_id,
        content=template_data.content,
        created_by=user_id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    category_name = None
    if template.category_id:
        category = db.query(Category).filter(Category.id == template.category_id).first()
        if category:
            category_name = category.name
    
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        category_id=str(template.category_id) if template.category_id else None,
        category_name=category_name,
        content=template.content,
        is_active=template.is_active,
        created_by=str(template.created_by) if template.created_by else None,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: UUID,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновляет шаблон
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template_data.name is not None:
        template.name = template_data.name
    if template_data.content is not None:
        template.content = template_data.content
    if template_data.is_active is not None:
        template.is_active = template_data.is_active
    if template_data.category_id is not None:
        if template_data.category_id:
            try:
                category_id = UUID(template_data.category_id)
                category = db.query(Category).filter(Category.id == category_id).first()
                if not category:
                    raise HTTPException(status_code=404, detail="Category not found")
                template.category_id = category_id
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid category_id format")
        else:
            template.category_id = None
    
    from datetime import datetime
    template.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(template)
    
    category_name = None
    if template.category_id:
        category = db.query(Category).filter(Category.id == template.category_id).first()
        if category:
            category_name = category.name
    
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        category_id=str(template.category_id) if template.category_id else None,
        category_name=category_name,
        content=template.content,
        is_active=template.is_active,
        created_by=str(template.created_by) if template.created_by else None,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )


@router.delete("/{template_id}")
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Удаляет шаблон
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully", "template_id": str(template_id)}

