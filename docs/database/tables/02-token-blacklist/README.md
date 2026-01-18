# token_blacklist Table

## Genel Bakış

**Amaç:** JWT token revocation (logout functionality)

**Tip:** Security Table
**Primary Key:** jti (JWT Token ID)
**Pattern:** Add token on logout, check on every request
**Cleanup:** Delete expired tokens daily

---

## Tablo Özellikleri

| Özellik | Değer |
|---------|-------|
| **Primary Key** | jti (VARCHAR) |
| **Foreign Keys** | None (performance) |
| **Referenced By** | None |
| **Cascade Deletes** | None |
| **Indexes** | 3 indexes (jti, user_id, expires_at) |
| **Row Estimate** | Variable (grows with usage) |

---

## Kolonlar

### jti (varchar) - Primary Key
- **Açıklama:** JWT Token ID (unique identifier)
- **Örnek:** baae b20f-fa3a-4829-9aef-df2b4da7094c

### user_id (uuid)
- **Nullable:** NO
- **References:** users.id (not enforced)
- **Açıklama:** Token owner

### expires_at (timestamptz)
- **Nullable:** NO
- **Açıklama:** Token expiration time
- **Index:** YES (for cleanup)

### blacklisted_at (timestamptz)
- **Nullable:** NO
- **Açıklama:** When token was revoked
- **Default:** NOW()

---

## Workflow

### 1. Logout (Add to Blacklist)

```python
# Extract jti from token
payload = jwt.decode(token, SECRET_KEY)
jti = payload["jti"]
exp = payload["exp"]

# Add to blacklist
blacklist_entry = TokenBlacklist(
    jti=jti,
    user_id=user_id,
    expires_at=datetime.fromtimestamp(exp, UTC),
    blacklisted_at=datetime.now(UTC)
)
await db.add(blacklist_entry)
await db.commit()
```

### 2. Token Validation (Check Blacklist)

```python
# On every protected endpoint
is_blacklisted = await db.scalar(
    select(exists().where(TokenBlacklist.jti == jti))
)

if is_blacklisted:
    raise HTTPException(401, "Token has been revoked")
```

### 3. Cleanup (Delete Expired)

```python
# Run daily cron job
await db.execute(
    delete(TokenBlacklist)
    .where(TokenBlacklist.expires_at < datetime.now(UTC))
)
await db.commit()
```

---

## Index'ler

### 1. token_blacklist_pkey (UNIQUE)
**Purpose:** Primary key lookup
**Query:** WHERE jti = ?

### 2. ix_token_blacklist_user_id
**Purpose:** Find all revoked tokens for user
**Query:** WHERE user_id = ?

### 3. ix_token_blacklist_expires_at
**Purpose:** Cleanup expired tokens
**Query:** WHERE expires_at < NOW()
**Criticality:** ⚠️ CRITICAL (for cleanup job)

---

**Last Updated:** 2026-01-18
**Status:** ✅ Production Ready
**Pattern:** Add on logout, check on request, cleanup expired
