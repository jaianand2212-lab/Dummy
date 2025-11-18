"""
Event Handler for Real-Time Event Processing
Implements event handling logic from resource_allocation_system_design.md Section 3
"""

from typing import Dict, List
from datetime import datetime, timedelta
from models import *
from allocation_engine import AllocationEngine
import heapq


class EventPriority:
    """Event priority levels for processing queue"""
    CRITICAL = 1
    SAFETY = 1
    MATERIAL_SHORTAGE = 2
    OPERATOR_CHANGE = 3
    ROUTINE = 4


class Event:
    """Event object for priority queue"""
    def __init__(self, priority: int, event_type: str, data: Dict):
        self.priority = priority
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()
    
    def __lt__(self, other):
        return self.priority < other.priority


class EventHandler:
    """
    Handles real-time events and triggers reallocations
    Processing rate: Up to 50 events/second
    """
    
    def __init__(self, allocation_engine: AllocationEngine):
        self.engine = allocation_engine
        self.event_queue = []
        self.event_log = []
        
    def add_event(self, priority: int, event_type: str, data: Dict):
        """Add event to priority queue"""
        event = Event(priority, event_type, data)
        heapq.heappush(self.event_queue, event)
        self.event_log.append({
            'timestamp': event.timestamp,
            'type': event_type,
            'priority': priority,
            'data': data
        })
    
    def handle_machine_breakdown(self, machine_id: str):
        """
        Handle machine breakdown event
        Steps:
        1. Mark machine as breakdown
        2. Identify affected work order
        3. Find alternative machine
        4. Reallocate or block work order
        """
        print(f"\n🔴 CRITICAL: Machine breakdown detected - {machine_id}")
        print("-" * 60)
        
        machine = self.engine.machines.get(machine_id)
        if not machine:
            print(f"✗ Machine {machine_id} not found")
            return
        
        # Mark machine as breakdown
        machine.current_status = MachineStatus.BREAKDOWN
        print(f"  → Machine {machine.name} marked as BREAKDOWN")
        
        # Find affected work order
        if machine.current_work_order:
            work_order = self.engine.work_orders[machine.current_work_order]
            operator_id = work_order.assigned_operator
            
            print(f"  → Affected work order: {work_order.work_order_id}")
            print(f"  → Calculating remaining work time...")
            
            # Deallocate resources
            work_order.assigned_machine = None
            work_order.status = WorkOrderStatus.BLOCKED
            
            # Try to find alternative machine
            alternative = self.engine.find_best_allocation(work_order)
            
            if alternative:
                new_operator, new_machine, score = alternative
                print(f"  ✓ Alternative found: Machine {new_machine.name}")
                
                # If different operator needed, free current operator
                if operator_id and operator_id != new_operator.operator_id:
                    old_operator = self.engine.operators[operator_id]
                    old_operator.current_status = OperatorStatus.AVAILABLE
                    old_operator.current_work_order = None
                    print(f"  → Released operator {old_operator.name}")
                
                # Reallocate to new machine
                self.engine.allocate_resources(work_order.work_order_id)
            else:
                print(f"  ✗ No alternative machine available")
                print(f"  → Work order {work_order.work_order_id} BLOCKED")
                
                # Free the operator for other work
                if operator_id:
                    operator = self.engine.operators[operator_id]
                    operator.current_status = OperatorStatus.AVAILABLE
                    operator.current_work_order = None
                    print(f"  → Released operator {operator.name}")
                    
                    # Try to assign operator to another work order
                    print(f"  → Attempting to reassign operator to other work...")
                    self.engine.process_allocations()
    
    def handle_machine_maintenance(self, machine_id: str, duration_minutes: int = 60):
        """Handle scheduled machine maintenance"""
        print(f"\n🔵 Scheduled maintenance: {machine_id} ({duration_minutes} min)")
        
        machine = self.engine.machines.get(machine_id)
        if not machine:
            return
        
        machine.current_status = MachineStatus.MAINTENANCE
        machine.last_maintenance = datetime.now()
        print(f"  → Machine {machine.name} in maintenance mode")
    
    def handle_operator_available(self, operator_id: str):
        """
        Handle operator becoming available
        Steps:
        1. Update operator status
        2. Try to allocate to pending work orders
        """
        operator = self.engine.operators.get(operator_id)
        if not operator:
            return
        
        print(f"\n✓ Operator available: {operator.name}")
        operator.current_status = OperatorStatus.AVAILABLE
        operator.current_work_order = None
        
        # Try to allocate to pending work orders
        pending_count = sum(1 for wo in self.engine.work_orders.values() 
                          if wo.status == WorkOrderStatus.PENDING)
        
        if pending_count > 0:
            print(f"  → Attempting allocation to {pending_count} pending work orders...")
            self.engine.process_allocations()
    
    def handle_work_order_completion(self, work_order_id: str):
        """
        Handle work order completion
        Steps:
        1. Mark work order as completed
        2. Calculate efficiency metrics
        3. Release materials
        4. Free resources
        """
        work_order = self.engine.work_orders.get(work_order_id)
        if not work_order:
            return
        
        print(f"\n✓ Work order completed: {work_order_id}")
        print("-" * 60)
        
        work_order.status = WorkOrderStatus.COMPLETED
        work_order.completion_time = datetime.now()
        work_order.progress = 100.0
        
        # Calculate efficiency
        if work_order.start_time:
            actual_duration = (work_order.completion_time - work_order.start_time).seconds / 60
         #dummy   
            if actual_duration > 0:
                efficiency = (work_order.estimated_duration / actual_duration) * 100
            else:
                # If no actual duration recorded (immediate completion), assume 100% efficiency
                efficiency = 100.0
            
            on_time = "✓" if work_order.completion_time <= work_order.deadline else "✗"
            print(f"  → Duration: {actual_duration:.1f} min (estimated: {work_order.estimated_duration} min)")
            print(f"  → Efficiency: {efficiency:.1f}%")
            print(f"  → On-time: {on_time}")
        
        # Release materials
        for mat_req in work_order.required_materials:
            material = self.engine.materials[mat_req.material_id]
            material.quantity_reserved -= mat_req.quantity
            material.quantity_available -= mat_req.quantity
        print(f"  → Materials released and consumed")
        
        # Free resources
        if work_order.assigned_operator:
            self.handle_operator_available(work_order.assigned_operator)
        
        if work_order.assigned_machine:
            machine = self.engine.machines[work_order.assigned_machine]
            machine.current_status = MachineStatus.IDLE
            machine.current_work_order = None
            print(f"  → Machine {machine.name} now IDLE")
    
    def handle_material_shortage(self, material_id: str):
        """
        Handle material shortage event
        Steps:
        1. Identify affected work orders
        2. Block affected work orders
        3. Free resources for reallocation
        """
        print(f"\n🔴 CRITICAL: Material shortage - {material_id}")
        print("-" * 60)
        
        material = self.engine.materials.get(material_id)
        if not material:
            return
        
        # Find affected work orders
        affected_orders = []
        for wo in self.engine.work_orders.values():
            for mat_req in wo.required_materials:
                if mat_req.material_id == material_id:
                    affected_orders.append(wo)
                    break
        
        print(f"  → {len(affected_orders)} work orders affected")
        
        # Block affected work orders and free resources
        for wo in affected_orders:
            if wo.status == WorkOrderStatus.IN_PROGRESS:
                print(f"  → Blocking {wo.work_order_id}")
                wo.status = WorkOrderStatus.BLOCKED
                
                # Free operator
                if wo.assigned_operator:
                    operator = self.engine.operators[wo.assigned_operator]
                    operator.current_status = OperatorStatus.AVAILABLE
                    operator.current_work_order = None
                    print(f"    • Released operator {operator.name}")
                
                # Free machine
                if wo.assigned_machine:
                    machine = self.engine.machines[wo.assigned_machine]
                    machine.current_status = MachineStatus.IDLE
                    machine.current_work_order = None
                    print(f"    • Released machine {machine.name}")
        
        print(f"  → Notifying supply chain team...")
        print(f"  → Checking for substitute materials...")
    
    def handle_material_delivered(self, material_id: str, quantity: float):
        """Handle material delivery event"""
        print(f"\n✓ Material delivered: {material_id} (+{quantity})")
        
        material = self.engine.materials.get(material_id)
        if not material:
            return
        
        material.quantity_available += quantity
        print(f"  → New available quantity: {material.quantity_available}")
        
        # Unblock affected work orders
        unblocked = 0
        for wo in self.engine.work_orders.values():
            if wo.status == WorkOrderStatus.BLOCKED:
                for mat_req in wo.required_materials:
                    if mat_req.material_id == material_id:
                        wo.status = WorkOrderStatus.PENDING
                        unblocked += 1
                        break
        
        if unblocked > 0:
            print(f"  → Unblocked {unblocked} work orders")
            print(f"  → Attempting reallocation...")
            self.engine.process_allocations()
    
    def process_events(self):
        """Process all events in priority queue"""
        print(f"\n⚡ Processing {len(self.event_queue)} events...")
        print("=" * 60)
        
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            
            if event.event_type == "machine_breakdown":
                self.handle_machine_breakdown(event.data['machine_id'])
            
            elif event.event_type == "machine_maintenance":
                duration = event.data.get('duration_minutes', 60)
                self.handle_machine_maintenance(event.data['machine_id'], duration)
            
            elif event.event_type == "operator_available":
                self.handle_operator_available(event.data['operator_id'])
            
            elif event.event_type == "work_order_complete":
                self.handle_work_order_completion(event.data['work_order_id'])
            
            elif event.event_type == "material_shortage":
                self.handle_material_shortage(event.data['material_id'])
            
            elif event.event_type == "material_delivered":
                quantity = event.data.get('quantity', 0)
                self.handle_material_delivered(event.data['material_id'], quantity)
            
            else:
                print(f"⚠ Unknown event type: {event.event_type}")
    
    def get_event_statistics(self) -> Dict:
        """Get statistics about processed events"""
        event_counts = {}
        for log_entry in self.event_log:
            event_type = log_entry['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            'total_events': len(self.event_log),
            'by_type': event_counts,
            'pending': len(self.event_queue)
        }
