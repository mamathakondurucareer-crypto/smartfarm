# CRITICAL SECURITY ISSUE - ACTION REQUIRED

**Issue:** Production Credentials Exposed in Git Repository
**Severity:** CRITICAL
**Status:** ⚠️ NOT YET FIXED - REQUIRES IMMEDIATE ACTION
**Timeline:** URGENT - Within 24 hours

---

## Overview

The file `.env.prod` contains plaintext production database and API credentials that are committed to the Git repository. This is a CRITICAL vulnerability that compromises the security of the entire production environment.

---

## Exposed Credentials

**File:** `/Users/usangaraju/Downloads/smartfarm/.env.prod`

### Credentials at Risk:
```
Line 7:  POSTGRES_PASSWORD=SfPr0d2024!
Line 10: SECRET_KEY=be602bc33abd848b293029e7fbd44bfd11d82fb76c8970abdd814c819a200953
Line 17: ADMIN_PASSWORD=Admin@SmartFarm2024!
```

### Impact:
- **Database Access**: Anyone with the repo can connect to the PostgreSQL database
- **Session Hijacking**: The SECRET_KEY can be used to forge JWT tokens
- **Admin Takeover**: The ADMIN_PASSWORD allows admin account access
- **Deployment Compromise**: Can be used to deploy malicious code

---

## Root Cause

Although `.env.prod` is in `.gitignore`, the file was committed to the repository BEFORE the gitignore rule was added. This means it exists in git history permanently and can be recovered.

**Check git history:**
```bash
git log --all --oneline -- .env.prod
```

---

## Immediate Actions Required

### Step 1: Rotate All Production Credentials (IMMEDIATELY)

Generate new credentials:

```bash
# New PostgreSQL password (32 random characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# New SECRET_KEY (64 hex characters)
python3 -c "import secrets; print(secrets.token_hex(32))"

# New ADMIN_PASSWORD (strong password with complexity)
python3 -c "import secrets; print('Admin_' + secrets.token_urlsafe(16))"
```

**Update in production database immediately:**
1. Connect to PostgreSQL as admin
2. Change password: `ALTER ROLE smartfarm WITH PASSWORD 'NEW_PASSWORD';`
3. Update admin user password in users table
4. Change SECRET_KEY in environment (requires app restart)

### Step 2: Remove .env.prod from Git History

Choose ONE of these methods:

#### Option A: Using BFG Repo-Cleaner (Recommended - Faster)

```bash
# Install bfg (if not already installed)
brew install bfg  # macOS
apt-get install bfg  # Linux
# or download from: https://rtyley.github.io/bfg-repo-cleaner/

# Navigate to repo
cd /Users/usangaraju/Downloads/smartfarm

# Remove .env.prod from entire history
bfg --delete-files .env.prod

# Verify
git reflog expire --expire=now --all && git gc --prune=now --aggressive

# Force push to remote (WARNING: destructive operation)
git push --force --all
```

#### Option B: Using git filter-branch (Slower but Built-in)

```bash
cd /Users/usangaraju/Downloads/smartfarm

# Remove .env.prod from all commits
git filter-branch --tree-filter 'rm -f .env.prod' -- --all

# Clean up refs
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: destructive operation)
git push --force --all
```

### Step 3: Verify .env.prod is Removed from History

```bash
# Should return nothing (no commits involving .env.prod)
git log --all --oneline -- .env.prod

# Should return nothing (.env.prod not in tracked files)
git ls-files | grep .env.prod
```

### Step 4: Verify .gitignore is Correct

```bash
# Should show .env.prod in gitignore
cat .gitignore | grep .env.prod
```

Current content should have:
```
.env
.env.prod
```

### Step 5: Update GitHub Secrets

1. Go to: GitHub Repo → Settings → Secrets and variables → Actions
2. Update these secrets with NEW values:
   - `POSTGRES_PASSWORD` - new secure password
   - `SECRET_KEY` - new secure key
   - `ADMIN_PASSWORD` - new secure password
   - `ANTHROPIC_API_KEY` - verify it's set (if using AI features)

3. Verify CI/CD pipeline uses secrets (not env files):
   - `.github/workflows/deploy.yml` should reference `${{ secrets.POSTGRES_PASSWORD }}`
   - No `.env.prod` file should be checked in

