# ADR-0003: Immutable Lot-Aware Inventory Ledger

```text
status = proposed
```

## Decision

Inventory truth is an immutable transaction/entry ledger linked to lots. Current
balances are projections. Allocation uses FEFO when expiry exists and FIFO otherwise;
accepted commands never create negative stock.

## Consequences

- Corrections use compensating transactions, never editing posted entries.
- Contested consumption requires locking/constraint tests.
- Imports with shortage produce allocation exceptions rather than negative balances.
- Reports can reconcile theoretical and actual consumption from stable evidence.
