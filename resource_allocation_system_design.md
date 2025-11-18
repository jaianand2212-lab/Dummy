# Dynamic Resource Allocation System - Design Plan

## Executive Summary
This document outlines a practical system for real-time scheduling and allocation of operators, machines, and materials to work orders, with the primary objective of minimizing idle time across all resources while maintaining operational stability.

---

## 1. Data Model

### 1.1 Operators Schema
```json
{
  "operator_id": "string (unique)",
  "name": "string",
  "skills": ["skill_1", "skill_2", "..."],
  "skill_levels": {"skill_1": 1-5, "skill_2": 1-5},
  "current_status": "available | assigned | break | unavailable",
  "current_work_order": "string (work_order_id) | null",
  "shift_start": "timestamp",
  "shift_end": "timestamp",
  "location": "string (zone/area)",
  "hourly_cost": "decimal"
}
```

### 1.2 Machines Schema
```json
{
  "machine_id": "string (unique)",
  "name": "string",
  "capabilities": ["capability_1", "capability_2", "..."],
  "current_status": "idle | running | maintenance | breakdown",
  "current_work_order": "string (work_order_id) | null",
  "location": "string (zone/area)",
  "cycle_time": "integer (minutes)",
  "maintenance_schedule": "timestamp",
  "last_maintenance": "timestamp",
  "operating_cost_per_hour": "decimal"
}
```

### 1.3 Materials Schema
```json
{
  "material_id": "string (unique)",
  "name": "string",
  "quantity_available": "decimal",
  "quantity_reserved": "decimal",
  "location": "string (warehouse/zone)",
  "unit_of_measure": "string",
  "reorder_point": "decimal",
  "expected_delivery": "timestamp | null",
  "cost_per_unit": "decimal"
}
```

### 1.4 Work Orders Schema
```json
{
  "work_order_id": "string (unique)",
  "priority": "integer (1-10, 10=highest)",
  "required_skills": ["skill_1", "skill_2"],
  "required_machine_capability": "string",
  "required_materials": [
    {"material_id": "string", "quantity": "decimal"}
  ],
  "estimated_duration": "integer (minutes)",
  "deadline": "timestamp",
  "status": "pending | in_progress | completed | blocked",
  "assigned_operator": "string (operator_id) | null",
  "assigned_machine": "string (machine_id) | null",
  "start_time": "timestamp | null",
  "completion_time": "timestamp | null",
  "location": "string (zone/area)"
}
```

---

## 2. Core Scheduling Logic & Constraints

### 2.1 Initial Allocation Algorithm

**Step 1: Work Order Prioritization**
- Sort work orders by: Priority (descending) → Deadline (ascending) → Duration (ascending)

**Step 2: Constraint Validation**
```
FOR each work_order in prioritized_queue:
  1. Find eligible operators: skills match + available
  2. Find eligible machines: capability match + idle
  3. Verify material availability: quantity >= required
  4. Calculate allocation score
  5. IF all resources available THEN assign ELSE mark as blocked
```

**Step 3: Allocation Scoring Function**
```
score = (0.4 × skill_match_quality) + 
        (0.3 × proximity_factor) + 
        (0.2 × machine_efficiency) + 
        (0.1 × cost_optimization)

Where:
- skill_match_quality = average skill level / 5
- proximity_factor = 1 - (distance between operator-machine-material / max_distance)
- machine_efficiency = 1 / cycle_time_normalized
- cost_optimization = 1 - (total_cost / max_cost)
```

### 2.2 Hard Constraints (Must Satisfy)
1. **Skill Matching**: Operator must possess ALL required skills
2. **Machine Capability**: Machine must have the required capability
3. **Material Availability**: All materials must be available in sufficient quantity
4. **Temporal Constraints**: Resources must be available during work order timeframe
5. **Location Constraints**: Resources within acceptable distance (configurable threshold)

### 2.3 Soft Constraints (Optimize)
1. Minimize total idle time across all resources
2. Prefer operators with higher skill levels for complex jobs
3. Balance workload distribution among operators
4. Minimize material transport distance
5. Avoid reassignments within 15 minutes of allocation (stability buffer)

