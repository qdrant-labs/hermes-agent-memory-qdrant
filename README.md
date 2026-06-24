# hermes-agent-memory-qdrant

Qdrant-backed memory plugin for [Hermes Agent](https://hermes-agent.nousresearch.com/). Stores facts and conversation turns as hybrid vectors (dense + BM25 sparse), recalls them with semantic search, and extracts durable facts at session boundaries. Local by default.

## Installation

1. Copy or symlink the plugin into Hermes's user plugin directory:

```sh
ln -s /path/to/hermes-agent-memory-qdrant ~/.hermes/plugins/qdrant
```

2. Install dependencies into the Hermes venv:

```sh
~/.hermes/bin/uv pip install --python ~/.hermes/hermes-agent/venv/bin/python3 \
  "qdrant-client>=1.18.0" "fastembed>=0.8.0" "pyyaml>=6.0.3"
```

3. Activate the plugin in `~/.hermes/config.yaml`:

```yaml
memory:
  provider: qdrant
```

Start a new Hermes session. The embedding model downloads on first use.

## Tools

| Tool              | Description                                                |
| ----------------- | ---------------------------------------------------------- |
| `qdrant_remember` | Store a durable fact                                       |
| `qdrant_recall`   | Semantic search over stored facts                          |
| `qdrant_read`     | Fetch one memory by ID with full content and provenance    |
| `qdrant_forget`   | Preview candidates by description, then delete by exact ID |

## Configuration

Settings go under `plugins.qdrant` in `~/.hermes/config.yaml`. Defaults:

```yaml
plugins:
  qdrant:
    connection:
      mode: local                  # "local" (embedded) or "remote" (Qdrant server)
      path: null                   # local: storage path (default: ~/.hermes/qdrant)
      url: null                    # remote: e.g. http://localhost:6333
      api_key_env: null            # remote: env var holding the API key

    embedding:
      provider: fastembed
      model: BAAI/bge-small-en-v1.5
      sparse_model: Qdrant/bm25

    retrieval:
      mode: vector                 # "vector" or "hybrid"
      top_k: 10

    extraction:
      enabled: true
      min_turns: 3                 # skip extraction for very short sessions
```

**Switching to a remote Qdrant server:**

```yaml
plugins:
  qdrant:
    connection:
      mode: remote
      url: http://localhost:6333
```

Run a local server with Docker: `docker run -p 6333:6333 qdrant/qdrant`

> **Note:** changing the embedding model against an existing collection requires deleting `~/.hermes/qdrant/` to start fresh.

## Hooks

- `on_session_end`: extract facts from a completed session
- `on_pre_compress`: extract facts before context compression discards old messages
- `on_memory_write`: mirror built-in memory tool writes into Qdrant
- `on_session_switch`: update session scope on `/resume`, `/branch`, `/reset`
