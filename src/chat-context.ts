export interface ChatHistoryMessage {
  role: "user" | "assistant";
  content: string;
}

/**
 * Keep the most recent useful turns within a predictable character budget.
 * This is a defensive context budget, not an exact tokenizer; providers apply
 * their own tokenization to the final prompt.
 */
export function compactChatHistory(value: unknown): ChatHistoryMessage[] {
  const entries = Array.isArray(value) ? value.slice(-10) : [];
  const selected: ChatHistoryMessage[] = [];
  let remaining = 8_000;

  for (let index = entries.length - 1; index >= 0 && selected.length < 8 && remaining > 0; index -= 1) {
    const entry = entries[index];
    if (!entry || typeof entry !== "object") continue;
    const item = entry as Record<string, unknown>;
    if ((item.role !== "user" && item.role !== "assistant") || typeof item.content !== "string") continue;
    const content = item.content.trim();
    if (!content) continue;
    const budget = Math.min(1_800, remaining);
    const bounded = content.length > budget ? content.slice(-budget) : content;
    if (!bounded) continue;
    selected.push({ role: item.role, content: bounded });
    remaining -= bounded.length;
  }
  return selected.reverse();
}
