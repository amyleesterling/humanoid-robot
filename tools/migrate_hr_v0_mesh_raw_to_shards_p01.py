#!/usr/bin/env python3
"""Losslessly shard large raw mesh bundles without changing numerical evidence."""
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
import numpy as np
from hr_v0_mesh_raw_shards import LINEAR_KEYS,TET10_KEYS,load_shards,split_raw

ROOT=Path(__file__).resolve().parents[1]
PACKAGES=(
    "hr-v0-j2-c07-pe-topology-mesh-p0.1",
    "hr-v0-j2-c07-pe-frontal-mesh-p0.1",
    "hr-v0-j2-c07-pe-seam-free-mesh-p0.1",
    "hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1",
)
RELEASE_NAMES={
    "hr-v0-j2-c07-pe-topology-mesh-p0.1":"j2-c07-pe-topology-mesh-p0.1",
    "hr-v0-j2-c07-pe-frontal-mesh-p0.1":"j2-c07-pe-frontal-mesh-p0.1",
    "hr-v0-j2-c07-pe-seam-free-mesh-p0.1":"j2-c07-pe-seam-free-mesh-p0.1",
    "hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1":"j2-c07-pe-seam-free-jacobian-mesh-p0.1",
}
PRE_MIGRATION_STATUS_REFERENCES={
    "hr-v0-j2-c07-pe-topology-mesh-p0.1":("mechanical/analysis/hr-v0-j2-c07-pe-frontal-mesh-p0.1/analysis-status.json","r293_baseline_status_sha256"),
    "hr-v0-j2-c07-pe-frontal-mesh-p0.1":("mechanical/analysis/hr-v0-j2-c07-pe-frontal-disposition-p0.1/execution-provenance.json","r295_status_sha256"),
    "hr-v0-j2-c07-pe-seam-free-mesh-p0.1":("mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1/analysis-status.json","r298_baseline_status_sha256"),
    "hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1":("mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-failure-localization-p0.1/execution-provenance.json","r300_status_sha256"),
}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write_csv(p:Path,data:list[dict[str,object]])->None:
    fields=[]
    for r in data:
        for f in r:
            if f not in fields:fields.append(f)
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(data)
def main()->int:
    migration_sha=sha(Path(__file__).resolve());helper_sha=sha(ROOT/"tools/hr_v0_mesh_raw_shards.py")
    for package_name in PACKAGES:
        package=ROOT/"mechanical/analysis"/package_name;raw=package/"raw-conformal-zone-mesh.npz";linear=package/"raw-linear-mesh.npz";tet10=package/"raw-tet10-mesh.npz"
        if raw.exists():
            original_sha=sha(raw);split_raw(raw,linear,tet10);combined=load_shards(package)
            with np.load(raw) as original:
                for key in LINEAR_KEYS+TET10_KEYS:
                    if not np.array_equal(original[key],combined[key]):raise RuntimeError(f"lossless shard failure {package_name}:{key}")
            raw.unlink()
        elif linear.exists() and tet10.exists():
            provenance=json.loads((package/"execution-provenance.json").read_text(encoding="utf-8"));original_sha=provenance["raw_evidence_original_sha256"]
            load_shards(package)
        else:raise RuntimeError(f"raw evidence missing: {package_name}")
        if linear.stat().st_size>=100_000_000 or tet10.stat().st_size>=100_000_000:raise RuntimeError(f"shard still exceeds GitHub hard limit: {package_name}")
        reference_path,reference_key=PRE_MIGRATION_STATUS_REFERENCES[package_name]
        pre_migration_status_sha=json.loads((ROOT/reference_path).read_text(encoding="utf-8"))[reference_key]
        status_path=package/"analysis-status.json";status=json.loads(status_path.read_text(encoding="utf-8"));status.update({"raw_evidence_layout":"LOSSLESS TWO-SHARD NPZ","raw_evidence_original_sha256":original_sha,"raw_linear_mesh_sha256":sha(linear),"raw_tet10_mesh_sha256":sha(tet10),"raw_shard_array_count":len(LINEAR_KEYS)+len(TET10_KEYS)});status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
        provenance_path=package/"execution-provenance.json";provenance=json.loads(provenance_path.read_text(encoding="utf-8"));provenance.update({"pre_raw_shard_migration_status_sha256":pre_migration_status_sha,"pre_raw_shard_migration_status_reference_path":reference_path,"pre_raw_shard_migration_status_reference_key":reference_key,"raw_evidence_layout":"LOSSLESS TWO-SHARD NPZ","raw_evidence_original_sha256":original_sha,"raw_linear_mesh_sha256":sha(linear),"raw_tet10_mesh_sha256":sha(tet10),"raw_shard_migration_generator_sha256":migration_sha,"raw_shard_helper_sha256":helper_sha,"raw_shard_array_keys":[*LINEAR_KEYS,*TET10_KEYS]});provenance_path.write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
        warning=status["warning"];manifest=[]
        for p in sorted(package.iterdir()):
            if p.is_file() and p.name!="file-manifest.csv":manifest.append({"relative_path":p.name,"sha256":sha(p),"bytes":p.stat().st_size,"warning":warning})
        write_csv(package/"file-manifest.csv",manifest)
        release=ROOT/"release/hr-v0"/RELEASE_NAMES[package_name]
        if release.exists():shutil.rmtree(release)
        release.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(package,release)
        print(f"PASS shard migration {package_name}: linear={linear.stat().st_size} tet10={tet10.stat().st_size}")
    return 0
if __name__=="__main__":raise SystemExit(main())
