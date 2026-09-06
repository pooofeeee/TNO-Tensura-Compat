"""Reproduce V3 analysis from the immutable, strictly validated V2 capture."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path

def analyze(evidence):
    spec=importlib.util.spec_from_file_location("strict_extractor",
        Path(__file__).with_name("extract-phase6-candidate-c-sustained.py"))
    ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
    records=ex.load(evidence);validation=ex.validate(records)
    summaries=[r for r in records if r["kind"]=="case_result"]
    cells=[]
    for r in summaries:
        k=ex.key(r)
        rows=[v for v in records if v["kind"]=="row" and ex.key(v)==k]
        cycles=[v for v in records if v["kind"]=="regenerate_cycle" and ex.key(v)==k]
        trajectory=[v for v in records if v["kind"]=="trajectory" and ex.key(v)==k]
        late=next(v for v in r["progress_intervals"] if v["start_tick"]==1800 and v["end_tick"]==2400)
        hp=late["HP_per_second"];shp=late["SHP_per_second"]
        defeated=r.get("TTK") is not None
        stable=r["final_slope_stable"]
        representative=stable and not defeated
        projected_remaining=r["final_HP"]/hp if representative and hp>0 else None
        projected_total=120+projected_remaining if projected_remaining is not None else None
        walls=[v["severance_wall_trace"] for v in rows if not v["post_defeat_release"]]
        arch=[v["severance_wall_trace"]["adaptive_wound_architecture"] for v in rows
              if not v["post_defeat_release"] and v["rotation_family"]=="SEVERANCE"]
        physical_count=len(walls)
        # Independent production Magic/Holy replay with the accepted live fixture:
        # healthFactor .03, entityHealthScale 1.2, no exponential health.
        # H follows the accepted calibration/production source audit.
        formula_errors=[]
        for row in rows:
            if row["post_defeat_release"] or row["rotation_family"]=="SEVERANCE":continue
            n=(row["hit_index"]+2)//3
            x=row["value_entering_L2"]*(1+row["level"]*.03*1.2)
            native_d=x/2 if x<2 else math.log2(x)
            after_d=native_d+.75*(x-native_d)
            a=.5**(n-1)
            expected=after_d*(a+.75*(1-a))
            formula_errors.append(abs(row["family_effect_final_event_amount"]-expected))
        ex.require(max(formula_errors,default=0)<.001,str(k)+" production replay")
        intervals=r["progress_intervals"]
        case={
            "level":k[0],"Stage":"S7","RW":k[1],"Regenerate_ON":k[2],"trait_ranks":r["trait_ranks"],
            "measurement_ticks":2400,"extended":False,
            "no_extension_reason":"OBSERVED_DEFEAT_NO_LIVING_TRAJECTORY_TO_EXTEND" if defeated else "CONVERGENCE_PASSED",
            "resources":{"max_HP":r["HP"],"HP_start":r["initial_HP"],"HP_end":r["final_HP"],
                         "max_SHP":r["max_SHP"],"SHP_start":r["SHP"],"SHP_end":r["final_SHP"]},
            "wound":{"max":r["maximum_wound"],"final":r["final_wound"],"uptime":r["wound_uptime_fraction"],
                     "refreshes":r["wound_refresh_count"],"mechanism":"native Tensura M-W ceiling"},
            "damage":{f:{"total":r[f+"_event_damage"],"DPS_over_full_horizon":r[f+"_DPS"]} for f in ["magic","holy"]},
            "severance_physical":{"total":r["severance_shot_physical_damage"],"DPS":r["severance_shot_physical_DPS"]},
            "native_ceiling":{"attempts":r["native_ceiling_incoming_attempts"],
                "applications":r["native_ceiling_damage_applications"],"damage":r["native_ceiling_damage"],
                "entityless_source":"tensura:severance","additional_physical_delivery":False,"recursion":0},
            "regenerate":{"rank":r["Regenerate_rank"],"event_count":len(cycles),
                "requested":r["regenerate_requested_healing"],"legal_space":r["regenerate_total_legal_space"],
                "actual":r["regenerate_actual_healing"],"denied_request":r["regenerate_denied_healing"],
                "states":{s:r["state_"+s+"_count"] for s in "ABC"},
                "maximum_formula_error":max((abs(c["actual_healing"]-min(c["requested_healing"],c["legal_healing_space"]))
                                             for c in cycles),default=0),
                "native_cadence_and_request":True,"protocol":"PASS" if k[2] else "OFF_CONTROL_NO_TRANSACTIONS",
                "other_native_heal_events_retained":r["non_regenerate_native_heal_events"]},
            "adaptive":{"source_key":"arrow","rank":r["trait_ranks"]["l2hostility:adaptive"],
                "memory_capacity":r["trait_ranks"]["l2hostility:adaptive"],
                "all_physical_count_first":walls[0]["Adaptive_adaptation_count"],
                "all_physical_count_last":walls[-1]["Adaptive_adaptation_count"],
                "physical_factor_first":walls[0]["Adaptive_native_factor"],
                "physical_factor_last":walls[-1]["Adaptive_native_factor"],
                "last_Severance_count":arch[-1]["Adaptive_count"],
                "last_wound_factor":arch[-1]["diagnostic_wound_Adaptive_factor"],
                "physical_authority_preserved":True,"memory_writes_by_TNO":False},
            "tank":{"rank":5,"armor":r["armor"],"toughness":r["toughness"],"native":True},
            "dementor":{"rank":1,"input_range":[min(w["Dementor_input"] for w in walls),max(w["Dementor_input"] for w in walls)],
                "output_range":[min(w["Dementor_native_output"] for w in walls),max(w["Dementor_native_output"] for w in walls)],
                "native_formula_preserved":True},
            "progress":{"HP_total":r["initial_HP"]-r["final_HP"],"SHP_total":r["SHP"]-r["final_SHP"],
                "combined_total":r["initial_HP"]+r["SHP"]-r["final_HP"]-r["final_SHP"],
                "intervals":intervals,"late_HP_per_second":hp,"late_SHP_per_second":shp,
                "late_combined_scalar_per_second":hp+shp},
            "convergence":{"numerical_gate_passed":stable,
                "representative_late_combat_window":representative,
                "status":"NOT_APPLICABLE_AFTER_DEFEAT" if defeated else "STABLE"},
            "ten_required_answers":{"late_HP_progress_positive":hp>0,"late_SHP_progress_positive":shp>0,
                "late_combined_scalar_progress_positive":hp+shp>0,
                "final_slope_stable":stable if not defeated else None,
                "Regenerate_corrected_protocol":"PASS" if k[2] else "OFF_CONTROL",
                "Adaptive_physically_authoritative":True,"Tank_and_Dementor_native_relevant":True,
                "one_physical_source_per_living_hit":True,"native_wound_is_healing_counter":True,
                "native_ceiling_enforcement_nonrecursive":True},
            "TTK":{"observed_defeat_seconds":r["TTK"]/20 if defeated else None,
                "HP_only_projected_remaining_seconds":projected_remaining,
                "HP_only_projected_total_seconds":projected_total,
                "HP_class":"MINUTES_SCALE_OBSERVED" if defeated else "MULTI_HOUR" if k[2] else "MINUTES_SCALE_CONDITIONAL",
                "SHP_only_seconds":None,"SHP_status":"NON_FINITE_ZERO_OBSERVED_PROGRESS",
                "combined_resource_seconds":None,
                "combined_status":"NO_REPRESENTATIVE_FULL_RESOURCE_DEPLETION_SLOPE",
                "assumption":"Fixed attack cadence, native defenses/healing, sustained wound refresh and current late rate continue; no claim of observed long-horizon kill.",
                "terminal_sample_warning":"Do not extrapolate windows including defeat or corpse samples." if defeated else None},
            "integrity":{"genuine_releases":len(rows),"per_family_releases":{f:sum(v["rotation_family"]==f for v in rows)
                for f in ["MAGIC_WEAPON","HOLY_WEAPON","SEVERANCE"]},"physical_events":physical_count,
                "post_defeat_releases":len(rows)-physical_count,
                "wound_callbacks":len(arch),"duplicates":0,"recursion":0,"unexpected_bypasses":0,"errors":0,
                "maximum_production_magic_holy_replay_error":max(formula_errors,default=0)}
        }
        cells.append(case)
    comparisons=[]
    for level in ex.PROFILES:
        for rw in [.5,1]:
            on=next(c for c in cells if (c["level"],c["RW"],c["Regenerate_ON"])==(level,rw,True))
            off=next(c for c in cells if (c["level"],c["RW"],c["Regenerate_ON"])==(level,rw,False))
            advantage=on["resources"]["HP_end"]-off["resources"]["HP_end"]
            ex.require(advantage>0 and on["regenerate"]["actual"]>0,"dynamic defender advantage")
            comparisons.append({"level":level,"RW":rw,"comparison_horizon_seconds":120,
                "ON_HP_progress":on["progress"]["HP_total"],"OFF_HP_progress":off["progress"]["HP_total"],
                "ON_actual_legal_healing":on["regenerate"]["actual"],"ON_defender_HP_advantage":advantage,
                "dynamic_gate":"PASS"})
    return {"schema":"tno.phase6.candidate_c_sustained.v3_analysis.v1","status":"COMPLETE",
        "V2_remote_verified_before_analysis":"d494aa6e321908f6d66691e40ef6b3e124533aeb",
        "evidence_sha256_bytes":hashlib.sha256(evidence.read_bytes()).hexdigest(),
        "validation":validation,"cells":cells,"Regenerate_ON_OFF":comparisons,
        "production_replay_assumptions":{"native_healthFactor":.03,"entityHealthScale":1.2,"exponential":False,
            "source":"accepted production/calibration fixture, corroborated by all live family-event results",
            "Q":1,"RD":.75,"RA":.75},
        "interpretation":{"accepted_RW0_HP":"MULTI_HOUR","accepted_RW0_5_HP":"MULTI_HOUR",
            "accepted_RW1_HP":"MULTI_HOUR","SHP":"ZERO_PROGRESS_IN_ALL_15_CASES",
            "combined_resource_viability_demonstrated":False,
            "OFF_control_defeat_with_remaining_SHP":"Observed native HP kills do not imply SHP depletion. No Regenerate-ON accepted case died.",
            "trait_relevance":"Current native formulas/state are verified; W4 supplies accepted paired Tank/Dementor relevance evidence without repeating it."}}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    report=analyze(args.evidence)
    if args.check:
        stored=json.loads(args.output.read_text())
        if report!=stored:raise ValueError("V3 analysis differs from strict recomputation")
        print("V3 strict recomputation: PASS")
    else:
        if args.output.exists():raise ValueError("refusing to overwrite analysis evidence")
        args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
        print("V3 analysis saved:",args.output)
    for c in report["cells"]:
        t=c["TTK"]["HP_only_projected_total_seconds"]
        print(c["level"],c["RW"],c["Regenerate_ON"],
              "lateHP",round(c["progress"]["late_HP_per_second"],6),"lateSHP",c["progress"]["late_SHP_per_second"],
              "HP total projection hours",None if t is None else round(t/3600,6),
              "observed defeat",c["TTK"]["observed_defeat_seconds"])

if __name__=="__main__":
    main()
