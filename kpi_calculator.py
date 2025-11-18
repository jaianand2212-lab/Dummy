"""
KPI Calculator for Performance Monitoring
Implements KPI metrics from resource_allocation_system_design.md Section 5
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from models import *


class KPICalculator:
    """
    Calculate and monitor Key Performance Indicators
    Provides real-time insights into system performance
    """
    
    def __init__(self, engine):
        self.engine = engine
    
    def calculate_operator_utilization(self) -> Dict[str, any]:
        """
        Calculate operator utilization rate
        Formula: (Actual Working Time / Available Time) × 100
        Target: >85%
        """
        utilization = {}
        total_working = 0
        total_available = 0
        
        for op_id, operator in self.engine.operators.items():
            if not operator.shift_start or not operator.shift_end:
                continue
            
            shift_duration = (operator.shift_end - operator.shift_start).seconds / 3600  # hours
            
            # Calculate active time (simplified for demo)
            if operator.current_status == OperatorStatus.ASSIGNED:
                active_time = shift_duration * 0.85  # Assume 85% if assigned
            elif operator.current_status == OperatorStatus.AVAILABLE:
                active_time = 0
            else:
                active_time = 0
            
            utilization[op_id] = (active_time / shift_duration * 100) if shift_duration > 0 else 0
            total_working += active_time
            total_available += shift_duration
        
        avg_utilization = (total_working / total_available * 100) if total_available > 0 else 0
        
        return {
            'by_operator': utilization,
            'average': avg_utilization,
            'target': 85.0,
            'status': '✓' if avg_utilization >= 85 else '⚠' if avg_utilization >= 70 else '✗'
        }
    
    def calculate_machine_utilization(self) -> Dict[str, any]:
        """
        Calculate machine utilization rate
        Formula: (Running Time / Total Available Time) × 100
        Target: >80%
        """
        utilization = {}
        
        for m_id, machine in self.engine.machines.items():
            if machine.current_status == MachineStatus.RUNNING:
                utilization[m_id] = 100.0
            elif machine.current_status == MachineStatus.IDLE:
                utilization[m_id] = 0.0
            elif machine.current_status == MachineStatus.MAINTENANCE:
                utilization[m_id] = 0.0
            else:  # breakdown
                utilization[m_id] = 0.0
        
        avg_utilization = sum(utilization.values()) / len(utilization) if utilization else 0
        
        # Count by status
        status_counts = {
            'running': sum(1 for m in self.engine.machines.values() if m.current_status == MachineStatus.RUNNING),
            'idle': sum(1 for m in self.engine.machines.values() if m.current_status == MachineStatus.IDLE),
            'maintenance': sum(1 for m in self.engine.machines.values() if m.current_status == MachineStatus.MAINTENANCE),
            'breakdown': sum(1 for m in self.engine.machines.values() if m.current_status == MachineStatus.BREAKDOWN),
        }
        
        return {
            'by_machine': utilization,
            'average': avg_utilization,
            'status_counts': status_counts,
            'target': 80.0,
            'status': '✓' if avg_utilization >= 80 else '⚠' if avg_utilization >= 65 else '✗'
        }
    
    def calculate_work_order_metrics(self) -> Dict:
        """
        Calculate work order performance metrics
        - Throughput
        - On-time delivery rate (Target: >95%)
        - Status distribution
        """
        completed = [wo for wo in self.engine.work_orders.values() 
                    if wo.status == WorkOrderStatus.COMPLETED]
        in_progress = [wo for wo in self.engine.work_orders.values() 
                      if wo.status == WorkOrderStatus.IN_PROGRESS]
        blocked = [wo for wo in self.engine.work_orders.values() 
                  if wo.status == WorkOrderStatus.BLOCKED]
        pending = [wo for wo in self.engine.work_orders.values() 
                  if wo.status == WorkOrderStatus.PENDING]
        
        # On-time delivery rate
        on_time = sum(1 for wo in completed if wo.completion_time and wo.completion_time <= wo.deadline)
        otd_rate = (on_time / len(completed) * 100) if completed else 0
        
        # Average cycle time efficiency
        cycle_times = []
        for wo in completed:
            if wo.start_time and wo.completion_time:
                actual_duration = (wo.completion_time - wo.start_time).seconds / 60
                efficiency = (wo.estimated_duration / actual_duration) * 100 if actual_duration > 0 else 0
                cycle_times.append(efficiency)
        
        avg_cycle_efficiency = sum(cycle_times) / len(cycle_times) if cycle_times else 0
        
        return {
            'completed': len(completed),
            'in_progress': len(in_progress),
            'blocked': len(blocked),
            'pending': len(pending),
            'total': len(self.engine.work_orders),
            'otd_rate': otd_rate,
            'otd_target': 95.0,
            'otd_status': '✓' if otd_rate >= 95 else '⚠' if otd_rate >= 90 else '✗',
            'avg_cycle_efficiency': avg_cycle_efficiency,
        }
    
    def calculate_allocation_conflicts(self) -> Dict:
        """
        Calculate number of allocation conflicts
        Target: <5 per day
        """
        blocked_count = sum(1 for wo in self.engine.work_orders.values() 
                          if wo.status == WorkOrderStatus.BLOCKED)
        
        # In production, track reallocations from event logs
        reallocation_count = len(self.engine.last_reallocation_time)
        total_allocations = sum(1 for wo in self.engine.work_orders.values() 
                               if wo.status in [WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.COMPLETED])
        
        reallocation_rate = (reallocation_count / total_allocations * 100) if total_allocations > 0 else 0
        
        return {
            'blocked_orders': blocked_count,
            'reallocation_rate': reallocation_rate,
            'target_rate': 15.0,
            'status': '✓' if reallocation_rate <= 15 else '⚠' if reallocation_rate <= 25 else '✗'
        }
    
    def generate_kpi_summary(self) -> str:
        """
        Generate comprehensive KPI summary dashboard
        Displays all key metrics with targets and status indicators
        """
        op_util = self.calculate_operator_utilization()
        mach_util = self.calculate_machine_utilization()
        wo_metrics = self.calculate_work_order_metrics()
        conflicts = self.calculate_allocation_conflicts()
        
        summary = f"""
