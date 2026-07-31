import { cp, mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const output = resolve(root, "public");

await rm(output, { recursive: true, force: true });
await mkdir(resolve(output, "projects"), { recursive: true });

for (const file of ["index.html", "styles.css", "portfolio.js"]) {
  await cp(resolve(root, file), resolve(output, file));
}

await cp(resolve(root, "projects", "octoavatar"), resolve(output, "projects", "octoavatar"), {
  recursive: true
});

await cp(resolve(root, "projects", "markov-network-lab"), resolve(output, "projects", "markov-network-lab"), {
  recursive: true
});

await cp(resolve(root, "projects", "global-support-agent"), resolve(output, "projects", "global-support-agent"), {
  recursive: true
});
