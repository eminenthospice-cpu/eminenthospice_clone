const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const downloads = "C:\\Users\\emine\\Downloads";
const subtitleRoot = path.join(root, "deliverables", "youtube-subtitles");
const outRoot = path.join(root, "deliverables");
const cache = JSON.parse(fs.readFileSync(path.join(root, "audit", "context_translation_cache.json"), "utf8"));

const jobs = [
  { id: "9g98EDnOAUI", slug: "suction-machine", source: "YTDown_YouTube_Media_9g98EDnOAUI_001_1080p (1).mp4" },
  { id: "qWl3XdJ4rck", slug: "hospice-aide-perspective", source: "YTDown_YouTube_Media_qWl3XdJ4rck_001_1080p.mp4" },
  { id: "jsPCywsMe5Y", slug: "hospice-nurse-perspective", source: "YTDown_YouTube_Media_jsPCywsMe5Y_001_1080p.mp4" },
];

function parseTime(value) {
  const [h, m, rest] = value.replace(",", ".").split(":");
  return Number(h) * 3600 + Number(m) * 60 + Number(rest);
}

function stamp(seconds, ass = false) {
  const scale = ass ? 100 : 1000;
  let n = Math.round(seconds * scale);
  const h = Math.floor(n / (3600 * scale)); n %= 3600 * scale;
  const m = Math.floor(n / (60 * scale)); n %= 60 * scale;
  const s = Math.floor(n / scale);
  const fraction = String(n % scale).padStart(ass ? 2 : 3, "0");
  return ass ? `${h}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}.${fraction}`
    : `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")},${fraction}`;
}

function parseSrt(file) {
  return fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "").replace(/\r/g, "").trim()
    .split(/\n{2,}/).map(block => {
      const lines = block.split("\n");
      if (lines.length < 3 || !lines[1].includes("-->")) return null;
      const [start, end] = lines[1].split("-->").map(v => v.trim());
      return { start: parseTime(start), end: parseTime(end), text: lines.slice(2).join(" ").trim() };
    }).filter(Boolean);
}

function groupRows(rows) {
  const noise = new Set(["ah", "ahhh", "ugh", "hahaha", "222", "4", "yes"]);
  const groups = []; let current = null;
  for (const row of rows) {
    const normalized = row.text.replace(/[^A-Za-z가-힣]+/g, "").toLowerCase();
    if (row.text === "[Music]" || noise.has(normalized) || normalized.length <= 1) {
      if (current) groups.push(current), current = null;
      if (row.text === "[Music]") groups.push({...row});
      continue;
    }
    if (!current) { current = {...row}; continue; }
    if (current.text.length + row.text.length > 105 || row.end - current.start > 10) {
      groups.push(current); current = {...row};
    } else {
      current.end = row.end; current.text += " " + row.text;
    }
  }
  if (current) groups.push(current);
  return groups;
}

function polish(text) {
  const replacements = [
    [/Eminent (Speech|Peace) Care/gi, "Eminent Hospice"],
    [/\bhostess\b/gi, "hospice"],
    [/\bhose pass\b/gi, "hospice"],
    [/\bSpieth\b/gi, "hospice"],
    [/\bFolst\b|\bHolst\b|\bPoles\b/g, "POLST"],
    [/\bLine One\b/g, "911"],
    [/cardiopulmonary aquatic therapy/gi, "cardiopulmonary resuscitation"],
    [/\brain\b/gi, "pain"],
    [/\bcaregiver teacher\b/gi, "care team"],
    [/\bdrug treatment\b/gi, "medication management"],
    [/\bterminally ill cancer patients\b/gi, "patients with terminal cancer"],
    [/\bphlegm inhaler\b/gi, "suction machine"],
    [/\binhaler suction device\b/gi, "suction machine"],
    [/\bsuction special lecture\b/gi, "suction tubing"],
  ];
  let result = text || "";
  for (const [from, to] of replacements) result = result.replace(from, to);
  result = result.replace(/\s+/g, " ").trim();
  if (result && result !== "[Music]" && !/[.?!]$/.test(result)) result += ".";
  return result;
}

function wrap(text, width = 42) {
  if (text === "[Music]") return [text];
  const words = text.split(/\s+/); const lines = []; let line = "";
  for (const word of words) {
    if (line && `${line} ${word}`.length > width) { lines.push(line); line = word; }
    else line = line ? `${line} ${word}` : word;
  }
  if (line) lines.push(line);
  if (lines.length <= 2) return lines;
  const joined = words.join(" "); let best = 1; let delta = Infinity;
  for (let i = 1; i < joined.length; i++) if (joined[i] === " ") {
    const d = Math.abs(i - (joined.length - i - 1));
    if (d < delta) best = i, delta = d;
  }
  return [joined.slice(0, best), joined.slice(best + 1)];
}

function txt(entries) {
  return entries.map(e => `[${stamp(e.start)} --> ${stamp(e.end)}] ${e.text}`).join("\n") + "\n";
}

function srt(entries) {
  return entries.map((e, i) => `${i+1}\n${stamp(e.start)} --> ${stamp(e.end)}\n${wrap(e.text).join("\n")}`).join("\n\n") + "\n";
}

function ass(entries) {
  const header = `[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`;
  return header + entries.map(e => `Dialogue: 0,${stamp(e.start,true)},${stamp(e.end,true)},Default,,0,0,0,,${wrap(e.text).join("\\N").replace(/[{}]/g,"")}`).join("\n") + "\n";
}

for (const job of jobs) {
  const sourceFolder = path.join(subtitleRoot, `${job.id}-${job.slug}`);
  const grouped = groupRows(parseSrt(path.join(sourceFolder, "ko-transcript.srt")));
  const ko = grouped.map((e, i) => ({...e, end: Math.max(e.start + 0.35, Math.min(e.end, grouped[i+1] ? grouped[i+1].start - 0.04 : e.end))}));
  const en = ko.map(e => ({start: e.start, end: e.end, text: polish(cache[e.text] || "")})).filter(e => e.text);
  const folder = path.join(outRoot, `korean-video-${job.id}`);
  const archive = path.join(outRoot, "subtitle-reference", `${job.id}-${job.slug}`);
  fs.mkdirSync(folder, {recursive: true}); fs.mkdirSync(archive, {recursive: true});
  const base = path.parse(job.source).name.replace(" (1)", "");
  const artifacts = {
    [`${base}_korean_transcript.txt`]: txt(ko),
    [`${base}_korean_transcript.json`]: JSON.stringify(ko, null, 2) + "\n",
    [`${base}_english_translation.txt`]: txt(en),
    [`${base}_english_translation.json`]: JSON.stringify(en, null, 2) + "\n",
    [`${base}_english.srt`]: srt(en),
    [`${base}_english_clean.ass`]: ass(en),
  };
  for (const [name, body] of Object.entries(artifacts)) {
    fs.writeFileSync(path.join(folder, name), body, "utf8");
    fs.writeFileSync(path.join(archive, name), body, "utf8");
  }
  fs.writeFileSync(path.join(folder, "source-path.txt"), path.join(downloads, job.source) + "\n", "utf8");
  console.log(JSON.stringify({ ...job, folder, base, cues: en.length }));
}
