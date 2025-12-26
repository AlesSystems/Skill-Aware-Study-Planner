# Phase 3 — Intelligence & Decision Layer

Goal: Add higher-level reasoning so the planner makes informed decisions under constraints, not just recalculations.

---

## TICKET-301: Topic Dependency Graph

**Type:** Feature  
**Priority:** Critical  

### Description
Model dependencies between topics (prerequisites and follow-ups).

### Examples
- Recursion → Dynamic Programming
- Graph Basics → Shortest Path Algorithms

### Requirements
- Directed dependency graph
- Detect circular dependencies
- Support multiple prerequisites

### Acceptance Criteria
- Dependencies stored and validated
- Planner respects prerequisite order
- Blocked topics are deprioritized automatically

---

## TICKET-302: Dependency-Aware Priority Adjustment

**Type:** Feature  
**Priority:** Critical  

### Description
Adjust topic priorities based on dependency status.

### Rules
- If prerequisite skill < threshold → boost prerequisite priority
- Dependent topic priority capped until prerequisite improves

### Acceptance Criteria
- Planner never recommends advanced topics too early
- Prerequisites rise naturally in plan

---

## TICKET-303: Time Constraint Optimization Engine

**Type:** Feature  
**Priority:** High  

### Description
Optimize study allocation under limited available time.

### Inputs
- Daily available hours
- Exam proximity
- Topic priority
- Dependency constraints

### Output
- Optimal subset of topics
- Time allocation per topic

### Acceptance Criteria
- Total allocated time ≤ available time
- Low-value topics dropped when time is scarce
- High-impact topics preserved

---

## TICKET-304: What-If Scenario Simulator

**Type:** Feature  
**Priority:** High  

### Description
Allow users to simulate different study strategies.

### Scenarios
- “What if I study 2h/day instead of 4?”
- “What if I ignore low-weight topics?”
- “What if exam is moved earlier?”

### Acceptance Criteria
- Simulations do not modify real data
- Results include projected skill levels
- Clear comparison output

---

## TICKET-305: Expected Exam Score Estimator

**Type:** Feature  
**Priority:** High  

### Description
Estimate expected exam performance based on current skills and weights.

### Model
- Weighted sum of topic skills
- Penalty for dependencies not satisfied
- Uncertainty margin included

### Output
- Estimated score range
- Risk indicators per topic

### Acceptance Criteria
- Estimates update dynamically
- High-risk topics clearly identified
- Model behavior documented

---

## TICKET-306: Study Strategy Comparison Engine

**Type:** Feature  
**Priority:** Medium  

### Description
Compare multiple study strategies and rank them.

### Strategies
- Balanced revision
- High-weight focus
- Weak-topic focus

### Acceptance Criteria
- Strategies evaluated on same constraints
- Clear ranking provided
- Best strategy highlighted with explanation

---

## TICKET-307: Drop-or-Skip Topic Advisor

**Type:** Feature  
**Priority:** Medium  

### Description
Advise the user when a topic is not worth studying given constraints.

### Criteria
- Low weight
- High time cost
- Low dependency impact
- Imminent exam

### Acceptance Criteria
- Advisor explains reasoning
- User can override advice
- Decisions logged

---

## TICKET-308: Risk Analysis & Warning System

**Type:** Feature  
**Priority:** High  

### Description
Identify risk factors that threaten exam success.

### Risk Examples
- Critical prerequisite not mastered
- Overconfidence (high self-assessment, low quiz score)
- Insufficient remaining time

### Acceptance Criteria
- Risks listed clearly
- Severity levels assigned
- Risks affect planning decisions

---

## TICKET-309: Decision Trace & Explainability

**Type:** Feature  
**Priority:** Medium  

### Description
Expose why the planner made specific recommendations.

### Examples
- “Topic X prioritized because weight=0.3 and skill=45”
- “Topic Y delayed due to unmet prerequisite”

### Acceptance Criteria
- Planner outputs explanations
- Decisions are traceable
- Logic is transparent to user

---

## TICKET-310: Phase 3 Documentation

**Type:** Task  
**Priority:** Medium  

### Description
Document the intelligence layer.

### Content
- Dependency graph design
- Optimization logic
- Score estimation model
- Decision explainability

### Acceptance Criteria
- README updated
- Examples provided
- Phase 3 behavior clearly understood

---

## Phase 3 Definition of Done

- Planner respects topic dependencies
- Decisions adapt to time pressure
- Users can simulate strategies
- Planner explains its decisions
- System advises what to skip
