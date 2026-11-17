# Secrets and external configuration

Add these values in GitHub repository Settings → Secrets and variables → Actions. Never commit secret values or paste them into repository files, issues or screenshots. Deployment uploads runtime values from a temporary file and deletes it after use.

## Required for initial deployment

| GitHub Actions secret | Purpose | Where to obtain |
|---|---|---|
| CLOUDFLARE_API_TOKEN | Deploy Worker, apply D1 migrations and configure Queue consumer | Cloudflare Dashboard → My Profile → API Tokens |
| TELEGRAM_BOT_TOKEN | Telegram bot authentication | Create a bot with https://t.me/BotFather |
| TELEGRAM_WEBHOOK_SECRET | Authenticate Telegram webhook requests | Generate a random 32+ character value using A-Z, a-z, 0-9, underscore or hyphen |
| TAVILY_API_KEY | Main web search provider | https://app.tavily.com/ |

Generate a webhook secret with OpenSSL: openssl rand -hex 32.

## Cloudflare token permissions

Create a scoped API token for this repository. The workflow needs:
- Account → Workers Scripts: Edit
- Account → D1: Edit
- Account → Queues: Edit

If Cloudflare's current token UI requires an additional read scope, add only the minimum scope requested by the CLI/API error. Do not use the Global API Key.

Cloudflare account ID is already recorded in cloudflare.config.ts and the workflow: 1172c01120a2470aa12f81e5b4778556.

## Recommended

| Secret | Purpose | Notes |
|---|---|---|
| ALLOWED_TELEGRAM_USER_IDS | Restrict use to the owner's numeric Telegram ID | Comma-separated IDs. Initially optional so first deploy can occur; message /id, then add your ID and redeploy. Without IDs, only /id and /start bootstrap responses work. |
| TELEGRAM_ARCHIVE_CHAT_ID | Destination for result archives and website snapshot documents | Create a private channel, add bot as administrator with post permission, then obtain channel ID (usually starts with -100). |

## Optional search and AI providers

| Secret | Feature |
|---|---|
| EXA_API_KEY | Semantic research discovery |
| BRAVE_SEARCH_API_KEY | Backup web/news search |
| TINYFISH_API_KEY | TinyFish Search and Fetch; enables /read and Deep Search source enrichment |
| OPENROUTER_API_KEY | AI synthesis for Deep Search |
| OPENROUTER_MODEL | Legacy single model ID; still supported |
| OPENROUTER_MODELS | Optional comma- or semicolon-separated model IDs, tried in priority order |
| AI_ROUTER_CONFIG | Multi-provider JSON config containing AI provider/key/model routes; supports OpenAI-compatible, Anthropic Messages and Gemini Interactions |
| GITHUB_TOKEN_SEARCH | Optional authenticated GitHub Search API |

The workflow maps GITHUB_TOKEN_SEARCH to Worker secret GITHUB_TOKEN. It does not store a short-lived GitHub Actions job token in the deployed Worker.

### Configure the multi-provider AI Router

Add one GitHub Actions secret named `AI_ROUTER_CONFIG`. Its value must be a **single-line JSON object**. Do not commit it to Git or paste real keys into chat, issues or screenshots. Every entry under `providers` represents one API key. To register several keys from the same vendor, add separate entries with different `id` labels and the same `baseUrl`/model list.

Supported protocols:
- `openai-compatible`: OpenAI-style `/chat/completions` endpoint. Examples of documented base URLs: OpenAI `https://api.openai.com/v1`, Groq `https://api.groq.com/openai/v1`, DeepSeek `https://api.deepseek.com`, Mistral `https://api.mistral.ai/openai/v1`, Together AI `https://api.together.ai/v1`, OpenRouter `https://openrouter.ai/api/v1`.
- `anthropic-messages`: Anthropic Messages API. Default base URL: `https://api.anthropic.com`.
- `gemini-interactions`: Google Gemini Interactions API. Default base URL: `https://generativelanguage.googleapis.com/v1beta`.

Example structure (all keys and model IDs below are placeholders):

