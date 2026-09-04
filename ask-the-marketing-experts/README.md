# Ask the Marketing Experts — backend wiring

**Status: Ready for Dev.** Owner: Mo. Raised by Dave.

> **Staging drop — passthrough only.** These files live in the `handoffs` repo until you
> move them into the real product repo/host. Once you've migrated them, that copy is
> canonical and this folder is stale. Don't build long-term from here.
> **This repo is public — never add keys, `.env`, or client data.**

## The one-line problem

The client-facing tool **"Ask the Marketing Experts"** works inside Claude's preview but
**can't answer questions once it's on our own hosting.** It calls the Anthropic API with no
key attached — that only works inside Claude's preview, which supplies credentials behind
the scenes. On our hosting there's no key, so the button can't return an answer.

## The fix

Stand up a small **server-side proxy** that holds the API key and makes the call for the
browser. Browser → our proxy → Anthropic. The key never reaches the front-end.

The site is on Netlify, so the natural home is a **Netlify Function**. Any serverless
endpoint (Cloudflare Worker, Vercel function, small Express server) works the same way.

```
Browser (tool.html)  --POST /api/ask {question}-->  Function (ask.js)
                                                     adds x-api-key + version
                                                          |
                                                          v
                                             api.anthropic.com/v1/messages
```

## Files in this folder

| File | Where it goes in the product repo | What it is |
| --- | --- | --- |
| `netlify/functions/ask.js` | `netlify/functions/ask.js` | The proxy. Holds the system prompt, calls Anthropic. |
| `netlify.toml` | site root | Functions dir + `/api/ask` redirect. |
| `tool.html` | site root | Production front-end. Already calls `/api/ask`; prompt removed from browser. |

The system prompt has been moved out of the browser into `ask.js`, so it isn't exposed or
editable client-side.

## Steps

1. **Move these into the product repo/host** (create it if it doesn't exist — nothing
   upstream depends on it existing first).
2. **Get an Anthropic API key** at `console.anthropic.com` under Dave's org. Treat as a secret.
3. **Set it as a Netlify environment variable — not in any file:**
   Site configuration → Environment variables → `ANTHROPIC_API_KEY = sk-ant-...`
4. **Place the files** — `netlify/functions/ask.js`, `netlify.toml` at root, `tool.html` at root.
5. **Deploy.** Netlify auto-detects and builds the function.

## API notes (please don't skip)

- **Model:** the file uses `claude-sonnet-5`. The Claude preview used `claude-sonnet-4-6`,
  which is an **internal preview identifier — do not use it against the real API.** Confirm
  the current production model on the models page and pin a dated snapshot for production.
- **Headers** (already in `ask.js`): `x-api-key`, `anthropic-version: 2023-06-01`,
  `content-type: application/json`. Note it's `x-api-key`, **not** `Authorization: Bearer`.
- **Request shape:** `max_tokens` is required; `system` is its own top-level field, not a
  message. Already handled.
- **Response:** `ask.js` passes Anthropic's response straight back, so the front-end parsing
  needs no change.

## Guardrails for a public "ask anything" box

- **Cost:** every answer is a paid API call. Small each, but a public box can be hit hard and
  there's no revenue per use — it's top-of-funnel.
- **Abuse:** `ask.js` caps question length at 1000 chars. Please add simple per-IP rate
  limiting, and a referrer/domain check if abuse appears, so it isn't used as a free LLM elsewhere.
- **Key stays server-side only.** Verify in browser dev tools that no key appears in any request.

## Done when

1. Public tool page: type a question, hit **Get direction** → a real answer card returns
   (read → steps → frameworks → "Want help doing this?" offer).
2. Dev tools → Network shows the browser calling **`/api/ask`**, with **no Anthropic key
   visible client-side**.
3. The **Book a strategy session** button opens the booking page.

## Full context

Decision log, four-box gate verdict, kill condition (3 Nov 2026) and the integrity guardrail
live in Notion: **AI KB → Ideas & Opportunities → "Ask the Marketing Experts — instant-answer
lead gen tool (NLA)"**, and the handoff page under **Handoffs → Mo**.

- Booking page (live): https://askthe-expert.netlify.app/
- GHL booking calendar: https://lnk.connectme2.net/widget/booking/UFXyEoVLBMjW76HxQUak
