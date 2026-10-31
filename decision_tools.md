# Decisions inside an agent episode

An agent may issue decision.assess for an allowlisted bounded question and then resume its own
generation context. The same permission and budget checks apply to primes and children.
The selected backend receives only the caller's permitted context references.

The user chooses LLM-only, shadow or selected-active mode. LLM-only judges through the generation
model. Shadow records a separate opinion without returning it to the acting context. Active
routing returns a valid specialist answer; unavailable or invalid answers may fall back to the
generation model within the same remaining budget. No decision certifies empirical correctness.

Configure a chat-completions or typed JSON endpoint by service URL, endpoint path, model and
a private key environment variable. There are no built-in account or model aliases. Unsupported
protocols require another adapter. [Configuration and JSON contracts](docs/DECISION_PROVIDERS.md).

Request, token and timing receipts retain the configured provider identity and resolved model.
Child decisions inherit permissions and shared resource limits. An exhausted budget does not
permit another specialist request, retry or fallback. Model-reported probabilities describe the
judgment, not measured research uncertainty. [Statistical choices](statistical_analysis.md).
