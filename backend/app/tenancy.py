"""Multi-tenant SaaS models (Phase 1 — additive future layer).

Hierarchy: Organization -> Workspace -> Business -> Users -> financial data.
Current queries keep using `user_id` unchanged; these models + indexes
prepare the migration without breaking any existing behavior.

Roles: owner, admin, accountant, ca, employee, client, viewer.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models import PyObjectId


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    CA = "ca"
    EMPLOYEE = "employee"
    CLIENT = "client"
    VIEWER = "viewer"


MUTATING_ROLES = {Role.OWNER, Role.ADMIN, Role.ACCOUNTANT, Role.CA, Role.EMPLOYEE}


class Organization(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    plan: str = "free"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"


class Workspace(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    organization_id: PyObjectId
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"


class Business(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    workspace_id: PyObjectId
    name: str
    business_type: Optional[str] = None
    gstin: Optional[str] = None
    financial_year: str = "2024-25"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"


class Membership(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    organization_id: PyObjectId
    user_id: PyObjectId
    role: Role = Role.VIEWER
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"


class AuditEvent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    action: str
    user_id: Optional[PyObjectId] = None
    organization_id: Optional[PyObjectId] = None
    object: Optional[str] = None
    meta: dict = {}
    request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"


class Notification(BaseModel):
    """In-app notification model. Delivery stays in-app/browser (no paid providers)."""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    title: str
    body: Optional[str] = None
    severity: str = "info"
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
