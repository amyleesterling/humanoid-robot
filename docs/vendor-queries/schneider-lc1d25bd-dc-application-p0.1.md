# Schneider LC1D25BD DC application request P0.1

Status: **UNSENT - PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, TESTING, OR ENERGIZATION**

This is a prepared technical-support request. It must not be sent until every row marked `required_before_supplier_query=yes` in `electrical/contactor/hr-v0-lc1d25bd-application-inputs-p0.2.csv` has accepted evidence and the program owner separately authorizes supplier contact.

## Subject

Application disposition request: two LC1D25BD contactors, three poles in series per device, 12 VDC electronic/regenerative robot load

## Draft request

Project Button is evaluating two Schneider Electric `LC1D25BD` contactors as redundant final switching elements for a guarded bench robot prototype in Boston, Massachusetts, USA. Each device has its three main poles connected in series. The two devices are then connected in series with each other:

`12 V source -> protection -> K1 1L1-2T1 -> 3L2-4T2 -> 5L3-6T3 -> K2 1L1-2T1 -> 3L2-4T2 -> 5L3-6T3 -> electronic actuator bus`

Both coils are the integral 24 VDC `BD` version. K1 and K2 are commanded by separate safety-relay outputs. Their integral `21-22` NC mirror contacts are proposed in the external-device-monitoring return. No claim of application suitability or functional-safety performance is being made.

The load contains electronic servo drives, bus capacitance, wiring inductance and possible reverse/regenerative current. It is not being classified as DC-1 by assumption. Schneider catalog `MKTED210011EN`, July 2026, version 17.1, pages A5/120-A5/123 provides DC-1 through DC-5 tables and warns that lower current can reduce durability because of critical current. The current historical 11.1 A summed stall-endpoint screen is not a measured break current and is below the catalog's 32 A / 24 V LC1D25 row.

Before sending, attach an accepted configuration drawing and populate this exact measured envelope:

- normal contact current: **SELECTION REQUIRED A**;
- peak forward contact current: **SELECTION REQUIRED A**;
- current at commanded opening: **SELECTION REQUIRED A**;
- current at E-stop opening: **SELECTION REQUIRED A**;
- maximum reverse/regenerative current: **SELECTION REQUIRED A**;
- contact voltage during opening: **SELECTION REQUIRED V**;
- downstream bus capacitance: **SELECTION REQUIRED uF**;
- accepted equivalent time constant or `L/R`: **SELECTION REQUIRED ms**;
- source current-limit and regeneration response: **SELECTION REQUIRED**;
- prospective fault current at K1 input: **SELECTION REQUIRED A**;
- upstream/downstream protection and interrupting capacities: **SELECTION REQUIRED**;
- conductor/terminal details, lengths and routing: **SELECTION REQUIRED**;
- ambient, enclosure, duty and mounting orientation: **SELECTION REQUIRED**;
- required operations, service life and maximum cycles/hour: **SELECTION REQUIRED**; and
- maximum permitted opening, rail-decay and total stopping time: **SELECTION REQUIRED ms**.

Please provide an identifiable written disposition addressing:

1. whether `LC1D25BD` is suitable for the submitted measured 12 VDC electronic/capacitive/regenerative envelope with all three main poles in series;
2. the applicable utilization category or other Schneider application classification;
3. the catalog critical-current warning and expected electrical durability at the submitted currents and required life;
4. permitted reverse/regenerative current and contact-voltage transient behavior;
5. required protection/coordination and any source/capacitance/time-constant limitations;
6. whether both power and load may use the shown pole direction and jumper sequence;
7. permitted mounting orientation, ambient, enclosure and cycles/hour;
8. whether the integral `21-22` NC auxiliary is the correct mirror contact for external-device monitoring in this exact device; and
9. any mandatory inspection, replacement or maintenance interval for this application.

Please cite the applicable Schneider document revision/date and identify any assumptions or limits in the response. If `LC1D25BD` is not suitable, please state that directly and recommend the exact Schneider family/application route only if the submitted envelope supports doing so.

## Contact boundary

No supplier contact has occurred. No email, web ticket or telephone request has been sent. A response cannot by itself release wiring, protection, functional safety, fabrication, motion or energization; it must be archived, configuration-matched and independently reviewed with the physical evidence.
