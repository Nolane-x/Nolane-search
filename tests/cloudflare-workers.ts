/** Test-only runtime shim for Cloudflare module entrypoint classes.
 * The production Worker bundle resolves these classes from workerd.
 * Vitest imports src/index.ts in Node only to exercise ordinary HTTP routes.
 */
export class WorkerEntrypoint<Env = unknown> {
  protected readonly ctx: any;
  protected readonly env: Env;
  constructor(ctx: any, env: Env) {
    this.ctx = ctx;
    this.env = env;
  }
}

export class DurableObject<Env = unknown> {
  protected readonly ctx: any;
  protected readonly env: Env;
  constructor(ctx: any, env: Env) {
    this.ctx = ctx;
    this.env = env;
  }
}
