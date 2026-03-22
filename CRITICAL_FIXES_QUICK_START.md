# Critical Security Fixes - Quick Start Guide

## EMERGENCY FIX #1: Remove .env.prod from Git History (30 minutes)

### Step 1: Install BFG Repo-Cleaner
```bash
brew install bfg  # macOS
# OR
apt-get install bfg-repo  # Linux
# OR download from https://rtyley.github.io/bfg-repo-cleaner/
```

### Step 2: Create backup of current directory
```bash
cd /Users/usangaraju/Downloads
cp -r smartfarm smartfarm.backup
```

### Step 3: Clean the repository
```bash
cd smartfarm
git reflog expire --expire=now --all
bfg --delete-files .env.prod
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all  # DANGER: Force push to clean history
```

### Step 4: Verify removal
```bash
git log --all --full-history -- .env.prod  # Should show nothing
git show HEAD:.env.prod  # Should fail with "not found"
```

### Step 5: Rotate ALL production credentials IMMEDIATELY
```bash
# Database
ALTER USER smartfarm WITH PASSWORD 'NEW_RANDOM_PASSWORD_HERE';

# Generate new SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate new admin password
# Force password reset on first login for admin user
```

---

## EMERGENCY FIX #2: Remove Anthropic API Key from Frontend (15 minutes)

### Step 1: Delete CLAUDE_API_KEY from config
**File:** `mobile/src/config/apiConfig.js`

```javascript
// REMOVE THIS LINE:
// export const CLAUDE_API_KEY = "";

// Keep only:
export const API_BASE =
  process.env.EXPO_PUBLIC_API_URL || "http://localhost:8002";
```

### Step 2: Update AIScreen.jsx to use backend proxy
**File:** `mobile/src/screens/AIScreen.jsx`

```javascript
// Line 19 - REMOVE:
// import { CLAUDE_API_KEY } from "../config/apiConfig";

// Replace sendMessage function (around line 88):
const sendMessage = useCallback(async (text) => {
  const trimmed = text.trim();
  if (!trimmed || isLoading) return;

  const userMsg = { role: "user", text: trimmed, time: new Date().toLocaleTimeString() };
  const updated = [...messages, userMsg];
  setMessages(updated);
  setInputText("");
  setIsLoading(true);

  try {
    const token = useAuthStore((s) => s.token);  // Get JWT token
    if (!token) throw new Error("Not authenticated");

    // Call BACKEND proxy instead of Anthropic directly
    const response = await api.ai.analyze({
      query: trimmed,
      context_modules: ["aquaculture", "financial", "operations", "inventory"]
    }, token);

    const aiMsg = { role: "assistant", text: response.response, time: new Date().toLocaleTimeString() };
    const withReply = [...updated, aiMsg];
    setMessages(withReply);
    saveConversations(withReply);
  } catch (err) {
    console.error("AI analysis failed", err);
    const errMsg = { role: "error", text: err.message, time: new Date().toLocaleTimeString() };
    setMessages([...updated, errMsg]);
  } finally {
    setIsLoading(false);
  }
}, [isLoading, messages, saveConversations]);
```

### Step 3: Add API endpoint to frontend api.js
**File:** `mobile/src/services/api.js`

```javascript
// Add to api object:
ai: {
  analyze: (data, token) => request("POST", "/api/ai/analyze", data, token),
},
```

### Step 4: Verify backend endpoint exists
```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Farm health check","context_modules":["aquaculture"]}'
```

---

## CRITICAL FIX #3: Encrypt Frontend Token Storage (2 hours)

### Step 1: Install encrypted storage library
```bash
cd mobile
npm install react-native-encrypted-storage
# For Expo, also run:
npx expo prebuild --clean  # Rebuild native modules
```

### Step 2: Replace AsyncStorage with EncryptedStorage
**File:** `mobile/src/store/useAuthStore.js`

