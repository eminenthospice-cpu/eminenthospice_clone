const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const root = path.resolve(__dirname, "..");
const downloads = "C:\\Users\\emine\\Downloads";
const jobs = [
  ["3mgBE6CaI4I", "end-of-life-timing", "YTDown_YouTube_Media_3mgBE6CaI4I_001_720p.mp4"],
  ["edmwae3Iglk", "nebulizer", "YTDown_YouTube_Media_edmwae3Iglk_001_1080p (2).mp4"],
  ["Vq5rIpelzhk", "oxygen-concentrator", "YTDown_YouTube_Media_Vq5rIpelzhk_001_1080p (1).mp4"],
];

const replacements = [
  [/\bEminent Peace Care\b/gi, "Eminent Hospice Care"],
  [/\bEminent Hospice\b/gi, "Eminent Hospice Care"],
  [/\bhostess\b/gi, "hospice"],
  [/\boxygen machine\b/gi, "oxygen concentrator"],
  [/\bgas tank\b/gi, "humidifier bottle"],
  [/\bwater tank\b/gi, "humidifier bottle"],
  [/\bdisinfected distilled water\b/gi, "sterile distilled water"],
  [/\boxygen bottle\b/gi, "oxygen tubing"],
  [/\boxygen device\b/gi, "oxygen concentrator"],
  [/\bamount of oxygen\b/gi, "oxygen flow rate"],
  [/\bthe patient's soju\b/gi, "the patient's nasal cannula"],
  [/\bexpand the womb\b/gi, "allow the lungs to expand"],
  [/\b2l\b/gi, "2 L/min"],
  [/\b2 a\.m\.\b/gi, "a comfortable fit"],
  [/\bmedication infusion container\b/gi, "nebulizer medication cup"],
  [/\bmedication container\b/gi, "medication cup"],
  [/\bfill bottle lid\b/gi, "medication cup lid"],
  [/\bno gas\b/gi, "no mist"],
  [/\bdirect my stomach\b/gi, "breathe out slowly"],
  [/\bWhen will you return\?\b/gi, "How much time does the patient have left?"],
  [/\bpredicted life expectancy\b/gi, "estimated life expectancy"],
];

const curated = {
  edmwae3Iglk: [
    [12.300, 18.000, "I will explain how to use a nebulizer."],
    [18.000, 26.340, "A nebulizer turns medication into a fine mist for inhalation."],
    [26.340, 33.150, "It may help patients with shortness of breath or excess mucus."],
    [33.150, 39.840, "Plug in the machine and connect the tubing to its air outlet."],
    [39.840, 47.000, "Add the prescribed medication to the nebulizer cup and attach the mask."],
    [47.000, 54.800, "Place the mask securely over the patient's nose and mouth."],
    [54.800, 62.820, "Keep the patient upright and have them breathe slowly and normally."],
    [63.600, 72.270, "Treatment takes about 10 minutes, until the mist stops."],
    [72.270, 78.000, "When the medication is gone, turn off the machine."],
    [78.000, 84.500, "After treatment, have the patient rinse their mouth with water."],
    [84.500, 90.000, "Wipe any medication from the patient's face."],
  ],
  Vq5rIpelzhk: [
    [12.900, 18.060, "I will explain how to use an oxygen concentrator."],
    [18.060, 24.060, "Plug it directly into a wall outlet. Do not use an extension cord."],
    [24.060, 30.270, "Some models use a humidifier bottle; others do not."],
    [30.270, 35.129, "If required, fill the humidifier bottle with sterile distilled water."],
    [35.129, 43.379, "Attach the humidifier bottle directly or with the supplied tubing."],
    [43.379, 49.200, "Connect the oxygen tubing or nasal cannula to the outlet."],
    [49.200, 58.620, "Without a humidifier bottle, connect the cannula directly to the concentrator."],
    [58.620, 68.039, "Turn on the concentrator using the power switch."],
    [68.039, 78.000, "For a flow check, briefly set the flowmeter to 5 L/min."],
    [78.000, 84.810, "Adjust the knob until the center of the ball reaches the 5 mark."],
    [84.810, 94.640, "Check for flow by feeling air at the cannula or placing its tip in water."],
    [94.640, 104.640, "Low flow can be hard to feel, so use 5 L/min only for this brief check."],
    [104.640, 115.890, "After confirming flow, return to the prescribed rate and apply the cannula."],
    [115.890, 122.369, "Keep the patient upright when possible to support lung expansion."],
    [122.369, 131.430, "Place the prongs in the nostrils, loop the tubing over the ears, and secure it."],
    [131.430, 137.000, "Do not overtighten the tubing; keep the patient comfortable."],
  ],
};

function polish(text) {
  let out = text.replaceAll("â€œ", '"').replaceAll("â€", '"').replaceAll("â€™", "'");
  for (const [pattern, value] of replacements) out = out.replace(pattern, value);
  return out.replace(/\s+/g, " ").trim();
}

function seconds(value) {
  const [h, m, tail] = value.replace(".", ",").split(":");
  const [s, ms = "0"] = tail.split(",");
  return +h * 3600 + +m * 60 + +s + +ms.padEnd(3, "0").slice(0, 3) / 1000;
}

function srtTime(value) {
  let ms = Math.max(0, Math.round(value * 1000));
  const h = Math.floor(ms / 3600000); ms %= 3600000;
  const m = Math.floor(ms / 60000); ms %= 60000;
  const s = Math.floor(ms / 1000); ms %= 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
}

function assTime(value) {
  return srtTime(value).replace(/^0/, "").replace(",", ".").slice(0, -1);
}

function parseSrt(file, doPolish = false) {
  return fs.readFileSync(file, "utf8").replace(/\r/g, "").trim().split(/\n{2,}/).flatMap((block) => {
    const lines = block.split("\n");
    const at = lines.findIndex((line) => line.includes("-->"));
    if (at < 0) return [];
    const [start, end] = lines[at].split("-->").map((v) => seconds(v.trim()));
    let text = lines.slice(at + 1).join(" ").replace(/\s+/g, " ").trim();
    if (doPolish) text = polish(text);
    if (!text || /^(ah+|ah ah ah ah|\[music\])$/i.test(text)) return [];
    return [{ start, end, text }];
  });
}

function splitText(text, limit = 76) {
  if (text.length <= limit) return [text];
  const words = text.split(/\s+/);
  const result = [];
  while (words.length) {
    let count = 1;
    while (count < words.length && words.slice(0, count + 1).join(" ").length <= limit) count++;
    result.push(words.splice(0, count).join(" "));
  }
  return result;
}

function newSuffix(previous, current) {
  const a = previous.split(/\s+/);
  const b = current.split(/\s+/);
  for (let n = Math.min(a.length, b.length); n >= 1; n--) {
    if (a.slice(-n).join(" ").toLowerCase() === b.slice(0, n).join(" ").toLowerCase()) return b.slice(n);
  }
  return b;
}

function rebuildRolling(cues) {
  const additions = [];
  let previous = "";
  for (const cue of cues) {
    const words = newSuffix(previous, cue.text);
    if (words.length) additions.push({ start: cue.start, end: cue.end, text: words.join(" ") });
    previous = cue.text;
  }
  const groups = [];
  let group = null;
  for (const cue of additions) {
    if (!group) group = { ...cue };
    else if (cue.end - group.start <= 7.2 && `${group.text} ${cue.text}`.length <= 76) {
      group.end = cue.end;
      group.text += ` ${cue.text}`;
    } else {
      groups.push(group);
      group = { ...cue };
    }
    if (/[.!?]$/.test(group.text) && group.text.length >= 24) {
      groups.push(group);
      group = null;
    }
  }
  if (group) groups.push(group);
  return groups;
}

function balance(text, width = 42) {
  if (text.length <= width) return text;
  const words = text.split(/\s+/);
  let best = null;
  for (let i = 1; i < words.length; i++) {
    const left = words.slice(0, i).join(" ");
    const right = words.slice(i).join(" ");
    if (left.length <= width && right.length <= width) {
      const score = Math.abs(left.length - right.length);
      if (!best || score < best.score) best = { score, left, right };
    }
  }
  return best ? `${best.left}\n${best.right}` : text;
}

function cleanTimeline(cues, duration) {
  const output = [];
  cues.forEach((cue, index) => {
    const nextStart = index + 1 < cues.length ? cues[index + 1].start : duration;
    const end = Math.min(cue.end, nextStart, duration);
    const parts = splitText(cue.text);
    const total = parts.reduce((sum, part) => sum + part.length, 0);
    let cursor = cue.start;
    for (let p = 0; p < parts.length; p++) {
      const pieceEnd = p === parts.length - 1 ? end : cursor + (end - cue.start) * parts[p].length / total;
      if (pieceEnd - cursor >= 0.35) output.push({ start: cursor, end: pieceEnd, text: parts[p] });
      cursor = pieceEnd;
    }
  });
  return output;
}

for (const [id, topic, sourceName] of jobs) {
  const source = path.join(downloads, sourceName);
  const sourceSubs = path.join(root, "deliverables", "youtube-subtitles", `${id}-${topic}`);
  const out = path.join(root, "deliverables", `korean-video-${id}`);
  const archive = path.join(root, "deliverables", "subtitle-reference", `${id}-${topic}`);
  fs.mkdirSync(out, { recursive: true });
  fs.mkdirSync(archive, { recursive: true });
  const duration = +execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", source], { encoding: "utf8" }).trim();
  const base = path.parse(sourceName).name;
  const ko = parseSrt(path.join(sourceSubs, "ko-transcript.srt"));
  const en = curated[id]
    ? curated[id].map(([start, end, text]) => ({ start, end, text }))
    : cleanTimeline(rebuildRolling(parseSrt(path.join(sourceSubs, "en-subtitles.srt"), true)), duration);
  const koSrt = path.join(out, `${base}_korean_transcript.srt`);
  fs.copyFileSync(path.join(sourceSubs, "ko-transcript.srt"), koSrt);
  fs.copyFileSync(path.join(sourceSubs, "ko-transcript.txt"), path.join(out, `${base}_korean_transcript.txt`));
  fs.writeFileSync(path.join(out, `${base}_korean_transcript.json`), JSON.stringify(ko, null, 2) + "\n");
  fs.writeFileSync(path.join(out, `${base}_english_translation.json`), JSON.stringify(en, null, 2) + "\n");
  fs.writeFileSync(path.join(out, `${base}_english_translation.txt`), en.map((x) => `[${srtTime(x.start)} --> ${srtTime(x.end)}] ${x.text}`).join("\n") + "\n");
  fs.writeFileSync(path.join(out, `${base}_english_clean.srt`), en.map((x, i) => `${i + 1}\n${srtTime(x.start)} --> ${srtTime(x.end)}\n${balance(x.text)}`).join("\n\n") + "\n");
  const header = `[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: Clean,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,0,0,3,1,0,2,72,72,42,1\n\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n`;
  fs.writeFileSync(path.join(out, `${base}_english_clean.ass`), header + en.map((x) => `Dialogue: 0,${assTime(x.start)},${assTime(x.end)},Clean,,0,0,0,,${balance(x.text).replace("\n", "\\N")}`).join("\n") + "\n");
  for (const name of fs.readdirSync(out).filter((name) => name.startsWith(`${base}_`) && !name.endsWith(".mp4"))) fs.copyFileSync(path.join(out, name), path.join(archive, name));
  console.log(`${id}|${duration.toFixed(3)}|${en.length}|${out}`);
}