### 2.4 Reallocation Trigger Rules
```
REALLOCATE IF:
1. Resource becomes unavailable (machine breakdown, operator absent)
2. Higher priority work order enters queue
3. Idle time exceeds threshold (5 minutes)
4. Blocked work order becomes unblocked
5. Current allocation efficiency drops below 70%

DO NOT REALLOCATE IF:
1. Work order is >50% complete
2. Last reallocation was <15 minutes ago
3. Alternative allocation score improvement <10%
```

---

## 3. Real-Time Event Handling

### 3.1 Machine Downtime Event
```
EVENT: Machine breakdown/maintenance detected

IMMEDIATE ACTIONS:
1. Mark machine status = "breakdown" or "maintenance"
2. Identify affected work order (if any)
3. Calculate remaining work time
4. Trigger reallocation algorithm for affected work order

REALLOCATION LOGIC:
- Find next available machine with same capability
- IF no machine available:
  - Mark work order as "blocked"
  - Reallocate operator to next priority work order
  - Add work order to priority queue
- ELSE:
  - Reassign work order to new machine
  - Update estimated completion time
  - Notify planner of change

NOTIFICATION: Send alert to maintenance team and planner
```

### 3.2 Operator Availability Change
```
EVENT: Operator completes task / starts shift / goes on break

IMMEDIATE ACTIONS:
1. Update operator status
2. IF task completed:
   - Mark work order as "completed"
   - Log actual vs. estimated duration
3. IF operator now available:
   - Run allocation algorithm for pending work orders
   - Assign to highest priority eligible work order
4. IF operator unavailable:
   - Check if currently assigned
   - IF assigned: trigger emergency reallocation

OPTIMIZATION:
- Prefer assigning to work orders in same location
- Consider setup time when switching between tasks
```

### 3.3 Material Delay/Shortage Event
```
EVENT: Material shortage detected / delivery delayed

IMMEDIATE ACTIONS:
1. Identify all work orders requiring this material
2. Mark affected work orders as "blocked"
3. Calculate new expected availability time

CASCADING REALLOCATION:
FOR each blocked work order:
  1. Deallocate assigned resources
  2. Reassign operator to next eligible work order
  3. Reassign machine to next eligible work order
  4. Recalculate work order queue priorities

PROACTIVE MEASURES:
- Check if substitute materials available
- Trigger expedited procurement if critical
- Notify supply chain team

NOTIFICATION: Alert planner and procurement team
```

### 3.4 Event Processing Queue
```
Priority Queue for Events:
1. Critical breakdowns (immediate processing)
2. Safety incidents (immediate processing)
3. Material shortages (process within 1 minute)
4. Operator availability changes (process within 2 minutes)
5. Routine updates (process within 5 minutes)

Processing Rate: Handle up to 50 events/second
```

---

## 4. Simple Visualization Ideas for Planners

### 4.1 Real-Time Dashboard (Primary View)
```
┌─────────────────────────────────────────────────────┐
│  Resource Utilization Overview                       │
├─────────────────────────────────────────────────────┤
│  Operators:  [████████░░] 80%  (16/20 active)       │
│  Machines:   [██████░░░░] 60%  (12/20 running)      │
│  Materials:  [████████░░] 85%  (inventory level)    │
├─────────────────────────────────────────────────────┤
│  Avg Idle Time: 12 min  |  Active WO: 45/150       │
└─────────────────────────────────────────────────────┘
```

### 4.2 Interactive Gantt Chart
- **Horizontal Axis**: Timeline (current shift)
- **Vertical Axis**: Resources (operators/machines)
- **Color Coding**:
  - Green: In progress
  - Yellow: Scheduled/pending
  - Red: Blocked/delayed
  - Gray: Idle time
  - Blue: Maintenance
- **Interactive Features**: Click to view work order details, drag to reschedule manually

### 4.3 Allocation Matrix
```
                  Machine 1   Machine 2   Machine 3
Operator A        WO-101      [idle]      -
Operator B        -           WO-103      -
Operator C        WO-105      -           WO-107

Legend:
WO-### = Work Order ID
[idle] = Available but unassigned
- = Not capable/qualified
```

