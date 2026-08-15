# HR-30 energy and safety spine P0.1

**PRELIMINARY - ENERGY/SAFETY ARCHITECTURE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This package replaces the unsafe architectural assumption that a nominal 14.8 V 4S LiPo can directly feed actuators whose published maximum is also 14.8 V. The first whole-robot configuration is now **tether-first**: a qualified external enclosure contains the mains supply, safety relay and two series contactors, while the robot receives a controlled touch-safe DC feed and distributes it through eight still-unselected protected branches.

The 179 W operating budget is 14.92 A at 12 V. The 727 W short-peak estimate is 60.58 A. The 41.7 A tether-supply candidate and the later 18 A continuous / 40 A for 2 s battery candidate therefore both require deterministic current and torque caps; neither closes the provisional peak by itself.

The three XC330 TTL branches use a 9 V regulator candidate rather than an unregulated 12 V rail. The XH/XM branches use the controlled main rail. Exact regulation, protection, wiring, thermal behavior and fault response remain open.

Reset only makes the safety outputs eligible. It cannot command motion. No functional-safety approval, wiring release, protection selection, connection approval or permission to energize is granted here.

Open the [interactive energy and safety guide](index.html), then inspect `configuration-register.csv`, `power-tree-register.csv`, `safety-function-boundary.csv`, `terminal-interface-register.csv`, and `unresolved-input-register.csv`.
