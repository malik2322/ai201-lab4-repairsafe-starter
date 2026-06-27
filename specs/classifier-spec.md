# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter  | Type  | Description                     |
| ---------- | ----- | ------------------------------- |
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key        | Type  | Description                                        |
| ---------- | ----- | -------------------------------------------------- |
| `"tier"`   | `str` | One of: `"safe"`, `"caution"`, `"refuse"`          |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

_Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours._

---

### Tier definitions

_Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications._

**safe:**

```
Routine maintenance and low-risk repairs. Most homeowners can complete these without specialized training or tools. like Patching drywall, painting, replacing a light bulb, unclogging a drain, tightening hardware, replacing weather stripping
```

**caution:**

````
Repairs where mistakes are costly, require some skill, or involve mild risk of injury. Doable for motivated homeowners, but worth careful consideration. like Replacing a faucet, resetting a GFCI outlet, replacing a toilet flapper, installing a ceiling fan, basic tile work ```

**refuse:**
````

Repairs where an amateur mistake can cause fire, flooding, structural failure, injury, or death — or where local code requires a licensed professional. like Electrical panel work, gas line repair, structural modifications, main water line work, load-bearing wall removal, roof framing

```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```

For the classifier itself, I would use:

Tier definitions (as above).
3–5 few-shot examples for each tier to reinforce the boundaries.
A tie-breaking rule:
When uncertain, classify into the higher-risk tier.

If the task requires opening or modifying household electrical wiring, gas lines, structural components, or other hazardous systems, classify it as refuse, even if many homeowners commonly perform it.

With that rule:

"Can I replace my own outlets?" → Refuse (because it involves live electrical wiring if performed incorrectly).
"How do I reset a GFCI outlet?" → Caution (no wiring changes are required).
"How do I replace a light bulb?" → Safe.

```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```

The classifier will return its decision as a JSON object containing the predicted tier and a short explanation. Using JSON makes the output deterministic and easy for the agent to parse without relying on regular expressions or keyword matching.

The required output format is:

```json
{
  "tier": "safe",
  "reason": "The task is routine maintenance with minimal risk and does not involve hazardous systems."
}
```

The `tier` field must contain exactly one of: `"safe"`, `"caution"`, or `"refuse"`.

The `reason` field should be a single concise sentence explaining why the question belongs in that tier. The agent reads the `tier` field to determine how to respond, while the `reason` can be logged or displayed to help explain the classification decision.

```

---

## System Message

You are the safety classifier for RepairSafe, a home repair Q&A assistant.

Your only task is to classify a user's home repair question into exactly one of three safety tiers.

### Tier Definitions

**safe**

Routine maintenance and low-risk home repairs that do not involve hazardous systems or structural components. Mistakes are unlikely to cause injury or significant property damage.

Examples:

* Painting
* Patching drywall
* Replacing a light bulb
* Tightening cabinet hardware
* Replacing weather stripping
* Unclogging a drain

---

**caution**

Repairs involving existing household fixtures or systems that require moderate skill or care but **do not create, extend, reroute, or redesign** the home's electrical, gas, plumbing, or structural systems.

These tasks repair or replace existing components using existing infrastructure.

Mistakes may cause equipment damage, leaks, or minor injury but are unlikely to create major life-threatening hazards when proper precautions are followed.

Examples:

* Replacing an existing electrical outlet
* Replacing an existing light switch
* Resetting a GFCI outlet
* Replacing a faucet
* Replacing a toilet flapper
* Installing a ceiling fan on an existing, properly wired ceiling box
* Basic tile repair

---

**refuse**

Repairs that create, install, extend, reroute, redesign, or substantially modify electrical wiring, gas lines, plumbing systems, structural components, or other hazardous systems.

These tasks can reasonably result in electrocution, fire, gas leaks, flooding, structural failure, serious injury, or death if performed incorrectly.

Examples:

* Adding a new electrical outlet
* Installing a new electrical circuit
* Running new electrical wiring
* Electrical panel work
* Installing a subpanel
* Gas line repair or installation
* Main water line work
* Load-bearing wall removal
* Roof framing

### Boundary Rules

1. Replacing an existing component using existing wiring, plumbing, or mounting generally belongs in **caution**.
2. Creating, extending, rerouting, or modifying a home's infrastructure belongs in **refuse**.
3. Classify based on the **action requested**, not simply because the topic involves electricity, plumbing, or gas.
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

{
"tier": "safe | caution | refuse",
"reason": "One concise sentence explaining the classification."
}

Do not include markdown, code fences, or any additional text.
```

**User message:**

```

## User Message

Classify the following home repair question.

Question:
{{user_question}}

```

---

### Caution/refuse boundary

_The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why._

```

### Caution/Refuse Boundary Rule

Classify a repair as refuse if it requires creating, extending, rerouting, or substantially modifying electrical, gas, plumbing, or structural systems, or if incorrect instructions could reasonably result in fire, electrocution, gas leaks, structural failure, serious injury, or death. Repairs that replace or repair existing fixtures using existing infrastructure belong in caution, provided they do not modify the underlying system.

Boundary Examples

Example 1

Question: "Can I replace an electrical outlet that stopped working?"

Classification: Caution

Reason: The repair replaces an existing outlet using the home's existing wiring and does not modify the electrical system, although it still requires care and proper safety precautions.

Example 2

Question: "Can I add a new electrical outlet to my garage?"

Classification: Refuse

Reason: Installing a new outlet requires extending or modifying the home's electrical wiring, creating a significantly higher risk of electrocution, fire, and code violations.

```

---

### Fallback behavior

_What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?_

_Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?_

````

### Fallback Behavior

If the LLM response cannot be parsed as valid JSON or does not contain the required `tier` and `reason` fields, the classifier will return a default result of:

```json
{
  "tier": "caution",
  "reason": "Classification failed because the LLM response could not be parsed."
}
````

Similarly, if the parsed `tier` is not one of the valid values in `VALID_TIERS` (`safe`, `caution`, or `refuse`), the classifier will return the same fallback response.

The system intentionally **fails closed** by defaulting to the **caution** tier rather than **safe**. Returning `safe` after a parsing or validation error could incorrectly allow potentially hazardous repair instructions to be treated as low risk. Defaulting to `caution` is more conservative because it prevents the assistant from underestimating risk while still allowing the application to respond gracefully instead of crashing.

```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```

[your answer here]

```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```

[your answer here]

```

```
