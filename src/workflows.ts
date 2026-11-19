import type { Env } from "./types";
import { validateToolPipelineDefinition, validateToolWorkflowGraph } from "./tools";
import type { ToolPipelineStep, ToolWorkflowGraph } from "./tools";

export interface ToolWorkflow {
  id: string;
  userId: number;
  chatId: number;
  name: string;
  /** Legacy linear definition. For DAG workflows this is the topological tool order. */
  steps: ToolPipelineStep[];
  graph?: ToolWorkflowGraph;
  createdAt: number;
  updatedAt: number;
}

export interface PendingToolWorkflow {
  userId: number;
  chatId: number;
  workflowId: string;
}

const WORKFLOW_PREFIX = "tool-workflow:";
const PENDING_PREFIX = "tool-workflow-pending:";
const WORKFLOW_EXPIRES_AT = Number.MAX_SAFE_INTEGER;
const PENDING_TTL_MS = 15 * 60 * 1000;

function workflowKey(userId: number, id: string): string {
  return WORKFLOW_PREFIX + userId + ":" + id;
}

function pendingKey(userId: number, chatId: number): string {
  return PENDING_PREFIX + userId + ":" + chatId;
}

function normalizeWorkflowName(value: string): string {
  return value.normalize("NFKC").trim().replace(/\s+/g, " ");
}

function parseWorkflow(value: unknown, expectedUserId: number): ToolWorkflow | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const item = value as Record<string, unknown>;
  if (item.userId !== expectedUserId || typeof item.id !== "string" ||
      !/^[a-f0-9]{12}$/i.test(item.id) || typeof item.chatId !== "number" ||
      !Number.isSafeInteger(item.chatId) || typeof item.name !== "string" ||
      typeof item.createdAt !== "number" || typeof item.updatedAt !== "number") return null;
  let steps: ToolPipelineStep[];
  let graph: ToolWorkflowGraph | undefined;
  if (item.graph !== undefined) {
    const checked = validateToolWorkflowGraph(item.graph);
    if (!checked.ok) return null;
    graph = checked.graph;
    steps = checked.graph.nodes.map(node => ({ toolId: node.toolId, ...(node.reason ? { reason: node.reason } : {}) }));
  } else {
    const pipeline = validateToolPipelineDefinition(item.steps);
    if (!pipeline.ok) return null;
    steps = pipeline.steps;
  }
  return {
    id: item.id,
    userId: expectedUserId,
    chatId: item.chatId,
    name: normalizeWorkflowName(item.name),
    steps,
    ...(graph ? { graph } : {}),
    createdAt: item.createdAt,
    updatedAt: item.updatedAt,
  };
}

export async function listToolWorkflows(env: Env, userId: number): Promise<ToolWorkflow[]> {
  const rows = await env.DB.prepare(
    "SELECT payload FROM search_cache WHERE cache_key LIKE ? AND expires_at > ? ORDER BY created_at DESC",
  ).bind(WORKFLOW_PREFIX + userId + ":%", Date.now())
    .all<{ payload: string }>();
  const workflows: ToolWorkflow[] = [];
  for (const row of rows.results) {
    try {
      const item = parseWorkflow(JSON.parse(row.payload), userId);
      if (item) workflows.push(item);
    } catch { /* Ignore malformed or obsolete workflow records. */ }
  }
  return workflows;
}

export async function getToolWorkflow(env: Env, userId: number, id: string): Promise<ToolWorkflow | null> {
  if (!/^[a-f0-9]{12}$/i.test(id)) return null;
  const row = await env.DB.prepare(
    "SELECT payload FROM search_cache WHERE cache_key = ? AND expires_at > ?",
  ).bind(workflowKey(userId, id), Date.now()).first<{ payload: string }>();
  if (!row?.payload) return null;
  try { return parseWorkflow(JSON.parse(row.payload), userId); }
  catch { return null; }
}

export async function saveToolWorkflow(
  env: Env,
  userId: number,
  chatId: number,
  rawName: string,
  rawSteps: unknown,
): Promise<ToolWorkflow> {
  const name = normalizeWorkflowName(rawName);
  if (name.length < 3 || name.length > 40 || /[\u0000-\u001f\u007f]/.test(name)) {
    throw new Error("Tên workflow phải dài 3–40 ký tự và không chứa ký tự điều khiển.");
  }
  const pipeline = validateToolPipelineDefinition(rawSteps);
  if (!pipeline.ok) throw new Error(pipeline.error);

  const existing = await listToolWorkflows(env, userId);
  if (existing.some(item => item.name.toLocaleLowerCase("en-US") === name.toLocaleLowerCase("en-US"))) {
    throw new Error("Đã có workflow trùng tên. Hãy chọn tên khác hoặc xóa bản cũ.");
  }

  const now = Date.now();
  let id = "";
  for (let attempt = 0; attempt < 4; attempt++) {
    id = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
    if (!(await getToolWorkflow(env, userId, id))) break;
    id = "";
  }
  if (!id) throw new Error("Không thể tạo ID workflow duy nhất. Hãy thử lại.");
  const workflow: ToolWorkflow = {
    id, userId, chatId, name, steps: pipeline.steps, createdAt: now, updatedAt: now,
  };
  await env.DB.prepare(
    "INSERT INTO search_cache (cache_key, payload, expires_at, created_at) VALUES (?, ?, ?, ?)",
  ).bind(workflowKey(userId, id), JSON.stringify(workflow), WORKFLOW_EXPIRES_AT, now).run();
  return workflow;
}


