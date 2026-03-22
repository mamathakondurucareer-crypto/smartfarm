# Security Fixes Implemented

**Date:** March 22, 2026
**Status:** COMPLETED
**Severity:** 3 Critical/High Issues Fixed

---

## Summary

This document details the critical security fixes that have been implemented to remediate vulnerabilities identified in the security audit.

---

## Fix #1: Authorization - Missing Ownership Validation in Leave Request Submission

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/financial.py`
**Lines:** 318-323
**Severity:** HIGH
**Status:** ✅ FIXED

### Problem
The `POST /api/financial/leave-requests` endpoint allowed any authenticated employee to submit leave requests for any other employee, without verifying ownership.

### Solution Implemented
Added ownership validation:
- Regular employees can only submit leave for themselves
- HR/Managers can submit leave for any employee
- Added check for overlapping leave requests to prevent duplicates
- Added activity logging for leave request submissions

### Code Changes
```python
# Before: No validation
lr = LeaveRequest(**data.model_dump())

# After: Proper authorization
if current_user.role.name not in HR_ROLES:
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee or data.employee_id != employee.id:
        raise HTTPException(403, "You can only submit leave requests for yourself...")
```

### Testing
The fix ensures that:
- POST request with different employee_id returns 403 Forbidden
- Leave requests from HR/managers for other employees still work
- Activity logging tracks who submitted what leave request

---

## Fix #2: Authorization - Arbitrary Value Injection in Leave Request Approval

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/financial.py`
**Lines:** 326-336
**Severity:** HIGH
**Status:** ✅ FIXED

### Problem
The `PUT /api/financial/leave-requests/{lr_id}/approve` endpoint accepted an `approved_by` parameter directly from the client, allowing HR staff to approve leave "as if" it was approved by someone else.

### Solution Implemented
Removed the `approved_by` parameter from the request:
- The approver is always set to `current_user.id`
- Client cannot specify who approved the request
- Only HR role can approve leave requests
- Added validation that only "pending" requests can be approved
- Added activity logging for leave approvals

### Code Changes
```python
# Before: Arbitrary value from client
def approve_leave(lr_id: int, approved_by: int, ...):
    lr.approved_by = approved_by  # ← Vulnerability

# After: Uses current_user.id only
def approve_leave(lr_id: int, ...):
    lr.approved_by = current_user.id  # ← Fixed
```

### Testing
The fix ensures that:
- PUT request no longer accepts `approved_by` parameter
- `approved_by` field in database always matches the HR user who approved it
- Cannot approve already-approved or rejected requests

---

## Fix #3: Authorization - Added Leave Request Rejection Endpoint

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/financial.py`
**Lines:** 360+
**Severity:** HIGH
**Status:** ✅ FIXED

### Problem
There was no way to reject a leave request, only approve it.

### Solution Implemented
Added new `/leave-requests/{lr_id}/reject` endpoint:
- Only HR can reject leave requests
- Supports optional rejection reason
- Sets `approved_by` to current HR user
- Validates that only "pending" requests can be rejected
- Added activity logging

### Code Changes
```python
@router.put("/leave-requests/{lr_id}/reject")
def reject_leave(lr_id: int, reason: Optional[str] = None, ...):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    lr.status = "rejected"
    lr.approved_by = current_user.id
    if reason:
        lr.rejection_reason = reason
    db.commit()
```

### Model Changes
Updated LeaveRequest model to add `rejection_reason` field:
```python
rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
```

### Testing
The fix ensures that:
- Employees cannot call reject endpoint (403)
- Only pending requests can be rejected
- Rejection reason is properly stored in database

---

## Fix #4: Rate Limiting - AI Analysis Endpoint Cost Exhaustion Protection

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/ai_analysis.py`
**Lines:** 79-169
**Severity:** MEDIUM
**Status:** ✅ FIXED

### Problem
The `/api/ai/analyze` endpoint had no rate limiting, allowing attackers to exhaustively call the Anthropic API and incur significant costs.

### Solution Implemented
Added per-user rate limiting:
- 10 requests per minute per user
- Requests tracked in-memory with timestamps
- Old timestamps automatically cleaned up
- Returns 429 Too Many Requests when limit exceeded
- Includes logging for rate limit violations

### Code Changes
```python
# New rate limiting implementation
_ai_request_timestamps = defaultdict(list)

def _check_ai_rate_limit(user_id: int) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - _RATE_LIMIT_WINDOW

    # Clean old timestamps
    _ai_request_timestamps[user_id] = [
        ts for ts in _ai_request_timestamps[user_id]
        if ts > window_start
    ]

    # Check limit
    if len(_ai_request_timestamps[user_id]) >= _RATE_LIMIT_REQUESTS:
        raise HTTPException(429, f"Too many AI requests. Max {_RATE_LIMIT_REQUESTS} per minute.")

    _ai_request_timestamps[user_id].append(now)

# Called in analyze() endpoint
_check_ai_rate_limit(current_user.id)
```

### Testing
The fix ensures that:
- First 10 requests per minute succeed
- 11th request returns 429 Forbidden
- Each user has independent rate limit counter
- Limit resets after 1 minute of inactivity

---

## Fix #5: Error Handling - Better Logging in AI Analysis

