# SmartFarm Security Remediation Plan

**Date:** March 22, 2026
**Status:** IN PROGRESS
**Priority:** CRITICAL - Multiple Authorization & Secrets Issues

---

## Executive Summary

The security audit identified **12 issues** across backend and mobile applications. This document provides a **step-by-step remediation plan** prioritized by severity and impact.

**Critical Issues Requiring Immediate Action:**
1. **Production credentials exposed in .env.prod** (CRITICAL)
2. **Arbitrary value injection in leave request approval** (HIGH)
3. **Missing ownership validation in leave submission** (HIGH)

---

## CRITICAL FIXES - DO FIRST

### Fix #1: Remove and Rotate Production Credentials

**Current Status:** ❌ NOT FIXED
**Impact:** High - Credentials can be read by anyone with repo access
**Timeline:** IMMEDIATE (within 2 hours)

#### Steps:

1. **Remove .env.prod from git history:**
```bash
cd /Users/usangaraju/Downloads/smartfarm

# Option A: Using git filter-branch (keep if you need older history)
git filter-branch --tree-filter 'rm -f .env.prod' -- --all

# Option B: Using bfg-repo-cleaner (faster, cleaner)
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
bfg --delete-files .env.prod

# Force push to remote
git push --force --all
```

2. **Rotate all secrets in production:**
   - [ ] Create NEW PostgreSQL password (generate random 32-char string)
   - [ ] Create NEW SECRET_KEY (generate random 64-char hex string)
   - [ ] Create NEW ADMIN_PASSWORD (12+ chars, complexity required)
   - [ ] Regenerate ANTHROPIC_API_KEY

3. **Update GitHub Secrets:**
   - [ ] Go to Settings → Secrets and variables → Actions
   - [ ] Update: `POSTGRES_PASSWORD`, `SECRET_KEY`, `ADMIN_PASSWORD`
   - [ ] Verify deploy workflow uses secrets (not env files)

4. **Verify .env.prod is NOT committed:**
```bash
git log --all --oneline -- .env.prod  # Should show no results
git ls-files | grep .env.prod         # Should show nothing
```

---

### Fix #2: Authorization - Arbitrary Value Injection in Leave Approval

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/financial.py`
**Lines:** 326-336
**Current Status:** ❌ NOT FIXED
**Severity:** HIGH
**Risk:** HR staff can approve leave for unauthorized approvers

#### Problem Code:
```python
@router.put("/leave-requests/{lr_id}/approve")
def approve_leave(lr_id: int, approved_by: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == lr_id).first()
    if not lr:
        raise HTTPException(404, "Leave request not found")
    lr.status = "approved"
    lr.approved_by = approved_by  # ← BUG: User can set any ID
    db.commit()
    return {"message": "Leave approved"}
```

#### Required Fix:

Replace lines 326-336 with:

```python
@router.put("/leave-requests/{lr_id}/approve")
def approve_leave(lr_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    """Approve a leave request. Only HR can approve. approved_by is always current_user."""
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == lr_id).first()
    if not lr:
        raise HTTPException(404, "Leave request not found")
    if lr.status != "pending":
        raise HTTPException(400, f"Cannot approve a {lr.status} leave request")
    lr.status = "approved"
    lr.approved_by = current_user.id  # ← FIX: Always use current_user.id
    lr.approved_at = datetime.utcnow()
    db.commit()
    log_activity(db, "LEAVE_APPROVED", "hr",
                 leave_request_id=lr.id, approver_id=current_user.id)
    return {"id": lr.id, "message": "Leave approved"}
```

#### Testing:
```python
# Test: HR tries to approve leave with arbitrary user ID
POST /api/financial/leave-requests/1/approve
Body: {}  # No approved_by parameter should be sent

# Should return:
{"id": 1, "message": "Leave approved"}

# Verify in database: approved_by == current_user.id, NOT an arbitrary value
```

---

### Fix #3: Authorization - Missing Ownership Check in Leave Submission

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/financial.py`
**Lines:** 318-323
**Current Status:** ❌ NOT FIXED
**Severity:** HIGH
**Risk:** Employees can submit leave requests for colleagues

