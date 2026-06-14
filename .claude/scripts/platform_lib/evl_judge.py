"""Per-criterion LLM judge protocol — ports the sibling eval honesty contract.

The judge scores ONE criterion against its evidence bundle and returns a
CriterionScore dict {criterion_id, score, citation, tier, justification, verdict}.
It NEVER fabricates a pass: a score with no real citation+tier is UNVERIFIED, an
unparseable reply is ERROR. The LLM is reached only through an injectable client —
FakeLLMClient drives every test (no network, no key); the real client is built by
make_client() solely when credentials exist (deferred path, needs human review),
so CI can never hit the network.

The actual high-stakes orchestration (spawning N input-isolated judges) is the
skill's job via the Agent tool; this module is the stateless, testable protocol.
"""
import json
import os
import re

from platform_lib.evl_aggregate import VALID_TIERS

PASS, FAIL, UNVERIFIED, ERROR = "PASS", "FAIL", "UNVERIFIED", "ERROR"
ARTIFACT_CAP = 24000  # chars of evidence fed to the judge (keeps the prompt bounded)

JUDGE_SYSTEM = (
    "You are a strict, skeptical evidence-based rubric judge. You score ONE criterion "
    "for ONE character against the supplied evidence ONLY. Use the rubric's anchor scale. "
    "You MUST cite exactly one evidence item by its source and tier; if NO supplied evidence "
    "supports a score, return score null with verdict UNVERIFIED — never guess, never give "
    "the benefit of the doubt. Do NOT explain outside the JSON, do NOT use a code fence. "
    "Your ENTIRE response must be exactly one JSON object and nothing else: "
    '{"score": <number|null>, "citation": "<source>"|null, "tier": "T1".."T5"|null, '
    '"justification": "<one short sentence>", "verdict": "PASS"|"FAIL"|"UNVERIFIED"}'
)


class FakeLLMClient:
    """Deterministic client for tests. ``responder`` is a callable (system,user)->str,
    a list popped in call order, a dict mapping a user-substring to a reply, or a str."""

    def __init__(self, responder):
        self._responder = responder
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        r = self._responder
        if callable(r):
            return r(system, user)
        if isinstance(r, list):
            return r.pop(0) if r else ""
        if isinstance(r, dict):
            for needle, reply in r.items():
                if needle in user:
                    return reply
            return r.get("_default", "")
        return str(r)


class UrllibAnthropicClient:
    """Minimal stdlib client for an Anthropic-compatible Messages endpoint. No SDK
    dependency; built only when credentials exist. Untested in CI by design."""

    def __init__(self, token: str, base_url: str, model: str):
        self._token, self._base, self._model = token, base_url.rstrip("/"), model

    def complete(self, system: str, user: str) -> str:
        import urllib.request

        body = json.dumps({"model": self._model, "max_tokens": 1024, "system": system,
                           "messages": [{"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(
            f"{self._base}/v1/messages", data=body,
            headers={"content-type": "application/json", "anthropic-version": "2023-06-01",
                     "x-api-key": self._token, "authorization": f"Bearer {self._token}",
                     "user-agent": "anthropic-sdk-python/0.39.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310 (explicit gen path)
            data = json.loads(resp.read())
        return "".join(p.get("text", "") for p in data.get("content", []) if isinstance(p, dict))


def make_client():
    """Return a real LLM client, or raise. Deferred path: needs credentials + review."""
    token = os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    model = (os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL")
             or os.environ.get("ANTHROPIC_MODEL") or "claude-sonnet-4-6")
    if not token:
        raise RuntimeError(
            "evl_judge real run needs ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY (deferred path: "
            "key + human review required). Tests inject FakeLLMClient and never reach here.")
    return UrllibAnthropicClient(token, base, model)


# --- prompt + parse ----------------------------------------------------------

def build_judge_prompt(criterion: dict, evidence: list, scale: dict, character_ctx: str = "") -> str:
    anchors = "; ".join(f"{k}={v}" for k, v in (criterion.get("anchors") or {}).items())
    lines = [f"[{e.get('tier') or '?'}] {e.get('source')} — {e.get('text', '')}" for e in evidence]
    bundle = "\n".join(lines) or "(no evidence supplied)"
    if len(bundle) > ARTIFACT_CAP:
        bundle = bundle[:ARTIFACT_CAP] + "\n…[truncated]"
    rng = f"{scale.get('min')}..{scale.get('max')}" if scale else "the rubric scale"
    return (
        f"{('CHARACTER CONTEXT: ' + character_ctx.strip() + chr(10) + chr(10)) if character_ctx else ''}"
        f"CRITERION (id={criterion.get('id')}): {criterion.get('text', '').strip()}\n"
        f"SCORE RANGE: {rng}\nANCHORS: {anchors}\nMINIMUM EVIDENCE TIER: {criterion.get('min_tier')}\n\n"
        f"CANDIDATE EVIDENCE (cite one by its source + tier):\n{bundle}\n\n"
        'Now output ONLY the JSON verdict object and nothing else.')


def _score_obj(score, citation, tier, justification, verdict) -> dict:
    return {"score": score, "citation": citation, "tier": tier,
            "justification": justification, "verdict": verdict}


def _num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _norm_tier(t):
    if t is None:
        return None
    s = str(t).upper()
    s = s if s.startswith("T") else f"T{s}"
    return s if s in VALID_TIERS else None


def parse_verdict(raw: str) -> dict:
    """Parse a judge reply into a CriterionScore. JSON-first, tolerant of prose.
    Uncited/invalid → UNVERIFIED; unparseable → ERROR. Never invents a PASS."""
    m = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(0))
        except (ValueError, TypeError):
            obj = None
        if isinstance(obj, dict):
            return _from_obj(obj)
    head = (raw or "").strip().upper()
    if head.startswith(UNVERIFIED):
        return _score_obj(None, None, None, "(bare UNVERIFIED)", UNVERIFIED)
    return _score_obj(None, None, None, f"unparseable judge reply: {(raw or '')[:80]!r}", ERROR)


def _from_obj(obj: dict) -> dict:
    score = _num(obj.get("score"))
    citation = obj.get("citation") or None
    tier = _norm_tier(obj.get("tier"))
    just = str(obj.get("justification") or obj.get("rationale") or "").strip() or "(no justification)"
    explicit = str(obj.get("verdict") or "").strip().upper()
    verified = score is not None and bool(citation) and bool(tier)
    if explicit in (FAIL, UNVERIFIED, ERROR):
        verdict = explicit
    else:  # blank or a claimed PASS — only a truly-verified score earns PASS
        verdict = PASS if verified else UNVERIFIED
    return _score_obj(score, citation, tier, just, verdict)


def judge_criterion(criterion: dict, evidence: list, client, scale: dict = None,
                    character_ctx: str = "") -> dict:
    try:
        raw = client.complete(JUDGE_SYSTEM, build_judge_prompt(criterion, evidence, scale, character_ctx))
        cs = parse_verdict(raw)
    except Exception as e:  # noqa: BLE001 — a broken judge call is loud, not a crash
        cs = _score_obj(None, None, None, f"judge call raised {type(e).__name__}: {e}", ERROR)
    cs["criterion_id"] = criterion["id"]
    return cs


def judge_rubric(rubric: dict, evidence_by_criterion: dict, client, character_ctx: str = "") -> list:
    scale = rubric.get("scale")
    return [judge_criterion(c, evidence_by_criterion.get(c["id"], []), client, scale, character_ctx)
            for d in rubric["domains"] for c in d["criteria"]]
