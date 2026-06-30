const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const root = path.resolve(__dirname, "..");
const jobs = [
  ["42r5f9uf-0U", "polst", "42r5f9uf-0U-polst", 720],
  ["K0bgtz2gV40", "hospice-core-services", "K0bgtz2gV40-hospice-core-services", 720],
  ["v9-onN7EsWo", "hospice-myths", "v9-onN7EsWo-hospice-myths", 720],
  ["XeGjlf7fILA", "after-death-hospice", "XeGjlf7fILA-after-death-hospice", 720],
  ["SNGsCjicC8E", "after-death-non-hospice-polst", "SNGsCjicC8E-after-death-non-hospice", 720],
  ["3mgBE6CaI4I", "end-of-life-timing", "3mgBE6CaI4I-end-of-life-timing", 720],
  ["edmwae3Iglk", "nebulizer", "edmwae3Iglk-nebulizer", 720],
  ["Vq5rIpelzhk", "oxygen-concentrator", "Vq5rIpelzhk-oxygen-concentrator", 720],
  ["9g98EDnOAUI", "suction-machine", "9g98EDnOAUI-suction-machine", 720],
  ["qWl3XdJ4rck", "hospice-aide-perspective", "qWl3XdJ4rck-hospice-aide-perspective", 720],
  ["jsPCywsMe5Y", "hospice-nurse-perspective", "jsPCywsMe5Y-hospice-nurse-perspective", 720],
  ["xnI28GlZwZI", "american-hospice-nurse", "xnI28GlZwZI-american-hospice-nurse", 360],
  ["Rv1Cbnb4QDA", "emergency-medications", "Rv1Cbnb4QDA-emergency-medications", 720],
  ["2Ci1inVJrrc", "chaplain-perspective", "2Ci1inVJrrc-chaplain-perspective", 720],
];

const prohibitedName = /Kim (?:Jung Ah|Jung-ah|Jeong-ah)/i;

function srtSeconds(value) {
  const match = value.match(/^(\d+):(\d+):(\d+),(\d+)$/);
  if (!match) throw new Error(`Invalid SRT time: ${value}`);
  return +match[1] * 3600 + +match[2] * 60 + +match[3] + +match[4] / 1000;
}

function parseSrt(file) {
  return fs.readFileSync(file, "utf8").trim().split(/\r?\n\r?\n/).map((block) => {
    const lines = block.split(/\r?\n/);
    const times = lines[1]?.match(/^(.+?) --> (.+)$/);
    if (!times) throw new Error(`Invalid SRT block in ${file}`);
    return {
      start: srtSeconds(times[1]),
      end: srtSeconds(times[2]),
      lines: lines.slice(2),
      text: lines.slice(2).join(" "),
    };
  });
}

function findOne(directory, suffix) {
  const matches = fs.readdirSync(directory)
    .filter((name) => name.toLowerCase().endsWith(suffix.toLowerCase()))
    .map((name) => path.join(directory, name));
  if (matches.length !== 1) {
    throw new Error(`Expected one *${suffix} in ${directory}; found ${matches.length}`);
  }
  return matches[0];
}

function findCanonicalSrt(directory) {
  const names = fs.readdirSync(directory);
  const plain = names.find((name) => name.toLowerCase().endsWith("_english.srt"));
  const clean = names.find((name) => name.toLowerCase().endsWith("_english_clean.srt"));
  const selected = plain || clean;
  if (!selected) throw new Error(`Missing canonical English SRT in ${directory}`);
  return path.join(directory, selected);
}

function ffprobe(file) {
  return JSON.parse(execFileSync("ffprobe", [
    "-v", "error",
    "-show_entries", "format=duration,size",
    "-show_entries", "stream=codec_type,codec_name,width,height",
    "-of", "json",
    file,
  ], { encoding: "utf8" }));
}

const report = [];
let failed = false;

for (const [id, slug, topic, height] of jobs) {
  const errors = [];
  const deliverable = path.join(root, "deliverables", `korean-video-${id}`);
  const archive = path.join(root, "deliverables", "subtitle-reference", topic);
  const youtubeSrt = path.join(root, "deliverables", "youtube-subtitles", topic, "en-subtitles.srt");
  const websiteMp4 = path.join(root, "public", "videos", `${slug}.mp4`);
  const srt = findCanonicalSrt(deliverable);
  const ass = findOne(deliverable, "_english_clean.ass");
  const captioned = findOne(deliverable, "_english_captioned.mp4");
  const cues = parseSrt(srt);
  const assText = fs.readFileSync(ass, "utf8");

  for (let index = 0; index < cues.length; index++) {
    const cue = cues[index];
    if (cue.lines.length > 2) errors.push(`cue ${index + 1} has ${cue.lines.length} lines`);
    if (cue.end <= cue.start) errors.push(`cue ${index + 1} has non-positive duration`);
    if (index && cue.start < cues[index - 1].end - 0.0005) {
      errors.push(`cue ${index + 1} overlaps cue ${index}`);
    }
    if (prohibitedName.test(cue.text)) errors.push(`cue ${index + 1} has prohibited name spelling`);
  }

  const expectedStyle = height === 360
    ? /Style: Default,Arial,13,&H00FFFFFF,[^,]*,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,1,0,2,60,60,26,1/
    : /Style: Default,Arial,24,&H00FFFFFF,[^,]*,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1/;
  if (!expectedStyle.test(assText)) errors.push("ASS style does not match canonical standard");
  if (!/WrapStyle: 2/.test(assText)) errors.push("ASS WrapStyle is not 2");
  if (prohibitedName.test(assText)) errors.push("ASS has prohibited name spelling");

  for (const required of [archive, youtubeSrt, websiteMp4, captioned]) {
    if (!fs.existsSync(required)) errors.push(`missing ${required}`);
  }

  if (fs.existsSync(youtubeSrt)) {
    const archived = parseSrt(youtubeSrt);
    archived.forEach((cue, index) => {
      if (cue.lines.length > 2) errors.push(`archived cue ${index + 1} has >2 lines`);
      if (index && cue.start < archived[index - 1].end - 0.0005) {
        errors.push(`archived cue ${index + 1} overlaps`);
      }
    });
  }

  if (fs.existsSync(websiteMp4)) {
    const media = ffprobe(websiteMp4);
    const video = media.streams.find((stream) => stream.codec_type === "video");
    const audio = media.streams.find((stream) => stream.codec_type === "audio");
    const expectedWidth = height === 360 ? 640 : 1280;
    if (video?.codec_name !== "h264" || audio?.codec_name !== "aac") errors.push("website codecs are not H.264/AAC");
    if (video?.width !== expectedWidth || video?.height !== height) errors.push("website resolution is incorrect");
    if (+media.format.size > 23.5 * 1024 * 1024) errors.push("website MP4 exceeds 23.5 MiB");
  }

  if (errors.length) failed = true;
  report.push({ id, slug, cues: cues.length, height, errors });
}

const reportPath = path.join(root, "deliverables", "caption-standard-verification.json");
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify(report, null, 2));
if (failed) process.exitCode = 1;