```javascript
// REPLACE at top:
// import AsyncStorage from "@react-native-async-storage/async-storage";

import EncryptedStorage from 'react-native-encrypted-storage';
import { Platform } from 'react-native';

const AUTH_KEY = "smartfarm-auth-v1";

const useAuthStore = create((set, get) => ({
  token:     null,
  user:      null,
  authReady: false,

  // ─── Hydrate from storage on app launch ───────────────────────
  loadAuth: async () => {
    setUnauthorizedHandler(() => {
      // Use EncryptedStorage instead
      EncryptedStorage.removeItem(AUTH_KEY);
      set({ token: null, user: null });
    });

    try {
      const raw = await EncryptedStorage.getItem(AUTH_KEY);
      if (raw) {
        const { token, user } = JSON.parse(raw);
        if (!user.role && user.role_name) user.role = user.role_name;
        if (user.role) user.role = user.role.toUpperCase();

        try {
          await api.me(token);
          set({ token, user, authReady: true });
        } catch {
          await EncryptedStorage.removeItem(AUTH_KEY);
          set({ authReady: true });
        }
      } else {
        set({ authReady: true });
      }
    } catch {
      set({ authReady: true });
    }
  },

  // ─── Login ────────────────────────────────────────────────────
  login: async (username, password) => {
    const tokenData = await api.login(username, password);
    const user      = await api.me(tokenData.access_token);
    user.role = (tokenData.role || "").toUpperCase();
    const payload = { token: tokenData.access_token, user };
    // Use EncryptedStorage
    await EncryptedStorage.setItem(AUTH_KEY, JSON.stringify(payload));
    set(payload);
  },

  // ─── Logout ───────────────────────────────────────────────────
  logout: async () => {
    // Securely wipe encrypted storage
    await EncryptedStorage.removeItem(AUTH_KEY);
    set({ token: null, user: null });
  },

  // ─── Role helpers ─────────────────────────────────────────────
  hasRole: (...roles) => {
    const { user } = get();
    return !!user && roles.includes(user.role);
  },
}));

export default useAuthStore;
```

### Step 3: Test encrypted storage
```bash
npm test  # Run existing tests to ensure token flow works
```

---

## CRITICAL FIX #4: Add Authorization Checks (3-5 days)

### Step 1: Create authorization helper
**File:** `backend/utils/auth_helpers.py`

```python
from fastapi import HTTPException
from backend.models.user import User

def require_owner_or_admin(resource_user_id: int, current_user: User, admin_roles: list = None):
    """Check if user is owner of resource or has admin role."""
    if admin_roles is None:
        admin_roles = ["admin", "manager"]

    is_owner = resource_user_id == current_user.id
    is_admin = current_user.role.name in admin_roles

    if not (is_owner or is_admin):
        raise HTTPException(403, "Not authorized to access this resource")

def require_admin(current_user: User, allowed_roles: list = None):
    """Check if user has admin role."""
    if allowed_roles is None:
        allowed_roles = ["admin"]

    if current_user.role.name not in allowed_roles:
        raise HTTPException(403, f"Requires one of: {', '.join(allowed_roles)}")
```

### Step 2: Add checks to service_requests router
**File:** `backend/routers/service_requests.py`

```python
from backend.utils.auth_helpers import require_owner_or_admin, require_admin

@router.get("/{request_id}", response_model=ServiceRequestOut)
def get_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Service request not found")

    # ADD THIS CHECK:
    require_owner_or_admin(req.requested_by, current_user,
                          admin_roles=["admin", "manager", "store_manager"])

    return req
```

### Step 3: Audit other routers
Run this script to find all vulnerable patterns:

```bash
grep -rn "db.query.*filter.*\.id.*==" backend/routers/*.py | \
grep -v "current_user.id\|user_id.*!=" | \
head -20
```

For each result, add authorization check.

### Step 4: Write tests
**File:** `tests/test_idor_protection.py`

```python
def test_user_cannot_access_others_service_request(client, auth_token_user1, auth_token_user2, db):
    """User1 should not access User2's service request."""
    # User1 creates a request
    req_response = client.post(
        "/api/service-requests",
        json={"title": "My Request", ...},
        headers={"Authorization": f"Bearer {auth_token_user1}"}
    )
    req_id = req_response.json()["id"]

    # User2 tries to access it
    response = client.get(
        f"/api/service-requests/{req_id}",
        headers={"Authorization": f"Bearer {auth_token_user2}"}
    )

    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]
```

