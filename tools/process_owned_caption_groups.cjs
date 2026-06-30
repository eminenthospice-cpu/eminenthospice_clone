const fs = require("fs");
const path = require("path");
const cp = require("child_process");

const root = path.resolve(__dirname, "..");
const groups = [
  ["SNGsCjicC8E", "after-death-non-hospice", "after-death-non-hospice-polst"],
  ["3mgBE6CaI4I", "end-of-life-timing", "end-of-life-timing"],
  ["edmwae3Iglk", "nebulizer", "nebulizer"],
  ["Vq5rIpelzhk", "oxygen-concentrator", "oxygen-concentrator"],
];
const maxLine = 42, maxCue = 84, sizeLimit = Math.floor(23.5 * 1024 * 1024);
const run = (args) => cp.execFileSync(args[0], args.slice(1), { cwd: root, stdio: "inherit" });
const files = (dir) => fs.readdirSync(dir).map((name) => path.join(dir, name));
const pick = (dir, regex) => {
  const match = files(dir).find((file) => regex.test(path.basename(file)));
  if (!match) throw new Error(`Missing ${regex} in ${dir}`);
  return match;
};
const probe = (file) => JSON.parse(cp.execFileSync("ffprobe", [
  "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name",
  "-of", "json", file
], { encoding: "utf8" }));
const toMs = (stamp) => {
  const [h, m, rest] = stamp.replace(".", ",").split(":");
  const [s, ms] = rest.split(",");
  return ((+h * 60 + +m) * 60 + +s) * 1000 + +ms;
};
const srtStamp = (value) => {
  let ms = Math.max(0, Math.round(value));
  const h = Math.floor(ms / 3600000); ms %= 3600000;
  const m = Math.floor(ms / 60000); ms %= 60000;
  const s = Math.floor(ms / 1000); ms %= 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
};
const assStamp = (value) => {
  let cs = Math.max(0, Math.round(value / 10));
  const h = Math.floor(cs / 360000); cs %= 360000;
  const m = Math.floor(cs / 6000); cs %= 6000;
  const s = Math.floor(cs / 100); cs %= 100;
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(cs).padStart(2, "0")}`;
};
function parseSrt(file) {
  return fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").trim()
    .split(/\n{2,}/).map((block) => {
      const lines = block.split("\n");
      const i = lines.findIndex((line) => line.includes(" --> "));
      if (i < 0) return null;
      const [start, end] = lines[i].split(" --> ");
      const text = lines.slice(i + 1).map((x) => x.trim()).filter(Boolean).join(" ")
        .replace(/\s+/g, " ")
        .replace(/Kim Jung Ah|Kim Jung-ah|Kim Jeong-ah/gi, "Kim Jeong Ah");
      return [toMs(start.trim()), toMs(end.trim().split(/\s/)[0]), text];
    }).filter(Boolean);
}
function chunkText(text) {
  const result = [], words = text.split(" "); let current = [];
  for (const word of words) {
    if (current.length && [...current, word].join(" ").length > maxCue) {
      result.push(current.join(" ")); current = [word];
    } else current.push(word);
  }
  if (current.length) result.push(current.join(" "));
  return result;
}
function balance(text) {
  if (text.length <= maxLine) return [text];
  const words = text.split(" "); let best = null;
  for (let i = 1; i < words.length; i++) {
    const left = words.slice(0, i).join(" "), right = words.slice(i).join(" ");
    if (left.length <= maxLine && right.length <= maxLine) {
      const score = Math.abs(left.length - right.length);
      if (!best || score < best[0]) best = [score, left, right];
    }
  }
  if (best) return best.slice(1);
  const split = Math.max(1, text.lastIndexOf(" ", Math.floor(text.length / 2)));
  return [text.slice(0, split).trim(), text.slice(split).trim()];
}
function canonicalize(input) {
  const output = [];
  for (const [start, end, text] of input) {
    const pieces = chunkText(text), weights = pieces.map((x) => Math.max(1, x.replace(/ /g, "").length));
    const total = weights.reduce((a, b) => a + b, 0); let cursor = start, used = 0;
    pieces.forEach((piece, i) => {
      used += weights[i];
      const pieceEnd = i === pieces.length - 1 ? end : start + Math.round((end - start) * used / total);
      output.push([cursor, Math.max(cursor + 10, pieceEnd), balance(piece)]);
      cursor = pieceEnd;
    });
  }
  for (let i = 1; i < output.length; i++) {
    if (output[i][0] < output[i - 1][1]) output[i - 1][1] = output[i][0];
  }
  return output;
}
function writeSrt(file, cues) {
  fs.writeFileSync(file, cues.map(([start, end, lines], i) =>
    `${i + 1}\n${srtStamp(start)} --> ${srtStamp(end)}\n${lines.join("\n")}`
  ).join("\n\n") + "\n");
}
function writeAss(file, cues) {
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
  const events = cues.map(([start, end, lines]) =>
    `Dialogue: 0,${assStamp(start)},${assStamp(end)},Default,,0,0,0,,${lines.join("\\N")}`
  ).join("\n");
  fs.writeFileSync(file, header + events + "\n");
}
function encodePublic(master, destination, duration, passlog) {
  const audioRate = 96000;
  const videoRate = Math.max(180000, Math.floor((sizeLimit * 8 / duration - audioRate) * 0.94));
  const temp = destination.replace(/\.mp4$/, ".tmp.mp4");
  if (!fs.existsSync(temp)) {
    run(["ffmpeg", "-y", "-i", master, "-c:v", "libx264", "-preset", "slow", "-b:v", String(videoRate),
      "-maxrate", String(videoRate), "-bufsize", String(videoRate * 2), "-passlogfile", passlog,
      "-pass", "1", "-an", "-f", "mp4", "NUL"]);
    run(["ffmpeg", "-y", "-i", master, "-c:v", "libx264", "-preset", "slow", "-b:v", String(videoRate),
      "-maxrate", String(videoRate), "-bufsize", String(videoRate * 2), "-passlogfile", passlog,
      "-pass", "2", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", temp]);
  }
  fs.copyFileSync(temp, destination);
  fs.unlinkSync(temp);
  for (const suffix of ["-0.log", "-0.log.mbtree"]) {
    try { fs.unlinkSync(passlog + suffix); } catch {}
  }
}
const report = [];
const requestedIds = new Set(process.argv.slice(2));
for (const [id, topic, slug] of groups) {
  if (requestedIds.size && !requestedIds.has(id)) continue;
  const group = path.join(root, "deliverables", `korean-video-${id}`);
  let directSrt;
  try { directSrt = pick(group, /_english_clean\.srt$/); }
  catch { directSrt = pick(group, /_english\.srt$/); }
  let ass;
  try { ass = pick(group, /_english_clean\.ass$/); }
  catch { ass = directSrt.replace(/\.srt$/, ".ass"); }
  const source = pick(group, /_compressed\.mp4$/);
  const master = pick(group, /_english_captioned\.mp4$/);
  let refDir = path.join(root, "deliverables", "subtitle-reference", `${id}-${topic}`);
  if (!fs.existsSync(refDir)) refDir = path.join(root, "deliverables", "subtitle-reference", id);
  const refSrt = pick(refDir, /_english(?:_clean)?\.srt$/);
  const refAss = pick(refDir, /_english_clean\.ass$/);
  const youtubeSrt = path.join(root, "deliverables", "youtube-subtitles", `${id}-${topic}`, "en-subtitles.srt");
  const publicFile = path.join(root, "public", "videos", `${slug}.mp4`);
  const cues = canonicalize(parseSrt(directSrt));
  writeSrt(directSrt, cues);
  fs.copyFileSync(directSrt, refSrt);
  fs.copyFileSync(directSrt, youtubeSrt);
  writeAss(ass, cues);
  fs.copyFileSync(ass, refAss);
  const tempMaster = master.replace(/\.mp4$/, ".tmp.mp4");
  const escapedAss = ass.replace(/\\/g, "/").replace(":", "\\:");
  run(["ffmpeg", "-y", "-i", source, "-vf", `ass='${escapedAss}'`, "-c:v", "libx264",
    "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart", tempMaster]);
  fs.renameSync(tempMaster, master);
  const duration = +probe(source).format.duration;
  encodePublic(master, publicFile, duration, path.join(group, `caption-pass-${id}`));
  report.push({ id, cues: cues.length, duration, master: path.relative(root, master),
    publicBytes: fs.statSync(publicFile).size });
}
console.log(JSON.stringify(report, null, 2));
