const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const jobs = [
  ["v9-onN7EsWo", "hospice-myths", "YTDown_YouTube_Media_v9-onN7EsWo_001_1080p"],
  ["XeGjlf7fILA", "after-death-hospice", "YTDown_YouTube_Media_XeGjlf7fILA_001_1080p"],
  ["SNGsCjicC8E", "after-death-non-hospice", "YTDown_YouTube_Media_SNGsCjicC8E_001_1080p"],
];

function seconds(value) {
  const [h, m, rest] = value.replace(",", ".").split(":");
  return Number(h) * 3600 + Number(m) * 60 + Number(rest);
}

function srtTime(value) {
  const ms = Math.max(0, Math.round(value * 1000));
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms % 1000).padStart(3, "0")}`;
}

function assTime(value) {
  return srtTime(value).replace(/^0/, "").replace(",", ".").slice(0, -1);
}

function parseSrt(file) {
  return fs.readFileSync(file, "utf8").replace(/\r/g, "").trim().split(/\n{2,}/).flatMap((block) => {
    const lines = block.split("\n");
    if (lines.length < 3 || !lines[1].includes("-->")) return [];
    const [start, end] = lines[1].split("-->").map((v) => v.trim());
    return [{ start: seconds(start), end: seconds(end), text: lines.slice(2).join(" ").replace(/\s+/g, " ").trim() }];
  });
}

function newSuffix(previous, current) {
  const a = previous.split(/\s+/);
  const b = current.split(/\s+/);
  for (let n = Math.min(a.length, b.length); n >= 1; n--) {
    if (a.slice(-n).join(" ") === b.slice(0, n).join(" ")) return b.slice(n);
  }
  return b;
}

function rebuild(rows) {
  const additions = [];
  let previous = "";
  for (const row of rows) {
    let words = newSuffix(previous, row.text);
    if (!words.length) {
      previous = row.text;
      continue;
    }
    additions.push({ start: row.start, end: row.end, words });
    previous = row.text;
  }
  const groups = [];
  let group = null;
  for (const item of additions) {
    const text = item.words.join(" ");
    if (!group) group = { start: item.start, end: item.end, text };
    else if (item.end - group.start <= 15 && `${group.text} ${text}`.length <= 240) {
      group.end = item.end;
      group.text += ` ${text}`;
    } else {
      groups.push(group);
      group = { start: item.start, end: item.end, text };
    }
    if (/[.?!。？！]$/.test(group.text) && group.text.length >= 35) {
      groups.push(group);
      group = null;
    }
  }
  if (group) groups.push(group);
  return groups;
}

async function translate(text) {
  const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=ko&tl=en&dt=t&q=${encodeURIComponent(text)}`;
  for (let attempt = 0; attempt < 4; attempt++) {
    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      return data[0].map((part) => part[0]).join("").replace(/\s+/g, " ").trim();
    }
    await new Promise((resolve) => setTimeout(resolve, 1000 * 2 ** attempt));
  }
  throw new Error(`Translation failed: ${text}`);
}

function splitEnglish(text) {
  const words = text.split(/\s+/);
  const pieces = [];
  let current = [];
  for (const word of words) {
    if (current.length && [...current, word].join(" ").length > 82) {
      let cut = current.length;
      for (let i = current.length - 1; i >= Math.floor(current.length / 2); i--) {
        if (/[,:;.!?]$/.test(current[i - 1])) {
          cut = i;
          break;
        }
      }
      pieces.push(current.slice(0, cut).join(" "));
      current = [...current.slice(cut), word];
    } else {
      current.push(word);
    }
  }
  if (current.length) pieces.push(current.join(" "));
  return pieces;
}

function balance(text, width = 45) {
  const words = text.split(/\s+/);
  if (text.length <= width) return text;
  let best = 1;
  let score = Infinity;
  for (let i = 1; i < words.length; i++) {
    const left = words.slice(0, i).join(" ");
    const right = words.slice(i).join(" ");
    const next = Math.max(left.length, right.length) + Math.abs(left.length - right.length) * 0.2;
    if (next < score) [best, score] = [i, next];
  }
  return `${words.slice(0, best).join(" ")}\n${words.slice(best).join(" ")}`;
}

