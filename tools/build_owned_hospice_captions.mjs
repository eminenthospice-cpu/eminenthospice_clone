import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ITEMS = [
  ["42r5f9uf-0U", "polst"],
  ["K0bgtz2gV40", "hospice-core-services"],
  ["v9-onN7EsWo", "hospice-myths"],
  ["XeGjlf7fILA", "after-death-hospice"],
];
const MAX_PUBLIC = Math.floor(23.5 * 1024 * 1024);

function run(args) {
  console.log("+", args.join(" "));
  if (args[0] === "ffmpeg") args.splice(1, 0, "-hide_banner", "-loglevel", "error");
  execFileSync(args[0], args.slice(1), { stdio: "inherit" });
}
function files(dir, suffix) {
  return fs.readdirSync(dir).filter((name) => name.endsWith(suffix)).map((name) => path.join(dir, name));
}
function stampMs(value) {
  const [h, m, rest] = value.replace(".", ",").split(":");
  const [s, ms] = rest.split(",");
  return ((+h * 60 + +m) * 60 + +s) * 1000 + +(ms + "000").slice(0, 3);
}
function srtStamp(value) {
  const h = Math.floor(value / 3600000); value %= 3600000;
  const m = Math.floor(value / 60000); value %= 60000;
  const s = Math.floor(value / 1000), ms = value % 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
}
function assStamp(value) {
  const h = Math.floor(value / 3600000); value %= 3600000;
  const m = Math.floor(value / 60000); value %= 60000;
  const s = Math.floor(value / 1000), cs = Math.floor((value % 1000) / 10);
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(cs).padStart(2, "0")}`;
}
function parseSrt(file) {
  const raw = fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").trim();
  const cues = [];
  for (const block of raw.split(/\n{2,}/)) {
    const lines = block.split("\n");
    const ti = lines.findIndex((line) => line.includes("-->"));
    if (ti < 0) continue;
    const match = lines[ti].match(/\s*(\d+:\d\d:\d\d[,.]\d+)\s*-->\s*(\d+:\d\d:\d\d[,.]\d+)/);
    if (!match) throw new Error(`Bad timing in ${file}: ${lines[ti]}`);
    let text = lines.slice(ti + 1).map((line) => line.trim()).filter(Boolean).join(" ").replace(/\s+/g, " ");
    text = text.replace(/Kim Jung Ah|Kim Jung-ah|Kim Jeong-ah/gi, "Kim Jeong Ah");
    cues.push({ start: stampMs(match[1]), end: stampMs(match[2]), text });
  }
  if (!cues.length) throw new Error(`No cues in ${file}`);
  cues.forEach((cue, i) => {
    if (i && cue.start < cues[i - 1].start) throw new Error(`Out-of-order cue ${i + 1} in ${file}`);
    if (i) cues[i - 1].end = Math.min(cues[i - 1].end, cue.start);
    if (cue.end <= cue.start) throw new Error(`Non-positive cue ${i + 1} in ${file}`);
  });
  return cues;
}
function wrapText(text) {
  const words = text.split(" ");
  const lines = [""];
  for (const word of words) {
    const candidate = lines.at(-1) ? `${lines.at(-1)} ${word}` : word;
    if (candidate.length <= 52 || !lines.at(-1)) lines[lines.length - 1] = candidate;
    else lines.push(word);
  }
  if (lines.length <= 2) return lines;
  let best = 1, delta = Infinity;
  for (let i = 1; i < words.length; i++) {
    const d = Math.abs(words.slice(0, i).join(" ").length - words.slice(i).join(" ").length);
    if (d < delta) [best, delta] = [i, d];
  }
  return [words.slice(0, best).join(" "), words.slice(best).join(" ")];
}
function makeSrt(cues) {
  return cues.map((c, i) => `${i + 1}\n${srtStamp(c.start)} --> ${srtStamp(c.end)}\n${wrapText(c.text).join("\n")}`).join("\n\n") + "\n";
}
function makeAss(cues) {
  const header = `[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`;
  return header + cues.map((c) => {
    const text = wrapText(c.text).map((line) => line.replaceAll("\\", "\\\\").replaceAll("{", "\\{").replaceAll("}", "\\}")).join("\\N");
    return `Dialogue: 0,${assStamp(c.start)},${assStamp(c.end)},Default,,0,0,0,,${text}`;
  }).join("\n") + "\n";
}
function write(file, data) {
  const normalized = data.replace(/\r\n/g, "\n");
  if (!fs.existsSync(file) || fs.readFileSync(file, "utf8") !== normalized) fs.writeFileSync(file, normalized, "utf8");
}
function probe(file) {
  return JSON.parse(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration:stream=index,codec_type,codec_name,width,height", "-of", "json", file], { encoding: "utf8" }));
}
function encodePublic(captioned, output, duration) {
  const audioBps = 96000;
  const videoKbps = Math.max(80, Math.floor((((MAX_PUBLIC - 1800000) * 8 / duration) - audioBps) / 1000));
  const passlog = path.join(path.dirname(output), `.${path.parse(output).name}-pass`);
  const common = ["ffmpeg", "-y", "-i", captioned, "-c:v", "libx264", "-preset", "medium", "-b:v", `${videoKbps}k`,
    "-maxrate", `${videoKbps * 2}k`, "-bufsize", `${videoKbps * 4}k`, "-pix_fmt", "yuv420p", "-passlogfile", passlog];
  run([...common, "-pass", "1", "-an", "-f", "mp4", "NUL"]);
  run([...common, "-pass", "2", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", output]);
  for (const file of fs.readdirSync(path.dirname(output))) if (file.startsWith(path.basename(passlog))) fs.unlinkSync(path.join(path.dirname(output), file));
}

const results = [];
for (const [id, slug] of ITEMS) {
  const videoDir = path.join(ROOT, "deliverables", `korean-video-${id}`);
  const source = files(videoDir, "_compressed.mp4")[0];
  const direct = files(videoDir, "_english.srt")[0];
  const stem = path.basename(source, "_compressed.mp4");
  const canonicalSrt = path.join(videoDir, `${stem}_english.srt`);
  const cleanAss = path.join(videoDir, `${stem}_english_clean.ass`);
  const captioned = path.join(videoDir, `${stem}_english_captioned.mp4`);
  const cues = parseSrt(direct), srt = makeSrt(cues), ass = makeAss(cues);
  write(canonicalSrt, srt); write(cleanAss, ass);
  for (const target of files(videoDir, "_english_clean.srt")) write(target, srt);

  const refDir = path.join(ROOT, "deliverables", "subtitle-reference", `${id}-${slug}`);
  for (const target of files(refDir, "_english.srt")) write(target, srt);
  for (const target of files(refDir, "_english_clean.srt")) write(target, srt);
  write(path.join(refDir, `${stem}_english_clean.ass`), ass);
  write(path.join(ROOT, "deliverables", "youtube-subtitles", `${id}-${slug}`, "en-subtitles.srt"), srt);

  const escapedAss = cleanAss.replaceAll("\\", "/").replace(":", "\\:");
  if (!fs.existsSync(captioned) || fs.statSync(captioned).mtimeMs < fs.statSync(cleanAss).mtimeMs) {
    run(["ffmpeg", "-y", "-i", source, "-vf", `ass='${escapedAss}'`, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
      "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", captioned]);
  }
  const sourceInfo = probe(source), captionInfo = probe(captioned);
  const duration = +captionInfo.format.duration;
  const publicFile = path.join(ROOT, "public", "videos", `${slug}.mp4`);
  if (!fs.existsSync(publicFile) || fs.statSync(publicFile).mtimeMs < fs.statSync(captioned).mtimeMs ||
      fs.statSync(publicFile).size >= MAX_PUBLIC) encodePublic(captioned, publicFile, duration);
  const publicInfo = probe(publicFile);
  if (fs.statSync(publicFile).size >= MAX_PUBLIC) throw new Error(`${publicFile} exceeds 23.5 MiB`);
  for (const [info, label] of [[captionInfo, "captioned"], [publicInfo, "public"]]) {
    if (!info.streams.some((s) => s.codec_type === "video" && s.codec_name === "h264")) throw new Error(`${label} is not H.264`);
    if (!info.streams.some((s) => s.codec_type === "audio" && s.codec_name === "aac")) throw new Error(`${label} audio is not AAC`);
  }
  if (Math.abs(+sourceInfo.format.duration - duration) > 0.15) throw new Error(`Duration mismatch for ${id}`);
  results.push([id, cues.length, duration, fs.statSync(captioned).size, fs.statSync(publicFile).size]);
}
for (const result of results) console.log("RESULT", ...result);
