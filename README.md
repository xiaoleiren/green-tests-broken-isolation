# green-tests-broken-isolation

A 66-line, dependency-free demo for the article
"Who Checks the Tests When an Agent Rewrites the Code?"

It shows one failure mode: a rewrite drops a tenant-isolation check and the
existing tests stay green. No LLM is involved; the "rewrite" is deliberately flawed rewrite
so the result is deterministic.

## Run

```
python3 tenant_demo.py
```

Requires Python 3.8+. No packages.

## Expected output

```
original  + happy-path tests                 3/3 passed  GREEN
rewrite   + happy-path tests                 3/3 passed  GREEN
rewrite   + cross-tenant negative test       3/4 passed  RED

Mutation check: remove the tenant condition from the original.
  happy-path  suite: mutant SURVIVED (check is unprotected)
  security    suite: mutant KILLED
```

## What it shows, and what it doesn't

- Shows: tests written from one tenant's point of view cannot detect a lost
  tenant check; one negative test can; deleting the check (a mutation) tells
  you which suite actually protects it.
- Doesn't show: how often coding agents make this mistake. For evidence on
  agents and tests, see UTBoost (ACL 2025) and ImpossibleBench (ICLR 2026).

## License

MIT
