# HR-V0 Lot A supplier and metrology inquiry P0.2

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-LOT-A-INQUIRY-P0.2**  
Date: 2026-08-11  
Parents: `HR-V0-LOT-A-SRC-P0.1`, `HR-V0-EVAL-ACQ-P0.1`, `HR-V0-JOINT-MET-P0.2`

## Result

R255 consolidates the stale, fragmented Lot A inquiry records into a current, send-ready but **UNSENT** evidence package. It does not send messages, request stock reservation, place an order, disclose a private address, select a provider or authorize work.

Two independent paths are controlled:

- ROBOTIS America sales/orders and technical-support inquiries resolve the `XM540-W270-T` title/SKU/TTL versus `XM540-W270-R` package-table conflict, exact contents/revision/origin, allocation, no-substitution, shipping/return terms and the absence or presence of official assembly hardware/torque/reuse instructions.
- Three Boston-area metrology research candidates receive provider-specific questions and separate `BID`/`NO BID` rows for each of R254's five methods. Published capability is not method acceptance.

The [interactive guide](../release/hr-v0/lot-a-inquiry-p0.2/index.html) presents five routes, 12 ROBOTIS questions, 32 unique metrology questions repeated into 96 independently attributable provider rows, 15 method-bid rows, 18 required returned-evidence records, 15 decision gates and 14 workflow steps.

## Recipient isolation and transmission control

Each route has its own blank response workbook and message hash. The two ROBOTIS workbooks contain only their eight sales/order or four technical questions. Each metrology candidate workbook contains only that provider's 32 rows. No provider receives another provider's bid surface.

Every transmittal retains:

- sender identity: `SELECTION REQUIRED`;
- reply address: `SELECTION REQUIRED`;
- send authorization: `NOT AUTHORIZED`; and
- sent state: `NOT SENT`.

The package contains no final ship-to address, payment credential or personal contact detail. Any later transmission must name the exact recipient, sender, reply address, message and attachment hashes in a separately signed authorization.

## Current official contact evidence

Official pages were rechecked on 2026-08-11:

- [ROBOTIS Support](https://www.robotis.us/Support) publishes `cs@robotis.com` and `949-377-0377`;
- [ROBOTIS Contact Us](https://www.robotis.us/contact-us/) publishes `america@robotis.com` and the same phone number;
- [ROBOTIS shipping/return policy](https://www.robotis.us/shipping-returns-warranty/) directs domestic insurance and shipping questions to `america@robotis.com` and requires an RMA route for returns;
- [East Coast Metrology](https://eastcoastmetrology.com/services/) publishes Topsfield CMM/scan and contact capabilities;
- [3D ProScan](https://www.3dproscan.com/metrology-services.html) publishes Clinton CMM, vision and balance capabilities and ISO 9001—not an ISO/IEC 17025 result scope; and
- [Celero Partners](https://celeropartners.com/) publishes Woburn scanning capability and contact details, but no CMM, calibration, traceability or uncertainty claim is inferred.

These pages identify inquiry routes only. Exact equipment, serials, calibration, accreditation scope, method, uncertainty, availability, price and application acceptance require written returned evidence and qualified disposition.

## Decision separation

Fifteen open gates prevent collapsing unlike decisions:

1. authorizing information-only transmission;
2. accepting supplier identity, contents and no-substitution evidence;
3. accepting an unexpired quote and maximum spend;
4. authorizing a receipt/quarantine-only purchase;
5. receiving and reconciling exact articles;
6. accepting provider identity, equipment, calibration, scope, methods and uncertainty by method;
7. commercially selecting a provider;
8. authorizing article shipment and work; and
9. separately authorizing any temporary threaded assembly.

No gate is closed. No response, quote, article or physical evidence exists.

## Configuration effect

`HR-V0-CONFIG-REC-P0.19` supersedes P0.18 as the configuration record only. R255 supersedes `HR-V0-LOT-A-SRC-P0.1` and `HR-V0-EVAL-ACQ-P0.1` for current inquiry planning while preserving their historical source/price/provider evidence. P0.19 contains 38 current records, 30 supersession records, 97 open holds and 130 blank/unexecuted acceptance rows.

R255 closes zero Sol blockers and supplies no procurement, fabrication, assembly, connection, powered-test, motion, functional-safety or energization authority.

