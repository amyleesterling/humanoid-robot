# HR-V0 fabrication capability and DFM packets P0.1

**Identifier:** `HR-V0-FAB-RFI-P0.1`

**Status:** **PRELIMINARY - CAPABILITY/DFM REQUEST ONLY - NOT A PURCHASE ORDER - DO NOT FABRICATE**

## Purpose

R50 selected safe quotation routes but did not provide bounded upload artifacts. R51 generates three deterministic inquiry ZIPs under [`release/hr-v0/fabrication-rfi/`](../release/hr-v0/fabrication-rfi/). They request written capability, DFM, budgetary cost and lead-time information only.

| Packet | Route | Payload boundary |
|---|---|---|
| `RFI-001` | `FAB-001` / `FAB-002` one-stop CNC | Finished candidate STEP plus readable SVG drawings for `MV0-001` through `MV0-003`; no DXF and no profile-only blank |
| `RFI-002` | `FAB-003` profile operation | Only the zero-hole `PROFILE_ONLY_RFQ` STEP/DXF, blank manifest and route guide; no finished geometry or drawing |
| `RFI-003` | `FAB-004` local secondary machining | Both traceable blank geometry and finished candidate STEP/drawings for capability and fixture discussion; no work authorization |

No packet is generated for `FAB-005`, `FAB-006`, or `FAB-007`. FabVille remains prototyping/training only, Boston Public Library remains excluded from the structural-metal route on checked evidence, and `MV0-004` remains on site hold.

## Configuration control

Each ZIP contains:

- `README-FIRST.txt`, which states the authorization boundary and supplier questions;
- `MANIFEST.csv`, which binds every payload file to its repository path, byte count and SHA-256; and
- the exact controlled payload under `payload/`.

ZIP member timestamps are fixed to 1980-01-01, files are stored without compression, and member permissions are fixed. Regeneration is therefore byte-for-byte deterministic. [`packet-index.csv`](../release/hr-v0/fabrication-rfi/packet-index.csv) records each ZIP's outer hash, size, payload count, permitted action, forbidden action and state.

The generator is [`tools/generate_hr_v0_fabrication_rfi_packets.py`](../tools/generate_hr_v0_fabrication_rfi_packets.py). The checker independently opens every ZIP, verifies exact membership, timestamps, stored bytes, internal hashes, source equality, route-specific exclusions, packet-index hashes and the absence of PDFs. It also proves that `MV0-004` is absent.

## Use sequence

1. Run the packet generator and checker from a clean controlled commit.
2. Choose only the packet matching the intended capability inquiry.
3. Record the packet SHA-256 from `packet-index.csv` in the supplier-response row.
4. Send as an inquiry, not an order. Do not accept portal language that automatically authorizes manufacture.
5. Record every response in [`tests/forms/hr-v0-fabrication-supplier-quote-template.csv`](../tests/forms/hr-v0-fabrication-supplier-quote-template.csv), including assumptions, substitutions, quote expiry and DFM exceptions.
6. Compare routes only after received-interface coupons freeze finished dimensions and tolerances.
7. Obtain qualified mechanical disposition before separately authorizing one first article.

The first-article authorization must be a new controlled artifact tied to the selected supplier, exact process, exact drawing revision, exact hashes and numerical acceptance criteria. These packets cannot be relabeled into that authorization.

## Remaining holds

- Critical finished-hole sizes and position tolerances remain `SELECTION REQUIRED`.
- Protolabs' advertised 6061-T651 and the project's 6061-T6 callout require explicit disposition.
- The two-process route requires secondary-shop datum/fixture control and material traceability.
- No supplier response, quote, DFM acceptance, material certificate or FAI exists.
- `EG-006` remains partial.

No packet authorizes procurement, fabrication, assembly or energization.
