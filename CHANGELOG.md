# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2026-01-26]

### Added
- Add `/update-docs` Claude Code skill for automated documentation updates (`.claude/skills/update-docs/SKILL.md`)
- Add CHANGELOG.md with Keep a Changelog format
- Add changelog template for consistent entry formatting (`.claude/skills/update-docs/changelog-template.md`)

### Changed
- Simplify CLAUDE.md to essential quick reference information
- Update .gitignore to track `.claude/skills/` directory

### Removed
- Remove QUICKSTART_AUTH.md (consolidated into other docs)

### Documentation
- Reorganize documentation structure into `docs/` subdirectories:
  - `docs/api/` - API specifications
  - `docs/architecture/` - Architecture documents
  - `docs/database/` - Database schemas and documentation
  - `docs/research/` - Research notes
- Move deployment docs to `docs/DEPLOYMENT.md`
- Move getting started guide to `docs/GETTING_STARTED.md`
- Move project status to `docs/PROJECT_STATUS.md`
- Move API specification to `docs/api/SPECIFICATION.md`
- Move architecture analysis to `docs/architecture/ANALYSIS.md`
- Move architecture overview to `docs/architecture/OVERVIEW.md`
- Move database schema to `docs/database/VISUAL_SCHEMA.md`
- Move research docs to `docs/research/NOCODE_PLATFORM.md`
- Add development workflow guide (`docs/DEVELOPMENT_WORKFLOW.md`)
- Add frontend requirements research (`docs/research/FRONTEND_REQUIREMENTS.md`)

## [2026-01-25]

### Added
- Add log rotation with ISO 8601 timestamps to `start.sh`
- Add `start.sh` and `stop.sh` scripts for venv-based server management
- Add comprehensive database documentation for all tables
- Add Frontend Developer Guide with API examples

### Fixed
- Fix Object Fields API trailing slash issues
- Fix Relationship Records API service errors

## [2026-01-24]

### Added
- Initial project setup with FastAPI + PostgreSQL + SQLAlchemy (async)
- Custom JWT authentication system with bcrypt password hashing
- Complete CRUD operations for Fields, Objects, Records, Relationships
- JSONB-based dynamic data storage pattern
- Row Level Security (RLS) policies for multi-tenancy
- Alembic migrations for database schema management

### Documentation
- Add comprehensive API specification (`docs/api/SPECIFICATION.md`)
- Add database visual schema (`docs/database/VISUAL_SCHEMA.md`)
- Add architecture overview and analysis documents
- Add Claude Code rules for code style, API design, testing, security, database
