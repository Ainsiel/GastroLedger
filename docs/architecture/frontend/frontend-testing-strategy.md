# Frontend Testing Strategy

| Behavior | Level | Boundary | Required states |
|---|---|---|---|
| Registration and first session | End-to-end | Next.js + FastAPI + PostgreSQL | success, duplicate, validation |
| Recipe editor and approval | Feature integration | UI + typed API substitute/contract | draft, missing cost, conflict |
| Receiving form | Feature integration | UI + contract | partial, rejected line, duplicate |
| Blind count | End-to-end | Next.js + FastAPI + PostgreSQL | blind entry, recount, denied self-approval |
| Sales import preview/status | Feature + end-to-end | Browser + API/job | pending, partial, exception, duplicate |
| Cost variance report | Feature integration | UI + contract | loading, complete, incomplete, filtered |
| Permission visibility | Feature integration | UI + policy result | authorized and unauthorized |

All critical forms require keyboard operation, accessible names, preserved input
after recoverable errors and visible correlation IDs for unexpected failures.
