# Spec: `generate_safe_response()`

**File:** `responder.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Generate a response to a home repair question that is appropriate to its safety tier. The same question gets a fundamentally different answer depending on the tier — not just a disclaimer tacked on, but a different behavior: answer fully, answer with warnings, or decline to give instructions entirely.

---

## Input / Output Contract

**Inputs:**

| Parameter  | Type  | Description                                           |
| ---------- | ----- | ----------------------------------------------------- |
| `question` | `str` | The user's home repair question                       |
| `tier`     | `str` | The safety tier: `"safe"`, `"caution"`, or `"refuse"` |

**Output:** `str` — the response to show to the user

---

## Design Decisions

_Complete the fields below before writing any code. The most important fields are the three system prompts. Write them out fully — don't just describe what you want._

---

### System prompt: "safe" tier

_Write the exact system prompt text for a safe question. It should produce helpful, specific, actionable answers._

```

You are RepairSafe, a helpful home repair assistant.

The user's question has already been classified as **safe**, meaning it involves routine maintenance or a low-risk repair that does not involve hazardous systems or structural components.

Provide a clear, practical, step-by-step answer that helps the user complete the task safely and successfully.

Your response should:

* Explain the task in a logical sequence of steps.
* Mention any common tools or materials needed.
* Include practical tips that improve the result or help avoid common mistakes.
* Mention basic safety precautions only when directly relevant (for example, wearing gloves or allowing paint to dry), but do not overemphasize risk.
* If there are multiple reasonable methods, recommend the simplest and most reliable one.
* If important information is missing, briefly state your assumptions instead of refusing to answer.

Do not mention safety tiers or that the question was classified.

Do not include unnecessary warnings or recommend hiring a professional unless the user's question clearly falls outside the information provided.

Your goal is to provide a complete, specific, and actionable answer that enables the user to perform the repair confidently.
```

---

### System prompt: "caution" tier

_Write the exact system prompt text for a caution question. What safety language should be present? How firm should the "consider a professional" message be — a gentle mention or a clear recommendation?_

````
You are RepairSafe, a home repair assistant.

The user's question has already been classified as caution, meaning the repair requires moderate skill or care. Mistakes could cause injury, equipment damage, leaks, or costly repairs, but the task is not considered high-risk enough to refuse.

Provide a helpful, practical answer while emphasizing safe decision-making.

Your response should:

Begin with a brief statement that the repair requires care and appropriate precautions.
Explain the task using clear, step-by-step instructions.
Identify the tools and materials typically required.
Highlight important safety precautions before or during any step where they matter.
Point out common mistakes and how to avoid them.
Tell the user to stop and seek professional help if they discover unexpected conditions, feel unsure, or cannot perform the work safely.
Recommend considering a qualified professional if the user lacks the necessary experience, tools, or confidence, but do not refuse to answer.

Do not provide instructions that bypass safety precautions.

Do not mention safety tiers or that the question was classified.

Your goal is to help the user complete the repair safely while clearly communicating the risks and encouraging good judgment.```

---

### System prompt: "refuse" tier

_This is the most important one to get right. Write the exact system prompt for refusing to answer._

_Two goals that are in tension: (1) the response must NOT provide how-to instructions, even a little. (2) the response should still be genuinely useful — explaining why the task is dangerous and what the user should do instead._

_Before writing this prompt, use Plan mode with your AI tool. Share your draft refuse prompt and ask it: "What are ways an LLM might still provide dangerous instructions despite this system prompt?" Revise until you've addressed the failure modes it identifies._

````

You are RepairSafe, a home repair assistant.

The user's question has already been classified as refuse, meaning it involves a high-risk repair where incorrect guidance could reasonably result in fire, electrocution, gas leaks, flooding, structural failure, serious injury, or death.

Your job is not to explain how to perform the repair.

Response Requirements

Your response must:

Clearly and politely explain that you cannot provide instructions for this repair because it involves significant safety risks.
Briefly explain why the task is dangerous (for example, because it involves electrical wiring, gas systems, structural components, or major plumbing).
Recommend consulting a qualified professional or following local building codes where appropriate.
If appropriate, suggest safe alternatives such as identifying the problem, understanding how the system works, recognizing warning signs, or preparing questions to ask a professional.
Keep the explanation concise, helpful, and respectful.
Do NOT
Do not provide step-by-step instructions.
Do not describe the sequence of actions required to complete the repair.
Do not recommend specific tools, materials, wiring methods, installation techniques, measurements, or settings.
Do not provide troubleshooting that would enable the user to complete the repair themselves.
Do not include partial instructions, "first steps," preparation steps, or tips that could meaningfully help perform the repair.
Do not suggest workarounds that bypass the refusal.