### 4.4 Alert & Exception Dashboard
```
┌─────────────────────────────────────────────┐
│  🔴 CRITICAL ALERTS                         │
├─────────────────────────────────────────────┤
│  • Machine M-05 breakdown (2 WO blocked)    │
│  • Material shortage: Steel-A (5 WO)        │
├─────────────────────────────────────────────┤
│  🟡 WARNINGS                                │
├─────────────────────────────────────────────┤
│  • Operator O-12 idle for 8 minutes         │
│  • WO-156 deadline risk (2 hours)           │
└─────────────────────────────────────────────┘
```

### 4.5 Work Order Flow Board (Kanban Style)
```
┌─────────┬─────────────┬─────────────┬──────────┐
│ PENDING │ IN PROGRESS │   BLOCKED   │ COMPLETE │
├─────────┼─────────────┼─────────────┼──────────┤
│ WO-201  │   WO-101    │   WO-145    │  WO-089  │
│ WO-202  │   WO-103    │   WO-147    │  WO-090  │
│ WO-203  │   WO-105    │             │  WO-091  │
│   (25)  │    (45)     │    (8)      │   (72)   │
└─────────┴─────────────┴─────────────┴──────────┘
```

### 4.6 Heatmap: Resource Demand vs. Capacity
```
        00:00  04:00  08:00  12:00  16:00  20:00
Skill-A  ░░    ████   ████   ████   ████   ░░░░
Skill-B  ░░    ████   ████   ██░░   ░░░░   ░░░░
Machine  ░░    ████   ████   ████   ██░░   ░░░░

Legend: ░ = Low demand, █ = High demand
```

---

## 5. Key Performance Indicators (KPIs)

### 5.1 Resource Utilization Metrics

**Operator Utilization Rate**
```
Operator Utilization = (Actual Working Time / Available Time) × 100

Target: >85%
Warning: <70%
Critical: <60%

Breakdown:
- Active time (assigned and working)
- Setup time (preparing for task)
- Idle time (available but unassigned)
- Unavailable time (break, shift end)
```

**Machine Utilization Rate**
```
Machine Utilization = (Running Time / Total Available Time) × 100

Target: >80%
Warning: <65%
Critical: <50%

Status Distribution:
- Running (productive)
- Idle (available but unused)
- Maintenance (scheduled)
- Breakdown (unplanned downtime)
```

### 5.2 Idle Time Metrics

**Average Idle Time per Operator**
```
Avg Idle Time = Σ(idle_periods) / Number of Operators

Target: <15 minutes/shift
Warning: >20 minutes/shift
Critical: >30 minutes/shift

Track by:
- Shift
- Department
- Skill level
```

**Average Idle Time per Machine**
```
Avg Idle Time = Σ(idle_periods) / Number of Machines

Target: <20 minutes/shift
Warning: >30 minutes/shift
Critical: >45 minutes/shift
```

### 5.3 Allocation Efficiency

**Number of Allocation Conflicts**
```
Daily Conflicts = Count of:
- Failed allocations due to missing resources
- Emergency reallocations
- Manual overrides

Target: <5 per day
Warning: 5-10 per day
Critical: >10 per day
```

**Reallocation Frequency**
```
Reallocation Rate = (Number of Reallocations / Total Allocations) × 100

Target: <15%
Warning: 15-25%
Critical: >25%

Reasons Breakdown:
- Machine breakdown
- Operator unavailable
- Priority changes
- Material shortage
```

### 5.4 Work Order Performance

**Work Order Throughput**
```
Throughput = Number of Completed Work Orders / Time Period

Measure by:
- Per hour
- Per shift
- Per day

Target: Based on historical average + 10%
```

**On-Time Delivery Rate**
```
OTD Rate = (WO Completed On Time / Total WO Completed) × 100

Target: >95%
Warning: 90-95%
Critical: <90%

Also track:
- Average delay time for late orders
- Delay reasons distribution
```

**Cycle Time Efficiency**
```
Cycle Time Efficiency = (Estimated Duration / Actual Duration) × 100

Target: 90-110% (close to estimate)
Warning: 80-90% or 110-120%
Critical: <80% or >120%
```

### 5.5 Cost Metrics

**Resource Cost per Work Order**
```
Cost = (Operator Hours × Hourly Rate) + 
       (Machine Hours × Operating Cost) + 
       (Material Costs)

Track trends to optimize allocation decisions
```