function cleanEnglish(text) {
  const replacements = [
    [/Eminent Peace Care/gi, "Eminent Hospice Care"],
    [/Eminent Speech Care/gi, "Eminent Hospice Care"],
    [/\bhostess\b/gi, "hospice"],
    [/\bHospice contacted\b/gi, "hospice is started"],
    [/Will I return soon if I go to hospice\?/gi, "Will I die soon if I start hospice care?"],
    [/Yes\. To conclude, it is not true\. The hospice is the cause\./gi, "No. Hospice care does not cause a patient to die sooner."],
    [/If the patient accepts it,/gi, "If the patient passes away,"],
    [/If the patient approves,/gi, "If the patient passes away,"],
    [/\bAdce Tiv\b/gi, "advance directive"],
    [/\bFolst\b|\bHolst\b|\bPolest\b/gi, "POLST"],
    [/\bcardiopulmonary aquatic therapy\b/gi, "cardiopulmonary resuscitation"],
    [/\bCounty Corona\b|\bKaoni Corona\b/gi, "County Coroner"],
    [/\bLine One\b/g, "911"],
    [/\bphysician station\b/gi, "funeral home"],
    [/\bdisability company\b|\bdisabled company\b/gi, "funeral home"],
    [/Kaoni Corona/gi, "County Coroner"],
    [/Yangno's hotel/gi, "a nursing facility"],
    [/seasoned hotels/gi, "nursing facilities"],
    [/nursing home hotel/gi, "nursing facility"],
    [/Physician Station/gi, "funeral home"],
    [/\bmakeup company\b/gi, "cremation provider"],
    [/\bmakeup\b/gi, "cremation"],
    [/\u00e2\u20ac\u0153|\u00e2\u20ac\u009c/g, '"'],
    [/\u00e2\u20ac\u009d/g, '"'],
    [/\u00e2\u20ac\u2122/g, "'"],
  ];
  let output = text;
  for (const [pattern, value] of replacements) output = output.replace(pattern, value);
  return output.replace(/\s+/g, " ").trim();
}

function normalizeTimeline(items) {
  const clean = items.filter((item) => item.text.trim()).map((item) => ({ ...item, text: cleanEnglish(item.text) }));
  for (let i = 0; i < clean.length; i++) {
    if (i > 0 && clean[i].start < clean[i - 1].end) clean[i].start = clean[i - 1].end;
    const nextStart = i + 1 < clean.length ? clean[i + 1].start : Infinity;
    clean[i].end = Math.min(clean[i].end, nextStart);
    if (clean[i].end - clean[i].start < 0.8) clean[i].end = clean[i].start + 0.8;
  }
  return clean;
}

async function main() {
  for (const [id, slug, base] of jobs) {
    const sourceDir = path.join(root, "deliverables", "youtube-subtitles", `${id}-${slug}`);
    const outDir = path.join(root, "deliverables", `korean-video-${id}`);
    fs.mkdirSync(outDir, { recursive: true });
    const rows = parseSrt(path.join(sourceDir, "ko-transcript.srt"));
    const groups = rebuild(rows);
    const translated = [];
    for (let i = 0; i < groups.length; i++) {
      const english = await translate(groups[i].text);
      const pieces = splitEnglish(english);
      const duration = groups[i].end - groups[i].start;
      let cursor = groups[i].start;
      for (let p = 0; p < pieces.length; p++) {
        const end = p === pieces.length - 1 ? groups[i].end : cursor + duration * pieces[p].split(/\s+/).length / english.split(/\s+/).length;
        translated.push({ start: cursor, end, text: pieces[p] });
        cursor = end;
      }
      process.stdout.write(`\r${id}: ${i + 1}/${groups.length}`);
    }
    console.log();
    const finalTranslated = normalizeTimeline(translated);
    fs.copyFileSync(path.join(sourceDir, "ko-transcript.txt"), path.join(outDir, `${base}_korean_transcript.txt`));
    fs.copyFileSync(path.join(sourceDir, "ko-transcript.srt"), path.join(outDir, `${base}_korean_transcript.srt`));
    fs.writeFileSync(path.join(outDir, `${base}_korean_transcript.json`), JSON.stringify(groups, null, 2));
    fs.writeFileSync(path.join(outDir, `${base}_english_translation.json`), JSON.stringify(finalTranslated, null, 2));
    fs.writeFileSync(path.join(outDir, `${base}_english_translation.txt`), finalTranslated.map((x) => `[${srtTime(x.start)} --> ${srtTime(x.end)}] ${x.text}`).join("\n"));
    fs.writeFileSync(path.join(outDir, `${base}_english.srt`), finalTranslated.map((x, i) => `${i + 1}\n${srtTime(x.start)} --> ${srtTime(x.end)}\n${balance(x.text)}`).join("\n\n") + "\n");
    const header = `[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,24,&H00FFFFFF,&H000000FF,&H90000000,&HC0000000,-1,0,0,0,100,100,0,0,3,2,0,2,38,38,42,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n`;
    const events = finalTranslated.map((x) => `Dialogue: 0,${assTime(x.start)},${assTime(x.end)},Default,,0,0,0,,${balance(x.text).replace("\n", "\\N")}`).join("\n");
    fs.writeFileSync(path.join(outDir, `${base}_english_clean.ass`), header + events + "\n");
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
