const fs = require("fs");

const [source, srtOutput, assOutput] = process.argv.slice(2);
if (!source || !srtOutput || !assOutput) {
  throw new Error("Usage: node reflow_subtitles.js source.srt output.srt output.ass");
}

function parseTime(value) {
  const [h, m, rest] = value.split(":");
  const [s, ms] = rest.split(",");
  return +h * 3600 + +m * 60 + +s + +ms / 1000;
}

function srtTime(value) {
  let ms = Math.round(Math.max(0, value) * 1000);
  const h = Math.floor(ms / 3600000);
  ms %= 3600000;
  const m = Math.floor(ms / 60000);
  ms %= 60000;
  const s = Math.floor(ms / 1000);
  ms %= 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
}

function assTime(value) {
  let cs = Math.round(Math.max(0, value) * 100);
  const h = Math.floor(cs / 360000);
  cs %= 360000;
  const m = Math.floor(cs / 6000);
  cs %= 6000;
  const s = Math.floor(cs / 100);
  cs %= 100;
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(cs).padStart(2, "0")}`;
}

function parseSrt(text) {
  return text.trim().split(/\r?\n\r?\n/).map((block) => {
    const lines = block.split(/\r?\n/);
    const match = lines[1].match(/^(.+?) --> (.+)$/);
    return {
      start: parseTime(match[1]),
      end: parseTime(match[2]),
      text: lines.slice(2).join(" ").replace(/\s+/g, " ").trim(),
    };
  });
}

function splitWords(text, limit) {
  const words = text.split(" ");
  const chunks = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (current && next.length > limit) {
      chunks.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}

function splitCue(text, limit = 86) {
  if (text.length <= limit) return [text];
  const clauses = text.split(/(?<=[.!?;,])\s+/);
  const chunks = [];
  let current = "";
  for (const clause of clauses) {
    const next = current ? `${current} ${clause}` : clause;
    if (current && next.length > limit) {
      chunks.push(...splitWords(current, limit));
      current = clause;
    } else {
      current = next;
    }
  }
  if (current) chunks.push(...splitWords(current, limit));
  return chunks;
}

function balancedLines(text) {
  if (text.length <= 48) return [text];
  const words = text.split(" ");
  let best = null;
  for (let cut = 1; cut < words.length; cut++) {
    const left = words.slice(0, cut).join(" ");
    const right = words.slice(cut).join(" ");
    if (Math.max(left.length, right.length) <= 48) {
      const score = Math.abs(left.length - right.length);
      if (!best || score < best.score) best = { score, lines: [left, right] };
    }
  }
  if (!best) throw new Error(`Cannot fit cue in two lines: ${text}`);
  return best.lines;
}

const sourceCues = parseSrt(fs.readFileSync(source, "utf8"));
const cues = [];
for (const cue of sourceCues) {
  const chunks = splitCue(cue.text);
  const weights = chunks.map((text) => Math.max(1, text.replace(/ /g, "").length));
  const total = weights.reduce((sum, value) => sum + value, 0);
  const duration = cue.end - cue.start;
  let cursor = cue.start;
  chunks.forEach((text, index) => {
    const end = index === chunks.length - 1 ? cue.end : cursor + duration * weights[index] / total;
    cues.push({ start: cursor, end, text });
    cursor = end;
  });
}

const srt = cues.map((cue, index) =>
  `${index + 1}\n${srtTime(cue.start)} --> ${srtTime(cue.end)}\n${balancedLines(cue.text).join("\n")}`
).join("\n\n") + "\n";
fs.writeFileSync(srtOutput, srt, "utf8");

const header = `[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H78000000,&H78000000,0,0,0,0,100,100,0,0,3,6,0,2,24,24,112,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`;
const events = cues.map((cue) =>
  `Dialogue: 0,${assTime(cue.start)},${assTime(cue.end)},Default,,0,0,0,,${balancedLines(cue.text).join("\\N")}`
).join("\n");
fs.writeFileSync(assOutput, `${header}${events}\n`, "utf8");
console.log(`Wrote ${cues.length} clean cues; maximum two lines.`);
