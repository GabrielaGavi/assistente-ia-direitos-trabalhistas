import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const frontend = resolve(here, "..");
const workspace = resolve(frontend, "..");
const source = join(workspace, "specs", "002-frontend-foundation", "references", "optivo", "optivio.html");
const publicDir = join(frontend, "public");
const vendorDir = join(publicDir, "vendor");

await mkdir(vendorDir, { recursive: true });
await copyFile(join(frontend, "node_modules", "three", "build", "three.module.js"), join(vendorDir, "three.module.js"));
await copyFile(join(frontend, "node_modules", "three", "build", "three.core.js"), join(vendorDir, "three.core.js"));
await copyFile(join(frontend, "node_modules", "lenis", "dist", "lenis.mjs"), join(vendorDir, "lenis.mjs"));

let html = await readFile(source, "utf8");
const heroVideo = /<video src="https:\/\/framerusercontent\.com\/assets\/fWNemIeXFDQFKLDjdAfNlE4R6s\.mp4"[^>]*><\/video>/;
if (!heroVideo.test(html)) throw new Error("Hero video do Optivio não encontrado na referência.");
html = html.replace(heroVideo, '<div id="interactive-hands-canvas" aria-hidden="true"></div>');
html = html.replace(/<title>[^<]*<\/title>/, "<title>Direito em claro | Informação trabalhista com fontes</title>");
html = html.replace("</head>", '<link rel="stylesheet" href="/optivio-overrides.css"></head>');
html = html.replace("</body>", '<script type="module" src="/optivio-canvas.js"></script></body>');
await writeFile(join(publicDir, "landing.html"), html, "utf8");

console.log("Landing Optivio preparada com canvas Three.js.");
