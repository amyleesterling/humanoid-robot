# Primary Sources Consulted

Retrieved or rechecked 2026-08-05 through 2026-08-06. Manufacturer and standards pages must be rechecked at each procurement/release gate.

- ROBOTIS XM540-W270 e-Manual; rechecked 2026-08-06: 10.6 N m stall at 12 V/4.4 A and 165 g. Stall is not continuous torque: https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/
- ROBOTIS XH540-W270 e-Manual; rechecked 2026-08-06: 9.9 N m at 12 V/4.9 A, 11.7 N m at 14.8 V/5.9 A, 39/46 rpm, 10.0-14.8 V input, 165 g, 15 arcmin backlash, and 40 N radial load at 10 mm: https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/
- ROBOTIS XC430-W240 e-Manual; rechecked 2026-08-06: https://emanual.robotis.com/docs/en/dxl/x/xc430-w240/
- ROBOTIS OpenMANIPULATOR-X specification and open hardware basis: https://emanual.robotis.com/docs/en/platform/openmanipulator_x/specification/
- ROBOTIS XM540-W270-T manufacturer CAD and compatible-frame downloads for XMHD-540, FR13-H101K, FR13-S101K, and FR13-S102K; retrieved 2026-08-06 with resolved URLs and SHA-256 values in `cad/vendor/robotis/vendor-manifest.csv`. The current e-Manual's S101 STEP link mapping discrepancy is recorded rather than silently corrected.
- 80/20 40-4040 40 mm T-slot profile; rechecked 2026-08-06: 6063-T6 profile and 13.787 cm^4 X/Y moment of inertia: https://8020.net/40-4040.html
- 80/20 40-series 40-4334 wide gusset and 40-4332 two-hole gusset candidate interfaces; rechecked 2026-08-06: https://8020.net/40-4334.html and https://8020.net/fasteningmethods/externalfasteners/bracketsgussetscorners/standardgussetedbrackets/2holegussetedinsidecornerbracket/40-series.html
- SendCutSend 6061-T6 stock/process and accepted file formats; rechecked 2026-08-06: https://sendcutsend.com/materials/6061-aluminum/ and https://sendcutsend.com/faq/what-file-formats-do-you-accept/
- ROBOTIS U2D2 interface and pin names: https://docs.robotis.com/docs/parts/interface/u2d2/
- ROBOTIS U2D2 current store identifier, SKU `902-0132-000`, and August 2025 USB-C production-change notice; rechecked 2026-08-06: https://robotis.us/u2d2/
- ROBOTIS U2D2 Power Hub pinout, 3.5-24.0 V range, 10.0 A maximum, and wire-gauge information: https://docs.robotis.com/docs/parts/interface/u2d2_power_hub/
- ROBOTIS U2D2 Power Hub Board Set current store identifier, SKU `902-0145-001`; rechecked 2026-08-06: https://robotis.us/u2d2-power-hub-board-set/
- ROBOTIS current US store identifiers for proposed HR-V0 hardware, rechecked 2026-08-06: XM540-W270-T SKU `902-0137-000` (https://robotis.us/dynamixel-xm540-w270-t/), XM430-W350-T SKU `902-0124-000` (https://robotis.us/dynamixel-xm430-w350-t/), FR13-H101K Set SKU `903-0270-300` (https://robotis.us/fr13-h101k-set/), and FR13-S102K Set SKU `903-0269-300` (https://robotis.us/fr13-s102k-set/). Store package-list T/R text inconsistencies require PO/received-device verification rather than inference.
- ROBOTIS DYNAMIXEL SDK device setup and daisy-chain context: https://docs.robotis.com/docs/software/dynamixel_sdk/device_setup/
- Raspberry Pi hardware and power documentation: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
- Raspberry Pi Pico 1 official product page and order code `SC0915`; rechecked 2026-08-06. This ordinary RP2040 board receives no safety-integrity credit: https://www.raspberrypi.com/products/raspberry-pi-pico/
- Pilz PNOZ s4 24 VDC order code 750104 product page and operating manual 21396-EN-23, current product file dated 2026-06-22 and PDF colophon 2026-02: https://www.pilz.com/en-INT/eshop/product/750104
- Schneider Electric LC1D25BD product data: https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF
- Mean Well LRS-350 series specification, file revision 2025-09-12: https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF
- Mean Well enclosed-type installation manual, dated 2025-12-17: https://www.meanwell.com/Upload/PDF/Enclosed_Type_EN.pdf
- Mean Well HDR-30 series specification: https://www.meanwell.com/Upload/PDF/HDR-30/HDR-30-SPEC.PDF
- Mean Well GST280A series specification, file `GST280A-SPEC 2026-04-03`; V3 source candidate facts include 12 V/21 A/252 W, 95 A maximum cold-start inrush at 115 VAC, C6P pin assignment, IEC C14 inlet, and internal `-V` to AC FG connection: https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF
- Mean Well GST40A series specification, file `GST40A-SPEC 2026-04-03`; V3 control-source candidate facts include 24 V/1.67 A/40 W, class I IEC C14 input, P1J center-positive output, and no output `-V` to AC FG connection: https://www.meanwell.com/Upload/PDF/GST40A/GST40A-SPEC.PDF
- Schneider Electric LC1D25BD product data sheet; current candidate facts include 24 VDC 5.4 W coil, built-in bidirectional peak-limiting diode suppression, 16-24 ms opening time, mechanically linked 1NO+1NC auxiliaries, and NC mirror contact: https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF
- Schneider Electric TeSys DC application guidance and DC-1 through DC-5 catalog pointer, updated 2026-02-05; Schneider explicitly notes that the cited DC selection ratings are not UL-listed and application suitability still requires review: https://www.se.com/uk/en/faqs/FAQ000273244/ and https://www.se.com/us/en/faqs/FA353576/
- IDEC XW emergency-stop exact candidate example XW1E-BV402M-R (not a released selection), accessed 2026-08-05: https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/emergency-stop-switches/xw-22mm-estop/xw1e-bv402m-r
- IDEC HW1B-M1F10-B momentary 1NO screw-terminal pushbutton exact electrical candidate for RESET/ARM, not a released human-factors selection; product page/catalog rechecked 2026-08-06 and supporting catalog listed as updated 2026-07-23: https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-b
- IDEC Emergency Stop Switches catalog EP1430, XW type table p.22 and terminal arrangement p.26; current site supporting file last updated 2024-06-24: https://us.idec.com/idec-us/en/USD/medias/EP1430-Estop.pdf?context=bWFzdGVyfGRvY3VtZW50c3wzODI4NDk2fGFwcGxpY2F0aW9uL3BkZnxkb2N1bWVudHMvaDhhL2g2NS84OTI5NjY2NjI5NjYyLnBkZnwxYmVmMmMyN2VkZTBmYjMwM2Y0NDNmNzY5NzQzN2Q0MTU5OTFiOTczZjRhYmQwYWNlMDQ2MDZiOGJmNGI0Nzc1
- Phoenix Contact PLC-RSC-24DC/21-21 relay module, item `2967060`; official product data-maintenance date 2026-04-01, rechecked 2026-08-06. Published 24 VDC/two-changeover characteristics support screening only; the device is not a safety relay and exact terminal drawing/application review remain open: https://www.phoenixcontact.com/de-de/produkte/relaismodul-plc-rsc-24dc21-21-2967060
- ISO 10218-1:2025 scope and status: https://www.iso.org/standard/73933.html
- ISO/TS 15066:2016 scope and status: https://www.iso.org/standard/62996.html
- ROBOTIS OP3 510 mm, 3.5 kg, 20-DOF reference architecture: https://emanual.robotis.com/docs/en/platform/op3/introduction/
- Poppy Humanoid 25-DOF architecture and build documentation: https://docs.poppy-project.org/en/assembly-guides/poppy-humanoid/
- ISO 13482:2014 personal-care robot safety scope: https://www.iso.org/standard/53820.html
- ISO/FDIS 13482 service-robot revision status: https://www.iso.org/standard/83498.html
- ROBOTIS DYNAMIXEL Y-series continuous/maximum torque and mass table: https://emanual.robotis.com/docs/en/dxl/y/
- ROBOTIS YM070-210-R099-RH detailed specification: https://emanual.robotis.com/docs/en/dxl/y/ym070-210-r099-rh/
- CubeMars AK70-10 official product page; rechecked 2026-08-06: 521 g, 8.3 N m rated, 24.8 N m peak, 24/48 V, CAN: https://www.cubemars.com/product/ak70-10-kv100-robotic-actuator.html
- CubeMars AK-series CAN control manual: https://img.cubemars.com/products/cubemars-product-parameter/AK-Series-Driver-and-Control-Manual-v1.0.14.pdf
- ODrive warning that drive inputs are not safety-rated: https://docs.odriverobotics.com/v/latest/manual/endstops.html

These sources support component screening and risk framing. They do not replace the complete manuals, application-specific calculations, or professional review.
