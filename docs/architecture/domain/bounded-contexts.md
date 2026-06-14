# Bounded Contexts

## Platform & Organization

Owns tenant lifecycle, local identities, sessions, scoped roles, branches and
warehouses. Its invariant is that every membership and operational scope belongs to
one tenant.

## Menu Engineering

Owns units, ingredients, recipe versions, component quantities, branch prices and
cost snapshots. It prevents incompatible conversion, recipe cycles and uncosted
approval.

## Procurement

Owns suppliers, versioned offers, purchase orders, receipts and returns. It records
commercial-looking amounts only as operational cost evidence; it never pays or
posts accounting entries.

## Inventory & Production

Owns lots and the immutable inventory ledger. It allocates FEFO/FIFO, prevents
negative balances and records production, transfers, waste, counts and exceptions.

## Store Operations

Owns operational sales imports, cash-shift records, schedules and attendance. It
does not process payments or calculate payroll.

## Control & Insights

Owns royalty policies/estimates, ordering holds, audit, jobs, notifications and
report projections. It does not mutate source business facts.
