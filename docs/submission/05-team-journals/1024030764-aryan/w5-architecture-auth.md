# Week 5: Architecture and Authentication Scaffold

## Objective

Convert the approved proposal into an executable architecture and establish the shared role/security core.

## Work completed

- Selected Django with SQLite for the thin prototype.
- Defined the custom User role model for Student, TA / Faculty, and Placement Admin.
- Configured session authentication, CSRF middleware, templates, static files, media, and timezone.
- Created the first migration and repository run/check commands.
- Drafted the SRS IDs and architecture boundaries used by both modules.

## Technical decision

Server-rendered Django was preferred over a separate frontend/API because authentication, forms, persistence, and testing are the Week 7 risks. The ORM keeps a later PostgreSQL move possible.

## Evidence

`python code/manage.py check` completed with zero issues; the initial migration applies on an empty database.
