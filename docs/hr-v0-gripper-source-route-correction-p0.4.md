# HR-V0 gripper source-route correction P0.4

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-GRIP-SRC-ROUTE-P0.4**  
Date: 2026-08-08  
Scope: current publisher-source discovery for the OpenMANIPULATOR-X complete gripper mechanism

## Decision

R72's current-source statement is superseded narrowly: ROBOTIS endpoint `767` is a live official route to a public Onshape document. The document exposes a view-only full TurtleBot3/OpenMANIPULATOR assembly, an `OpenManipulator Chain <1>` instance, and metadata for an original full-robot STEP blob.

This finding does **not** make the gripper buildable. Anonymous export was not exposed in the view-only interface, the relevant blob endpoint required authorization, and no STEP/native assembly payload was acquired. The mutable workspace is therefore a source-discovery record, not a controlled manufacturing release.

R116 records the completed anonymous-route recheck. Thingiverse file and ZIP requests returned HTTP 403, its API returned HTTP 401, and the Onshape blob request returned HTTP 403. No credential, scraping or access-control bypass was attempted. Those results establish only current anonymous access state; they do not establish file content, permission, geometry or revision. The anonymous route is exhausted until ROBOTIS supplies or enables an authorized export, or a separately authorized received article enters controlled metrology.

## Reproducible identities

| Item | Identity | Observed state |
|---|---|---|
| ROBOTIS route | `https://www.robotis.com/service/download.php?no=767` | Live route to Onshape |
| Onshape document | `1535c2d7f05d4986e5ab539c` | Public, anonymous view access |
| Main workspace | `72b49bd8c74a47b010391012` | Mutable workspace; modified timestamp recorded |
| Selected assembly | `454b64d637f42073514486f4` | Viewable; definition/export not acquired |
| Original STEP blob | `7beff6dfbe34475b2c29540f` | Metadata only; bytes not acquired |
| Blob element microversion | `c4b57aeaa8da757bd23e6e05` | Identity metadata only |
| Parts Part Studio | `e262f4f20bc9613b1ef4f9f3` | Identity metadata only |

The controlled field-level record is `references/gripper/robotis-onshape-element-index-p0.1.csv`. It distinguishes the visible `OpenManipulator Chain <1>` assembly-instance label from an element ID; no standalone element ID was observed for that instance.

## Evidence boundary

The official ROBOTIS overview calls RM-X52-TNM open-source hardware and links its STL/3D-printing resources. Onshape's sharing guidance permits an owner to control export from a link. The observed link provided anonymous view access but did not expose an export command. A public view is therefore not equivalent to permission, file custody, revision control, manufacturing definition, or fit evidence.

No dimensions were screen-measured. No mate, transform, material, tolerance, fastener, cable, pad, force, current, mass, wear, drop, guard or fabrication value was inferred.

## Fail-closed branch decision

`GRH-001` complete mechanism and `GRH-002` H104 registration remain open. The next acceptable evidence is one of:

1. publisher-supplied or publisher-enabled export of an immutable complete gripper assembly/native source with revision, license, units, coordinates and mate definitions; or
2. separately authorized receipt of RM-X52-TNM followed by the controlled inventory and metrology plan, with qualified disposition.

The prepared publisher request is `docs/vendor-queries/robotis-openmanipulator-source-request-p0.2.md`. It remains **UNSENT**. No supplier contact, purchase, fabrication or physical work is authorized.

## Sol review disposition

Sol R12's central finding remains valid: HR-V0 is a preliminary architecture, not a buildable machine. This correction improves the evidence chain for one source route but closes none of Sol's 18 blockers, none of the 30 energization gates, and none of the physical verification requirements.

This document closes no energization gate.
