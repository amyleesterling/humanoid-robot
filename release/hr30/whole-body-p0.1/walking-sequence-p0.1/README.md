# HR-30 whole-body walking sequence P0.1

**PRELIMINARY - SIMULATOR-ONLY KINEMATIC SEQUENCE - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION**

This package converts the active 9.901 kg tether-first whole-body model into two complete 50 Hz minimum-jerk step candidates. Each sequence begins in neutral double support, crouches, transfers weight, lifts one foot, reaches a 40 mm capture-step target and ends in a nominally flat double-support touchdown. All 25 joint positions, velocities and accelerations are present at every sample, and the exact keyframes are loadable in the tether MJCF model.

The web guide animates the entire body from the generated link transforms. It is an engineering visualization and simulator handoff, not a motion-control interface. No DYNAMIXEL packet, actuator ID, torque-enable request or firmware command is emitted.

Positive projected-COM margin and in-limit interpolation are narrow kinematic screens. They do not establish dynamic balance, actuator capability, contact behavior, tracking, collision clearance, fall restraint, stopping, recovery or safety.