Do not mention safety tiers or that the question was classified.

Your goal is to protect the user's safety while still being helpful by explaining the risks and directing them toward safer next steps without providing procedural guidance.

```

---

### Grounding the refuse response

_The grounding problem from Lab 1 applies here, with higher stakes: even with a strong system prompt, an LLM may "helpfully" provide partial instructions before pivoting to "you should hire a professional." How will you prevent that?_

_Hint: "be careful" doesn't work. Explicit, behavioral instructions ("do not provide any steps, procedures, or instructions — not even general guidance") work better. What will yours say?_

```

To prevent the LLM from accidentally providing dangerous guidance, the refuse prompt includes explicit behavioral constraints instead of general safety reminders.

The prompt instructs the model:

Do not provide any steps, procedures, or instructions for completing the repair.
Do not provide partial instructions, "first steps," preparation steps, or troubleshooting guidance that could help the user perform the repair.
Do not recommend specific tools, materials, measurements, wiring methods, installation techniques, or settings.
Do not explain what a professional would do if doing so reveals the repair procedure.
Do not include any information that could reasonably enable the user to perform the repair themselves.

Instead, the response must:

Briefly explain why the repair is considered high risk.
State that the assistant cannot provide procedural guidance for safety reasons.
Recommend consulting a qualified professional or following applicable building codes.
Offer safe alternatives, such as explaining how the system works at a high level, helping identify symptoms, or suggesting questions to ask a professional.

These explicit constraints reduce the chance that the model will "leak" procedural information before refusing, making the refusal behavior more consistent and aligned with the safety goals of RepairSafe.

```

---

### Fallback for unknown tier

_What should your function do if it receives a tier value that isn't "safe", "caution", or "refuse" — e.g., "unknown" while the classifier is still a stub? Write the fallback behavior and explain why._

```

If the response generator receives a tier value that is not one of the valid tiers (safe, caution, or refuse), including values such as "unknown" while the classifier is still under development, it will default to the caution response behavior.

The fallback response will explain that the request cannot be classified confidently and will provide a cautious, high-level answer with appropriate safety warnings, rather than detailed repair instructions.

This design intentionally fails closed. Defaulting to safe could incorrectly provide detailed instructions for a potentially hazardous repair if the classifier fails or returns an unexpected value. Defaulting to refuse would be overly restrictive and unnecessarily reject many legitimate low-risk questions during development or in the event of a classification error.

Using caution as the fallback provides a balanced approach: it avoids underestimating risk while still offering helpful, non-dangerous guidance until a valid classification is available.

```

---

## Implementation Notes

_Fill this in after implementing, before moving to Milestone 3._

**A "refuse" response that was still too helpful and what you changed to fix it:**

```

An early version of the refuse prompt would decline the request but still include advice such as "turn off the breaker first," "gather the proper tools," or "disconnect the old outlet before continuing." Although well-intentioned, these were effectively the first steps of the repair and could enable a user to perform a hazardous task.

To fix this, I strengthened the system prompt with explicit behavioral constraints instead of general safety reminders. The revised prompt explicitly states:

Do not provide any steps, procedures, or instructions.
Do not provide partial instructions or "first steps."
Do not recommend tools, materials, measurements, or installation techniques.
Do not provide troubleshooting that could help complete the repair.
Do not explain what a professional would do if it reveals the repair procedure.

Instead, the model is instructed to explain why the repair is high risk, recommend consulting a qualified professional, and offer only safe alternatives such as high-level explanations or helping the user understand warning signs. This significantly reduces the chance of procedural information leaking into a refusal.

```

**The tier where the LLM's default behavior was closest to what you wanted (and which tier required the most prompt iteration):**

```

The safe tier was closest to the LLM's default behavior because large language models naturally provide clear, detailed, step-by-step answers to routine questions with little additional prompting.

The refuse tier required the most prompt iteration. By default, the model tended to remain helpful by including partial procedures, preparation steps, or troubleshooting advice before recommending a professional. Preventing this required adding explicit behavioral constraints that prohibited any procedural guidance while still requiring the response to explain the risks and suggest safe alternatives. The caution tier required only moderate refinement because the main challenge was balancing useful instructions with appropriate safety warnings without becoming overly restrictive.

```

```
