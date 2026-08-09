"""Controlled manufacturer/package metadata for critical watchdog PCB ICs.

The values in this module identify devices and package/land evidence only.
They do not select an assembly process or authorize fabrication.
"""

from __future__ import annotations


WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"

FOOTPRINT_METADATA = {
    "UDRV1": {
        "Manufacturer": "Texas Instruments",
        "ManufacturerPartNumber": "TPL7407LPWR",
        "PackageCode": "PW / TSSOP-16",
        "PrimaryDocument": "TPL7407L datasheet SLRS066D",
        "PrimaryDocumentRevisionDate": "Revision D / March 2016",
        "PackageDrawing": "PW0016A; drawing 4220204/B; December 2023",
        "LandBasis": "TI TPL7407L example board layout; 0.45 x 1.50 mm pads, 0.65 mm pitch, 5.80 mm row-center spacing",
        "AssemblyProcess": "SELECTION REQUIRED",
        "FabricationStatus": WARNING,
    },
    "UDRV2": {
        "Manufacturer": "Texas Instruments",
        "ManufacturerPartNumber": "TPL7407LPWR",
        "PackageCode": "PW / TSSOP-16",
        "PrimaryDocument": "TPL7407L datasheet SLRS066D",
        "PrimaryDocumentRevisionDate": "Revision D / March 2016",
        "PackageDrawing": "PW0016A; drawing 4220204/B; December 2023",
        "LandBasis": "TI TPL7407L example board layout; 0.45 x 1.50 mm pads, 0.65 mm pitch, 5.80 mm row-center spacing",
        "AssemblyProcess": "SELECTION REQUIRED",
        "FabricationStatus": WARNING,
    },
    "UFB1": {
        "Manufacturer": "Texas Instruments",
        "ManufacturerPartNumber": "ISO1212DBQ",
        "PackageCode": "DBQ / SSOP-16",
        "PrimaryDocument": "ISO1212 datasheet SLLSEY7G",
        "PrimaryDocumentRevisionDate": "Revision G / February 2025",
        "PackageDrawing": "DBQ0016A; drawing 4214846/A; March 2014",
        "LandBasis": "TI ISO1212 example board layout; 0.41 x 1.60 mm pads, 0.635 mm pitch, 5.40 mm row-center spacing; R0.05 pad corner is project-controlled",
        "AssemblyProcess": "SELECTION REQUIRED",
        "FabricationStatus": WARNING,
    },
    "ISO1": {
        "Manufacturer": "Vishay",
        "ManufacturerPartNumber": "VO618A-4X017T",
        "PackageCode": "SMD-4 option 7",
        "PrimaryDocument": "VO618A datasheet 83432",
        "PrimaryDocumentRevisionDate": "Revision 2.1 / 22 January 2025",
        "PackageDrawing": "VO618A option-7 dimensioned package and land drawing",
        "LandBasis": "Vishay option-7 land drawing; 1.52 x 1.78 mm pads, 9.53 x 2.54 mm center pattern, 8.01 mm inner gap, 11.05 mm overall span",
        "AssemblyProcess": "SELECTION REQUIRED",
        "FabricationStatus": WARNING,
    },
}


def apply_metadata(footprint) -> None:
    """Apply hidden KiCad footprint fields when the reference is controlled."""
    fields = FOOTPRINT_METADATA.get(footprint.GetReference())
    if fields is None:
        return
    for name, value in fields.items():
        footprint.SetField(name, value)
        footprint.GetField(name).SetVisible(False)
