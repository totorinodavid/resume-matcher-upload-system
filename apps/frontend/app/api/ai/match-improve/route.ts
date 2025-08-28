import OpenAI from "openai";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
// Adjust based on your Vercel plan; keep within limits to avoid 504s
export const maxDuration = 60;

// Stream OpenAI chat completion directly to the browser to minimize latency and avoid large JSON payloads
export async function POST(req: Request) {
  const { prompt } = await req.json();
  if (!prompt || typeof prompt !== "string") {
    return new Response(JSON.stringify({ error: "Missing 'prompt'" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  // Use server-side environment variable
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: "OPENAI_API_KEY not configured" }), {
      status: 500,
      headers: { "content-type": "application/json" },
    });
  }

  const openai = new OpenAI({ apiKey, timeout: 60_000 });

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    stream: true,
    temperature: 0.2,
    max_tokens: 800,
    messages: [
      { role: "system", content: "Du bist ein präziser CV-ATS-Matcher." },
      { role: "user", content: prompt },
    ],
  });

  const enc = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      try {
        // Emit a very small prelude so clients see first bytes <2s consistently
        controller.enqueue(enc.encode(""));
        for await (const part of completion) {
          const delta = (part as any)?.choices?.[0]?.delta?.content ?? "";
          if (delta) controller.enqueue(enc.encode(delta));
        }
        controller.close();
      } catch (e) {
        controller.error(e);
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
