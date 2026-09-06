"""Strict, read-only validation of Candidate C V1/V2 captures; writes only with --output."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "tno.phase6.candidate_c_sustained.v1"
STATE_TOL = 0.01
FORMULA_TOL = 0.001
PROFILES = {
    600: {"adaptive": 3, "dementor": 1, "drain": 2, "regenerate": 4, "tank": 5, "wither": 1},
    800: {"adaptive": 5, "dementor": 1, "drain": 2, "regenerate": 5, "tank": 5, "wither": 1},
    1000: {"adaptive": 5, "dementor": 1, "dispell": 2, "drain": 2, "regenerate": 5, "tank": 5, "wither": 1},
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def close(a, b, tolerance=FORMULA_TOL):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b) <= tolerance

def state(hp, ceiling, requested):
    if hp >= ceiling-STATE_TOL:
        return "C"
    return "A" if hp+requested <= ceiling+STATE_TOL else "B"

def key(r):
    return (r["level"], r.get("RW", r.get("wound_Adaptive_recovery_RW")),
            r.get("Regenerate_ON", r.get("Regenerate_rank", 0) > 0))

def load(path):
    records = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        marker = "TNO_PHASE6_ADAPTIVE_WOUND "
        if marker in line:
            line = line.split(marker, 1)[1]
        if not line.startswith("{"):
            continue
        r = json.loads(line)
        if r.get("schema") == SCHEMA:
            records.append(r)
    return records

def validate(records, smoke=False):
    counts = Counter(r["kind"] for r in records)
    require(not any("error" in r["kind"] for r in records), "runtime errors")
    expected = {(600, 1.0, True)} if smoke else {
        (level, rw, on) for level in PROFILES for rw, on in
        [(0, True), (.5, True), (1, True), (.5, False), (1, False)]}
    require(counts["catalog"] == counts["suite_result"] == 1, "catalog/suite count")
    cat = next(r for r in records if r["kind"] == "catalog")
    suite = next(r for r in records if r["kind"] == "suite_result")
    require(cat["checkpoint"] == ("V1_HARNESS_SMOKE" if smoke else "V2_SUSTAINED"), "checkpoint")
    require(cat["state_classification_tolerance_HP"] == STATE_TOL
            and cat["formula_validation_tolerance_HP"] == FORMULA_TOL, "tolerance declaration")
    require(not cat["target_clock_rewind_during_measurement"]
            and not cat["other_native_healing_cancelled"], "mutating harness mode")
    require(suite["status"] == "complete" and suite["case_count"] == len(expected)
            and suite["requested_case_count"] == len(expected), "suite incomplete")
    results = [r for r in records if r["kind"] == "case_result"]
    starts = [r for r in records if r["kind"] == "case_start"]
    require(len(results) == len(starts) == len(expected), "case counts")
    require({key(r) for r in results} == {key(r) for r in starts} == expected, "matrix coverage")
    global_uuids = set()
    for summary in results:
        k = key(summary)
        level, rw, on = k
        label = str(k)
        rows = [r for r in records if r["kind"] == "row" and key(r) == k]
        cycles = [r for r in records if r["kind"] == "regenerate_cycle" and key(r) == k]
        trajectory = [r for r in records if r["kind"] == "trajectory" and key(r) == k]
        end = summary["measurement_ticks"]
        require(end in ([660] if smoke else [2400, 3600]), label+" duration")
        require(summary["status"] == "ok" and summary["TNO_stage"] == "S7"
                and summary["APO_profile"] == "NONE" and not summary["royal_arrow_mark_enabled"], label+" identity")
        expected_traits = {"l2hostility:"+t: rank for t, rank in PROFILES[level].items()
                           if on or t != "regenerate"}
        require(summary["trait_ranks"] == expected_traits, label+" profile")
        if not on:
            require(summary["removed_trait_budget_not_reallocated"], label+" removed budget")
        require([r["tick"] for r in trajectory] == list(range(end+1)), label+" trajectory continuity")
        require([r["hit_index"] for r in rows] == list(range(1,end//20+1)), label+" release count")
        require([r["release_tick"] for r in rows] == list(range(1,end,20)), label+" schedule")
        require(summary["shots_released"] == len(rows), label+" summary release count")
        require(not summary["production_Magic_Holy_behavior_changed"]
                and not summary["direct_TNO_wound_write"]
                and summary["target_clock_rewinds_during_measurement"] == 0
                and summary["non_regenerate_native_heals_cancelled_by_harness"] == 0, label+" ownership")
        require((summary["production_Magic_Holy_Q"], summary["production_Magic_Holy_RD"],
                 summary["production_Magic_Holy_RA"]) == (1, .75, .75), label+" production policy")
        live = [r for r in trajectory if r["alive"]]
        require(all(r["target_tick"] == r["tick"] for r in live), label+" natural target clock")
        require(all(close(r["max_HP"], 10000) and close(r["max_SHP"], {600:51300,800:67500,1000:83700}[level])
                    and close(r["ceiling"],r["max_HP"]-r["wound"]) for r in trajectory), label+" resource authority")
        require(close(summary["final_HP"], trajectory[-1]["HP"])
                and close(summary["final_SHP"],trajectory[-1]["SHP"]), label+" final resources")
        require(close(summary["maximum_wound"], max(r["wound"] for r in trajectory))
                and close(summary["final_wound"],trajectory[-1]["wound"]), label+" wound summary")
        require(close(summary["wound_uptime_fraction"],
                sum(r["wound"] > .0001 for r in trajectory[1:])/end), label+" wound uptime")
        require(summary["wound_refresh_count"] == sum(
            b["wound_seconds_remaining"] > a["wound_seconds_remaining"]
            or b["wound"] > a["wound"]+.0001 for a,b in zip(trajectory,trajectory[1:])), label+" refresh count")
        for interval in summary["progress_intervals"]:
            a,b = interval["start_tick"],interval["end_tick"]
            hp = (trajectory[a]["HP"]-trajectory[b]["HP"])*20/(b-a)
            shp = (trajectory[a]["SHP"]-trajectory[b]["SHP"])*20/(b-a)
            require(close(hp,interval["HP_per_second"]) and close(shp,interval["SHP_per_second"])
                    and close(hp+shp,interval["combined_per_second"]), label+" slope")
        if not smoke:
            def slope(resource,a,b):
                return (trajectory[a][resource]-trajectory[b][resource])*20/(b-a)
            def stable_at(t):
                return all(abs(slope(resource,t-1200,t-600)-slope(resource,t-600,t))
                    <= max(.01,.05*max(abs(slope(resource,t-1200,t-600)),abs(slope(resource,t-600,t))))
                    for resource in ["HP","SHP"])
            require(summary["final_slope_stable"] == stable_at(end),label+" convergence")
            if end == 3600:
                require(not stable_at(2400) and trajectory[2400]["alive"]
                        and summary["extension_reason"] == "HP_OR_SHP_FINAL_30S_DIFFERS_FROM_PREVIOUS_30S",
                        label+" extension not justified")
        admitted = 0
        for row in rows:
            i = row["hit_index"]
            family = ["MAGIC_WEAPON","HOLY_WEAPON","SEVERANCE"][(i-1)%3]
            require(row["rotation_family"] == family and row["released_projectile_count"] == 1
                    and row["projectile_entity_id"] == "royalvariations:royal_arrow", label+" native release")
            uuid = row["released_projectile_uuids"][0]
            require(uuid not in global_uuids, "duplicate physical projectile")
            global_uuids.add(uuid)
            for flag in ["unexpected_source_duplication","event_recursion_observed",
                         "l2_layer_bypassed_unexpectedly","tensura_layer_bypassed_unexpectedly"]:
                require(row[flag] is False, label+" "+flag)
            if row["post_defeat_release"]:
                require(row["physical_damage_event_count"] == 0 and row["engraving_damage_event_count"] == 0,
                        label+" damage after defeat")
                continue
            admitted += 1
            require(row["physical_damage_event_count"] == 1
                    and row["physical_damage_source_id"] == "minecraft:arrow"
                    and row["severance_wall_trace_count"] == 1, label+" one physical source")
            wall = row["severance_wall_trace"]
            require(wall["Adaptive_source_msgId"] == "arrow"
                    and wall["Adaptive_trait_rank"] == PROFILES[level]["adaptive"]
                    and wall["Adaptive_memory_capacity"] == PROFILES[level]["adaptive"]
                    and wall["Adaptive_adaptation_count"] == admitted, label+" native Adaptive state")
            require(math.isclose(wall["Adaptive_native_factor"], .5**(admitted-1), rel_tol=1e-5, abs_tol=1e-45),
                    label+" native Adaptive factor")
            require(close(wall["Adaptive_native_result"],row["combined_physical_post_damage"]),
                    label+" physical authority")
            require(wall["Tank_present"] and wall["Tank_rank"] == 5 and wall["Dementor_applied"],label+" native traits")
            din=wall["Dementor_input"]
            dout=din/2 if din < 2 else math.log2(din)
            require(close(dout,wall["Dementor_native_output"]),label+" native Dementor")
            require(wall["wound_attempt_count"] == (1 if family == "SEVERANCE" else 0), label+" callback count")
            if family != "SEVERANCE":
                source = "tensura:magic" if family == "MAGIC_WEAPON" else "tensura:holy_damage"
                require(row["family_damage_source_id"] == source and row["engraving_damage_event_count"] == 1
                        and close(row["engraving_native_amount"],8)
                        and close(row["engraving_after_stage_coefficient"],11.2)
                        and wall["adaptive_wound_trace_count"] == 0,label+" Magic/Holy isolation")
            else:
                a=wall["adaptive_wound_architecture"]
                factor=a["Adaptive_native_factor"]+rw*(1-a["Adaptive_native_factor"])
                pre=a["eligible_physical_post_round"]*max(0,min(1,a["post_Dementor_physical"]/a["combined_physical_pre_L2"]))
                extra=max(0,.5*pre*(factor-a["Adaptive_native_factor"]))
                offer=min(a["native_Severance_candidate"],a["native_post_clamp_offer"]+extra)
                require(close(a["diagnostic_RW"],rw) and close(a["diagnostic_wound_Adaptive_factor"],factor)
                        and close(a["eligible_pre_Adaptive"],pre) and close(a["diagnostic_eligible_extra"],extra)
                        and close(a["negotiated_native_storage_offer"],offer),label+" Candidate C formula")
                require(not a["physical_damage_changed_by_prototype"] and not a["Adaptive_state_changed_by_prototype"]
                        and not a["direct_TNO_wound_write"] and a["wound_state_identity"] == "tensura:effect_storage"
                        and wall["native_arrow_base_post_round"] == 8,label+" wound/base ownership")
                require(close(a["wound_after_native_storage"]-a["wound_before_native_storage"],
                              offer*a["native_Severance_Protection_multiplier"]),label+" native storage")
            require(all(v=="NONE" for v in row["native_severance_source_entity_ids"])
                    and all(v=="NONE" for v in row["native_severance_direct_entity_ids"]),label+" ceiling source")
        require(summary["physical_source_count"] == admitted,label+" physical total")
        require(len(cycles) == (sum(r["tick"]>0 and r["tick"]%20==0 for r in live) if on else 0),
                label+" native transaction count")
        for i,c in enumerate(cycles,1):
            hp,ceiling,request=c["HP_before_Regenerate"],c["wound_ceiling_before_Regenerate"],c["requested_healing"]
            legal=max(0,ceiling-hp)
            require(c["cycle_index"] == i and c["target_tick_count"]%20==0 and c["native_Regenerate_stack_verified"]
                    and c["Regenerate_rank"] == PROFILES[level]["regenerate"]
                    and close(request,10000*.01*PROFILES[level]["regenerate"]),label+" native request")
            require(close(c["legal_healing_space"],legal) and close(c["expected_actual_healing"],min(request,legal))
                    and close(c["actual_healing"],min(request,legal))
                    and close(c["denied_healing"],request-c["actual_healing"]),label+" counter formula")
            require(c["state"]==state(hp,ceiling,request) and c["cycle_complete"],label+" classified state")
            require(close(c["SHP_before_Regenerate"],c["SHP_after_Regenerate"])
                    and close(c["wound_before_Regenerate"],c["wound_after_Regenerate"])
                    and c["HP_after_Regenerate"] <= c["wound_ceiling_after_Regenerate"]+FORMULA_TOL,
                    label+" healed wounded HP/SHP")
        for metric,field in [("requested_healing","regenerate_requested_healing"),
                             ("actual_healing","regenerate_actual_healing"),("denied_healing","regenerate_denied_healing"),
                             ("legal_healing_space","regenerate_total_legal_space")]:
            require(close(sum(c[metric] for c in cycles),summary[field]),label+" transaction totals")
        for st in "ABC":
            require(summary["state_"+st+"_count"]==sum(c["state"]==st for c in cycles),label+" state totals")
    return {"schema":"tno.phase6.candidate_c_sustained.validation.v1","status":"PASS",
            "checkpoint":"V1" if smoke else "V2","counts":dict(counts),"case_count":len(results),
            "measurement_ticks":sum(r["measurement_ticks"] for r in results),
            "release_count":counts["row"],"Regenerate_events":counts["regenerate_cycle"],
            "A_B_C":{st:sum(r["state_"+st+"_count"] for r in results) for st in "ABC"},
            "requested":sum(r["regenerate_requested_healing"] for r in results),
            "actual":sum(r["regenerate_actual_healing"] for r in results),
            "denied":sum(r["regenerate_denied_healing"] for r in results),
            "state_tolerance_HP":STATE_TOL,"formula_tolerance_HP":FORMULA_TOL,
            "errors":0,"duplicates":0,"recursion":0,"unexpected_bypasses":0}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--report",type=Path)
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args()
    records=load(args.input)
    report=validate(records,args.smoke)
    encoded="\n".join(json.dumps(r,separators=(",",":"),ensure_ascii=False) for r in records)+"\n"
    report["evidence_sha256"]=hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    if args.output:
        require(not args.output.exists(),"refusing to overwrite existing evidence")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(encoded,encoding="utf-8",newline="\n")
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()

