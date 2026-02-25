# API Examples - Cheque Tally Agent

All examples assume the API is running on `http://localhost:8000`
Replace `{access_token}` with your actual JWT token from login response

## Health Check

```bash
# Check API health
curl http://localhost:8000/health

# Check readiness (database connection)
curl http://localhost:8000/health/ready
```

## Authentication Endpoints

### Register New User

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Response:

```json
{
  "id": "uuid-here",
  "email": "user@example.com"
}
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Response:

```json
{
  "user_id": "uuid-here",
  "email": "user@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

## Session Management

### Create New Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions/create \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "February 2026 Monthly Reconciliation"
  }'
```

Response:

```json
{
  "id": "session-uuid",
  "user_id": "user-uuid",
  "session_name": "February 2026 Monthly Reconciliation",
  "created_at": "2026-02-24T16:20:48.421Z"
}
```

### List All Sessions

```bash
curl -X GET http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer {access_token}"
```

### Get Session Details

```bash
curl -X GET http://localhost:8000/api/v1/sessions/{session_id} \
  -H "Authorization: Bearer {access_token}"
```

Response:

```json
{
  "id": "session-uuid",
  "user_id": "user-uuid",
  "session_name": "February 2026 Monthly Reconciliation",
  "created_at": "2026-02-24T16:20:48.421Z",
  "company_expenses": [...],
  "bank_transactions": [...]
}
```

## Data Upload

### Upload Company Expenses

```bash
# From file
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/upload-company-expenses \
  -H "Authorization: Bearer {access_token}" \
  -F "file=@company_cheques.txt"

# Response includes extracted cheques and notes
```

Sample Company Expenses File Format:

```
Cheque #001
Payee: ABC Corp
Amount: 50000
Date: 2026-02-01

Cheque #002
Payee: XYZ Ltd
Amount: 25500.50
Date: 2026-02-05
```

### Upload Bank Transactions

```bash
# From file
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/upload-bank-transactions \
  -H "Authorization: Bearer {access_token}" \
  -F "file=@bank_transactions.txt"
```

Sample Bank Transactions File Format:

```
Cleared: #001
Amount: 50000
Date: 2026-02-02

Cleared: #002
Amount: 25500.50
Date: 2026-02-04
```

## Reconciliation

### Run Tally (Reconciliation)

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/run-tally \
  -H "Authorization: Bearer {access_token}"
```

Response:

```json
{
  "session_id": "session-uuid",
  "total_cashed_cheques": 2,
  "total_uncashed_cheques": 0,
  "total_cashed_amount": 75500.5,
  "total_uncashed_amount": 0.0,
  "cashed_cheques": [
    {
      "company_cheque_number": "001",
      "bank_cheque_number": "001",
      "payee_name": "ABC Corp",
      "amount": 50000.0,
      "issue_date": "2026-02-01",
      "clearing_date": "2026-02-02"
    },
    {
      "company_cheque_number": "002",
      "bank_cheque_number": "002",
      "payee_name": "XYZ Ltd",
      "amount": 25500.5,
      "issue_date": "2026-02-05",
      "clearing_date": "2026-02-04"
    }
  ],
  "uncashed_cheques": [],
  "created_at": "2026-02-24T16:20:48.421Z"
}
```

### Get Tally Report

```bash
curl -X GET http://localhost:8000/api/v1/sessions/{session_id}/tally-report \
  -H "Authorization: Bearer {access_token}"
```

## Error Handling Examples

### 401 - Unauthorized (Missing Token)

```bash
curl http://localhost:8000/api/v1/sessions
```

Response:

```json
{
  "detail": "Not authenticated"
}
```

### 404 - Session Not Found

```bash
curl -X GET http://localhost:8000/api/v1/sessions/invalid-session-id \
  -H "Authorization: Bearer {access_token}"
```

Response:

```json
{
  "status": "error",
  "detail": "Session not found",
  "timestamp": "2026-02-24T16:20:48.421Z"
}
```

### 400 - Bad Request (Missing Data)

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{session_id}/run-tally \
  -H "Authorization: Bearer {access_token}"
# If session doesn't have both company expenses and bank transactions
```

Response:

```json
{
  "status": "error",
  "detail": "Session must have both company expenses and bank transactions before running tally",
  "timestamp": "2026-02-24T16:20:48.421Z"
}
```

## Using httpie (Alternative to curl)

```bash
# Install: pip install httpie

# Login
http POST localhost:8000/auth/login \
  email=user@example.com \
  password=password123

# Create session
http POST localhost:8000/api/v1/sessions/create \
  "Authorization: Bearer {token}" \
  session_name="My Session"

# Upload file
http -f POST localhost:8000/api/v1/sessions/{session_id}/upload-company-expenses \
  "Authorization: Bearer {token}" \
  file@company_cheques.txt

# Run tally
http POST localhost:8000/api/v1/sessions/{session_id}/run-tally \
  "Authorization: Bearer {token}"

# Get report
http localhost:8000/api/v1/sessions/{session_id}/tally-report \
  "Authorization: Bearer {token}"
```

## Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create session
response = requests.post(
    f"{BASE_URL}/api/v1/sessions/create",
    headers=headers,
    json={"session_name": "My Session"}
)
session_id = response.json()["id"]

# Upload company expenses
with open("company_cheques.txt", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/upload-company-expenses",
        headers=headers,
        files={"file": f}
    )

# Upload bank transactions
with open("bank_transactions.txt", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions/{session_id}/upload-bank-transactions",
        headers=headers,
        files={"file": f}
    )

# Run tally
response = requests.post(
    f"{BASE_URL}/api/v1/sessions/{session_id}/run-tally",
    headers=headers
)
tally = response.json()

print(f"Cashed: {tally['total_cashed_cheques']}")
print(f"Pending: {tally['total_uncashed_cheques']}")
print(f"Total Cashed: PKR {tally['total_cashed_amount']}")
```

## WebSocket (Future Enhancement)

```javascript
// Real-time reconciliation updates (planned)
const ws = new WebSocket(
  "ws://localhost:8000/ws/reconciliation/{session_id}?token={access_token}",
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Update:", data);
};
```