**File:** `/Users/usangaraju/Downloads/smartfarm/backend/routers/ai_analysis.py`
**Lines:** 180-199
**Severity:** MEDIUM
**Status:** ✅ FIXED

### Problem
The endpoint had overly broad exception handling with no logging:
```python
except Exception:
    raise HTTPException(500, "AI analysis failed")
```

This masked the actual error and prevented debugging.

### Solution Implemented
Added specific exception handling with detailed logging:
- Logs timeout errors separately
- Logs connection errors separately
- Logs HTTP errors separately
- All unexpected errors logged with full traceback
- Each error includes user_id for audit trail

### Code Changes
```python
try:
    # ... AI API call ...
except httpx.TimeoutException as e:
    logger.error(f"AI API timeout. User: {current_user.id}. Error: {str(e)}")
    raise HTTPException(504, "AI service is taking too long...")
except httpx.ConnectError as e:
    logger.error(f"AI API connection failed. User: {current_user.id}. Error: {str(e)}")
    raise HTTPException(503, "Could not reach AI service...")
except httpx.HTTPStatusError as e:
    logger.error(f"AI API error. User: {current_user.id}. Status: {e.response.status_code}")
    raise HTTPException(502, "AI service returned an error...")
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Unexpected error. User: {current_user.id}. Error: {str(e)}", exc_info=True)
    raise HTTPException(500, "An unexpected error occurred")
```

### Testing
The fix ensures that:
- All errors are properly logged
- Timeout errors return 504
- Connection errors return 503
- Unexpected errors return 500 with full traceback in logs

---

## Fix #6: Input Validation - QA Trace Endpoint Parameter

**File:** `/Users/usangaraju/Downloads/smartfarm/mobile/src/services/api.js`
**Lines:** 318
**Severity:** MEDIUM
**Status:** ✅ FIXED

### Problem
The `trace()` function allowed arbitrary `lotCode` values to be interpolated into the URL without validation, potentially allowing path traversal or URL injection.

### Solution Implemented
Added input validation before URL construction:
- Only alphanumeric characters, hyphens, underscores, and dots allowed
- Uses `encodeURIComponent()` for safe URL encoding
- Throws clear error message for invalid inputs

### Code Changes
```javascript
// Before: No validation
trace: (lotCode, token) => request("GET", `/api/qa/lots/trace/${lotCode}`, null, token),

// After: With validation
trace: (lotCode, token) => {
    if (!/^[a-zA-Z0-9_\-\.]+$/.test(lotCode)) {
        throw new Error("Invalid lot code format. Only alphanumeric...");
    }
    return request("GET", `/api/qa/lots/trace/${encodeURIComponent(lotCode)}`, null, token);
}
```

### Testing
The fix ensures that:
- Valid codes like "LOT-2026-001" succeed
- Invalid codes with special characters are rejected
- URL encoding prevents injection attacks

---

## Summary of Changes

| Issue | File | Severity | Status | Tests |
|-------|------|----------|--------|-------|
| Leave ownership validation | financial.py | HIGH | ✅ | Verified |
| Leave approval arbitrary value | financial.py | HIGH | ✅ | Verified |
| Leave rejection endpoint | financial.py | HIGH | ✅ | Verified |
| AI rate limiting | ai_analysis.py | MEDIUM | ✅ | Verified |
| AI error handling | ai_analysis.py | MEDIUM | ✅ | Verified |
| QA trace input validation | api.js | MEDIUM | ✅ | Verified |

---

## Deployment Notes

1. **Database Migration Required**
   - The `rejection_reason` field was added to `LeaveRequest` model
   - Run Alembic migrations before deploying:
     ```bash
     alembic upgrade head
     ```

2. **API Breaking Changes**
   - The `approved_by` parameter is no longer accepted in `PUT /api/financial/leave-requests/{lr_id}/approve`
   - The new `PUT /api/financial/leave-requests/{lr_id}/reject` endpoint is available

3. **Rate Limiting**
   - AI analysis is now limited to 10 requests per minute per user
   - This is enforced in-memory (not persistent across app restarts)
   - Consider moving to Redis-based rate limiting for production

4. **Logging**
   - All security-relevant operations are now logged with user context
   - Check application logs for any rate limit violations or API errors

---

## NOT YET FIXED - Still Outstanding

⚠️ The following critical issue identified in the audit has NOT been fixed yet:

**CRITICAL: Production Credentials Exposed in .env.prod**
- File: `/Users/usangaraju/Downloads/smartfarm/.env.prod`
- Action Required: This file must be removed from git history and credentials rotated
- See SECURITY_REMEDIATION_PLAN.md for detailed instructions

---

## Verification Commands

To verify the fixes are working:

```bash
# 1. Run unit tests
pytest tests/test_financial.py::test_leave_requests -v
pytest tests/test_ai.py::test_ai_rate_limiting -v

# 2. Check database migration
python -c "from backend.models.user import LeaveRequest; print('rejection_reason' in LeaveRequest.__table__.columns)"

# 3. Verify git changes
git diff --stat

# 4. Test endpoints manually
curl -X POST http://localhost:8000/api/financial/leave-requests \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 1, "start_date": "2026-04-01", "end_date": "2026-04-05"}'
```

---

**End of Security Fixes Implementation Report**
