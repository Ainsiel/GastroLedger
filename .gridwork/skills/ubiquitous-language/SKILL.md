# Ubiquitous Language Skill

## Purpose

Create a precise language shared by domain experts, requirements, architecture, APIs and tests.

## Procedure

1. Extract domain nouns, verbs, states, policies and business events.
2. Group terms by subdomain or lifecycle.
3. Detect synonyms, overloaded words, vague words and implementation terms posing as domain terms.
4. Propose one canonical term and list aliases to avoid.
5. Define each term in one domain-focused sentence.
6. Record important relationships and cardinality.
7. Validate disputed terms with the user before treating them as canonical.
8. Apply accepted language consistently to later architecture artifacts.

## Output Shape

For each term record:

```text
term
definition
subdomain
aliases_to_avoid
related_terms
example_business_sentence
status = proposed|accepted|disputed
```

Also include:

- flagged ambiguities and their impact;
- relationships between important concepts;
- example dialogue demonstrating precise usage;
- terms deliberately excluded because they are technical rather than domain language.

## Rules

- Define what a term is, not only what it does.
- Do not use the same term for an actor, identity and organization unless the domain truly does.
- Do not convert every class name into a domain term.
- Treat language disagreements as architecture signals, not editorial cleanup.