export async function saveDagToolWorkflow(
  env: Env,
  userId: number,
  chatId: number,
  rawName: string,
  rawGraph: unknown,
): Promise<ToolWorkflow> {
  const name = normalizeWorkflowName(rawName);
  if (name.length < 3 || name.length > 40 || /[\u0000-\u001f\u007f]/.test(name)) {
    throw new Error("Tên workflow phải dài 3–40 ký tự và không chứa ký tự điều khiển.");
  }
  const checked = validateToolWorkflowGraph(rawGraph);
  if (!checked.ok) throw new Error(checked.error);
  const existing = await listToolWorkflows(env, userId);
  if (existing.some(item => item.name.toLocaleLowerCase("en-US") === name.toLocaleLowerCase("en-US"))) {
    throw new Error("Đã có workflow trùng tên. Hãy chọn tên khác hoặc xóa bản cũ.");
  }
  const now = Date.now();
  let id = "";
  for (let attempt = 0; attempt < 4; attempt++) {
    id = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
    if (!(await getToolWorkflow(env, userId, id))) break;
    id = "";
  }
  if (!id) throw new Error("Không thể tạo ID workflow duy nhất. Hãy thử lại.");
  const workflow: ToolWorkflow = {
    id, userId, chatId, name,
    steps: checked.graph.nodes.map(node => ({ toolId: node.toolId, ...(node.reason ? { reason: node.reason } : {}) })),
    graph: checked.graph,
    createdAt: now,
    updatedAt: now,
  };
  await env.DB.prepare(
    "INSERT INTO search_cache (cache_key, payload, expires_at, created_at) VALUES (?, ?, ?, ?)",
  ).bind(workflowKey(userId, id), JSON.stringify(workflow), WORKFLOW_EXPIRES_AT, now).run();
  return workflow;
}

export async function deleteToolWorkflow(env: Env, userId: number, id: string): Promise<boolean> {
  const workflow = await getToolWorkflow(env, userId, id);
  if (!workflow) return false;
  await env.DB.prepare("DELETE FROM search_cache WHERE cache_key = ?")
    .bind(workflowKey(userId, id)).run();
  return true;
}

export async function setPendingToolWorkflow(
  env: Env,
  userId: number,
  chatId: number,
  workflowId: string,
): Promise<ToolWorkflow> {
  const workflow = await getToolWorkflow(env, userId, workflowId);
  if (!workflow) throw new Error("Không tìm thấy workflow này trong tài khoản của bạn.");
  const now = Date.now();
  const pending: PendingToolWorkflow = { userId, chatId, workflowId };
  await env.DB.prepare(
    "INSERT INTO search_cache (cache_key, payload, expires_at, created_at) VALUES (?, ?, ?, ?) " +
    "ON CONFLICT(cache_key) DO UPDATE SET payload = excluded.payload, expires_at = excluded.expires_at, created_at = excluded.created_at",
  ).bind(pendingKey(userId, chatId), JSON.stringify(pending), now + PENDING_TTL_MS, now).run();
  return workflow;
}

export async function getPendingToolWorkflow(
  env: Env,
  userId: number,
  chatId: number,
): Promise<{ pending: PendingToolWorkflow; workflow: ToolWorkflow } | null> {
  const row = await env.DB.prepare(
    "SELECT payload FROM search_cache WHERE cache_key = ? AND expires_at > ?",
  ).bind(pendingKey(userId, chatId), Date.now()).first<{ payload: string }>();
  if (!row?.payload) return null;
  try {
    const item = JSON.parse(row.payload) as Partial<PendingToolWorkflow>;
    if (item.userId !== userId || item.chatId !== chatId ||
        typeof item.workflowId !== "string" || !/^[a-f0-9]{12}$/i.test(item.workflowId)) return null;
    const workflow = await getToolWorkflow(env, userId, item.workflowId);
    if (!workflow) return null;
    return { pending: { userId, chatId, workflowId: item.workflowId }, workflow };
  } catch { return null; }
}

export async function clearPendingToolWorkflow(env: Env, userId: number, chatId: number): Promise<void> {
  await env.DB.prepare("DELETE FROM search_cache WHERE cache_key = ?")
    .bind(pendingKey(userId, chatId)).run();
}
