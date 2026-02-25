# Cheque Tally Agent - Production-Grade Cheque Reconciliation System

A sophisticated FastAPI-based application that automates the reconciliation of company-issued cheques with bank-cleared cheques. It uses LLM (via Langchain and Groq) to extract structured data from raw text and provides a clean accounting reconciliation workflow.

## 🎯 Features

- **Automated Cheque Extraction**: Uses LLM to extract structured cheque data from raw text
- **Smart Reconciliation**: Compares company expenses with bank transactions to identify:
  - ✅ Cashed cheques
  - ⏳ Uncashed/Pending cheques
  - ❌ Amount mismatches
- **Production-Grade Security**:
  - JWT-based authentication
  - Role-protected endpoints
  - Security headers middleware
  - Request logging
- **RESTful API**: Complete API with Swagger documentation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **LLM Integration**: Langchain + Groq for intelligent data extraction

## 📋 Architecture

```
User → Create Session
    ↓
Upload Company Expenses (LLM-powered extraction)
    ↓
Upload Bank Transaction Data (LLM-powered extraction)
    ↓
Run Tally Reconciliation
    ↓
Store Cashed & Uncashed Cheques
    ↓
Return Final Report
```

## 🏗️ Project Structure

```
finance_agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main FastAPI application
│   ├── middleware.py           # Security middleware & CORS
│   ├── core/
│   │   └── config.py          # Application configuration
│   ├── db/
│   │   ├── base.py            # Database setup & session
│   │   └── models_import.py
│   ├── models/
│   │   ├── user.py            # User model
│   │   ├── session.py         # Session model
│   │   ├── company_expence.py # Company cheque model
│   │   ├── bank_transactions.py # Bank cheque model
│   │   └── tally_results.py   # Reconciliation results model
│   ├── routes/
│   │   ├── auth.py            # Authentication endpoints
│   │   └── session.py         # Session & reconciliation endpoints
│   ├── schemas/
│   │   ├── user.py            # User request/response schemas
│   │   ├── cheque.py          # Cheque schemas
│   │   ├── company_expence.py # Company expense schemas
│   │   ├── bank_transactions.py # Bank transaction schemas
│   │   └── session.py         # Session schemas
│   ├── services/
│   │   ├── llm.py             # LLM integration with Langchain
│   │   └── reconciliation.py  # Core reconciliation logic
│   └── utils/
│       ├── jwt_handler.py     # JWT token management
│       └── password_hashing.py # Password encryption
├── alembic/                    # Database migrations
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Groq API key (for LLM access)

### Installation

1. **Clone and Navigate**

```bash
cd finance_agent
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Environment**

Create or update `.env` file:

```env
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=43200
ALGORITHM=HS256
DEBUG=False
ENVIRONMENT=production
```

5. **Run the Application**

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Authentication Flow

1. **Register User**

