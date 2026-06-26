# Contract First Boundaries Skill

## Procedure

1. Confirm the approved boundary and its known consumer.
2. Confirm why the contract must exist before the first functional slice.
3. Materialize the smallest stable type, port or public schema required.
4. Keep methods and data limited to approved use cases.
5. Record source decision, consumer, protected boundary and deferrable details.
6. Defer any contract without complete traceability.

An interface is not architecture evidence by itself. Prefer no abstraction over an
abstraction created only for hypothetical reuse.

## Contract Test

Every contract must identify:

- approved architecture source;
- known consumer;
- first slice that needs it;
- boundary it protects;
- details deliberately deferred.

## Output

Produce minimal contracts and a traceability record. Do not produce adapter behavior.

## Gates

Stop before public contract decisions, unapproved methods, scope expansion or any
contract without a known consumer.
