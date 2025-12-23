# Broodmother API 🕷️

A multi-agent AI system powered by LangGraph, LangChain, and OpenAI. The system intelligently routes user queries to specialized AI agents, each with distinct capabilities and personalities.

## Architecture
```
                         User Request
                              │
                              ▼
                      ┌───────────────┐
                      │   FastAPI     │
                      │   Backend     │
                      └───────┬───────┘
                              │
                              ▼
                      ┌───────────────┐
                      │  Broodmother  │  ← LangGraph Router
                      │  (Classifier) │
                      └───────┬───────┘
                              │
        ┌─────────┬─────────┬─┴───┬─────────┬─────────┐
        ▼         ▼         ▼     ▼         ▼         ▼
     ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
     │ Nova │ │ Wolf │ │ Sage │ │Pixel │ │Scribe│ │ Onyx │
     └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
        │         │         │       │         │         │
        ▼         ▼         ▼       ▼         ▼         ▼
     Tavily   Wikipedia  NumExpr  GPT-4    Local     Local
     Search                      Vision    Files     Files
```

## Agents

| Agent | Specialty | Tools |
|-------|-----------|-------|
| **Nova** 🔍 | Web search, current events, news | Tavily Search |
| **Wolf** 📚 | Wikipedia, facts, history, research | Wikipedia API |
| **Sage** 🧮 | Math, calculations, equations | NumExpr Calculator |
| **Pixel** 🎨 | Image generation & analysis | Pollinations.ai, GPT-4 Vision |
| **Scribe** 📝 | Document creation & management | Local file system |
| **Onyx** ⚡ | Code generation & programming | Local file system |

## API Endpoints

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message to Broodmother |
| `GET` | `/agents` | List all available agents |
| `GET` | `/health` | Health check |

### Chat History (DynamoDB)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/history/{session_id}` | Get chat history for a session |
| `DELETE` | `/history/{session_id}` | Delete chat history for a session |

### Documents (RAG)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload a document (PDF, DOCX, TXT) |
| `GET` | `/documents/search` | Search your documents |
| `DELETE` | `/documents/{user_id}` | Delete all documents for a user |

## Tech Stack

- **Framework**: FastAPI
- **AI Orchestration**: LangGraph, LangChain
- **LLM**: OpenAI GPT-4.1-mini
- **Vector Database**: ChromaDB
- **Database**: AWS DynamoDB
- **Search**: Tavily API
- **Image Generation**: Pollinations.ai

## Project Structure
```
src/
├── main.py              # FastAPI application & endpoints
├── router.py            # Broodmother - LangGraph router
├── database.py          # DynamoDB integration
├── rag_service.py       # RAG service with ChromaDB
├── nova_agent.py        # Web search agent
├── wolf_agent.py        # Wikipedia agent
├── sage_agent.py        # Math agent
├── pixel_agent.py       # Image agent
├── scribe_agent.py      # Document agent
├── onyx_agent.py        # Code agent
├── documents/           # Uploaded documents (gitignored)
├── chroma_db/           # Vector database (gitignored)
└── outputs/             # User-generated files (gitignored)
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/MartinSG98/ai_chatbot.git
cd ai_chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the `src/` directory:
```
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
```

### 5. Configure AWS credentials
```bash
aws configure --profile broodmother
```
Enter your AWS Access Key ID, Secret Access Key, and region (eu-west-2).

### 6. Run the server
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0
```

### 7. Open API docs
Navigate to `http://127.0.0.1:8000/docs`

## AWS Resources

| Service | Resource | Purpose |
|---------|----------|---------|
| DynamoDB | `broodmother_chat_history` | Persistent chat history |
| IAM | `broodmother-user` | API access with DynamoDB permissions |

### DynamoDB Table Schema
- **Table name**: `broodmother_chat_history`
- **Partition key**: `session_id` (String)
- **Sort key**: `timestamp` (String)
- **Billing mode**: On-demand

## Usage Examples

### Send a chat message
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 25% of 200?"}'
```

### Upload a document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@document.pdf" \
  -F "user_id=default"
```

### Search documents
```bash
curl "http://localhost:8000/documents/search?query=refund%20policy&user_id=default"
```

## Features

- ✅ Multi-agent routing with context awareness
- ✅ Streaming responses
- ✅ Persistent chat history (DynamoDB)
- ✅ RAG document search (ChromaDB)
- ✅ User-specific file isolation
- ✅ Auto-generated API documentation

## Next Steps

- [ ] AWS deployment (ECS Fargate, API Gateway)
- [ ] S3 integration for document storage
- [ ] Cognito authentication
- [ ] React frontend

## License

MIT