┌──────────────────────────────────────────────────────────┐
│  📊 DAILY KPI SUMMARY                        Target      │
├──────────────────────────────────────────────────────────┤
│  Operator Utilization:      {op_util['average']:5.1f}%     {op_util['status']} >{op_util['target']}%     │
│  Machine Utilization:       {mach_util['average']:5.1f}%     {mach_util['status']} >{mach_util['target']}%     │
├──────────────────────────────────────────────────────────┤
│  Work Orders Completed:     {wo_metrics['completed']:3d}         ✓ Progress  │
│  Work Orders In Progress:   {wo_metrics['in_progress']:3d}         -          │
│  Work Orders Blocked:       {wo_metrics['blocked']:3d}         ⚠ Alert    │
│  Work Orders Pending:       {wo_metrics['pending']:3d}         -          │
├──────────────────────────────────────────────────────────┤
│  On-Time Delivery Rate:     {wo_metrics['otd_rate']:5.1f}%     {wo_metrics['otd_status']} >{wo_metrics['otd_target']}%     │
│  Avg Cycle Efficiency:      {wo_metrics['avg_cycle_efficiency']:5.1f}%     ✓ 90-110%  │
│  Reallocation Rate:         {conflicts['reallocation_rate']:5.1f}%     {conflicts['status']} <{conflicts['target_rate']}%     │
└──────────────────────────────────────────────────────────┘

Machine Status Distribution:
  • Running: {mach_util['status_counts']['running']} | Idle: {mach_util['status_counts']['idle']} | Maintenance: {mach_util['status_counts']['maintenance']} | Breakdown: {mach_util['status_counts']['breakdown']}
"""
        return summary
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        Export work order data to pandas DataFrame for analysis
        Useful for generating reports and visualizations
        """
        data = []
        for wo in self.engine.work_orders.values():
            row = {
                'work_order_id': wo.work_order_id,
                'priority': wo.priority,
                'status': wo.status.value,
                'assigned_operator': wo.assigned_operator or '-',
                'assigned_machine': wo.assigned_machine or '-',
                'estimated_duration': wo.estimated_duration,
                'deadline': wo.deadline,
                'progress': wo.progress,
                'location': wo.location
            }
            
            # Add timing information if available
            if wo.start_time:
                row['start_time'] = wo.start_time
            if wo.completion_time:
                row['completion_time'] = wo.completion_time
                actual_duration = (wo.completion_time - wo.start_time).seconds / 60
                row['actual_duration'] = actual_duration
                row['efficiency'] = (wo.estimated_duration / actual_duration * 100) if actual_duration > 0 else 0
                row['on_time'] = wo.completion_time <= wo.deadline
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def export_resource_utilization_df(self) -> pd.DataFrame:
        """Export resource utilization data to DataFrame"""
        op_util = self.calculate_operator_utilization()
        mach_util = self.calculate_machine_utilization()
        
        # Operators
        op_data = []
        for op_id, operator in self.engine.operators.items():
            op_data.append({
                'resource_id': op_id,
                'resource_type': 'Operator',
                'name': operator.name,
                'status': operator.current_status.value,
                'utilization': op_util['by_operator'].get(op_id, 0),
                'location': operator.location
            })
        
        # Machines
        for m_id, machine in self.engine.machines.items():
            op_data.append({
                'resource_id': m_id,
                'resource_type': 'Machine',
                'name': machine.name,
                'status': machine.current_status.value,
                'utilization': mach_util['by_machine'].get(m_id, 0),
                'location': machine.location
            })
        
        return pd.DataFrame(op_data)