```json
{
  "strategy": "balanced",
  "maxAttempts": 12,
  "providers": [
    {
      "id": "groq-key-1",
      "protocol": "openai-compatible",
      "baseUrl": "https://api.groq.com/openai/v1",
      "apiKey": "REPLACE_WITH_GROQ_KEY_1",
      "priority": 50,
      "models": [
        {
          "id": "REPLACE_WITH_GROQ_MODEL_ID",
          "tasks": ["fast", "chat", "summary", "translation"],
          "priority": 50,
          "inputCostUsdPerMillion": 0,
          "outputCostUsdPerMillion": 0
        }
      ]
    },
    {
      "id": "groq-key-2",
      "protocol": "openai-compatible",
      "baseUrl": "https://api.groq.com/openai/v1",
      "apiKey": "REPLACE_WITH_GROQ_KEY_2",
      "models": ["REPLACE_WITH_GROQ_MODEL_ID"]
    },
    {
      "id": "anthropic-main",
      "protocol": "anthropic-messages",
      "apiKey": "REPLACE_WITH_ANTHROPIC_KEY",
      "models": [
        {
          "id": "REPLACE_WITH_CLAUDE_MODEL_ID",
          "tasks": ["reasoning", "coding", "research", "chat"],
          "priority": 80
        }
      ]
    },
    {
      "id": "gemini-main",
      "protocol": "gemini-interactions",
      "apiKey": "REPLACE_WITH_GEMINI_KEY",
      "models": [
        {
          "id": "REPLACE_WITH_GEMINI_MODEL_ID",
          "tasks": ["chat", "research", "summary", "creative", "translation"],
          "priority": 60
        }
      ]
    },
    {
      "id": "custom-openai-compatible",
      "protocol": "openai-compatible",
      "baseUrl": "https://YOUR_PROVIDER_HOST/v1",
      "apiKey": "REPLACE_WITH_CUSTOM_PROVIDER_KEY",
      "models": ["REPLACE_WITH_MODEL_ID"]
    }
  ]
}
```

Router settings:
- `strategy`: `balanced` (default), `priority` or `cheapest`.
- `maxAttempts`: maximum routes attempted per request, from 1 to 24.
- Provider fields: `id` (safe label only), `protocol`, `baseUrl` (OpenAI-compatible only), `apiKey`, optional `priority`, optional `timeoutMs` (5–90 seconds), and `models`.
- Each model can be a plain string or an object with `id`, optional `tasks`, `priority`, `inputCostUsdPerMillion`, `outputCostUsdPerMillion`, and `maxOutputTokens`.
- Task names: `chat`, `fast`, `reasoning`, `coding`, `creative`, `translation`, `research`, `summary`, `classification`. Omit `tasks` to make a model eligible for every task.
- `cheapest` is only meaningful when both input and output price fields are supplied. Those rates are estimates in USD per million tokens.
- Custom endpoints must be public HTTPS. If a vendor only has an unrelated proprietary API, use an OpenAI-compatible gateway or add a dedicated adapter first.

Behavior:
- `balanced` rotates the starting candidate route per Worker isolate. It is not a globally coordinated round-robin across every Cloudflare isolate.
- `priority` tries higher provider+model priority values first.
- Each route is attempted at most once in a request. A 429, 5xx, authentication failure, unavailable model, timeout or empty response moves to the next route, up to `maxAttempts`.
- This failover cannot guarantee that a provider will not bill a rejected/failed request. Check each vendor's billing and quota dashboard.
- The router does not yet maintain a durable cross-provider billing ledger. Usage token counts are returned when the API supplies them; estimated cost is included only when both price fields are configured.
- Existing `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` and `OPENROUTER_MODELS` remain supported as a legacy fallback.

After saving the secret, run Deploy Cloudflare Worker. Test `/ai-status`, then `/ai fast ...`, `/ai reasoning ...` and `/ask ...`. `/ai-status` lists configured labels/models but does not validate keys; a real /ai request is the upstream acceptance test.

## Not required

No R2 credentials, KV namespace ID, VPS SSH key or local computer credentials are required for this MVP.

## After adding secrets

1. Push to main or run the Deploy Cloudflare Worker workflow.
2. Inspect Actions logs.
3. When deploy succeeds, message the bot with /id.
4. Add the numeric ID to ALLOWED_TELEGRAM_USER_IDS and redeploy.
5. Optionally create a private archive channel and add TELEGRAM_ARCHIVE_CHAT_ID.
6. Add optional providers only when needed. For TinyFish, create a key at https://agent.tinyfish.ai/api-keys and add it as TINYFISH_API_KEY. For multi-model OpenRouter, set OPENROUTER_API_KEY and add OPENROUTER_MODELS, for example: provider-a/model-id, provider-b/model-id. Use model IDs shown in your OpenRouter model catalogue. Keep OPENROUTER_MODEL if you want the legacy single-model setting; OPENROUTER_MODELS takes priority and the legacy value is appended as a fallback if not duplicated.

An existing secret can still be invalid or lack permissions. Deployment and runtime checks are the source of truth.
