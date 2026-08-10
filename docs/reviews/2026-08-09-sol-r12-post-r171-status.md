# Sol R12 status after R171

R171 narrows Sol's architecture-only compute and firmware-deployment finding. The package now contains a hash-controlled host overlay, disabled-by-default systemd candidate, pure-file preflight and launcher tests. The committed configuration produces 23 holds and exits before any subprocess or hardware backend.

Sol's overall verdict is unchanged. No target image exists; no GPIO/serial backend, exact package lock, service permissions, received hardware, HIL, power-loss/recovery, rollback or qualified evidence exists. `EG-017` remains partial. The package remains unready for installation, connection, powered test, motion or energization.