---

## CRITICAL FIX #5: Implement Persistent Rate Limiting (2 hours)

### Step 1: Install Redis
```bash
# macOS
brew install redis
brew services start redis

# Docker (recommended for production)
docker run -d -p 6379:6379 redis:7-alpine
```

### Step 2: Add Redis to requirements.txt
```bash
pip install redis==5.0.0
```

### Step 3: Create cache service
**File:** `backend/services/cache_service.py`

```python
import os
import redis
from datetime import datetime, timezone

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def check_login_rate_limit(identifier: str, max_attempts: int = 3, window_seconds: int = 1800):
    """Check if login attempts exceeded. Raises HTTPException if locked."""
    from fastapi import HTTPException

    key = f"login_attempt:{identifier}"
    attempts = redis_client.incr(key)

    if attempts == 1:
        redis_client.expire(key, window_seconds)

    if attempts > max_attempts:
        ttl = redis_client.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {ttl}s.",
            headers={"Retry-After": str(ttl)}
        )

def get_client_ip(request) -> str:
    """Get real client IP from request, accounting for proxies."""
    if "x-forwarded-for" in request.headers:
        # Return rightmost IP (actual client)
        return request.headers["x-forwarded-for"].split(",")[-1].strip()
    return request.client.host if request.client else "unknown"
```

### Step 4: Update auth router
**File:** `backend/routers/auth.py`

```python
from backend.services.cache_service import check_login_rate_limit, get_client_ip

# REMOVE old in-memory code:
# _failed: dict[str, list[float]] = defaultdict(list)
# _check_lockout, _record_failure, _clear_failures functions

@router.post("/login", response_model=TokenPair)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)
    identifier = f"{form.username}:{client_ip}"

    # Check rate limit (raises 429 if exceeded)
    check_login_rate_limit(identifier, max_attempts=3, window_seconds=1800)

    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        # Log failure for security audit
        log_activity(db, "LOGIN_FAILURE", "auth", username=form.username,
                     description=f"Failed login attempt from {client_ip}")
        raise HTTPException(401, "Invalid credentials")

    if not user.is_active:
        raise HTTPException(403, "Account disabled")

    # Clear rate limit on successful login
    redis_client.delete(f"login_attempt:{identifier}")

    # ... rest of login code ...
```

---

## Testing Your Fixes

```bash
# 1. Test token encryption
cd mobile && npm test

# 2. Test authorization
cd tests && pytest test_idor_protection.py -v

# 3. Test rate limiting
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=wrong" \
  # Repeat 3 times, 4th should fail with 429

# 4. Test AI endpoint works
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Farm health","context_modules":["aquaculture"]}'

# 5. Verify .env.prod removed from Git
git log --all --full-history -- .env.prod  # Should be empty
```

---

## Deployment Checklist

- [ ] .env.prod removed from Git history
- [ ] All production credentials rotated
- [ ] Pre-commit hook installed
- [ ] Client-side API key removed
- [ ] Frontend token encryption implemented
- [ ] Authorization checks added to all endpoints
- [ ] Rate limiting using Redis implemented
- [ ] All tests passing
- [ ] Manual testing completed
- [ ] Security team review
- [ ] Ready for deployment

---

## Timeline Estimate

| Fix | Effort | Timeline |
|-----|--------|----------|
| Remove .env.prod from Git | 30 min | Day 1 |
| Remove client API key | 15 min | Day 1 |
| Encrypt frontend tokens | 2 hours | Day 2-3 |
| Add authorization checks | 3-5 days | Days 4-8 |
| Implement rate limiting | 2 hours | Day 3 |
| **Total** | **~18 hours active work** | **8 business days** |

---

## Questions?

Refer to the full security audit report:
`/Users/usangaraju/Downloads/smartfarm/SECURITY_AUDIT_REPORT.md`
