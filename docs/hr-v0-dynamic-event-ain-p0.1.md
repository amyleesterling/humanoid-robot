# HR-V0 low-loading isolated event acquisition P0.1

> **PRELIMINARY - BENCH R&D EQUIPMENT ONLY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-DYN-EVENT-AIN-P0.1`

Date: 2026-08-10

## Decision

Seven TI `AMC3330EVM` boards are the preferred evaluation route for observing seven separate 24 V-class safety/control events without the approximately 2.25 mA typical input load of the R176 `ISO1212EVM` candidate. Each channel has its own isolation barrier and drives one adjacent LabJack T7 differential AIN pair. The R176 direct digital-input candidate is retained as historical evidence but is not preferred for field connection.

This change does **not** make any field tap connectable. TI specifies only a ±1 V differential input for AMC3330 and warns that the EVM is not certified for high-voltage operation. Every channel therefore needs a separately engineered divider/protection adapter. Exact field envelopes, allowed parallel current, resistor values, ratings, protection, creepage, clearance and fault behavior remain `SELECTION REQUIRED`.

## Exact output-side allocation

| EVM | Project event candidate | EVM output | T7 differential pair | DB37 pins |
|---|---|---|---|---|
| EVM1 | `SR1_S12` | J3.2 OUTP / J3.1 OUTN | AIN0-AIN1 | DB37-37/18 |
| EVM2 | `SR1_START_RETURN` | J3.2 OUTP / J3.1 OUTN | AIN2-AIN3 | DB37-36/17 |
| EVM3 | `ARM_AFTER_S2` | J3.2 OUTP / J3.1 OUTN | AIN4-AIN5 | DB37-35/16 |
| EVM4 | `K1_A1` | J3.2 OUTP / J3.1 OUTN | AIN6-AIN7 | DB37-34/15 |
| EVM5 | `K2_A1` | J3.2 OUTP / J3.1 OUTN | AIN8-AIN9 | DB37-33/14 |
| EVM6 | `EDM_K1_OUT` | J3.2 OUTP / J3.1 OUTN | AIN10-AIN11 | DB37-32/13 |
| EVM7 | `SRA1_START_RETURN` | J3.2 OUTP / J3.1 OUTN | AIN12-AIN13 | DB37-31/12 |

All EVM J3.3 and J1.2 logic grounds share the DAQ-side reference. EVM J1.1 requires a selected 3.0 V to 5.5 V bench supply. No T7 `VS` power-budget claim is made. AIN0-AIN3 may be connected at only one T7 terminal location because LabJack duplicates those channels internally.

## Field-side boundary

EVM J2.1 is INP. J2.2 INN must be tied externally to J2.3 HGND through the accepted input network. Direct application of a 24 V-class node to J2 is prohibited. The candidate does not assign a divider ratio, resistor value, voltage rating, surge protector or connector because the seven field envelopes and permissible node loading have not been established.

## Timing boundary

The candidate scan has eight addresses: seven differential AIN results and one `FIO_STATE` trigger-witness word. LabJack states that T7 acquisition is sequential, not simultaneous. At the manufacturer's typical 100 ksamples/s maximum under ±10 V and resolution-index 0 or 1 conditions, 12.5 kscan/s is only an arithmetic upper screen. Actual scan order, interchannel skew, settling, thresholds, overflow behavior and combined uncertainty must be frozen and measured on received hardware.

## Safety boundary

The EVMs, T7, host, thresholds and stored traces receive **ZERO SAFETY CREDIT**. They may observe only. They may not command motion, maintain actuator power, defeat a protective circuit or justify energization. `EG-025` remains open and `EG-026` remains partial.
