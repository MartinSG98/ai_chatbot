# Broodmother API

Broodmother is a multi-agent chatbot API. You send it a message and an orchestrator decides which of six specialised agents should answer it: Nova searches the web, Wolf looks things up on Wikipedia, Sage does the maths, Pixel generates and describes images, Scribe writes and manages documents and Onyx writes code files. Every message and reply is stored in DynamoDB, so a client can list past sessions and reload a conversation. You can also upload PDF, DOCX and TXT files, which are chunked, embedded and stored in a Chroma vector store for semantic search.

This repo holds the FastAPI service, the router and all six agents. The chat frontend lives in a separate private repo, `ai_chatbot_ui`. The API ran on AWS behind API Gateway, an Application Load Balancer and ECS Fargate. That hosted API is switched off, so the way to try it is to run it locally.

The router is a LangGraph graph and each agent is a LangChain agent built with `create_agent`. The router and all six agents run on OpenAI's gpt-4.1-mini. Search comes from Tavily and Wikipedia, calculations from NumExpr and images from Pollinations.ai.

## How a message is handled

1. **The request comes in.** `POST /chat` takes a message and, optionally, a session ID and a user ID. A missing session ID gets a new UUID and a missing user ID becomes `anonymous`. The user's message is written to DynamoDB before anything else happens.
2. **Broodmother picks an agent.** If the session already has an agent and the message reads like a follow-up ("delete it", "show me", "that file", "thanks" and a few more phrases), it goes straight back to that agent. Otherwise gpt-4.1-mini at temperature 0 is asked to name one of the six. An answer that is not a valid agent name falls back to Nova.
3. **The agent answers.** Each agent has its own system prompt, personality, temperature and tools, and keeps its own history for each session. It streams its reply from the model, which shows up word by word in the server console, and hands back the complete text.
4. **The reply goes back.** The reply is saved to DynamoDB with the agent's name and returned with `agent_used` and the `session_id`, so the client can keep the conversation going.

The agents' working memory and the last agent used in each session live in the process. A restart starts every conversation fresh, even though the transcript is still in DynamoDB.

```
                      Client (ai_chatbot_ui, curl, /docs)
                                     │
                                     ▼
                     API Gateway  →  ALB  →  ECS Fargate
                                     │
                                     ▼
                         FastAPI (src/main.py) ──────► DynamoDB chat history
                                     │
                                     ▼
                     Broodmother router (LangGraph)
                                     │
      ┌──────────┬──────────┬────────┴─┬───────────┬───────────┐
      ▼          ▼          ▼          ▼           ▼           ▼
    Nova       Wolf       Sage       Pixel       Scribe      Onyx
   Tavily    Wikipedia   NumExpr  Pollinations  outputs/   outputs/
                                  + vision                 code/
```

## Agents

| Agent | What it handles | Tools | Temperature |
|---|---|---|---|
| Nova | Web search, news, current events, anything time-sensitive | Tavily search, top 3 results | 0.7 |
| Wolf | Facts, history, definitions, research | Wikipedia, top 2 articles, up to 3,000 characters | 0.5 |
| Sage | Maths, percentages, equations | A NumExpr calculator that reads `^` as a power | 0.1 |
| Pixel | Generating and describing images | A Pollinations.ai image URL built from the prompt, and gpt-4.1-mini vision for an image URL you share | 0.7 |
| Scribe | Notes, reports, letters and other documents | Create, read, list and delete files in `outputs/<user_id>/` | 0.7 |
| Onyx | Code in any language | Create, read, list and delete files in `outputs/<user_id>/code/` | 0.2 |

Scribe and Onyx get the user ID in front of each message, so their file tools stay inside that user's folder. Onyx writes code but never runs it.

## Documents

An upload is saved as `documents/<user_id>_<filename>`, loaded with the PDF, DOCX or plain text loader, and split into chunks of 1,000 characters with 200 characters of overlap. The chunks are embedded with OpenAI embeddings and stored in a Chroma collection in `chroma_db/`, tagged with the user ID. A search embeds the query and returns the closest chunks for that user only. Deleting a user's documents removes their chunks from the store, and the uploaded files stay on disk.

Document search is its own endpoint. The chat agents do not query the vector store.

## Running locally

Requires Python 3.11 or newer, an OpenAI API key, a Tavily API key and AWS credentials that can read and write the DynamoDB table.

```bash
python -m venv venv
venv\Scripts\activate         # Windows
source venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
aws configure --profile broodmother
cd src
uvicorn main:app --reload
```

