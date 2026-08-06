# HR-30W release specification — untethered walking

Document ID: HR-REL-30W  
Revision: 0.1  
Program baseline: HR-30-SYS-R0.2  
Status: required end state; detailed design and test evidence not released

## Capability earned

The robot stands, starts, walks, turns, stops, and returns to quiet standing without external support on the released level indoor surface.

## Included configuration

- Released 25-axis walking configuration and real-time control stack.
- Professionally assembled protected four-series battery with pack fuse, BMS, precharge, service disconnect, independent telemetry, qualified enclosure, and released charging/storage procedure.
- Padded, access-controlled test area with no person inside the fall envelope.
- Released fall response, boundary monitoring, logging, and configuration control.

## Entry conditions

- HR-30D W3 acceptance and W4 fall characterization pass.
- Safe power-loss behavior, battery system, containment, thermal limits, test corridor, and operating procedure receive independent review.
- Every open critical or high walking risk is closed or formally accepted by authorized reviewers.

## Acceptance criteria

- Stand unsupported for 120 seconds.
- Start, walk 25 m at 0.10–0.20 m/s, stop within two steps, and remain standing.
- Complete five left and five right 90-degree turns within five steps each.
- Complete 30 minutes cumulative walking without exceeding released thermal or energy limits.
- Repeat the course ten times with at least nine complete successes, no hazardous failure, no corridor departure, and no padded-boundary contact.
- Logs match the released CAD, wiring, firmware, calibration, actuator, battery, and BOM configuration.

## Required evidence

Approved W4/W5 records including WALK-001 through WALK-012, battery inspection, fall-characterization evidence, corridor records, ten scored course logs, and final configuration audit.

## Boundary

Passing HR-30W authorizes controlled engineering operation only. It does not authorize walking among people, public deployment, or child-adjacent operation.
