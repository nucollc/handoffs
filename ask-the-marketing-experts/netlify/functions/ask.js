// netlify/functions/ask.js
// Server-side proxy for the "Ask the Marketing Experts" tool.
// The Anthropic API key lives ONLY here (as an env var), never in the browser.
// Node 18+ on Netlify has global fetch, so this needs no dependencies.

const SYSTEM_PROMPT = `You are a senior strategist at Next Level Agency. A business owner asked a real marketing question. Give a quick, punchy read and tell them exactly what to do — like a sharp expert giving fast, instructional feedback, not a consultant writing a report.

Rules:
- Lead with the real issue, stated plainly and specific to THEIR question. If it's vague, make one reasonable assumption and say it in a few words.
- The steps are the point: short, imperative, do-this-now instructions. One clear action each, with enough specifics to act on. 3-4 steps max.
- Keep everything tight. No filler, no hype, no long paragraphs. Sentence case.
- Ground the advice in real, publicly established marketing frameworks and name them honestly (e.g. Alex Hormozi's value equation / Grand Slam Offer; Gary Vaynerchuk's jab-jab-jab-right-hook; Donald Miller's StoryBrand; Seth Godin's permission marketing; April Dunford's positioning; Robert Cialdini's influence principles; the rule of seven). Only name one that truly fits.
- NEVER fabricate quotes or claim any named person said, endorses, or is affiliated with anything. You are applying their public framework, not speaking for them.

Respond with ONLY valid JSON - no code fences, no text before or after:
{
  "headline": "one short line: the core thing to fix",
  "feedback": "one or two tight sentences - your quick read on what's going wrong",
  "steps": ["imperative do-this-now instruction with specifics", "...", "..."],
  "frameworks": [{"name":"framework name","source":"who it comes from"}]
}`;

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  // pull + sanitise the question
  let question = '';
  try { question = String((JSON.parse(event.body || '{}').question) || '').trim(); }
  catch (_) { /* bad JSON -> handled below */ }

  if (!question) {
    return { statusCode: 400, body: JSON.stringify({ error: 'No question provided.' }) };
  }
  if (question.length > 1000) question = question.slice(0, 1000); // basic abuse guard

  if (!process.env.ANTHROPIC_API_KEY) {
    return { statusCode: 500, body: JSON.stringify({ error: 'Server missing ANTHROPIC_API_KEY' }) };
  }

  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-5',   // production model — confirm/pin on the models page
        max_tokens: 1000,
        system: SYSTEM_PROMPT,
        messages: [{ role: 'user', content: question }]
      })
    });

    // Pass the Anthropic response straight through — the front-end already parses
    // the standard { content: [...] } shape, so no other client change is needed.
    const data = await res.json();
    return {
      statusCode: res.status,
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(data)
    };
  } catch (err) {
    return { statusCode: 502, body: JSON.stringify({ error: 'Upstream request failed' }) };
  }
};
