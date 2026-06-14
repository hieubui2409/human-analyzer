"""Tests for evl_judge — the per-criterion judge protocol (honesty contract).

The crux is parse_verdict robustness: a clean score+citation passes, an uncited
score is downgraded to UNVERIFIED (a score with no evidence is NEVER a silent pass),
and garbage is ERROR (never PASS). CI uses FakeLLMClient only — make_client() must
raise without credentials so the real network path can never run here.
"""
import json

import pytest

from platform_lib import evl_judge as J


def _crit(cid="c1"):
    return {"id": cid, "text": "Shows conscientiousness", "min_tier": "T3",
            "anchors": {"0": "none", "2": "some", "5": "high"}}


def _evidence():
    return [{"text": "always meets deadlines", "source": "behavioral.md:4",
             "tier": "T2", "section": "Work", "character": "test-alpha"}]


# --- clean parse paths ------------------------------------------------------

def test_clean_json_score_is_pass():
    raw = json.dumps({"score": 4, "citation": "behavioral.md:4", "tier": "T2",
                      "justification": "meets deadlines"})
    cs = J.parse_verdict(raw)
    assert cs["verdict"] == J.PASS
    assert cs["score"] == 4 and cs["citation"] == "behavioral.md:4" and cs["tier"] == "T2"


def test_json_with_prose_around_it_still_parses():
    raw = 'Sure!\n{"score": 3, "citation": "x.md:1", "tier": "T1", "justification": "y"}\nDone.'
    assert J.parse_verdict(raw)["verdict"] == J.PASS


# --- honesty: uncited is never a silent pass --------------------------------

def test_score_without_citation_is_unverified():
    raw = json.dumps({"score": 3, "citation": None, "tier": None, "justification": "guess"})
    cs = J.parse_verdict(raw)
    assert cs["verdict"] == J.UNVERIFIED


def test_explicit_pass_without_citation_is_downgraded():
    # a judge claiming PASS with no evidence must NOT be trusted
    raw = json.dumps({"verdict": "PASS", "score": 5, "citation": None, "tier": None,
                      "justification": "trust me"})
    assert J.parse_verdict(raw)["verdict"] == J.UNVERIFIED


def test_explicit_unverified_token_object():
    raw = json.dumps({"verdict": "UNVERIFIED", "score": None, "citation": None,
                      "tier": None, "justification": "no evidence found"})
    assert J.parse_verdict(raw)["verdict"] == J.UNVERIFIED


def test_bare_unverified_token():
    assert J.parse_verdict("UNVERIFIED")["verdict"] == J.UNVERIFIED


# --- garbage is ERROR, never PASS -------------------------------------------

def test_garbage_reply_is_error():
    cs = J.parse_verdict("I think this person seems pretty conscientious overall")
    assert cs["verdict"] == J.ERROR
    assert cs["score"] is None


def test_empty_reply_is_error():
    assert J.parse_verdict("")["verdict"] == J.ERROR


def test_invalid_tier_in_reply_not_pass():
    raw = json.dumps({"score": 4, "citation": "x.md:1", "tier": "T9", "justification": "y"})
    # T9 is not a real tier → cannot be a verified PASS
    assert J.parse_verdict(raw)["verdict"] == J.UNVERIFIED


# --- judge_criterion via FakeLLMClient --------------------------------------

def test_judge_criterion_attaches_criterion_id():
    raw = json.dumps({"score": 4, "citation": "behavioral.md:4", "tier": "T2",
                      "justification": "meets deadlines"})
    client = J.FakeLLMClient(raw)
    cs = J.judge_criterion(_crit("c7"), _evidence(), client, scale={"min": 0, "max": 5})
    assert cs["criterion_id"] == "c7" and cs["verdict"] == J.PASS
    assert client.calls, "client must have been called"


def test_judge_criterion_client_raise_is_error():
    class Boom:
        def complete(self, s, u):
            raise RuntimeError("network down")
    cs = J.judge_criterion(_crit(), _evidence(), Boom(), scale={"min": 0, "max": 5})
    assert cs["verdict"] == J.ERROR and cs["criterion_id"] == "c1"


def test_judge_rubric_one_score_per_criterion():
    rubric = {"scale": {"min": 0, "max": 5}, "domains": [
        {"id": "d", "weight": 1.0, "criteria": [_crit("c1"), _crit("c2")]}]}
    raw = json.dumps({"score": 3, "citation": "x.md:1", "tier": "T2", "justification": "y"})
    out = J.judge_rubric(rubric, {"c1": _evidence(), "c2": _evidence()}, J.FakeLLMClient(raw))
    assert sorted(s["criterion_id"] for s in out) == ["c1", "c2"]


# --- real client is gated ----------------------------------------------------

def test_make_client_raises_without_credentials(monkeypatch):
    for k in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(RuntimeError):
        J.make_client()


def test_build_prompt_includes_criterion_and_evidence():
    p = J.build_judge_prompt(_crit(), _evidence(), {"min": 0, "max": 5})
    assert "conscientiousness" in p.lower()
    assert "behavioral.md:4" in p and "T2" in p
