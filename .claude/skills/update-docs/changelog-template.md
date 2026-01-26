# CHANGELOG.md Format Guidelines

Use [Keep a Changelog](https://keepachangelog.com/) format.

## Section Headers

```markdown
## [YYYY-MM-DD]

### Added
- New features

### Fixed
- Bug fixes

### Changed
- Breaking changes or modifications

### Removed
- Removed features

### Documentation
- Doc-only changes

### Security
- Security fixes
```

## Entry Format

Each entry should be:
- **Concise** - One line, max 80 characters
- **Actionable** - Start with a verb (Add, Fix, Update, Remove)
- **Traceable** - Include file reference when relevant

### Good Examples

```markdown
### Added
- Add JWT authentication middleware (`app/middleware/auth.py`)
- Add Field CRUD operations (`app/services/field_service.py`)

### Fixed
- Fix bcrypt version compatibility issue (pin to 4.1.3)
- Fix async session handling in record queries

### Changed
- Migrate from Pydantic v1 to v2 syntax across all schemas
- Update SQLAlchemy relationships to use string references

### Documentation
- Add API specification for Records endpoint (`docs/api/SPECIFICATION.md`)
- Update database schema documentation with new indexes
```

### Bad Examples

```markdown
# Too vague
- Fixed bug
- Updated code

# Too long
- Added a new authentication middleware that validates JWT tokens from Supabase and extracts user_id for use in protected endpoints

# Missing context
- Changed the function
```

## Commit Message Format

When committing documentation updates:

```
docs: Update CHANGELOG and API documentation

- Add entries for recent feature additions
- Update API specification for new endpoints
- Fix typos in README

Co-Authored-By: Claude <noreply@anthropic.com>
```