```bash
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

2. **Login**

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Session Management

#### Create Session

```bash
POST /api/v1/sessions/create
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "session_name": "Monthly Reconciliation - February 2026"
}
```

#### List Sessions

```bash
GET /api/v1/sessions
Authorization: Bearer {access_token}
```

#### Get Session Details

```bash
GET /api/v1/sessions/{session_id}
Authorization: Bearer {access_token}
```

### Data Upload

#### Upload Company Expenses

```bash
POST /api/v1/sessions/{session_id}/upload-company-expenses
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: <company_expenses.txt>
```

**Expected Text Format:**

```
Cheque #001, Payee: ABC Corp, Amount: 10000, Date: 2026-02-01
Cheque #002, Payee: XYZ Ltd, Amount: 5500, Date: 2026-02-05
...
```

#### Upload Bank Transactions

```bash
POST /api/v1/sessions/{session_id}/upload-bank-transactions
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: <bank_statements.txt>
```

**Expected Text Format:**

```
Cleared: #001, Amount: 10000, Date: 2026-02-10
Cleared: #002, Amount: 5500, Date: 2026-02-08
...
```

### Reconciliation

#### Run Tally

```bash
POST /api/v1/sessions/{session_id}/run-tally
Authorization: Bearer {access_token}
```

Response:

```json
{
  "session_id": "uuid",
  "total_cashed_cheques": 2,
  "total_uncashed_cheques": 0,
  "total_cashed_amount": 15500.0,
  "total_uncashed_amount": 0.0,
  "cashed_cheques": [
    {
      "company_cheque_number": "001",
      "bank_cheque_number": "001",
      "payee_name": "ABC Corp",
      "amount": 10000.0,
      "issue_date": "2026-02-01",
      "clearing_date": "2026-02-10"
    }
  ],
  "uncashed_cheques": [],
  "created_at": "2026-02-24T16:20:48.421Z"
}
```

#### Get Tally Report

```bash
GET /api/v1/sessions/{session_id}/tally-report
Authorization: Bearer {access_token}
```

## 🔐 Security Features

- **JWT Authentication**: Stateless token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Security Headers**:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security
  - Content-Security-Policy
- **CORS Protection**: Configurable cross-origin policies
- **Request Logging**: All requests and responses logged
- **Rate Limiting Ready**: Middleware structure supports rate limiting

## 🤖 LLM Integration

The system uses **Langchain** with **Groq API** for intelligent data extraction:

### Company Cheque Extraction

- Extracts: Cheque Number, Payee Name, Amount, Issue Date
- Handles various date formats
- Validates amount

### Bank Transaction Extraction

- Extracts: Cheque Number, Amount, Clearing Date
- Filters for cleared cheques only
- Handles various date formats

### Input Configuration

```python
# In app/services/llm.py
extract_company_cheques(raw_text) → CompanyChequeExtractionResult
extract_bank_cheques(raw_text) → BankChequeExtractionResult
```

## 💾 Database Models

### User Model

- id (String, Primary Key)
- email (String, Unique)
- password_hash (String)
- created_at (DateTime)
- sessions (Relationship)

### Session Model

- id (String, Primary Key)
- user_id (Foreign Key → User)
- session_name (String)
- created_at (DateTime)
- company_expenses (Relationship)
- bank_transactions (Relationship)
- tally (Relationship)

### CompanyExpense Model

- id (Integer, Primary Key)
- session_id (Foreign Key → Session)
- cheque_number (String)
- payee_name (String)
- amount (Float)
- issue_date (String)
- raw_text (Text)
- created_at (DateTime)

### BankTransaction Model

- id (Integer, Primary Key)
- session_id (Foreign Key → Session)
- cheque_number (String)
- amount (Float)
- clearing_date (String)
- raw_text (Text)
- created_at (DateTime)

### TallyResult Model

- id (Integer, Primary Key)
- session_id (Foreign Key → Session, Unique)
- cashed (Text - JSON)
- pending (Text - JSON)
- unmatched (Text - JSON)
- total_cashed_amount (Float)
- total_pending_amount (Float)
- created_at (DateTime)

## 🔄 Reconciliation Logic

The reconciliation algorithm:

1. **Normalize Cheque Numbers**: Convert to uppercase for comparison
2. **Create Lookup Maps**: Build dictionaries for O(1) lookups
3. **Match Cheques**: Compare company cheques with bank transactions
4. **Verify Amounts**: Check if amounts match (allowing small rounding differences)
5. **Classify Results**:
   - **Cashed**: Matched in both with correct amount
   - **Uncashed**: In company records but not cleared
   - **Unmatched**: In bank records but no company record
6. **Calculate Statistics**: Days outstanding, totals, counts
7. **Store Results**: Persist to database for audit trail

## 🧪 Testing

### Run Tests (when tests are added)

```bash
pytest tests/ -v
```

### Manual API Testing

```bash
# Using HTTPie
http POST localhost:8000/auth/signup email=test@example.com password=testpass123

# Using curl
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

## 📊 Health Checks

- **Health**: `GET /health`
- **Readiness**: `GET /health/ready`

## ⚙️ Configuration

All configuration is in `app/core/config.py`:

```python
class Settings(BaseSettings):
    # API
    API_TITLE: str
    API_VERSION: str

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    # LLM
    GROQ_API_KEY: str
    LLM_MODEL: str

    # Application
    DEBUG: bool
    ENVIRONMENT: str
```

## 📈 Performance Considerations

- **Database Indexing**: Cheque numbers indexed for fast lookups
- **LLM Caching**: Consider caching LLM results for identical inputs
- **Batch Processing**: Can process multiple sessions in parallel
- **Database Transactions**: Atomic operations for data consistency

## 🐛 Troubleshooting

### Database Connection Error

```
Add SSL mode configuration to DATABASE_URL:
postgresql://user:pass@host/db?sslmode=require
```

### LLM API Rate Limit

```
The system includes max_retries=2
Consider implementing exponential backoff for production
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Use a different port
python -m uvicorn app.main:app --port 8001
```

## 📝 Logging

Logs are output to console with format:

```
2026-02-24 16:20:48,421 - app.main - INFO - Database tables created successfully
```

Configure in `app/main.py` logging setup.

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Systemd

```ini
[Unit]
Description=Cheque Tally Agent
After=network.target

[Service]
Type=notify
User=appuser
WorkingDirectory=/path/to/finance_agent
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📜 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📞 Support

For issues and questions:

- GitHub Issues
- Email: support@example.com
- Documentation: http://localhost:8000/docs

---

**Version**: 1.0.0  
**Last Updated**: February 24, 2026  
**Status**: Production Ready
