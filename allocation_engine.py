"""
Allocation Engine for Dynamic Resource Allocation System
Implements core scheduling logic from resource_allocation_system_design.md Section 2
"""

import pandas as pd
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
import math
from models import *


class AllocationEngine:
    """
    Core allocation engine that assigns operators, machines, and materials to work orders
    Primary objective: Minimize idle time while respecting all constraints
    """
    
    def __init__(self):
        self.operators: Dict[str, Operator] = {}
        self.machines: Dict[str, Machine] = {}
        self.materials: Dict[str, Material] = {}
        self.work_orders: Dict[str, WorkOrder] = {}
        self.last_reallocation_time: Dict[str, datetime] = {}
        
        # Configuration parameters
        self.stability_buffer_minutes = 15
        self.min_improvement_threshold = 0.10  # 10% improvement required for reallocation
        self.idle_time_threshold_minutes = 5
        
    def calculate_distance(self, location1: str, location2: str) -> float:
        """
        Calculate distance between locations
        In production, this would use actual coordinates or facility layout
        """
        if location1 == location2:
            return 0.0
        # Simplified: different zones have fixed distance
        return 10.0
    
    def calculate_allocation_score(
        self, 
        work_order: WorkOrder, 
        operator: Operator, 
        machine: Machine
    ) -> float:
        """
        Calculate allocation score based on weighted factors:
        - Skill match quality (40%)
        - Proximity factor (30%)
        - Machine efficiency (20%)
        - Cost optimization (10%)
        
        Returns: Score between 0 and 1 (higher is better)
        """
        
        # 1. Skill match quality (average skill level / 5)
        skill_levels = [
            operator.skill_levels.get(skill, 0) 
            for skill in work_order.required_skills
        ]
        skill_match_quality = (sum(skill_levels) / len(skill_levels) / 5.0) if skill_levels else 0
        
        # 2. Proximity factor (minimize distance between operator-machine-material)
        max_distance = 100.0  # Configurable maximum distance
        operator_machine_distance = self.calculate_distance(operator.location, machine.location)
        machine_wo_distance = self.calculate_distance(machine.location, work_order.location)
        avg_distance = (operator_machine_distance + machine_wo_distance) / 2
        proximity_factor = 1 - min(avg_distance / max_distance, 1.0)
        
        # 3. Machine efficiency (based on cycle time)
        max_cycle_time = 120  # minutes
        machine_efficiency = 1 - (machine.cycle_time / max_cycle_time) if machine.cycle_time else 0.5
        machine_efficiency = max(0, min(machine_efficiency, 1))
        
        # 4. Cost optimization
        max_cost = 100.0  # per hour (configurable)
        total_cost = operator.hourly_cost + machine.operating_cost_per_hour
        cost_optimization = 1 - min(total_cost / max_cost, 1.0)
        
        # Weighted score calculation
        score = (
            0.4 * skill_match_quality +
            0.3 * proximity_factor +
            0.2 * machine_efficiency +
            0.1 * cost_optimization
        )
        
        return score
    
    def check_hard_constraints(
        self, 
        work_order: WorkOrder, 
        operator: Operator, 
        machine: Machine
    ) -> Tuple[bool, str]:
        """
        Validate all hard constraints that must be satisfied
        Returns: (is_valid, reason)
        """
        
        # 1. Skill Matching: Operator must possess ALL required skills
        for skill in work_order.required_skills:
            if skill not in operator.skills:
                return False, f"Operator missing required skill: {skill}"
        
        # 2. Machine Capability: Machine must have the required capability
        if work_order.required_machine_capability not in machine.capabilities:
            return False, "Machine lacks required capability"
        
        # 3. Material Availability: All materials must be available
        for mat_req in work_order.required_materials:
            material = self.materials.get(mat_req.material_id)
            if not material:
                return False, f"Material not found: {mat_req.material_id}"
            
            available = material.quantity_available - material.quantity_reserved
            if available < mat_req.quantity:
                return False, f"Insufficient material: {mat_req.material_id} (need {mat_req.quantity}, have {available})"
        
        # 4. Resource Availability: Resources must be available
        if operator.current_status != OperatorStatus.AVAILABLE:
            return False, f"Operator not available (status: {operator.current_status.value})"
        
        if machine.current_status != MachineStatus.IDLE:
            return False, f"Machine not idle (status: {machine.current_status.value})"
        
        return True, "All constraints satisfied"
    
    def prioritize_work_orders(self) -> List[WorkOrder]:
        """
        Sort work orders by: Priority (desc) → Deadline (asc) → Duration (asc)
        Returns: Prioritized list of pending work orders
        """
        pending_orders = [
            wo for wo in self.work_orders.values() 
            if wo.status == WorkOrderStatus.PENDING
        ]
        
        if not pending_orders:
            return []
        
        # Convert to DataFrame for efficient sorting
        df = pd.DataFrame([{
            'work_order': wo,
            'priority': wo.priority,
            'deadline': wo.deadline,
            'duration': wo.estimated_duration
        } for wo in pending_orders])
        
        # Sort by priority (desc), deadline (asc), duration (asc)
        df = df.sort_values(
            by=['priority', 'deadline', 'duration'],
            ascending=[False, True, True]
        )
        
        return df['work_order'].tolist()
    
    def find_best_allocation(
        self, 
        work_order: WorkOrder
    ) -> Optional[Tuple[Operator, Machine, float]]:
        """
        Find best operator-machine pair for work order
        Returns: (operator, machine, score) or None if no valid allocation
        """
        best_score = -1
        best_allocation = None
        
        # Get available resources
        available_operators = [
            op for op in self.operators.values() 
            if op.current_status == OperatorStatus.AVAILABLE
        ]
        idle_machines = [
            m for m in self.machines.values() 
            if m.current_status == MachineStatus.IDLE
        ]
        
        # Try all combinations
        for operator in available_operators:
            for machine in idle_machines:
                # Check hard constraints
                valid, reason = self.check_hard_constraints(work_order, operator, machine)
                if not valid:
                    continue
                
                # Calculate score for valid allocation
                score = self.calculate_allocation_score(work_order, operator, machine)
                
                if score > best_score:
                    best_score = score
                    best_allocation = (operator, machine, score)
        
        return best_allocation
    
    def allocate_resources(self, work_order_id: str) -> bool:
        """
        Allocate resources to a specific work order
        Returns: True if allocation successful, False otherwise
        """
        work_order = self.work_orders.get(work_order_id)
        if not work_order:
            print(f"✗ Work order {work_order_id} not found")
            return False
        
        # Find best allocation
        allocation = self.find_best_allocation(work_order)
        if not allocation:
            work_order.status = WorkOrderStatus.BLOCKED
            print(f"✗ WO-{work_order_id} blocked - no valid allocation found")
            return False
        
        operator, machine, score = allocation
        
        # Reserve materials
        for mat_req in work_order.required_materials:
            material = self.materials[mat_req.material_id]
            material.quantity_reserved += mat_req.quantity
        
        # Update assignments
        work_order.assigned_operator = operator.operator_id
        work_order.assigned_machine = machine.machine_id
        work_order.status = WorkOrderStatus.IN_PROGRESS
        work_order.start_time = datetime.now()
        
        operator.current_status = OperatorStatus.ASSIGNED
        operator.current_work_order = work_order_id
        
        machine.current_status = MachineStatus.RUNNING
        machine.current_work_order = work_order_id
        
        # Track reallocation time
        self.last_reallocation_time[work_order_id] = datetime.now()
        
        print(f"✓ Allocated WO-{work_order_id}: {operator.name} + {machine.name} (Score: {score:.2f})")
        
        return True
    
    def should_reallocate(self, work_order: WorkOrder) -> bool:
        """
        Check if work order should be reallocated based on reallocation rules
        """
        # Don't reallocate if >50% complete
        if work_order.progress > 50:
            return False
        
        # Don't reallocate if last reallocation was <15 minutes ago
        if work_order.work_order_id in self.last_reallocation_time:
            time_since_last = (datetime.now() - self.last_reallocation_time[work_order.work_order_id]).seconds / 60
            if time_since_last < self.stability_buffer_minutes:
                return False
        
        return True
    
    def process_allocations(self) -> Dict[str, any]:
        """
        Main allocation process - allocate resources to all pending work orders
        Returns: Dictionary with allocation statistics
        """
        prioritized_orders = self.prioritize_work_orders()
        
        results = {
            'allocated': 0,
            'blocked': 0,
            'total': len(prioritized_orders)
        }
        
        print(f"\n🔄 Processing {len(prioritized_orders)} work orders...")
        print("-" * 60)
        
        for work_order in prioritized_orders:
            if self.allocate_resources(work_order.work_order_id):
                results['allocated'] += 1
            else:
                results['blocked'] += 1
        
        return results
    
    def get_resource_summary(self) -> Dict:
        """Get summary of resource states"""
        return {
            'operators': {
                'total': len(self.operators),
                'available': sum(1 for op in self.operators.values() if op.current_status == OperatorStatus.AVAILABLE),
                'assigned': sum(1 for op in self.operators.values() if op.current_status == OperatorStatus.ASSIGNED),
            },
            'machines': {
                'total': len(self.machines),
                'idle': sum(1 for m in self.machines.values() if m.current_status == MachineStatus.IDLE),
                'running': sum(1 for m in self.machines.values() if m.current_status == MachineStatus.RUNNING),
            },
            'work_orders': {
                'total': len(self.work_orders),
                'pending': sum(1 for wo in self.work_orders.values() if wo.status == WorkOrderStatus.PENDING),
                'in_progress': sum(1 for wo in self.work_orders.values() if wo.status == WorkOrderStatus.IN_PROGRESS),
                'completed': sum(1 for wo in self.work_orders.values() if wo.status == WorkOrderStatus.COMPLETED),
                'blocked': sum(1 for wo in self.work_orders.values() if wo.status == WorkOrderStatus.BLOCKED),
            }
        }
