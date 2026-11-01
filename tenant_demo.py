"""Green tests, broken isolation: a deterministic demo (no LLM involved).

1. The original get_invoice() enforces tenant isolation; the happy-path suite is green.
2. A "rewrite" swaps the scan for an id index and drops the tenant check; still green.
3. A cross-tenant negative test turns the rewrite red.
4. Security mutation check: delete the tenant check and see which suite notices.
"""

INVOICES = [
    {"id": 1, "tenant": "acme", "amount": 120},
    {"id": 2, "tenant": "acme", "amount": 80},
    {"id": 3, "tenant": "globex", "amount": 500},
]
BY_ID = {inv["id"]: inv for inv in INVOICES}


def get_invoice_original(user, invoice_id):
    for inv in INVOICES:
        if inv["id"] == invoice_id and inv["tenant"] == user["tenant"]:
            return inv
    return None


def get_invoice_rewrite(user, invoice_id):
    # "Optimized": O(1) lookup. The tenant check silently disappeared.
    return BY_ID.get(invoice_id)


def get_invoice_mutant(user, invoice_id):
    # Mutation of the original: the tenant condition is deleted, nothing else changes.
    for inv in INVOICES:
        if inv["id"] == invoice_id:
            return inv
    return None


def happy_path_suite(get_invoice):
    acme = {"name": "alice", "tenant": "acme"}
    return [
        get_invoice(acme, 1)["amount"] == 120,
        get_invoice(acme, 2)["amount"] == 80,
        get_invoice(acme, 99) is None,
    ]


def security_suite(get_invoice):
    acme = {"name": "alice", "tenant": "acme"}
    return happy_path_suite(get_invoice) + [
        get_invoice(acme, 3) is None,  # must not see another tenant's invoice
    ]


def run(label, suite, impl):
    results = suite(impl)
    status = "GREEN" if all(results) else "RED"
    print(f"{label:<44} {sum(results)}/{len(results)} passed  {status}")


if __name__ == "__main__":
    run("original  + happy-path tests", happy_path_suite, get_invoice_original)
    run("rewrite   + happy-path tests", happy_path_suite, get_invoice_rewrite)
    run("rewrite   + cross-tenant negative test", security_suite, get_invoice_rewrite)
    print("\nMutation check: remove the tenant condition from the original.")
    for name, suite in [("happy-path", happy_path_suite), ("security", security_suite)]:
        killed = not all(suite(get_invoice_mutant))
        print(f"  {name:<11} suite: mutant {'KILLED' if killed else 'SURVIVED (check is unprotected)'}")
