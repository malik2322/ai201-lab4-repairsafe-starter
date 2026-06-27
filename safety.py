import json

from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)

_SYSTEM_PROMPT = """\
You are the safety classifier for RepairSafe, a home repair Q&A assistant.

Your only task is to classify a user's home repair question into exactly one of three safety tiers.

### Tier Definitions

**safe**
Routine maintenance and low-risk home repairs that do not involve hazardous systems or structural components. Mistakes are unlikely to cause injury or significant property damage.

Examples:
- Painting
- Patching drywall
- Replacing a light bulb
- Tightening cabinet hardware
- Replacing weather stripping
- Unclogging a drain

**caution**
Repairs involving existing household fixtures or systems that require moderate skill or care but do not create, extend, reroute, or redesign the home's electrical, gas, plumbing, or structural systems. These tasks repair or replace existing components using existing infrastructure. Mistakes may cause equipment damage, leaks, or minor injury but are unlikely to create major life-threatening hazards when proper precautions are followed.

Examples:
- Replacing an existing electrical outlet
- Replacing an existing light switch
- Resetting a GFCI outlet
- Replacing a faucet
- Replacing a toilet flapper
- Installing a ceiling fan on an existing, properly wired ceiling box
- Basic tile repair

**refuse**
Repairs that create, install, extend, reroute, redesign, or substantially modify electrical wiring, gas lines, plumbing systems, structural components, or other hazardous systems. These tasks can reasonably result in electrocution, fire, gas leaks, flooding, structural failure, serious injury, or death if performed incorrectly.

Examples:
- Adding a new electrical outlet
- Installing a new electrical circuit
- Running new electrical wiring
- Electrical panel work
- Installing a subpanel
- Gas line repair or installation
- Main water line work
- Load-bearing wall removal
- Roof framing

### Boundary Rules

1. Replacing an existing component using existing wiring, plumbing, or mounting generally belongs in caution.
2. Creating, extending, rerouting, or modifying a home's infrastructure belongs in refuse.
3. Classify based on the action requested, not simply because the topic involves electricity, plumbing, or gas.
4. If a question reasonably fits two tiers, choose the higher-risk tier.

### Boundary Examples

Question: "Can I replace an electrical outlet that stopped working?"
Answer: caution

Question: "Can I replace a light switch?"
Answer: caution

Question: "Can I add a new electrical outlet to my garage?"
Answer: refuse

Question: "How do I run a new electrical circuit?"
Answer: refuse

Return only valid JSON in this exact format:

{"tier": "safe | caution | refuse", "reason": "One concise sentence explaining the classification."}

Do not include markdown, code fences, or any additional text."""

_FALLBACK = {"tier": "caution", "reason": "Classification failed because the LLM response could not be parsed."}


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned
    """
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify the following home repair question.\n\nQuestion:\n{question}"},
            ],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
    except Exception:
        return dict(_FALLBACK)

    try:
        parsed = json.loads(raw)
        tier = parsed.get("tier", "").strip().lower()
        reason = parsed.get("reason", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return dict(_FALLBACK)

    if tier not in VALID_TIERS:
        return dict(_FALLBACK)

    return {"tier": tier, "reason": reason}
