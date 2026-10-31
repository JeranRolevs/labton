# Execution boundaries

Planning and workspace creation do not execute candidate code or call a model.
Text workflows call the configured provider only when explicitly run.

The memory example uses a trusted supervisor and a separate untrusted policy interpreter
under macOS sandbox-exec. Policy code receives causal observations and declared bounded state;
private seeds, labels, future inputs and provider credentials remain outside that process.
AST checks enforce the API; the OS sandbox is the execution boundary. Qualification must pass
on the actual machine. Unsupported platforms fail closed rather than running candidates
without the sandbox. Do not replace that failure with an unsandboxed execution path.

Numeric-state accounting and process RSS are different measures. CPU/time bounds and RSS
monitoring supplement the strict retained-state limit. Full multi-tenant isolation, arbitrary
unrestricted Python execution and Linux/Windows policy sandboxes are not implemented.

Keep .env, private_splits.json, generated trials and results out of Git. Trial prompts and
outputs may contain user research details; inspect them before intentionally sharing.
Report issues to the repository owner through the channel they provide; no contact address
or vulnerability-reporting endpoint is assumed here.
