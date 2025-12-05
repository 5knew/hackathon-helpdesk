"""
Pydantic schemas for request/response validation
"""
from .ticket import TicketCreate, TicketResponse, TicketUpdate
from .user import UserCreate, UserResponse
from .category import CategoryCreate, CategoryResponse
from .department import DepartmentCreate, DepartmentResponse
from .operator import OperatorCreate, OperatorResponse

__all__ = [
    "TicketCreate",
    "TicketResponse",
    "TicketUpdate",
    "UserCreate",
    "UserResponse",
    "CategoryCreate",
    "CategoryResponse",
    "DepartmentCreate",
    "DepartmentResponse",
    "OperatorCreate",
    "OperatorResponse",
]

