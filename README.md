# AI-Driven Customer Support Assistant

An intelligent backend service that leverages the Mistral Large Language Model (LLM) via Ollama to provide automated customer support responses based on a predefined knowledge base. Built with FastAPI, SQLAlchemy, and SQLite for a production-ready, containerized solution.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture & Design Decisions](#architecture--design-decisions)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation & Setup](#installation--setup)
  - [Running from Scratch (Step-by-Step)](#running-from-scratch-step-by-step)
  - [Docker Deployment](#docker-deployment)
- [API Documentation](#api-documentation)
- [Knowledge Base](#knowledge-base)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [AI Tools Usage](#ai-tools-usage)
- [Future Enhancements](#future-enhancements)

## Overview

This project implements a prototype AI-driven customer support assistant as specified in the technical assessment. The system integrates Mistral LLM running locally via Ollama to answer customer queries using a predefined FAQ knowledge base. All interactions are persisted in a SQLite database for historical tracking and analysis.

The solution demonstrates modern backend development practices including:
- Clean, modular architecture with separation of concerns
- Comprehensive error handling and logging
- Container-based deployment
- Extensive test coverage
- Production-ready API design

## Features

### Core Features
- **AI-Powered Responses**: Integrates Mistral LLM via Ollama for intelligent, context-aware answers
- **Smart Context Retrieval**: Implements keyword-based context selection for relevant responses
- **Persistent Storage**: SQLite database stores all queries, responses, and timestamps
- **RESTful API**: Two endpoints as specified:
  - `POST /api/v1/ask` - Submit questions and receive AI-generated answers
  - `GET /api/v1/history` - Retrieve past Q&A interactions
- **Knowledge Base Integration**: Parses and loads FAQ content from local files (.md/.txt)
- **Containerized**: Full Docker support for consistent deployment

### Additional Features (Bonus)
- **Structured Logging**: JSON-formatted logs with rotation and request tracing
- **Error Handling**: Comprehensive exception handling with user-friendly error messages
- **Auto Documentation**: Swagger UI and ReDoc for API exploration
- **Test Coverage**: >70% test coverage with unit and integration tests
- **Request Tracking**: Unique request IDs for debugging and monitoring

## Architecture & Design Decisions

### Overall Architecture

The application follows a **layered architecture pattern** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                   │
│  • Routes (/ask, /history)                              │
│  • Request/Response validation (Pydantic)               │
│  • Exception handlers                                   │
├─────────────────────────────────────────────────────────┤
│                   Service Layer                         │
│  • LLM Integration (CustomerSupportLLM)                 │
│  • Knowledge Base Management                            │
│  • Business Logic & Prompt Engineering                  │
├─────────────────────────────────────────────────────────┤
│              Data Access Layer (Repository)             │
│  • QueryRepository (CRUD operations)                    │
│  • Database session management                          │
├─────────────────────────────────────────────────────────┤
│                 Database Layer (SQLite)                 │
│  • SQLAlchemy ORM                                      │
│  • Query logs persistence                               │
└─────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **FastAPI over Flask/Django**
   - **Reason**: Modern async framework with automatic API documentation, built-in validation, and excellent performance
   - **Benefits**: Type hints support, automatic OpenAPI schema generation, built-in OAuth2 support for future auth needs

2. **Repository Pattern Implementation**
   - **Reason**: Abstracts database operations from business logic
   - **Benefits**: Easier testing (can mock repositories), flexibility to change database, cleaner code organization

3. **Local LLM via Ollama**
   - **Reason**: Privacy-preserving (no data sent to external APIs), cost-effective, full control over the model
   - **Benefits**: No API rate limits, predictable costs, data sovereignty

4. **SQLite for Storage**
   - **Reason**: Perfect for prototypes and local development, zero configuration needed
   - **Benefits**: File-based storage, easy backup, simple migration path to PostgreSQL/MySQL

5. **Keyword-Based Context Retrieval**
   - **Reason**: Simple yet effective for FAQ-style knowledge bases
   - **Benefits**: Fast performance, no need for embedding models, easy to understand and debug

## Tech Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Web Framework** | FastAPI | High-performance, async support, automatic API docs |
| **ORM** | SQLAlchemy 2.0 | Industry standard, supports multiple databases |
| **Database** | SQLite | Lightweight, perfect for prototypes |
| **LLM Runtime** | Ollama | Run LLMs locally without external dependencies |
| **LLM Model** | Mistral | Balanced performance and quality for customer support |
| **Validation** | Pydantic | Type safety and automatic validation |
| **HTTP Client** | httpx | Modern async HTTP client for Ollama communication |
| **Logging** | Python logging + JSON formatter | Structured logs for production environments |
| **Testing** | pytest + httpx | Comprehensive testing framework |
| **Containerization** | Docker | Consistent deployment across environments |

## Requirements

### System Requirements
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB recommended for smooth LLM operations)
- **Storage**: 10GB free space for models and data
- **OS**: Linux, macOS, or Windows with WSL2

### Software Dependencies
- Ollama (for running Mistral LLM)
- Docker & Docker Compose (for containerized deployment)
- Git (for cloning the repository)

## Installation & Setup

### Running from Scratch (Step-by-Step)

#### Step 1: Install Ollama

Ollama is required to run the Mistral LLM locally.

**On macOS:**
```bash
brew install ollama
```

**On Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**On Windows:**
1. Download from [https://ollama.com/download/windows](https://ollama.com/download/windows)
2. Run the installer
3. Open PowerShell as Administrator

#### Step 2: Start Ollama Service

Start Ollama in a terminal:
```bash
ollama serve
```

Keep this terminal open - Ollama needs to be running for the application to work.

#### Step 3: Pull the Mistral Model

In a new terminal, download the Mistral model:
```bash
ollama pull mistral
```

This will download approximately 4GB. You can verify it's working:
```bash
ollama run mistral "Hello, test message"
```

#### Step 4: Clone the Repository

```bash
git clone https://github.com/yourusername/ai-customer-support-assistant.git
cd ai-customer-support-assistant
```

#### Step 5: Set Up Python Environment

Create a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

#### Step 6: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

#### Step 7: Configure Environment

Copy the example configuration:
```bash
cp .env.example .env
```

The default settings should work out of the box, but you can edit `.env` if needed:
```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TIMEOUT=30

# Database Configuration
DATABASE_URL=sqlite:///./customer_support.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/app.log
```

#### Step 8: Initialize the Database

The database will be created automatically on first run, but you can also initialize it manually:
```bash
python -c "from app.db.init_db import init_db; init_db()"
```

#### Step 9: Run the Application

Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Step 10: Verify Installation

1. **Check API is running**: Open http://localhost:8000
   - You should see: `{"name":"AI Customer Support Assistant","version":"0.1.0","status":"running"}`

2. **Check Swagger UI**: Open http://localhost:8000/docs
   - You should see the interactive API documentation

3. **Test the `/ask` endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is your refund policy?"}'
   ```

### Docker Deployment

#### Option 1: Using Docker with Host Ollama (Recommended)

This approach uses Ollama installed on your host machine:

1. **Ensure Ollama is running on your host**:
   ```bash
   ollama serve
   ollama pull mistral
   ```

2. **Build and run the container**:
   ```bash
   docker-compose up --build
   ```

   The application will connect to your host's Ollama instance.

#### Option 2: Fully Containerized Setup

To run everything in Docker including Ollama:

1. **Create a full Docker Compose file** (`docker-compose.full.yml`):
   ```yaml
   version: '3.8'

   services:
     ollama:
       image: ollama/ollama:latest
       container_name: ollama
       volumes:
         - ollama_data:/root/.ollama
       ports:
         - "11434:11434"
       command: serve
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:11434"]
         interval: 30s
         timeout: 10s
         retries: 3

     ollama-setup:
       image: ollama/ollama:latest
       depends_on:
         ollama:
           condition: service_healthy
       command: pull mistral
       network_mode: "service:ollama"

     app:
       build: .
       container_name: ai-customer-support
       depends_on:
         - ollama-setup
       ports:
         - "8000:8000"
       environment:
         - OLLAMA_HOST=http://ollama:11434
       volumes:
         - ./logs:/app/logs
         - ./data:/app/data
       networks:
         - app-network

   volumes:
     ollama_data:

   networks:
     app-network:
       driver: bridge
   ```

2. **Run the full stack**:
   ```bash
   docker-compose -f docker-compose.full.yml up --build
   ```

## API Documentation

### POST /api/v1/ask

Submit a question to receive an AI-generated answer.

**Request:**
```http
POST /api/v1/ask
Content-Type: application/json

{
  "question": "What is your refund policy?",
  "context_method": "keyword"  // optional: "all" or "keyword" (default)
}
```

**Response:**
```json
{
  "answer": "Our refund policy allows customers to return products within 30 days of purchase. The item must be in its original condition with all packaging intact. Once we receive the returned item, we will process your refund within 5-7 business days.",
  "question_id": 123,
  "timestamp": "2024-01-20T10:30:00Z",
  "processing_time": 1250
}
```

**Error Responses:**
- `400`: Invalid request (question too short/long)
- `422`: Validation error
- `503`: Ollama service unavailable
- `500`: Internal server error

### GET /api/v1/history

Retrieve past questions and answers.

**Request:**
```http
GET /api/v1/history?n=10&search=refund
```

**Query Parameters:**
- `n` (optional): Number of entries to return (1-100, default: 10)
- `search` (optional): Search term to filter questions (min 2 chars)

**Response:**
```json
{
  "entries": [
    {
      "id": 123,
      "question": "What is your refund policy?",
      "answer": "Our refund policy allows customers to return products...",
      "timestamp": "2024-01-20T10:30:00Z",
      "processing_time": 1250
    }
  ],
  "count": 1,
  "total": 150
}
```

## Knowledge Base

### Format

The knowledge base is stored in `data/knowledge_base.md` using a simple Q&A format:

```markdown
Q: What is the refund policy?
A: Our refund policy allows customers to return products within 30 days of purchase. The item must be in its original condition with all packaging intact.

Q: How can I contact support?
A: You can reach our support team through multiple channels:
- Email: support@example.com
- Phone: 1-800-SUPPORT (1-800-787-7678)
- Live Chat: Available on our website
```

### Adding New Q&A Pairs

1. Edit `data/knowledge_base.md`
2. Follow the Q: / A: format
3. Leave blank lines between Q&A pairs
4. Restart the application to reload

### Context Retrieval Methods

The system implements two context selection strategies:

1. **Keyword-based (default)**: 
   - Searches for Q&A pairs with matching keywords
   - Scores based on word overlap (questions weighted 2x)
   - Returns top 5 most relevant pairs

2. **All context**:
   - Includes entire knowledge base (limited to 5 pairs to prevent timeouts)
   - Useful for general queries

## Project Structure

```
ai-customer-support-assistant/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Settings and configuration
│   ├── api/
│   │   ├── dependencies.py      # Dependency injection
│   │   └── routes/
│   │       ├── ask.py           # /ask endpoint implementation
│   │       └── history.py       # /history endpoint implementation
│   ├── core/
│   │   ├── exceptions.py        # Custom exception classes
│   │   └── logging.py           # Logging configuration
│   ├── db/
│   │   ├── base.py              # SQLAlchemy base configuration
│   │   ├── session.py           # Database session management
│   │   ├── init_db.py           # Database initialization
│   │   └── repositories/
│   │       └── query_repository.py  # Data access layer
│   ├── models/
│   │   └── query_log.py         # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas (empty - using inline)
│   ├── services/
│   │   ├── llm_wrapper.py       # Ollama/Mistral integration
│   │   └── knowledge_base.py    # Knowledge base management
│   └── utils/
│       └── prompt_builder.py    # Prompt engineering utilities
├── data/
│   └── knowledge_base.md        # FAQ knowledge base
├── logs/                        # Application logs (created at runtime)
├── tests/
│   ├── conftest.py              # Test configuration and fixtures
│   ├── test_main.py             # Main app tests
│   ├── test_api/
│   │   ├── test_api_ask.py     # /ask endpoint tests
│   │   └── test_api_history.py # /history endpoint tests
│   ├── test_db/
│   │   └── test_repositories.py # Repository tests
│   └── test_services/
│       ├── test_knowledge_base.py  # Knowledge base tests
│       └── test_llm_wrapper.py     # LLM integration tests
├── .env.example                 # Example environment configuration
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project metadata and tool configuration
├── pytest.ini                   # Pytest configuration
├── Dockerfile                   # Docker build instructions
├── docker-compose.yml           # Docker Compose configuration
└── README.md                    # This file
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Run specific test files
pytest tests/test_api/test_api_ask.py

# Run with verbose output
pytest -v

# Run only unit tests (marked)
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Coverage

The project maintains >70% test coverage across:
- **Unit Tests**: Repository, services, utilities
- **Integration Tests**: API endpoints, database operations
- **Mocked LLM Tests**: Testing without requiring Ollama

### Test Structure

Tests are organized by component:
- `test_api/`: API endpoint tests
- `test_db/`: Database and repository tests  
- `test_services/`: Service layer tests
- `conftest.py`: Shared fixtures and test configuration

## AI Tools Usage

This project was developed with extensive AI assistance, demonstrating modern AI-augmented development practices.

### Claude (Anthropic) - Primary Development Partner

**Architecture and Design:**
- Engaged in detailed discussions about architectural patterns, ultimately choosing the repository pattern over simpler alternatives
- Debated FastAPI vs Flask, settling on FastAPI for its modern features
- Designed the modular structure with clear separation of concerns

**Implementation:**
- Generated 90% of the initial codebase including:
  - Complete FastAPI application with proper error handling
  - SQLAlchemy models and repository implementation
  - Ollama integration with retry logic and error handling
  - Knowledge base parser with keyword search
  - Comprehensive logging system with JSON formatting
- Iteratively refined code based on requirements and best practices

**Testing:**
- Created all test files with >70% coverage
- Designed test fixtures and mocking strategies
- Implemented both unit and integration tests

**Documentation:**
- Wrote this comprehensive README
- Created inline documentation and docstrings
- Generated API documentation examples

### ChatGPT (OpenAI) - Planning and Content

**Initial Planning:**
- Brainstormed project structure and technology choices
- Discussed pros/cons of different LLM integration approaches
- Helped design the prompt engineering strategy

**Knowledge Base Creation:**
- Generated the comprehensive FAQ content in `data/knowledge_base.md`
- Created realistic Q&A pairs covering various customer support scenarios
- Ensured consistent formatting and tone

**Docker Configuration:**
- Assisted with multi-stage Dockerfile optimization
- Helped design docker-compose configurations
- Suggested health checks and networking setup

### GitHub Copilot - Code Acceleration

**Development Speed:**
- Autocompleted repetitive code patterns
- Generated boilerplate for similar functions
- Helped with import statements and type hints

**Test Creation:**
- Accelerated test writing with pattern recognition
- Generated test fixtures and mock data
- Completed assertion statements

### AI-Driven Development Process

1. **Collaborative Design Phase**:
   - Started with requirements analysis using ChatGPT
   - Moved to Claude for detailed architecture discussions
   - Iterated on design decisions with AI feedback

2. **Implementation Strategy**:
   - Used AI to generate initial module structures
   - Refined each component through conversational programming
   - Let AI handle boilerplate while focusing on business logic

3. **Quality Assurance**:
   - AI-generated tests caught edge cases I hadn't considered
   - Used AI for code review and improvement suggestions
   - Leveraged AI for documentation consistency

4. **Learning and Improvement**:
   - Each AI interaction taught new patterns and best practices
   - AI suggested modern Python features (like Pydantic v2 compatibility)
   - Learned about production considerations through AI recommendations

## Future Enhancements

### Short-term Improvements
1. **Semantic Search**: Implement embedding-based similarity search
2. **Caching Layer**: Add Redis for frequently asked questions
3. **Rate Limiting**: Prevent API abuse
4. **Authentication**: Add API key authentication
5. **Metrics**: Add Prometheus metrics for monitoring

### Long-term Vision
1. **Multi-Model Support**: Switch between different LLMs
2. **Admin Dashboard**: Web UI for knowledge base management
3. **Analytics**: Track query patterns and response quality
4. **Feedback Loop**: Learn from user feedback
5. **Horizontal Scaling**: Support multiple Ollama instances

### Technical Debt
1. **Async LLM Calls**: Current implementation is synchronous
2. **Database Migrations**: Add Alembic for schema versioning
3. **Configuration Management**: Use Pydantic Settings more extensively
4. **API Versioning**: Implement proper versioning strategy
5. **Integration Tests**: Add end-to-end tests with real Ollama

## License

This project is licensed under the MIT License - see the LICENSE file for details.