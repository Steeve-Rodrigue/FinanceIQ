# app/repos/ conventions

- Repos are the only layer permitted to issue database queries. Services and routers must never import `sqlalchemy` or touch a `Session`/`AsyncSession` directly.
- Every repo function should have a corresponding test in `tests/repos/`.

If this project is multi-tenant, add a rule here that every repo function takes the tenant/user id as its first parameter. That decision is project-specific and is not assumed by this generic scaffold.
