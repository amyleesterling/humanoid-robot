# HR-V0 Boston Fabrication and Custom-Metal Sourcing

Status: **SOURCING RESEARCH — NOT A RELEASED MANUFACTURING PACKAGE**

Research date: 2026-08-06

Region: Boston, Massachusetts, USA

## Recommended path

Design HR-V0 so that most custom structure is two-dimensional cut or simple bent sheet, while bearings, shafts, spacers, standoffs, fasteners, and actuator frames are purchased standard parts. Reserve precision milling or turning for the smallest possible set of supported joint hubs and shafts.

This route best matches a light-duty robot without treating a low payload as permission to use unverified structure. Every load-bearing part still needs a released drawing, material/temper, tolerance, calculation, inspection method, and proof test.

### Manufacturing split

| Part class | Preferred process | Release file and notes |
|---|---|---|
| Base, upright cheeks, link side plates, guards, adapter plates | Laser or waterjet cut sheet; bend only where useful | DXF plus dimensioned PDF; specify alloy/temper, thickness, grain-sensitive bend direction where applicable, deburr/edge-break, and finish |
| Simple bent brackets and trays | Brake-formed 5052-H32 aluminum | Flat DXF and controlled formed STEP/drawing; supplier confirms bend radius and deduction |
| Flat stiff plates without bends | 6061-T6 aluminum where calculation supports it | DXF and drawing; do not substitute material or thickness without engineering disposition |
| Shoulder/elbow bearing hubs or precision spacers | CNC mill/lathe only if standard hardware cannot close the design | STEP plus dimensioned drawing with fits, datums, surface finish, threads, inspection, and material |
| Shafts, bearings, collars, spacers, standoffs, fasteners | Off-the-shelf catalog parts | Exact manufacturer part number and controlled BOM entry |
| Covers, cable guides, soft gripper fingers, drill/assembly fixtures | 3D print | Native CAD/STL, material, orientation, settings, and inspection; not a primary load path unless separately justified |

Plasma cutting is useful for prototypes and thicker steel but generally leaves a wider kerf and rougher edge than laser or waterjet. Do not assign bearing fits, precision datums, or small critical holes directly to a plasma-cut edge without a documented secondary machining operation.

## Boston-area hands-on options

### 1. Artisans Asylum — Allston

Artisans Asylum is the strongest local candidate because its official shop list includes machine, metal, CNC plasma, electronics/robotics, digital fabrication, and finishing facilities. Its CNC plasma shop lists a 4 ft × 8 ft Torchmate system for steel, aluminum, and stainless, and says members and day-pass users must complete tool testing. Day passes, classes, private lessons, and memberships are offered.

- Location: 96 Holton Street, Allston, MA 02134
- Contact: front-desk@artisansasylum.com; (617) 800-9010
- Verify before relying on it: current mill/lathe availability and certification, aluminum thickness/grade rules, minimum feature guidance, whether member-supplied stock is allowed, metrology access, and whether a qualified mentor can review bearing/shaft work.
- Official sources: [Artisans Asylum](https://www.artisansasylum.com/home), [CNC plasma shop](https://www.artisansasylum.com/shops/cnc-plasma), and [tool testing](https://www.artisansasylum.com/tool-testing-safety-training).

### 2. Mill Forge Makerspace — Norwood

Mill Forge describes a roughly 6,000 sq ft facility with CNC/3D, electronics, metalwork/welding, laser, and router capability, with training and 24/7 access for certified members. It is a credible secondary option, especially for prototyping and general metal fabrication.

- Location: 61 Endicott Street, Building 46, Norwood, MA 02062
- Contact: info@millforge.org; (781) 801-1818
- Verify before relying on it: exact CNC and laser makes/models, whether their laser is metal-capable, metal-milling capability, allowed alloys/thicknesses, tolerance and inspection tools, certification schedule, and project/storage fees.
- Official sources: [Mill Forge](https://millforge.org/) and [contact/FAQ](https://millforge.org/contact/).

### Library or other makerspace

Treat “has a CNC” as unconfirmed until the following checklist is answered. Many library CNC machines are routers limited to wood, foam, or approved plastics.

- Machine make/model and current operating status.
- Approved materials; specifically ask about aluminum, acetal, and fiber-reinforced plastics.
- Work envelope, spindle power/speed, workholding, tooling, coolant/chip-control, and stock thickness limits.
- Supported CAM workflow and file types; ask whether staff require their own CAM and whether STEP/DXF is accepted.
- Required class, certification, supervision, reservation duration, cost, and age/residency/card rules.
- Published accuracy is not enough: ask what tolerance staff will accept for a real part and what calipers, micrometers, height gauges, or bore gauges are available.
- Whether outside stock, cutting fluid, drilling/reaming, thread tapping, and repeat setups are allowed.

Use a library router for templates, plastics, fixtures, or noncritical prototypes unless its staff explicitly authorize metal and the released process can meet the drawing.

## Online manufacturing fallbacks

### SendCutSend

Best fit for flat and formed sheet parts because the supplier offers online laser/waterjet cutting with services such as bending, tapping, countersinking, hardware insertion, and finishing. The project should obtain actual quotes only after the controlled DXF and drawing exist. [Official site](https://sendcutsend.com/)

### Xometry

Best fit for the few genuinely three-dimensional milled or turned parts. Xometry accepts CAD/drawings and offers CNC milling/turning plus sheet-metal processes and inspection options. Its published general metal machining tolerance is ±0.005 in unless otherwise specified; critical fits must therefore be explicitly called out and quoted, not assumed. [Official CNC service](https://www.xometry.com/capabilities/cnc-machining-service/) and [official aluminum fabrication service](https://www.xometry.com/capabilities/sheet-metal-fabrication/aluminum-fabrication/)

These are sourcing candidates, not approved suppliers. Material certificates, inspection level, traceability, lead time, cost, and conformance must be selected per part and retained in the release evidence.

## Quote package required from this project

Do not send a visual mesh or website model to a fabricator as the manufacturing definition. Each custom metal part needs:

1. Unique part number and revision.
2. Native CAD plus neutral file: DXF for flat profiles and STEP for machined/formed geometry.
3. Dimensioned drawing with datums, tolerances, threads, fits, surface/edge condition, and inspection points.
4. Material alloy, temper, thickness, and permitted substitutions.
5. Finish, masking, hardware insertion, and post-process requirements.
6. Quantity, mating-part references, and revision-compatible assembly drawing.
7. Supplier quotation, DFM exceptions, material/conformance evidence, and received-part inspection record.

## Cost strategy while budget is open

No dollar estimate is released before geometry exists because online prices depend strongly on envelope, thickness, quantity, tolerance, finish, bend count, and lead time. Use three live quote baskets at CAD freeze:

- **Minimum viable:** deburred flat parts, standard finish, standard hardware, printed covers, no cosmetic machining.
- **Preferred prototype:** formed trays/brackets, selected captive hardware, basic finish, and one spare of critical sheet parts.
- **Precision fallback:** outsource only the supported joint hubs/shafts that cannot be made from catalog components.

Actuators and electrical hardware are expected to dominate HR-V0 cost. Structural parts should be simplified for mass, serviceability, and repeatable inspection—not weakened to chase a target price.

## Next decision

After the library reports its exact equipment and rules, classify every mechanical part into one of the four process rows above. Then release geometry, request comparable quotes, and select a fabrication route using evidence rather than assuming local capability.

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
