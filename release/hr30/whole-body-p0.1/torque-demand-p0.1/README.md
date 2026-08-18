# HR-30 whole-body torque demand P0.1

**PRELIMINARY - INVERSE-DYNAMICS DESIGN EVIDENCE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION**

This package converts the two complete 50 Hz walking references into an inverse-dynamics torque-demand envelope for all 23 rotary axes. It reports the contact-enabled, open-chain and gravity-only cases separately and compares them with the existing candidate current endpoint and published stall-output screens.

The result is a design input, not motion approval. MuJoCo's inverse result is model-specific, the pelvis is held by an ideal numerical fixture, contacts are soft, and neither current endpoint nor published stall torque is a continuous-duty rating.
