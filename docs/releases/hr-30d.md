# HR-30D release specification — tethered walking

Document ID: HR-REL-30D  
Revision: 0.1  
Program baseline: HR-30-SYS-R0.2  
Status: future gate; detailed design and test evidence not released

## Capability earned

The robot performs dynamic level-floor gait while a slack overhead tether arrests falls but does not carry its weight during scored trials.

## Included configuration

- HR-30C body, sensing, real-time controller, segmented joint buses, and independent fall/safety monitor.
- External current-limited 14.0–14.8 V tethered power.
- Rated slack fall-arrest tether and guarded test cell.
- Start, walk, turn, stop, controlled-kneel, tether-arrest, and power-cut states.

## Entry conditions

- HR-30C acceptance and walking-verification W2 pass.
- Sacrificial-mass tether arrest tests and reviewed dynamic-arrest procedures pass before any robot fall trial.
- Released gait, terrain, stop, fall, thermal, current, bus-deadline, and sensor-validity limits are configured.

## Acceptance criteria

- Tether load remains below 2% of robot weight except during an arrest.
- Ten 10 m trials complete at 0.08–0.15 m/s with starts, stops within two steps, and both 90-degree turn directions.
- The robot accumulates at least 10 minutes of motion without exceeding released thermal, current, voltage, energy, or deadline limits.
- Injected loss of high-level planner, one foot sensor, degraded IMU, low supply voltage, and commanded stop produces the defined response.
- Complete synchronized logs and configuration evidence exist for every scored trial.

## Required evidence

Approved W3 records including WALK-005, TEST-WALK-005 through TEST-WALK-007, tether-load measurement, arrest-test evidence, fault-injection records, and configuration audit.

## Boundary

HR-30D is not untethered walking and does not authorize operation near people or children.
