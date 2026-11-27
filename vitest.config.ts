import { defineConfig } from "vitest/config";

// Unit tests run in Node, not workerd. Replace only the Cloudflare base classes;
// the real Worker build continues to resolve cloudflare:workers natively.
export default defineConfig({
  resolve: {
    alias: {
      "cloudflare:workers": new URL("./tests/cloudflare-workers.ts", import.meta.url).pathname,
    },
  },
});