#### Problem Code:
```python
@router.post("/leave-requests", status_code=201)
def submit_leave(data: LeaveRequestCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    lr = LeaveRequest(**data.model_dump())  # ← BUG: No ownership validation
    db.add(lr)
    db.commit()
    return {"id": lr.id, "status": "pending"}
```

#### Required Fix:

Replace lines 318-323 with:

```python
@router.post("/leave-requests", status_code=201)
def submit_leave(data: LeaveRequestCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    """Submit a leave request. Employees can only request leave for themselves."""

    # HR/Manager can request leave for other employees
    if current_user.role.name not in ("hr", "manager", "admin"):
        # Regular employees can only request leave for themselves
        employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not employee or data.employee_id != employee.id:
            raise HTTPException(403,
                "You can only submit leave requests for yourself. Contact HR for others.")

    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(404, "Employee not found")

    # Check for duplicate pending requests (same date range)
    existing = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == data.employee_id,
        LeaveRequest.status.in_(["pending", "approved"]),
        LeaveRequest.start_date <= data.end_date,
        LeaveRequest.end_date >= data.start_date
    ).first()
    if existing:
        raise HTTPException(409,
            f"Overlapping leave request already exists (ID: {existing.id})")

    lr = LeaveRequest(**data.model_dump())
    db.add(lr)
    db.commit()
    db.refresh(lr)

    log_activity(db, "LEAVE_REQUESTED", "hr",
                 leave_request_id=lr.id, employee_id=data.employee_id,
                 description=f"Leave from {data.start_date} to {data.end_date}")

    return {"id": lr.id, "status": "pending"}
```

#### Testing:
```python
# Test 1: Regular employee requests leave for themselves
POST /api/financial/leave-requests
Headers: Authorization: Bearer alice_token
Body: {
    "employee_id": 5,  # alice's employee ID
    "start_date": "2026-04-01",
    "end_date": "2026-04-05",
    "reason": "Vacation"
}
# Expected: 201 Created ✓

# Test 2: Regular employee tries to request leave for someone else
POST /api/financial/leave-requests
Headers: Authorization: Bearer alice_token
Body: {
    "employee_id": 6,  # bob's employee ID (not alice)
    "start_date": "2026-04-01",
    "end_date": "2026-04-05",
    "reason": "Vacation"
}
# Expected: 403 Forbidden ✗

# Test 3: HR requests leave for another employee
POST /api/financial/leave-requests
Headers: Authorization: Bearer hr_token
Body: {
    "employee_id": 6,  # can request for anyone
    "start_date": "2026-04-01",
    "end_date": "2026-04-05",
    "reason": "Vacation"
}
# Expected: 201 Created ✓
```

---

## HIGH PRIORITY FIXES - DO NEXT

### Fix #4: Reject Unapproved Leave Requests

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/financial.py`
**Lines:** ~326-336 (after Fix #2)
**Current Status:** ❌ NOT FIXED
**Severity:** HIGH
**Risk:** Employees can still be marked approved even if they haven't been evaluated

#### Required Fix:

Add rejection endpoint and validate state transitions:

```python
@router.put("/leave-requests/{lr_id}/reject")
def reject_leave(lr_id: int, reason: str = Query(None), db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    """Reject a pending leave request. Only HR can reject."""
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == lr_id).first()
    if not lr:
        raise HTTPException(404, "Leave request not found")
    if lr.status != "pending":
        raise HTTPException(400, f"Cannot reject a {lr.status} leave request")

    lr.status = "rejected"
    lr.approved_by = current_user.id
    lr.approved_at = datetime.utcnow()
    lr.rejection_reason = reason
    db.commit()

    log_activity(db, "LEAVE_REJECTED", "hr",
                 leave_request_id=lr.id, reason=reason)

    return {"id": lr.id, "message": "Leave request rejected"}
