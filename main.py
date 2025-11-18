"""
Main Application for Dynamic Resource Allocation System
Complete demonstration of the system with sample data
Based on resource_allocation_system_design.md
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
from models import *
from allocation_engine import AllocationEngine
from event_handler import EventHandler, EventPriority
from kpi_calculator import KPICalculator


def create_sample_data():
    """Create comprehensive sample data for demonstration"""
    engine = AllocationEngine()
    
    # Add operators with various skills
    operators = [
        Operator(
            "OP-001", "John Smith", 
            ["welding", "assembly"], 
            {"welding": 5, "assembly": 4}, 
            OperatorStatus.AVAILABLE,
            shift_start=datetime.now(),
            shift_end=datetime.now() + timedelta(hours=8),
            location="Zone-A", 
            hourly_cost=25.0
        ),
        Operator(
            "OP-002", "Jane Doe", 
            ["machining", "assembly"], 
            {"machining": 4, "assembly": 5}, 
            OperatorStatus.AVAILABLE,
            shift_start=datetime.now(),
            shift_end=datetime.now() + timedelta(hours=8),
            location="Zone-B", 
            hourly_cost=28.0
        ),
        Operator(
            "OP-003", "Mike Johnson", 
            ["welding", "inspection"], 
            {"welding": 3, "inspection": 5}, 
            OperatorStatus.AVAILABLE,
            shift_start=datetime.now(),
            shift_end=datetime.now() + timedelta(hours=8),
            location="Zone-A", 
            hourly_cost=22.0
        ),
        Operator(
            "OP-004", "Sarah Williams", 
            ["machining", "programming"], 
            {"machining": 5, "programming": 4}, 
            OperatorStatus.AVAILABLE,
            shift_start=datetime.now(),
            shift_end=datetime.now() + timedelta(hours=8),
            location="Zone-B", 
            hourly_cost=30.0
        ),
    ]
    
    for op in operators:
        engine.operators[op.operator_id] = op
    
    # Add machines with capabilities
    machines = [
        Machine(
            "M-001", "Welder-A", ["welding"], MachineStatus.IDLE,
            location="Zone-A", cycle_time=30, operating_cost_per_hour=15.0
        ),
        Machine(
            "M-002", "CNC-Mill-B", ["machining"], MachineStatus.IDLE,
            location="Zone-B", cycle_time=45, operating_cost_per_hour=20.0
        ),
        Machine(
            "M-003", "Welder-C", ["welding"], MachineStatus.IDLE,
            location="Zone-A", cycle_time=25, operating_cost_per_hour=15.0
        ),
        Machine(
            "M-004", "CNC-Lathe-D", ["machining"], MachineStatus.IDLE,
            location="Zone-B", cycle_time=35, operating_cost_per_hour=18.0
        ),
    ]
    
    for m in machines:
        engine.machines[m.machine_id] = m
    
    # Add materials inventory
    materials = [
        Material(
            "MAT-001", "Steel Plate", 1000.0, 0.0, 
            "Warehouse-A", "kg", 200.0, cost_per_unit=5.0
        ),
        Material(
            "MAT-002", "Aluminum Bar", 500.0, 0.0, 
            "Warehouse-B", "kg", 100.0, cost_per_unit=8.0
        ),
        Material(
            "MAT-003", "Bolts", 5000.0, 0.0, 
            "Warehouse-A", "pcs", 1000.0, cost_per_unit=0.5
        ),
        Material(
            "MAT-004", "Cutting Fluid", 200.0, 0.0, 
            "Warehouse-B", "liters", 50.0, cost_per_unit=12.0
        ),
    ]
    
    for mat in materials:
        engine.materials[mat.material_id] = mat
    
    # Add work orders with varying priorities and requirements
    work_orders = [
        WorkOrder(
            "WO-101", 10, ["welding"], "welding",
            [MaterialRequirement("MAT-001", 50.0)],
            60, datetime.now() + timedelta(hours=2),
            WorkOrderStatus.PENDING, location="Zone-A"
        ),
        WorkOrder(
            "WO-102", 8, ["machining"], "machining",
            [MaterialRequirement("MAT-002", 20.0), MaterialRequirement("MAT-004", 5.0)],
            90, datetime.now() + timedelta(hours=4),
            WorkOrderStatus.PENDING, location="Zone-B"
        ),
        WorkOrder(
            "WO-103", 9, ["welding", "assembly"], "welding",
            [MaterialRequirement("MAT-001", 30.0), MaterialRequirement("MAT-003", 100.0)],
            75, datetime.now() + timedelta(hours=3),
            WorkOrderStatus.PENDING, location="Zone-A"
        ),
        WorkOrder(
            "WO-104", 7, ["welding"], "welding",
            [MaterialRequirement("MAT-001", 40.0)],
            45, datetime.now() + timedelta(hours=5),
            WorkOrderStatus.PENDING, location="Zone-A"
        ),
        WorkOrder(
            "WO-105", 6, ["machining"], "machining",
            [MaterialRequirement("MAT-002", 15.0), MaterialRequirement("MAT-004", 3.0)],
            60, datetime.now() + timedelta(hours=6),
            WorkOrderStatus.PENDING, location="Zone-B"
        ),
    ]
    
    for wo in work_orders:
        engine.work_orders[wo.work_order_id] = wo
    
    return engine


def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """Print formatted subsection"""
    print(f"\n{title}")
    print("-" * 70)


def create_comprehensive_dashboard(engine: AllocationEngine, kpi_calc: KPICalculator, title_prefix: str = ""):
    """Create a comprehensive dashboard with all visualizations in one view"""
    
    # Calculate KPIs - try different method names based on what's available
    try:
        if hasattr(kpi_calc, 'calculate_kpis'):
            kpis = kpi_calc.calculate_kpis()
        elif hasattr(kpi_calc, 'get_kpis'):
            kpis = kpi_calc.get_kpis()
        else:
            # Fallback: create basic KPIs manually
            kpis = {
                'operator_utilization': 0.0,
                'machine_utilization': 0.0,
                'material_efficiency': 0.0,
                'overall_efficiency': 0.0,
                'on_time_delivery_rate': 0.0,
                'total_work_orders': len(engine.work_orders),
                'completed_work_orders': sum(1 for wo in engine.work_orders.values() if wo.status == WorkOrderStatus.COMPLETED),
                'pending_work_orders': sum(1 for wo in engine.work_orders.values() if wo.status == WorkOrderStatus.PENDING),
                'blocked_work_orders': sum(1 for wo in engine.work_orders.values() if wo.status == WorkOrderStatus.BLOCKED),
                'avg_efficiency': 100.0,
                'avg_cycle_time': 60.0,
                'avg_delay_time': 0.0,
                'total_operators': len(engine.operators),
                'total_machines': len(engine.machines),
                'total_materials': len(engine.materials),
                'total_labor_cost': 0.0,
                'total_machine_cost': 0.0,
                'total_material_cost': 0.0,
                'total_cost': 0.0
            }
    except Exception as e:
        print(f"  ⚠️ Warning: Could not calculate KPIs - {str(e)}")
        # Use default values
        kpis = {
            'operator_utilization': 0.0,
            'machine_utilization': 0.0,
            'material_efficiency': 0.0,
            'overall_efficiency': 0.0,
            'on_time_delivery_rate': 0.0,
            'total_work_orders': len(engine.work_orders),
            'completed_work_orders': sum(1 for wo in engine.work_orders.values() if wo.status == WorkOrderStatus.COMPLETED),
            'pending_work_orders': sum(1 for wo in engine.work_orders.values() if wo.status == WorkOrderStatus.PENDING),
            'blocked_work_orders': sum(1 for wo in engine.work_orders.values() if wo.status == WorkOrderStatus.BLOCKED),
            'avg_efficiency': 100.0,
            'avg_cycle_time': 60.0,
            'avg_delay_time': 0.0,
            'total_operators': len(engine.operators),
            'total_machines': len(engine.machines),
            'total_materials': len(engine.materials),
            'total_labor_cost': 0.0,
            'total_machine_cost': 0.0,
            'total_material_cost': 0.0,
            'total_cost': 0.0
        }
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(4, 3, hspace=0.4, wspace=0.3)
    
    # Add main title
    fig.suptitle(f'{title_prefix}Resource Allocation System - Comprehensive Dashboard', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    # 1. Operator Status (Top Left)
    ax1 = fig.add_subplot(gs[0, 0])
    op_names = [op.name for op in engine.operators.values()]
    op_status = []
    for op in engine.operators.values():
        if hasattr(op, 'status'):
            op_status.append(op.status.value)
        else:
            is_busy = any(wo.assigned_operator == op.operator_id and wo.status == WorkOrderStatus.IN_PROGRESS 
                         for wo in engine.work_orders.values())
            op_status.append('busy' if is_busy else 'available')
    
    op_colors = ['green' if s == 'available' else 'orange' if s == 'busy' else 'red' 
                 for s in op_status]
    ax1.barh(op_names, [1]*len(op_names), color=op_colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    ax1.set_title('Operator Status', fontweight='bold', fontsize=11)
    ax1.set_xlim(0, 1)
    ax1.set_xticks([])
    ax1.tick_params(axis='y', labelsize=8)
    
    # 2. Machine Status (Top Middle)
    ax2 = fig.add_subplot(gs[0, 1])
    machine_names = [m.name for m in engine.machines.values()]
    machine_status = []
    for m in engine.machines.values():
        if hasattr(m, 'status'):
            machine_status.append(m.status.value)
        else:
            is_running = any(wo.assigned_machine == m.machine_id and wo.status == WorkOrderStatus.IN_PROGRESS 
                           for wo in engine.work_orders.values())
            machine_status.append('running' if is_running else 'idle')
    
    machine_colors = ['green' if s == 'idle' else 'orange' if s == 'running' else 'red' 
                      for s in machine_status]
    ax2.barh(machine_names, [1]*len(machine_names), color=machine_colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    ax2.set_title('Machine Status', fontweight='bold', fontsize=11)
    ax2.set_xlim(0, 1)
    ax2.set_xticks([])
    ax2.tick_params(axis='y', labelsize=8)
    
    # 3. Work Order Status Distribution (Top Right)
    ax3 = fig.add_subplot(gs[0, 2])
    status_counts = {}
    for wo in engine.work_orders.values():
        status = wo.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    colors_pie = {'pending': '#FFA07A', 'in_progress': '#90EE90', 
                  'completed': '#87CEEB', 'blocked': '#FFB6C1'}
    
    wedges, texts, autotexts = ax3.pie(
        status_counts.values(), 
        labels=[s.replace('_', ' ').title() for s in status_counts.keys()],
        colors=[colors_pie.get(s, '#CCCCCC') for s in status_counts.keys()],
        autopct='%1.0f%%',
        startangle=90,
        textprops={'fontsize': 8}
    )
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax3.set_title('Work Order Status', fontweight='bold', fontsize=11)
    
    # 4. KPI Performance Indicators (Second Row - Full Width)
    ax4 = fig.add_subplot(gs[1, :])
    categories = ['Operator\nUtilization', 'Machine\nUtilization', 'Material\nEfficiency', 
                  'Overall\nEfficiency', 'On-Time\nDelivery']
    values = [
        kpis['operator_utilization'],
        kpis['machine_utilization'],
        kpis['material_efficiency'],
        kpis['overall_efficiency'],
        kpis['on_time_delivery_rate']
    ]
    colors_bar = ['#FF6B6B' if v < 60 else '#FFA500' if v < 80 else '#4CAF50' for v in values]
    bars = ax4.bar(categories, values, color=colors_bar, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax4.set_ylabel('Percentage (%)', fontsize=10)
    ax4.set_title('Key Performance Indicators', fontsize=12, fontweight='bold')
    ax4.set_ylim(0, 100)
    ax4.axhline(y=80, color='green', linestyle='--', alpha=0.5, linewidth=1, label='Target (80%)')
    ax4.legend(fontsize=8)
    ax4.grid(axis='y', alpha=0.3)
    ax4.tick_params(labelsize=9)
    
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 5. Work Order Timeline (Third Row - Full Width)
    ax5 = fig.add_subplot(gs[2, :])
    work_orders = sorted(engine.work_orders.values(), key=lambda x: x.priority, reverse=True)
    now = datetime.now()
    colors_status = {'pending': '#FFA07A', 'in_progress': '#90EE90', 
                     'completed': '#87CEEB', 'blocked': '#FFB6C1'}
    
    y_pos = 0
    for wo in work_orders:
        color = colors_status.get(wo.status.value, '#CCCCCC')
        time_to_deadline = (wo.deadline - now).total_seconds() / 3600
        
        ax5.barh(y_pos, wo.estimated_duration/60, left=0, height=0.8, 
                color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
        ax5.plot([time_to_deadline, time_to_deadline], [y_pos-0.4, y_pos+0.4], 
                'r--', linewidth=1.5, alpha=0.8)
        
        label = f"{wo.work_order_id} (P{wo.priority})"
        ax5.text(-0.15, y_pos, label, ha='right', va='center', fontsize=8)
        y_pos += 1
    
    ax5.set_xlabel('Time (hours from now)', fontsize=10)
    ax5.set_title('Work Order Timeline (Duration vs Deadline)', fontsize=12, fontweight='bold')
    ax5.set_yticks([])
    ax5.axvline(x=0, color='black', linewidth=1.5, label='Current Time')
    ax5.grid(axis='x', alpha=0.3)
    ax5.tick_params(labelsize=9)
    
    legend_elements = [
        mpatches.Patch(color='#90EE90', label='In Progress', alpha=0.7),
        mpatches.Patch(color='#FFA07A', label='Pending', alpha=0.7),
        mpatches.Patch(color='#87CEEB', label='Completed', alpha=0.7),
        mpatches.Patch(color='#FFB6C1', label='Blocked', alpha=0.7),
        plt.Line2D([0], [0], color='r', linewidth=1.5, linestyle='--', label='Deadline')
    ]
    ax5.legend(handles=legend_elements, loc='upper right', fontsize=8, ncol=5)
    
    # 6. Average Metrics (Bottom Left)
    ax6 = fig.add_subplot(gs[3, 0])
    metrics = ['Avg\nEfficiency', 'Avg\nCycle Time', 'Avg\nDelay']
    metric_values = [kpis['avg_efficiency'], kpis['avg_cycle_time'], kpis['avg_delay_time']]
    bars_metrics = ax6.bar(metrics, metric_values, color=['#4CAF50', '#2196F3', '#FF9800'], 
                           alpha=0.7, edgecolor='black', linewidth=1)
    ax6.set_ylabel('Minutes', fontsize=9)
    ax6.set_title('Average Metrics', fontweight='bold', fontsize=11)
    ax6.grid(axis='y', alpha=0.3)
    ax6.tick_params(labelsize=8)
    
    for bar, value in zip(bars_metrics, metric_values):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 7. Resource Counts (Bottom Middle)
    ax7 = fig.add_subplot(gs[3, 1])
    resources = ['Operators', 'Machines', 'Materials']
    resource_counts = [kpis['total_operators'], kpis['total_machines'], kpis['total_materials']]
    bars_resources = ax7.bar(resources, resource_counts, color=['#9C27B0', '#FF5722', '#00BCD4'], 
                             alpha=0.7, edgecolor='black', linewidth=1)
    ax7.set_ylabel('Count', fontsize=9)
    ax7.set_title('Resource Inventory', fontweight='bold', fontsize=11)
    ax7.grid(axis='y', alpha=0.3)
    ax7.tick_params(labelsize=8)
    
    for bar, value in zip(bars_resources, resource_counts):
        height = bar.get_height()
        ax7.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    # 8. Cost Breakdown (Bottom Right)
    ax8 = fig.add_subplot(gs[3, 2])
    cost_categories = ['Labor', 'Machine', 'Material', 'Total']
    costs = [kpis['total_labor_cost'], kpis['total_machine_cost'], 
             kpis['total_material_cost'], kpis['total_cost']]
    bars_cost = ax8.bar(cost_categories, costs, color=['#E91E63', '#3F51B5', '#009688', '#FF5722'], 
                        alpha=0.7, edgecolor='black', linewidth=1)
    ax8.set_ylabel('Cost ($)', fontsize=9)
    ax8.set_title('Cost Breakdown', fontweight='bold', fontsize=11)
    ax8.grid(axis='y', alpha=0.3)
    ax8.tick_params(labelsize=8)
    
    for bar, cost in zip(bars_cost, costs):
        height = bar.get_height()
        ax8.text(bar.get_x() + bar.get_width()/2., height,
                f'${cost:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=7)
    
    # Save figure
    filename = f'c:/TSDE_Workarea/jan5cob/new/trainings/comprehensive_dashboard_{title_prefix.lower().replace(" ", "_")}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"  📊 Saved: {filename}")
    plt.show()


def main():
    """Main application demonstrating the complete resource allocation system"""
    
    print_header("DYNAMIC RESOURCE ALLOCATION SYSTEM - DEMONSTRATION")
    print("\nBased on: resource_allocation_system_design.md")
    print("Objective: Minimize idle time across operators, machines, and materials")
    
    # Initialize system
    print("\n🔧 Initializing system...")
    engine = create_sample_data()
    event_handler = EventHandler(engine)
    kpi_calc = KPICalculator(engine)
    
    # Display initial state
    print_section("📊 INITIAL SYSTEM STATE")
    summary = engine.get_resource_summary()
    print(f"Operators: {summary['operators']['available']}/{summary['operators']['total']} available")
    print(f"Machines:  {summary['machines']['idle']}/{summary['machines']['total']} idle")
    print(f"Work Orders: {summary['work_orders']['pending']} pending")
    
    # Show operators
    print("\n👥 Operators:")
    for op in engine.operators.values():
        skills_str = ", ".join(op.skills)
        print(f"  • {op.operator_id}: {op.name:20s} | Skills: {skills_str:30s} | {op.location}")
    
    # Show machines
    print("\n🏭 Machines:")
    for m in engine.machines.values():
        caps_str = ", ".join(m.capabilities)
        print(f"  • {m.machine_id}: {m.name:15s} | Capability: {caps_str:20s} | {m.location}")
    
    # Show materials
    print("\n📦 Materials Inventory:")
    for mat in engine.materials.values():
        print(f"  • {mat.material_id}: {mat.name:20s} | Available: {mat.quantity_available:6.0f} {mat.unit_of_measure}")
    
    # Show work orders
    print("\n📋 Work Orders:")
    for wo in engine.work_orders.values():
        deadline_str = wo.deadline.strftime("%H:%M")
        print(f"  • {wo.work_order_id}: Priority {wo.priority} | Deadline: {deadline_str} | Duration: {wo.estimated_duration} min")
    
    # Process initial allocations
    print_section("🔄 PROCESSING INITIAL ALLOCATIONS")
    results = engine.process_allocations()
    
    print(f"\n📈 Allocation Results:")
    print(f"  ✓ Successfully Allocated: {results['allocated']}")
    print(f"  ✗ Blocked (no resources): {results['blocked']}")
    print(f"  📊 Total Processed: {results['total']}")
    
    # Display allocation matrix using pandas
    print_section("📋 ALLOCATION MATRIX (pandas DataFrame)")
    df_allocations = pd.DataFrame([
        {
            'Work Order': wo.work_order_id,
            'Status': wo.status.value.upper(),
            'Priority': wo.priority,
            'Operator': engine.operators[wo.assigned_operator].name if wo.assigned_operator else '-',
            'Machine': engine.machines[wo.assigned_machine].name if wo.assigned_machine else '-',
            'Location': wo.location,
            'Duration': f"{wo.estimated_duration} min"
        }
        for wo in engine.work_orders.values()
    ])
    print(df_allocations.to_string(index=False))
    
    # Simulate real-time events
    print_section("⚡ SIMULATING REAL-TIME EVENTS")
    
    # Event 1: Machine breakdown
    print("\n[Event 1] Triggering machine breakdown...")
    event_handler.add_event(EventPriority.CRITICAL, "machine_breakdown", {'machine_id': 'M-001'})
    
    # Event 2: Work order completion
    completed_wo = [wo for wo in engine.work_orders.values() if wo.status == WorkOrderStatus.IN_PROGRESS]
    if completed_wo:
        print(f"[Event 2] Simulating work order completion...")
        event_handler.add_event(EventPriority.ROUTINE, "work_order_complete", 
                              {'work_order_id': completed_wo[0].work_order_id})
    
    # Event 3: Material shortage
    print("[Event 3] Simulating material shortage...")
    event_handler.add_event(EventPriority.MATERIAL_SHORTAGE, "material_shortage", 
                          {'material_id': 'MAT-001'})
    
    # Process all events
    event_handler.process_events()
    
    # Show event statistics
    event_stats = event_handler.get_event_statistics()
    print(f"\n📊 Event Processing Summary:")
    print(f"  Total Events Processed: {event_stats['total_events']}")
    for event_type, count in event_stats['by_type'].items():
        print(f"    • {event_type}: {count}")
    
    # Generate KPI summary
    print_section("📊 KEY PERFORMANCE INDICATORS (KPIs)")
    print(kpi_calc.generate_kpi_summary())
    
    # Generate comprehensive dashboard - Initial State
    print("\n📈 Generating Initial State Comprehensive Dashboard...")
    create_comprehensive_dashboard(engine, kpi_calc, title_prefix="INITIAL STATE - ")
    
    # Export work order analysis to DataFrame
    print_section("📁 WORK ORDER ANALYSIS (pandas DataFrame)")
    df_wo = kpi_calc.export_to_dataframe()
    print(df_wo.to_string(index=False))
    
    # Export resource utilization
    print_section("📁 RESOURCE UTILIZATION (pandas DataFrame)")
    df_resources = kpi_calc.export_resource_utilization_df()
    print(df_resources.to_string(index=False))
    
    # Generate final visualizations
    print_section("📈 FINAL STATE VISUALIZATIONS")
    print("\n📊 Generating Final Comprehensive Dashboard...")
    create_comprehensive_dashboard(engine, kpi_calc, title_prefix="FINAL STATE - ")
    
    # Final summary
    print_header("SIMULATION COMPLETE")
    
    final_summary = engine.get_resource_summary()
    print("\n✓ System Successfully Demonstrated:")
    print(f"  • Resource allocation with scoring algorithm")
    print(f"  • Real-time event handling (breakdowns, completions, shortages)")
    print(f"  • Automatic reallocation on resource changes")
    print(f"  • KPI calculation and monitoring")
    print(f"  • pandas DataFrame integration for analysis")
    
    print(f"\n📊 Final System State:")
    print(f"  • Work Orders Completed: {final_summary['work_orders']['completed']}")
    print(f"  • Work Orders In Progress: {final_summary['work_orders']['in_progress']}")
    print(f"  • Work Orders Blocked: {final_summary['work_orders']['blocked']}")
    print(f"  • Work Orders Pending: {final_summary['work_orders']['pending']}")
    
    print("\n" + "=" * 70)
    print("  Thank you for using the Resource Allocation System!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