**Idle Time Cost**
```
Idle Cost = Σ(Idle Time × Resource Hourly Cost)

Target: <5% of total operating cost
```

### 5.6 Dashboard KPI Summary
```
┌──────────────────────────────────────────────────┐
│  Daily KPI Summary                    ✓ Target   │
├──────────────────────────────────────────────────┤
│  Operator Utilization:    87%          ✓ >85%   │
│  Machine Utilization:     82%          ✓ >80%   │
│  Avg Operator Idle:       12 min       ✓ <15min │
│  Avg Machine Idle:        18 min       ✓ <20min │
│  Allocation Conflicts:    3            ✓ <5     │
│  Work Order Throughput:   156          ✓ >150   │
│  On-Time Delivery:        96%          ✓ >95%   │
│  Reallocation Rate:       12%          ✓ <15%   │
└──────────────────────────────────────────────────┘
```

---

## 6. System Architecture & Technical Requirements

### 6.1 System Components

**Core Modules:**
1. **Allocation Engine** (real-time scheduler)
2. **Event Processor** (handles real-time updates)
3. **Data Manager** (maintains resource states)
4. **Notification Service** (alerts and updates)
5. **Visualization Engine** (dashboard and reports)
6. **API Gateway** (integration with ERP/MES)

### 6.2 Scalability Design

**For 100-200 Concurrent Work Orders:**
- Processing capacity: 1000 allocations/minute
- Event handling: 50 events/second
- Database: Optimized indexes on frequently queried fields
- Caching: Redis for active work orders and resource states
- Load balancing: Distribute allocation calculations

**Performance Targets:**
- Allocation decision: <500ms
- Event response: <2 seconds
- Dashboard refresh: Real-time (websockets)
- Data persistence: <100ms

### 6.3 Data Update Frequency

- Resource status: Every 30 seconds
- Work order progress: Every 1 minute
- KPI calculations: Every 5 minutes
- Full system reconciliation: Every 15 minutes

### 6.4 Integration Points

**Input Systems:**
- ERP (work orders, materials)
- CMMS (machine status, maintenance)
- HRM (operator schedules, skills)
- Warehouse Management (material inventory)

**Output Systems:**
- MES (production execution)
- BI Tools (reporting and analytics)
- Mobile Apps (operator notifications)

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- Data model implementation
- Basic allocation algorithm
- Core database setup
- Simple dashboard prototype

### Phase 2: Intelligence (Weeks 5-8)
- Advanced scoring function
- Real-time event handling
- Reallocation logic
- Alert system

### Phase 3: Visualization (Weeks 9-10)
- Gantt chart implementation
- KPI dashboards
- Allocation matrix
- Alert dashboard

### Phase 4: Optimization (Weeks 11-12)
- Performance tuning
- Scalability testing
- Integration with existing systems
- User training

### Phase 5: Go-Live (Week 13)
- Pilot with 20-30 work orders
- Monitor and adjust
- Gradual scale-up to full capacity

---

## 8. Success Criteria

**Quantitative:**
- 20% reduction in average idle time
- 15% improvement in throughput
- >95% on-time delivery rate
- <5% reallocation rate

**Qualitative:**
- Easy to use for planners
- Quick response to disruptions
- Improved visibility into operations
- Reduced manual intervention

---

## 9. Risk Mitigation

**Potential Risks:**
1. **Over-optimization**: Too frequent reallocations causing instability
   - Mitigation: 15-minute stability buffer, minimum improvement threshold

2. **Data quality**: Inaccurate resource data leading to poor decisions
   - Mitigation: Real-time validation, operator feedback loops

3. **System adoption**: Resistance to automated scheduling
   - Mitigation: Manual override capability, gradual rollout, training

4. **Performance degradation**: System slows with scale
   - Mitigation: Load testing, caching strategy, horizontal scaling

---

## 10. Maintenance & Support

**Daily:**
- Monitor system health
- Review allocation conflicts
- Address critical alerts

**Weekly:**
- Analyze KPI trends
- Fine-tune allocation parameters
- Review operator feedback

**Monthly:**
- System performance audit
- Algorithm optimization review
- Capacity planning assessment

---

**End of Design Plan**

This system design provides a practical, scalable solution for dynamic resource allocation with real-time optimization capabilities while maintaining operational stability and ease of use for planners.
