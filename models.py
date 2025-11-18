"""
Data models for the Dynamic Resource Allocation System
Based on resource_allocation_system_design.md
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class OperatorStatus(Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    BREAK = "break"
    UNAVAILABLE = "unavailable"


class MachineStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    MAINTENANCE = "maintenance"
    BREAKDOWN = "breakdown"


class WorkOrderStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class Operator:
    """Operator data model with skills and availability"""
    operator_id: str
    name: str
    skills: List[str]
    skill_levels: Dict[str, int]  # skill: level (1-5)
    current_status: OperatorStatus
    current_work_order: Optional[str] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None
    location: str = ""
    hourly_cost: float = 0.0


@dataclass
class Machine:
    """Machine data model with capabilities and status"""
    machine_id: str
    name: str
    capabilities: List[str]
    current_status: MachineStatus
    current_work_order: Optional[str] = None
    location: str = ""
    cycle_time: int = 0  # minutes
    maintenance_schedule: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    operating_cost_per_hour: float = 0.0


@dataclass
class MaterialRequirement:
    """Material requirement for a work order"""
    material_id: str
    quantity: float


@dataclass
class Material:
    """Material inventory data model"""
    material_id: str
    name: str
    quantity_available: float
    quantity_reserved: float
    location: str
    unit_of_measure: str
    reorder_point: float
    expected_delivery: Optional[datetime] = None
    cost_per_unit: float = 0.0


@dataclass
class WorkOrder:
    """Work order with requirements and assignments"""
    work_order_id: str
    priority: int  # 1-10, 10=highest
    required_skills: List[str]
    required_machine_capability: str
    required_materials: List[MaterialRequirement]
    estimated_duration: int  # minutes
    deadline: datetime
    status: WorkOrderStatus
    assigned_operator: Optional[str] = None
    assigned_machine: Optional[str] = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    location: str = ""
    progress: float = 0.0  # 0-100%
