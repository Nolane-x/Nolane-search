import type { Env } from "./types";
import { validateToolDagDefinition, validateToolPipelineDefinition } from "./tools";
import type { ToolDagNode, ToolPipelineStep } from "./tools";

export interface ToolWorkflow {
  id: string;
  userId: number;
  chatId: number;
  name: string;
  steps: ToolPipelineStep[];
  /** Present for DAG workflows; steps is the topological compatibility view. */
  dag?: ToolDagNode[];
  createdAt: number;
  updatedAt: number;
}

export interface PendingToolWorkflow {
  userId: number;
  chatId: number;
  workflowId: string;
}

export interface ToolWorkflowPlan {
  mode: "single" | "pipeline" | "dag";
  summary: string;
  confidence: number;
  assumptions: string[];
  warnings: string[];
  steps: ToolPipelineStep[];
  dag?: ToolDagNode[];
  workload: { nodeCount: number; criticalPathLength: number; maxParallelism: number };
}

export interface PendingToolWorkflowPlan {
  id: string;
  userId: number;
  chatId: number;
  goal: string;
  plan: ToolWorkflowPlan;
  createdAt: number;
  expiresAt: number;
}

const WORKFLOW_PREFIX = "tool-workflow:";
const PENDING_PREFIX = "tool-workflow-pending:";
const PLAN_PREFIX = "tool-workflow-plan:";
const WORKFLOW_EXPIRES_AT = Number.MAX_SAFE_INTEGER;
const PENDING_TTL_MS = 15 * 60 * 1000;

function workflowKey(userId: number, id: string): string {
  return WORKFLOW_PREFIX + userId + ":" + id;
}

function pendingKey(userId: number, chatId: number): string {
  return PENDING_PREFIX + userId + ":" + chatId;
}

function planKey(userId: number, chatId: number, id: string): string {
  return PLAN_PREFIX + userId + ":" + chatId + ":" + id;
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
  if (item.dag !== undefined) {
    const dag = validateToolDagDefinition(item.dag);
    if (!dag.ok) return null;
    return {
      id: item.id, userId: expectedUserId, chatId: item.chatId,
      name: normalizeWorkflowName(item.name),
      steps: dag.nodes.map(node => ({ toolId: node.toolId, ...(node.reason ? { reason: node.reason } : {}) })),
      dag: dag.nodes, createdAt: item.createdAt, updatedAt: item.updatedAt,
    };
  }
  const pipeline = validateToolPipelineDefinition(item.steps);
  if (!pipeline.ok) return null;
  return {
    id: item.id, userId: expectedUserId, chatId: item.chatId,
    name: normalizeWorkflowName(item.name), steps: pipeline.steps,
    createdAt: item.createdAt, updatedAt: item.updatedAt,
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
  const candidate = Array.isArray(rawSteps) ? rawSteps[0] : null;
  const dagMode = !!candidate && typeof candidate === "object" && !Array.isArray(candidate) &&
    typeof candidate.id === "string" && Array.isArray(candidate.dependsOn);
  let workflowSteps: ToolPipelineStep[];
  let workflowDag: ToolDagNode[] | undefined;
  if (dagMode) {
    const validation = validateToolDagDefinition(rawSteps);
    if (!validation.ok) throw new Error(validation.error);
    workflowDag = validation.nodes;
    workflowSteps = validation.nodes.map(node => ({ toolId: node.toolId, ...(node.reason ? { reason: node.reason } : {}) }));
  } else {
    const validation = validateToolPipelineDefinition(rawSteps);
    if (!validation.ok) throw new Error(validation.error);
    workflowSteps = validation.steps;
  }

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
    id, userId, chatId, name, steps: workflowSteps,
    ...(workflowDag ? { dag: workflowDag } : {}),
    createdAt: now, updatedAt: now,
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

export async function storeToolWorkflowPlan(
  env: Env,
  userId: number,
  chatId: number,
  goal: string,
  plan: ToolWorkflowPlan,
): Promise<PendingToolWorkflowPlan> {
  if (goal.trim().length < 6 || goal.length > 1_200) throw new Error("Mục tiêu workflow không hợp lệ.");
  if (!Number.isSafeInteger(userId) || !Number.isSafeInteger(chatId) || chatId !== userId) {
    throw new Error("Bản nháp workflow chỉ được lưu cho tài khoản Telegram cá nhân.");
  }
  if (plan.mode === "dag") {
    const validation = validateToolDagDefinition(plan.dag);
    if (!validation.ok) throw new Error(validation.error);
  } else {
    const validation = validateToolPipelineDefinition(plan.steps);
    if (!validation.ok) throw new Error(validation.error);
    if (plan.mode === "single" && validation.steps.length !== 1) throw new Error("Bản nháp single chỉ được có một processor.");
  }
  const now = Date.now();
  const pending: PendingToolWorkflowPlan = {
    id: crypto.randomUUID().replace(/-/g, "").slice(0, 8),
    userId, chatId, goal: goal.trim().slice(0, 1_200), plan,
    createdAt: now, expiresAt: now + PENDING_TTL_MS,
  };
  await env.DB.prepare(
    "INSERT INTO search_cache (cache_key, payload, expires_at, created_at) VALUES (?, ?, ?, ?)",
  ).bind(planKey(userId, chatId, pending.id), JSON.stringify(pending), pending.expiresAt, now).run();
  return pending;
}

export async function getPendingToolWorkflowPlan(
  env: Env,
  userId: number,
  chatId: number,
  id: string,
): Promise<PendingToolWorkflowPlan | null> {
  if (!/^[a-f0-9]{8}$/i.test(id)) return null;
  const row = await env.DB.prepare(
    "SELECT payload FROM search_cache WHERE cache_key = ? AND expires_at > ?",
  ).bind(planKey(userId, chatId, id), Date.now()).first<{ payload: string }>();
  if (!row?.payload) return null;
  try {
    const value = JSON.parse(row.payload) as Partial<PendingToolWorkflowPlan>;
    if (value.id !== id || value.userId !== userId || value.chatId !== chatId ||
        typeof value.goal !== "string" || typeof value.createdAt !== "number" ||
        typeof value.expiresAt !== "number" || value.expiresAt <= Date.now() ||
        !value.plan || typeof value.plan !== "object") return null;
    const plan = value.plan;
    if (!["single", "pipeline", "dag"].includes(plan.mode) ||
        typeof plan.summary !== "string" || typeof plan.confidence !== "number" ||
        !Array.isArray(plan.assumptions) || !Array.isArray(plan.warnings) ||
        !Array.isArray(plan.steps) || !plan.workload || typeof plan.workload !== "object") return null;
    if (plan.mode === "dag") {
      if (!validateToolDagDefinition(plan.dag).ok) return null;
    } else if (!validateToolPipelineDefinition(plan.steps).ok ||
        (plan.mode === "single" && plan.steps.length !== 1)) return null;
    return value as PendingToolWorkflowPlan;
  } catch { return null; }
}

export async function deletePendingToolWorkflowPlan(
  env: Env,
  userId: number,
  chatId: number,
  id: string,
): Promise<void> {
  if (!/^[a-f0-9]{8}$/i.test(id)) return;
  await env.DB.prepare("DELETE FROM search_cache WHERE cache_key = ?")
    .bind(planKey(userId, chatId, id)).run();
}
