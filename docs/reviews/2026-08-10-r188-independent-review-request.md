# R188 independent review request - Q4X quote readiness

> **PRELIMINARY - COMMERCIAL EVIDENCE AMENDMENT ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review the exact commit containing artifact `HR-V0-Q4X-QUOTE-READINESS-P0.1`.

## Reproduce

```text
python tools/generate_hr_v0_q4x_quote_readiness_p01.py
python tools/check_hr_v0_q4x_quote_readiness_p01.py
```

## Required challenge

1. Reopen the direct DigiKey pages for Hammond `14F0907` and Phoenix Contact `1464484`. Confirm exact MPN, seller code, one-unit USD price, stock state, lead-time wording and any tariff notice.
2. Confirm `14F0907-ND` is the exact direct product line rather than the R187 associated-product reference. Distinguish factory stock from DigiKey shelf stock.
3. Confirm `277-1464484-ND` showed zero immediate stock. Do not convert an eight-week manufacturer standard lead time into a promised delivery date.
4. Independently reproduce the $211.63 fit-lot, $22.83 PTCB-lot and $234.46 combined snapshots from the frozen R187 lines plus the $0.33 panel delta.
5. Confirm shipping, sales tax, tariff, fees, allocation and price movement remain excluded.
6. Confirm the fit lot is ready only for a same-session cart or written quote and that the PTCB lot remains supply-blocked. No substitution is authorized.
7. Confirm every cart, quote, purchase, order, receiving, drilling, fabrication, connection, powered-test, motion and energization state remains negative.

Report BLOCKER / MAJOR / MINOR findings with exact file, row, seller source and correction. Review provides no purchase, work, safety or energization authority.
