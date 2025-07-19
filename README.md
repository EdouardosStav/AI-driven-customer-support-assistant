# AI-Driven Customer Support Assistant

An AI-powered backend service that uses Mistral LLM via Ollama to answer customer queries based on a predefined knowledge base. Built with FastAPI, SQLAlchemy, and SQLite.

## 🚀 Features

- **AI-Powered Responses**: Uses Mistral LLM through Ollama for intelligent answers
- **Knowledge Base Integration**: Loads and parses local FAQ documents
- **RESTful API**: Clean API endpoints with automatic OpenAPI/Swagger documentation
- **Persistent Storage**: Stores all queries and responses in SQLite database
- **Comprehensive Logging**: Structured logging with rotation and JSON formatting
- **Docker Support**: Fully containerized with Docker and docker-compose
- **Production Ready**: Error handling, request tracing, and health checks

## 📋 Requirements

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- Ollama (for running Mistral LLM locally)

## 🛠️ Installation

### Option 1: Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-customer-support-assistant.git
cd ai-customer-support-assistant
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

This will:
- Start Ollama container
- Automatically pull the Mistral model
- Start the FastAPI application
- Create the SQLite database

The API will be available at `http://localhost:8000`

### Option 2: Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-customer-support-assistant.git
cd ai-customer-support-assistant
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install and start Ollama:
```bash
# Follow instructions at https://ollama.com
ollama serve
```

5. Pull Mistral model:
```bash
ollama pull mistral
```

6. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

7. Run the application:
```bash
python -m uvicorn app.main:app --reload
```

## 📚 API Documentation

Once the application is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### API Endpoints

#### POST /api/v1/ask
Submit a question to get an AI-generated answer.

**Request:**
```json
{
  "question": "What is your refund policy?"
}
```

**Response:**
```json
{
  "answer": "Our refund policy allows customers to return products within 30 days...",
  "question_id": 123,
  "timestamp": "2024-01-20T10:30:00Z"
}
```

#### GET /api/v1/history?n=10
Retrieve the last N questions and answers.

**Response:**
```json
{
  "entries": [
    {
      "id": 123,
      "question": "What is your refund policy?",
      "answer": "Our refund policy...",
      "timestamp": "2024-01-20T10:30:00Z"
    }
  ],
  "count": 1,
  "total": 150
}
```

## 📁 Project Structure

```
ai-customer-support-assistant/
├── app/
│   ├── api/            # API routes and dependencies
│   ├── core/           # Core utilities (logging, exceptions)
│   ├── db/             # Database configuration
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── utils/          # Helper functions
│   ├── config.py       # Application configuration
│   └── main.py         # FastAPI application entry point
├── data/
│   └── knowledge_base.md  # FAQ knowledge base
├── logs/               # Application logs
├── tests/              # Test files
├── docker/             # Docker-related files
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🧠 Knowledge Base Format

The knowledge base should be a markdown or text file with Q&A pairs:

```markdown
Q: What is the refund policy?
A: Our refund policy allows customers to return products within 30 days of purchase with a valid receipt.

Q: How can I contact support?
A: You can reach us via email at support@example.com or call us at 1-800-SUPPORT.

Q: What are your business hours?
A: We are open Monday through Friday, 9 AM to 5 PM EST.
```

## 🔧 Configuration

Key configuration options in `.env`:

- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model to use (default: mistral)
- `DATABASE_URL`: SQLite database path
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `API_PREFIX`: API route prefix (default: /api/v1)

## 🧪 Testing

Run tests with pytest:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

## 🤖 AI Coding Assistant Usage

This project was developed with assistance from Claude (Anthropic). The AI assistant helped with:
- Initial project structure and boilerplate code generation
- Implementation of modular architecture patterns
- Docker configuration and containerization setup
- Comprehensive error handling and logging implementation
- API endpoint design and OpenAPI documentation
- Prompt engineering strategies for the Mistral integration

## 📈 Future Enhancements

- [ ] Implement similarity search for better context retrieval
- [ ] Add authentication and rate limiting
- [ ] Support multiple knowledge bases
- [ ] Implement caching for frequently asked questions
- [ ] Add metrics and monitoring (Prometheus/Grafana)
- [ ] Support for multiple LLM models
- [ ] Web UI for chat interface
- [ ] Admin panel for knowledge base management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Ollama](https://ollama.com/) for making LLMs accessible locally
- [Mistral AI](https://mistral.ai/) for the powerful language model
- [SQLAlchemy](https://www.sqlalchemy.org/) for the robust ORM