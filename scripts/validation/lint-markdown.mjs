import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { lint } from "markdownlint/sync";

const config = JSON.parse(readFileSync(".markdownlint.jsonc", "utf8"));
delete config.$schema;
const trackedMarkdownFiles = execFileSync(
  "git",
  [
    "ls-files",
    "--cached",
    "--others",
    "--exclude-standard",
    "-z",
    "--",
    ":(glob)**/*.md"
  ],
  { encoding: "utf8" }
).split("\0").filter(Boolean);

if (trackedMarkdownFiles.length === 0) {
  throw new Error("No Markdown files were found by git ls-files.");
}

const canaryResults = lint({
  strings: { "__sinayxa_markdownlint_canary__.md": "#Invalid heading\n" },
  config
});
if (!canaryResults["__sinayxa_markdownlint_canary__.md"]?.some(
  (error) => error.ruleNames?.includes("MD018")
)) {
  throw new Error("Markdown lint self-test failed: MD018 canary was not detected.");
}
console.log("Markdown lint self-test passed: MD018 canary detected.");

const results = lint({ files: trackedMarkdownFiles, config });
let errorCount = 0;

for (const [file, errors] of Object.entries(results)) {
  for (const error of errors) {
    errorCount++;
    const rule = error.ruleNames?.join("/") || "markdownlint";
    const detail = error.errorDetail || error.ruleDescription || "Rule violation";
    console.error(`${file}:${error.lineNumber || 0} ${rule}: ${detail}`);
  }
}

if (errorCount > 0) {
  console.error(`Markdown lint failed: ${errorCount} violation(s) in ${trackedMarkdownFiles.length} file(s).`);
  process.exitCode = 1;
} else {
  console.log(`Markdown lint passed: ${trackedMarkdownFiles.length} file(s).`);
}
