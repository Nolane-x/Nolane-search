import { readdir, readFile } from "node:fs/promises";
import { join, resolve } from "node:path";

const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
const databaseId = process.env.CLOUDFLARE_D1_DATABASE_ID;
const token = process.env.CLOUDFLARE_API_TOKEN;

if (!accountId || !databaseId || !token) {
  throw new Error("Missing CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_D1_DATABASE_ID or CLOUDFLARE_API_TOKEN.");
}

const endpoint = \`https://api.cloudflare.com/client/v4/accounts/\${accountId}/d1/database/\${databaseId}/query\`;

async function query(sql, params = []) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { authorization: \`Bearer \${token}\`, "content-type": "application/json" },
    body: JSON.stringify({ sql, params }),
  });
  const data = await response.json();
  if (!response.ok || !data.success) {
    const message = (data.errors || []).map((item) => item.message).join("; ");
    throw new Error(\`D1 query failed (\${response.status}): \${message || "unknown Cloudflare error"}\`);
  }
  return data.result?.[0]?.results ?? [];
}

await query("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)");
const appliedRows = await query("SELECT name FROM schema_migrations");
const applied = new Set(appliedRows.map((row) => row.name));
const directory = resolve("database/migrations");
const names = (await readdir(directory)).filter((name) => /^\d+_[a-z0-9_-]+\.sql$/i.test(name)).sort();

for (const name of names) {
  if (applied.has(name)) {
    console.log(\`skip \${name} (already applied)\`);
    continue;
  }
  const source = await readFile(join(directory, name), "utf8");
  const statements = source.split(";").map((part) => part.trim()).filter(Boolean);
  for (const sql of statements) await query(sql);
  await query("INSERT INTO schema_migrations (name) VALUES (?)", [name]);
  console.log(\`applied \${name}\`);
}

console.log("D1 migrations complete.");