### Step 6: Verify Deployment Process

Ensure `.env.prod` is:
1. **Never committed** to git
2. **Never tracked** in .gitignore
3. **Only created** in CI/CD pipeline from GitHub Secrets
4. **Deleted** after deployment in CI/CD

**Check deploy.yml:**
```bash
grep -A 5 ".env.prod" .github/workflows/deploy.yml
# Should show it's created from secrets and deleted after deployment
```

---

## Credentials Cleanup Checklist

After following the steps above:

- [ ] New POSTGRES_PASSWORD generated and set in database
- [ ] New SECRET_KEY generated and set in environment
- [ ] New ADMIN_PASSWORD generated and set in database
- [ ] .env.prod removed from git history (verified with git log)
- [ ] GitHub Secrets updated with new values
- [ ] .env.prod no longer in git ls-files
- [ ] CI/CD pipeline tested and working
- [ ] Production environment restarted with new credentials
- [ ] All team members notified of credential rotation

---

## Verification After Fix

Run these commands to verify the fix is complete:

```bash
# 1. Confirm .env.prod removed from history
git log --all --oneline -- .env.prod  # Should be empty

# 2. Confirm .env.prod not in current files
git ls-files | grep .env.prod  # Should be empty

# 3. Confirm .gitignore has entry
grep "\.env\.prod" .gitignore  # Should show .env.prod

# 4. Confirm no credentials in code
grep -r "SfPr0d2024" .  # Should be empty
grep -r "Admin@SmartFarm2024" .  # Should be empty
grep -r "be602bc33abd848b" .  # Should be empty

# 5. Verify GitHub Secrets are set
gh secret list  # Should show POSTGRES_PASSWORD, SECRET_KEY, etc.
```

---

## Prevention for Future

1. **Use `.env.example`** for documentation
   - Already exists: `/Users/usangaraju/Downloads/smartfarm/.env.prod.example`
   - Shows structure without actual secrets
   - Can be safely committed

2. **Pre-commit Hook** to prevent accidental secrets commit
   ```bash
   # Install git hooks
   pip install detect-secrets
   detect-secrets scan > .secrets.baseline
   ```

3. **GitHub Secret Scanning** is already enabled
   - Will alert if secrets are committed

4. **CI/CD Best Practices**
   - Only GitHub Secrets for sensitive data
   - Never commit `.env.prod`
   - Rotate secrets quarterly

---

## Timeline and Responsibility

| Task | Owner | Deadline | Status |
|------|-------|----------|--------|
| Generate new credentials | DevOps/DBA | 2 hours | ⏳ Pending |
| Update production database | DBA | 3 hours | ⏳ Pending |
| Remove from git history | DevOps | 4 hours | ⏳ Pending |
| Update GitHub Secrets | DevOps | 4 hours | ⏳ Pending |
| Test CI/CD pipeline | DevOps | 5 hours | ⏳ Pending |
| Verify in production | QA | 6 hours | ⏳ Pending |
| Notify stakeholders | Project Manager | 6 hours | ⏳ Pending |

---

## Risk Assessment Until Fixed

**Current Risk Level: CRITICAL**

- **Exposure Window**: Production credentials visible in git history
- **Attack Vector**: Clone repo → read .env.prod → connect to database
- **Potential Impact**: Complete database compromise, application takeover
- **Detection Method**: Credentials could be scraped from git history by automated tools

**Risk Mitigation**:
- [ ] Repo is private (reduces exposure)
- [ ] Access logs monitored for suspicious activity
- [ ] Database access logs checked for unauthorized connections
- [ ] Incident response plan in place

---

## References

- [GitHub: Removing Sensitive Data from History](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## Support

If you encounter issues during remediation:

1. **Git History Damaged**: Contact Git support, may need to re-clone
2. **Deployment Fails**: Verify GitHub Secrets are set correctly
3. **Database Connection Lost**: Verify POSTGRES_PASSWORD is correct in environment

---

**CRITICAL - DO NOT SKIP**
This issue must be resolved before the next production deployment.
Failure to address this vulnerability puts the entire farm's data and operations at risk.

**Status:** ⚠️ AWAITING REMEDIATION
**Last Updated:** March 22, 2026
