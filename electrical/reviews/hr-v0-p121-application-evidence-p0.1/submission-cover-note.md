# Unsent manufacturer application inquiry

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Subject: Project Button HR-V0 - application questions for PNOZ s4 750104 and PLC-RSC-24DC/21-21 2967060

This draft is **NOT SENT**. It is intended for separate submissions to Pilz and Phoenix Contact through the official routes in `submission-route-register.csv`.

Project Button is evaluating an unaccepted 24 V DC control-only topology. Two ordinary Phoenix Contact relay NO contacts, one from each of two separate 2967060 modules, would be placed in series between a protected 24 V control source and terminal A1 of one Pilz PNOZ s4 750104. The PNOZ A2 terminal returns directly to control 0 V. The PNOZ input and monitored-start circuits are separate from these ordinary relay contacts. The ordinary relays receive zero safety credit.

Pilz publishes 2.5 W nominal consumption and a maximum 0.5 A for 5 ms A1 startup pulse for 750104. Phoenix Contact publishes a 5 V/10 mA minimum load and 15 A for 300 ms maximum inrush for 2967060. We are not treating those figures as application acceptance.

Please answer the applicable rows in `manufacturer-question-register.csv`, identify the exact document revision/date supporting each answer, and state whether the proposed use is permitted, permitted with conditions, or prohibited. Please do not infer or certify the safety of the complete robot; we are seeking component-application limits only.

Attachments before any submission must include a configuration-controlled P1.21 circuit excerpt, terminal schedule, proposed cycle profile, supply/protection envelope and this package identifier. The cycle profile, protection and several dynamic limits are currently unresolved, so the inquiry shall not be represented as complete until those fields are filled.
