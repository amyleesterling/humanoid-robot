"""Controlled manufacturer/package metadata for critical watchdog PCB ICs.

The values in this module identify devices and package/land evidence only.
They do not select an assembly process or authorize fabrication.
"""

from __future__ import annotations


WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"

ASSEMBLY_IDENTITIES = {
    "CDEC1": ("Murata", "GRM21BR71H104KA01L", "100 nF, 50 V, X7R, 0805", "SMD_REFLOW"),
    "CDRV1": ("Murata", "GRM21BR71H104KA01L", "100 nF, 50 V, X7R, 0805", "SMD_REFLOW"),
    "CDRV2": ("Murata", "GRM21BR71H104KA01L", "100 nF, 50 V, X7R, 0805", "SMD_REFLOW"),
    "CFI1": ("TDK", "CGA3E2X7R1H103K080AA", "10 nF, 50 V, X7R, 0603", "SMD_REFLOW"),
    "CFI2": ("TDK", "CGA3E2X7R1H103K080AA", "10 nF, 50 V, X7R, 0603", "SMD_REFLOW"),
    "DC1": ("TRACO POWER", "TSR 1-2450", "24 V to 5 V, 1 A, non-isolated", "MANUAL_THT_POST_REFLOW"),
    "ISO1": ("Vishay", "VO618A-4X017T", "phototransistor optocoupler, option 7", "SMD_REFLOW"),
    "JWF1": ("Phoenix Contact", "1751248", "MKDS 1/2-3,5, 2 position", "MANUAL_THT_POST_REFLOW"),
    "JWH1": ("Phoenix Contact", "1751248", "MKDS 1/2-3,5, 2 position", "MANUAL_THT_POST_REFLOW"),
    "JWP1": ("Phoenix Contact", "1751264", "MKDS 1/4-3,5, 4 position", "MANUAL_THT_POST_REFLOW"),
    "RHB1": ("Panasonic Industry", "ERJ6ENF9100V", "910 ohm, 1%, 0805, 0.125 W", "SMD_REFLOW"),
    "RHP1": ("Panasonic Industry", "ERJ6ENF1002V", "10.0 kohm, 1%, 0805, 0.125 W", "SMD_REFLOW"),
    "RPD1": ("Panasonic Industry", "ERJ6ENF1002V", "10.0 kohm, 1%, 0805, 0.125 W", "SMD_REFLOW"),
    "RPD2": ("Panasonic Industry", "ERJ6ENF1002V", "10.0 kohm, 1%, 0805, 0.125 W", "SMD_REFLOW"),
    "RSN1": ("Panasonic Industry", "ERJ6ENF5620V", "562 ohm, 1%, 0805", "SMD_REFLOW"),
    "RSN2": ("Panasonic Industry", "ERJ6ENF5620V", "562 ohm, 1%, 0805", "SMD_REFLOW"),
    "RSO1": ("Panasonic Industry", "ERJ6ENF1001V", "1.00 kohm, 1%, 0805", "SMD_REFLOW"),
    "RSO2": ("Panasonic Industry", "ERJ6ENF1001V", "1.00 kohm, 1%, 0805", "SMD_REFLOW"),
    "RTH1": ("Vishay", "MMA02040C1001FB300", "1.00 kohm, 1%, 0.4 W, MELF", "SMD_REFLOW"),
    "RTH2": ("Vishay", "MMA02040C1001FB300", "1.00 kohm, 1%, 0.4 W, MELF", "SMD_REFLOW"),
    "RW1": ("Vishay", "CRCW12102K70FKEA", "2.70 kohm, 1%, 0.5 W, 1210", "SMD_REFLOW"),
    "RW2": ("Vishay", "CRCW12102K70FKEA", "2.70 kohm, 1%, 0.5 W, 1210", "SMD_REFLOW"),
    "UDRV1": ("Texas Instruments", "TPL7407LPWR", "seven-channel low-side driver, PW0016A", "SMD_REFLOW"),
    "UDRV2": ("Texas Instruments", "TPL7407LPWR", "seven-channel low-side driver, PW0016A", "SMD_REFLOW"),
    "UFB1": ("Texas Instruments", "ISO1212DBQ", "dual isolated 24 V input receiver, DBQ0016A", "SMD_REFLOW"),
    "WDCTRL1": ("Raspberry Pi", "SC0915", "Raspberry Pi Pico 1 / RP2040 module", "SMD_REFLOW"),
    **{f"TP{i}": ("Harwin", "S1751-46R", "SMT test point", "SMD_REFLOW") for i in range(1, 17)},
}

BASE_IDENTITY_FIELDS = (
    "Manufacturer", "ManufacturerPartNumber", "AssemblyDescription",
    "ProcessClass", "AlternatePolicy", "AssemblyProcessState", "FabricationStatus",
)

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
    identity = ASSEMBLY_IDENTITIES.get(footprint.GetReference())
    if identity is not None:
        manufacturer, mpn, description, process_class = identity
        base = {
            "Manufacturer": manufacturer,
            "ManufacturerPartNumber": mpn,
            "AssemblyDescription": description,
            "ProcessClass": process_class,
            "AlternatePolicy": "NO ALTERNATES WITHOUT WRITTEN PROJECT DISPOSITION",
            "AssemblyProcessState": "SELECTION REQUIRED",
            "FabricationStatus": WARNING,
        }
        for name, value in base.items():
            footprint.SetField(name, value)
            footprint.GetField(name).SetVisible(False)
    fields = FOOTPRINT_METADATA.get(footprint.GetReference())
    if fields is None:
        return
    for name, value in fields.items():
        footprint.SetField(name, value)
        footprint.GetField(name).SetVisible(False)