The API starts on http://127.0.0.1:8000. Check it is alive at http://127.0.0.1:8000/health and browse the interactive API reference at http://127.0.0.1:8000/docs. Start uvicorn from inside `src/`, because the `documents/`, `chroma_db/` and `outputs/` folders are created relative to the working folder on first run.

Locally the chat history uses the AWS profile `broodmother` in `eu-west-2`, and the table `broodmother_chat_history` has to exist there. Its partition key is `session_id` and its sort key is `timestamp`, both strings. `/chat` saves the message before it answers, so without the table every chat request fails with a 500.

To chat without the API or AWS, run `python router.py` from `src/`. It starts a terminal chat with the whole colony and only needs the two API keys. Each agent file runs on its own the same way (`python nova_agent.py`, for example), where `clear` resets its memory. `outputs/broodmother_in_action_example.txt` is a terminal session that goes through all six agents.

## Configuration

The keys are read from the environment, or from a `.env` file in `src/` or the repo root. `.env.example` lists both keys. Write the names in capitals as below, because environment variable names are case-sensitive outside Windows.

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | none | The router, all six agents, Pixel's image analysis and the document embeddings |
| `TAVILY_API_KEY` | none | Nova's web search |
| `AWS_ACCESS_KEY_ID` | unset | When set, DynamoDB uses credentials from the environment instead of the `broodmother` profile. This is how the container signs in |
| `AWS_SECRET_ACCESS_KEY` | unset | The secret that goes with the key ID |

The region (`eu-west-2`) and the table name are fixed in `src/database.py`.

## API

| Method | Path | What it does |
|---|---|---|
| POST | `/chat` | Send `{"message": "...", "session_id": "...", "user_id": "..."}` (both IDs optional), get `response`, `agent_used` and `session_id` back |
| GET | `/agents` | The six agents and what each one does |
| GET | `/health` | Liveness check |
| GET | `/sessions` | Every session ID in the chat history table |
| GET | `/history/{session_id}` | A session's messages, oldest first, with role, content, timestamp and the agent that answered |
| DELETE | `/history/{session_id}` | Delete a session's messages and return how many were deleted |
| POST | `/documents/upload` | Upload a PDF, DOCX or TXT as the multipart field `file`, with `?user_id=` (`default` if left out) |
| GET | `/documents/search` | The closest chunks to `?query=` for `?user_id=`, `?k=` of them (3 by default), each with its source file |
| DELETE | `/documents/{user_id}` | Delete a user's chunks from the vector store |

There is no authentication, and CORS allows every origin. Any other file type on upload returns 400. An error inside `/chat` or while indexing an upload returns 500 with the exception's message.

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 25% of 200?"}'

curl -X POST "http://127.0.0.1:8000/documents/upload?user_id=default" \
  -F "file=@document.pdf"

curl "http://127.0.0.1:8000/documents/search?query=refund%20policy&user_id=default"
```

## Deployment

The Dockerfile starts from `python:3.11-slim`, installs `requirements.txt`, copies `src/` into `/app` and runs uvicorn on port 8000.

```bash
docker build -t broodmother-api .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e TAVILY_API_KEY=your-key \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  broodmother-api
```

On AWS the image was pushed to ECR and ran as an ECS Fargate service. An Application Load Balancer and its target group sent traffic to the running task and gave the service a fixed DNS name, and API Gateway put an HTTPS endpoint in front of the load balancer. Chat history lived in the DynamoDB table `broodmother_chat_history` in `eu-west-2`, reached through an IAM user's keys passed to the container. The AWS resources are not defined in this repo. The uploaded documents, the Chroma store and the agents' files sit on the container's own disk, so they do not survive a new task.

## Structure

```
src/
├── main.py           FastAPI app, CORS and every endpoint
├── router.py         Broodmother: the LangGraph graph that picks an agent, plus a terminal chat
├── nova_agent.py     web search through Tavily
├── wolf_agent.py     Wikipedia lookups
├── sage_agent.py     the NumExpr calculator
├── pixel_agent.py    image generation (Pollinations.ai) and image analysis
├── scribe_agent.py   documents in outputs/<user_id>/
├── onyx_agent.py     code files in outputs/<user_id>/code/
├── database.py       DynamoDB chat history: save, read, delete
└── rag_service.py    document loading, chunking, embeddings and Chroma search
outputs/
└── broodmother_in_action_example.txt   a terminal session with all six agents
Dockerfile            python:3.11-slim image running uvicorn on port 8000
requirements.txt      pinned dependencies
.env.example          the two API keys
```