```

---

### Fix #5: Input Validation - QA Trace Parameter

**File:** `/Users/usangaraju/Downloads/smartfarm/mobile/src/services/api.js`
**Lines:** 318
**Current Status:** ❌ NOT FIXED
**Severity:** MEDIUM
**Risk:** Path traversal via lotCode parameter

#### Problem Code:
```javascript
trace: (lotCode, token) =>
    request("GET", `/api/qa/lots/trace/${lotCode}`, null, token)
```

#### Required Fix:

Add input validation:

```javascript
trace: (lotCode, token) => {
    // Validate lotCode is alphanumeric + hyphens/underscores only
    if (!/^[a-zA-Z0-9_-]+$/.test(lotCode)) {
        throw new Error("Invalid lot code format");
    }
    return request("GET", `/api/qa/lots/trace/${encodeURIComponent(lotCode)}`, null, token);
}
```

---

### Fix #6: Rate Limiting on AI Analysis Endpoint

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/ai_analysis.py`
**Lines:** 77-90
**Current Status:** ⚠️ PARTIAL (slowapi configured globally, but endpoint not decorated)
**Severity:** MEDIUM
**Risk:** Cost exhaustion attack, DOS via AI API calls

#### Required Fix:

```python
from slowapi import Limiter
from backend.main import limiter  # Import the limiter from main.py

@router.post("/analyze", response_model=AIQueryResponse)
@limiter.limit("10/minute")  # ← ADD THIS DECORATOR
def analyze(request: Request, data: AIQueryRequest, db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    # ... rest of endpoint
```

---

### Fix #7: Error Handling - Overly Broad Exception Catching

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/ai_analysis.py`
**Lines:** 121-124
**Current Status:** ❌ NOT FIXED
**Severity:** MEDIUM
**Risk:** Silent failures, difficult debugging

#### Problem Code:
```python
except Exception:
    return {"error": "Analysis failed"}
