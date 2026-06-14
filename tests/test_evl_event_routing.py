"""Tests for EVL wiring into the ORC event bus.

Locks the cascade shape: PSY.refresh + GRO.assessed trigger a rescore; EVL.scored
forwards to CRE only; a docs/profiles/*/eval/ write classifies to the EVL domain
(announcing a scorecard, NOT a rescore — that would loop); and the EVL branch is
acyclic (no back-edge to PSY/GRO).
"""
from platform_lib import event_routing as ER
from platform_lib import paths


def _downstream_skills(event):
    return {d["skill"] for d in ER.downstream_for(event)}


# --- routing table entries ---------------------------------------------------

def test_evl_events_are_routable():
    assert "EVL.scored" in ER.routable_events()
    assert "EVL.rescore" in ER.routable_events()


def test_evl_scored_forwards_to_cre_only():
    assert ER.emits_for("EVL.scored") == ["CRE.recalibrate"]


def test_evl_rescore_runs_the_score_skill():
    assert ER.emits_for("EVL.rescore") == ["EVL.scored"]
    assert "evl:score" in _downstream_skills("EVL.rescore")


# --- profile changes trigger a rescore --------------------------------------

def test_psy_refresh_triggers_rescore():
    assert "EVL.rescore" in ER.emits_for("PSY.refresh")
    assert "evl:score" in _downstream_skills("PSY.refresh")


def test_gro_assessed_triggers_rescore():
    assert "EVL.rescore" in ER.emits_for("GRO.assessed")
    assert "evl:score" in _downstream_skills("GRO.assessed")


# --- path reclassification ---------------------------------------------------

def test_eval_path_reclassifies_to_evl_scored():
    events = ER.detect_events(["docs/profiles/character-a/eval/psychometric-big-five.json"])
    assert any(e["domain"] == "EVL" and e["event"] == "EVL.scored" for e in events), events


def test_growth_path_still_reclassifies_to_gro():
    events = ER.detect_events(["docs/profiles/character-a/growth/competencies.md"])
    assert any(e["domain"] == "GRO" and e["event"] == "GRO.profiled" for e in events)


def test_ordinary_profile_change_is_psy_refresh():
    events = ER.detect_events(["docs/profiles/character-a/psychology/formulation.md"])
    assert any(e["domain"] == "PSY" and e["event"] == "PSY.refresh" for e in events)


# --- acyclicity: EVL is a forward-only sink ---------------------------------

def test_evl_branch_has_no_back_edge_to_psy_or_gro():
    def reachable(start):
        seen, stack = set(), [start]
        while stack:
            e = stack.pop()
            for nxt in ER.emits_for(e):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    for evl_event in ("EVL.scored", "EVL.rescore"):
        downstream = reachable(evl_event)
        offenders = [e for e in downstream if e.startswith("PSY.") or e.startswith("GRO.")]
        assert offenders == [], f"{evl_event} reaches {offenders} — cascade not acyclic"


# --- telemetry stream --------------------------------------------------------

def test_evl_event_stream_registered():
    assert "EVL" in paths.EVENT_STREAMS
    assert paths.EVENT_STREAMS["EVL"] == paths.EVAL_EVENTS
    assert paths.EVAL_EVENTS.name == "evl-events.jsonl"
