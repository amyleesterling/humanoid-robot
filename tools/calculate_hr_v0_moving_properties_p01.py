#!/usr/bin/env python3
"""Fail-closed nominal calculator for R248 physical mass/COM/inertia evidence.

This tool does not accept or approve evidence. It refuses incomplete, unexecuted,
or non-accepted inputs with EX_CONFIG (78).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

EX_CONFIG = 78


def positive(record, key):
    try:
        value = float(record[key])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"missing numeric {key}")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{key} must be finite and > 0")
    return value


def accepted(record):
    if record.get("execution_state") != "EXECUTED" or record.get("acceptance") != "ACCEPTED":
        raise ValueError("record is not EXECUTED and ACCEPTED")


def com(record):
    accepted(record)
    xa=float(record["support_a_coordinate_mm"]); xb=float(record["support_b_coordinate_mm"])
    ra=positive(record,"reaction_a_N"); rb=positive(record,"reaction_b_N")
    mass=positive(record,"independent_mass_kg")
    if xa == xb: raise ValueError("support span is zero")
    calculated=xa+(xb-xa)*rb/(ra+rb)
    reaction_mass=(ra+rb)/9.80665
    return {"calculated_com_mm":calculated,"reaction_mass_kg":reaction_mass,"independent_mass_kg":mass,"reaction_mass_difference_kg":reaction_mass-mass}


def inertia(cal1, cal2, article):
    for record in (cal1,cal2,article): accepted(record)
    mp1=positive(cal1,"pendulum_mass_kg"); mp2=positive(cal2,"pendulum_mass_kg")
    if not math.isclose(mp1,mp2,rel_tol=0,abs_tol=1e-9): raise ValueError("pendulum mass differs between calibration rows")
    i1=positive(cal1,"known_body_inertia_kg_m2"); i2=positive(cal2,"known_body_inertia_kg_m2")
    a1=(mp1+positive(cal1,"body_mass_kg"))*positive(cal1,"mean_period_s")**2
    a2=(mp2+positive(cal2,"body_mass_kg"))*positive(cal2,"mean_period_s")**2
    if math.isclose(a1,a2,rel_tol=0,abs_tol=1e-15): raise ValueError("calibration denominator is zero")
    k=(i1-i2)/(a1-a2)
    fixture=k*a1-i1
    result=k*(mp1+positive(article,"article_mass_kg"))*positive(article,"mean_period_s")**2-fixture
    if k <= 0 or fixture < 0 or result <= 0: raise ValueError("nonphysical fitted constant, fixture inertia, or article inertia")
    return {"fitted_K":k,"fitted_fixture_inertia_kg_m2":fixture,"calculated_inertia_kg_m2":result}


def load_one(path):
    with path.open(encoding="utf-8-sig",newline="") as handle: rows=list(csv.DictReader(handle))
    if len(rows)!=1: raise ValueError(f"{path}: expected exactly one data row")
    return rows[0]


def main():
    parser=argparse.ArgumentParser(description="Fail-closed HR-V0 moving-properties nominal calculator")
    sub=parser.add_subparsers(dest="mode",required=True)
    pcom=sub.add_parser("com"); pcom.add_argument("record",type=Path)
    pin=sub.add_parser("inertia"); pin.add_argument("calibration_1",type=Path); pin.add_argument("calibration_2",type=Path); pin.add_argument("article",type=Path)
    args=parser.parse_args()
    try:
        result=com(load_one(args.record)) if args.mode=="com" else inertia(load_one(args.calibration_1),load_one(args.calibration_2),load_one(args.article))
    except (OSError,ValueError,KeyError) as exc:
        print(f"EVIDENCE INCOMPLETE OR INVALID: {exc}",file=sys.stderr)
        return EX_CONFIG
    print(json.dumps(result,indent=2,sort_keys=True))
    print("NOMINAL CALCULATION ONLY - qualified uncertainty and acceptance remain separate",file=sys.stderr)
    return 0


if __name__=="__main__": raise SystemExit(main())