```

#### Required Fix:

```python
import logging
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=AIQueryResponse)
def analyze(request: Request, data: AIQueryRequest, db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    try:
        # ... AI analysis code ...
    except httpx.TimeoutException as e:
        logger.error(f"AI API timeout for user {current_user.id}: {str(e)}")
        raise HTTPException(504, "AI service timeout. Please try again.")
    except httpx.HTTPError as e:
        logger.error(f"AI API error for user {current_user.id}: {str(e)}")
        raise HTTPException(503, "AI service unavailable. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error in AI analysis for user {current_user.id}: {str(e)}")
        raise HTTPException(500, "An unexpected error occurred")
```

---

## MEDIUM PRIORITY FIXES

### Fix #8: Sensitive Data Exposure in Employee Endpoint

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/financial.py`
**Status:** ⚠️ NEEDS REVIEW
**Severity:** MEDIUM
**Risk:** Aadhar, PAN, bank details exposed without authorization

**Required Actions:**
- [ ] Add department/role based access control to employee endpoints
- [ ] Implement field-level authorization (only admins/HR see sensitive fields)
- [ ] Sanitize responses based on user role
- [ ] Document which roles can view which fields

---

### Fix #9: Activity Log - Unvalidated Search Parameter

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/activity_log.py`
**Status:** ⚠️ NEEDS VALIDATION
**Severity:** MEDIUM
**Risk:** Potential SQL injection (though SQLAlchemy protects)

**Required Actions:**
- [ ] Add enum validation for action filter
- [ ] Whitelist allowed action values
- [ ] Document allowed actions in API schema

---

### Fix #10: HTTPS Enforcement Dependency

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/middleware/security.py`
**Lines:** 17-19
**Status:** ⚠️ CONDITIONAL
**Severity:** MEDIUM
**Risk:** Requires reverse proxy to set x-forwarded-proto header

**Required Actions:**
- [ ] Document that deployment requires reverse proxy (nginx/cloudflare)
- [ ] Add deployment configuration examples
- [ ] Add logging for HTTP→HTTPS redirects
- [ ] Test with actual reverse proxy

---

## LOW PRIORITY FIXES

### Fix #11: User Enumeration via Login Endpoint

**Status:** ⚠️ DOCUMENTED
**Severity:** LOW
**Risk:** Attacker can discover valid usernames

**Mitigation:** Current error message "Invalid credentials" is uniform (good). No immediate fix needed.

---

### Fix #12: Missing CSRF Documentation

**Status:** ⚠️ DOCUMENTED
**Severity:** LOW
**Risk:** Developers may not understand CSRF exemption for API

**Mitigation:** Add comment in SecurityHeadersMiddleware explaining API exemption.

---

## Implementation Checklist

### Phase 1: CRITICAL (This Week)
- [ ] **Fix #1**: Remove .env.prod from git history & rotate secrets
- [ ] **Fix #2**: Fix arbitrary value injection in leave approval
- [ ] **Fix #3**: Add ownership validation in leave submission
- [ ] Create new git commits with fixes
- [ ] Run security tests to verify fixes
- [ ] Deploy to staging first
- [ ] Verify in production after deploy

### Phase 2: HIGH (Next 2 Weeks)
- [ ] **Fix #4**: Add leave rejection endpoint
- [ ] **Fix #5**: Add input validation to mobile API client
- [ ] **Fix #6**: Add rate limiting decorator to AI endpoint
- [ ] **Fix #7**: Improve error handling in AI endpoint

### Phase 3: MEDIUM (Next Month)
- [ ] **Fix #8**: Implement field-level access control for sensitive data
- [ ] **Fix #9**: Add enum validation for activity log search
- [ ] **Fix #10**: Document HTTPS enforcement requirements
- [ ] Run full security test suite

### Phase 4: LOW (Ongoing)
- [ ] **Fix #11**: Document user enumeration mitigations
- [ ] **Fix #12**: Add CSRF documentation

---

## Testing Strategy

### Unit Tests (Backend)
```python
# Test authorization fixes
def test_employee_cannot_request_leave_for_others():
    response = client.post("/api/financial/leave-requests",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"employee_id": OTHER_EMPLOYEE_ID, ...})
    assert response.status_code == 403

def test_hr_can_request_leave_for_others():
    response = client.post("/api/financial/leave-requests",
        headers={"Authorization": f"Bearer {hr_token}"},
        json={"employee_id": OTHER_EMPLOYEE_ID, ...})
    assert response.status_code == 201

def test_approved_by_uses_current_user():
    response = client.put(f"/api/financial/leave-requests/{lr_id}/approve",
        headers={"Authorization": f"Bearer {hr_token}"})
    leave_request = db.query(LeaveRequest).get(lr_id)
    assert leave_request.approved_by == CURRENT_USER_ID  # Not arbitrary value
```

### Integration Tests (Mobile)
```javascript
// Test invalid lot code rejected
test("should reject invalid lot code", () => {
    expect(() => api.trace("../../../etc/passwd", token))
        .toThrow("Invalid lot code format");
});

test("should accept valid lot code", () => {
    const result = api.trace("LOT-2026-001", token);
    expect(result).toBeTruthy();
});
```

---

## Verification Commands

```bash
# After implementing fixes, run:

# 1. Check .env.prod removed from history
git log --all --oneline -- .env.prod

# 2. Run unit tests
cd /Users/usangaraju/Downloads/smartfarm
pytest tests/test_auth.py -v
pytest tests/test_financial.py -v

# 3. Run security linter
npm audit fix
pip install bandit
bandit -r backend/ -ll

# 4. Check git diff for all changes
git diff --stat

# 5. Stage and commit with proper message
git add -A
git commit -m "Security: Fix authorization issues in leave requests and remove .env.prod"
```

---

## Post-Implementation

1. **Notify stakeholders** of security fixes
2. **Monitor logs** for any access attempts with invalid approver IDs
3. **Schedule quarterly security reviews**
4. **Update deployment procedures** to never commit .env.prod
5. **Train team** on secure coding practices

---

**End of Remediation Plan**
**Next Step:** Begin Phase 1 fixes (Fixes #1-3)
