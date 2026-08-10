"""Generate the P1.15-bound HR-V0 watchdog CAM P0.2 review package."""

from __future__ import annotations

import os

os.environ["HR_V0_WD_CAM_PROFILE"] = "p0.2"

from generate_hr_v0_watchdog_cam_p01 import main


if __name__ == "__main__":
    main()
