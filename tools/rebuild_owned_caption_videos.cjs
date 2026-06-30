const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const root = path.resolve(__dirname, "..");
const jobs = [
  ["9g98EDnOAUI", "suction-machine"],
  ["qWl3XdJ4rck", "hospice-aide-perspective"],
  ["jsPCywsMe5Y", "hospice-nurse-perspective"],
];

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { stdio: "inherit", ...options });
  if (result.status !== 0) throw new Error(`${command} failed (${result.status})`);
}

function capture(command, args) {
  const result = spawnSync(command, args, { encoding: "utf8" });
  if (result.status !== 0) throw new Error(result.stderr || `${command} failed`);
  return result.stdout;
}

function seconds(stamp) {
  const [h, m, rest] = stamp.replace(",", ".").split(":");
  return Number(h) * 3600 + Number(m) * 60 + Number(rest);
}

function assStamp(value) {
  const centis = Math.round(value * 100);
  const h = Math.floor(centis / 360000);
  const m = Math.floor((centis % 360000) / 6000);
  const s = Math.floor((centis % 6000) / 100);
  const cs = centis % 100;
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(cs).padStart(2, "0")}`;
}

function parseSrt(file) {
  return fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "").trim()
    .split(/\r?\n\s*\r?\n/)
    .map((block, index) => {
      const lines = block.split(/\r?\n/);
      const match = lines[1]?.match(/^(.+?)\s+-->\s+(.+)$/);
      if (!match || lines.length < 3) throw new Error(`${file}: invalid cue ${index + 1}`);
      return {
        startText: match[1],
        endText: match[2],
        start: seconds(match[1]),
        end: seconds(match[2]),
        lines: lines.slice(2).map((line) =>
          line.replace(/\b(?:Kim Jung Ah|Kim Jung-ah|Kim Jeong-ah)\b/g, "Kim Jeong Ah")),
      };
    });
}

function canonicalize(cues, file) {
  let previousEnd = 0;
  return cues.map((cue, index) => {
    if (!(cue.start >= previousEnd && cue.end > cue.start)) {
      throw new Error(`${file}: overlap or invalid timing at cue ${index + 1}`);
    }
    previousEnd = cue.end;
    if (cue.lines.length > 2) {
      const words = cue.lines.join(" ").split(/\s+/);
      let best = 1;
      let score = Infinity;
      for (let i = 1; i < words.length; i++) {
        const scoreAt = Math.abs(words.slice(0, i).join(" ").length - words.slice(i).join(" ").length);
        if (scoreAt < score) [best, score] = [i, scoreAt];
      }
      cue.lines = [words.slice(0, best).join(" "), words.slice(best).join(" ")];
    }
    if (cue.lines.length > 2 || cue.lines.some((line) => !line.trim())) {
      throw new Error(`${file}: non-canonical text at cue ${index + 1}`);
    }
    return cue;
  });
}

function writeSrt(file, cues) {
  const body = cues.map((cue, i) =>
    `${i + 1}\n${cue.startText} --> ${cue.endText}\n${cue.lines.join("\n")}`).join("\n\n");
  fs.writeFileSync(file, `${body}\n`, "utf8");
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
Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`;
  const events = cues.map((cue) =>
    `Dialogue: 0,${assStamp(cue.start)},${assStamp(cue.end)},Default,,0,0,0,,${cue.lines.join("\\N")}`);
  fs.writeFileSync(file, `${header}${events.join("\n")}\n`, "utf8");
}

for (const [id, slug] of jobs) {
  const folder = path.join(root, "deliverables", `korean-video-${id}`);
  const files = fs.readdirSync(folder);
  const sourceSrt = path.join(folder, files.find((name) => name.endsWith("_english.srt")));
  const compressed = path.join(folder, files.find((name) => name.endsWith("_compressed.mp4")));
  const base = path.basename(sourceSrt, "_english.srt");
  const canonicalSrt = path.join(folder, `${base}_english.srt`);
  const ass = path.join(folder, `${base}_english_clean.ass`);
  const master = path.join(folder, `${base}_english_captioned.mp4`);
  const cues = canonicalize(parseSrt(sourceSrt), sourceSrt);

  writeSrt(canonicalSrt, cues);
  writeAss(ass, cues);

  const escapedAss = ass.replace(/\\/g, "/").replace(":", "\\:");
  run("ffmpeg", ["-y", "-i", compressed, "-vf", `ass='${escapedAss}'`,
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", master]);

  const reference = path.join(root, "deliverables", "subtitle-reference", `${id}-${slug}`);
  const youtube = path.join(root, "deliverables", "youtube-subtitles", `${id}-${slug}`, "en-subtitles.srt");
  fs.copyFileSync(canonicalSrt, path.join(reference, path.basename(canonicalSrt)));
  fs.copyFileSync(ass, path.join(reference, path.basename(ass)));
  fs.copyFileSync(canonicalSrt, youtube);

  const publicFile = path.join(root, "public", "videos", `${slug}.mp4`);
  let crf = 23;
  do {
    run("ffmpeg", ["-y", "-i", master, "-c:v", "libx264", "-preset", "medium", "-crf", String(crf),
      "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", publicFile]);
    crf += 2;
  } while (fs.statSync(publicFile).size >= 23.5 * 1024 * 1024 && crf <= 35);
  if (fs.statSync(publicFile).size >= 23.5 * 1024 * 1024) throw new Error(`${publicFile}: size limit exceeded`);

  const media = JSON.parse(capture("ffprobe", ["-v", "error", "-show_entries",
    "format=duration,size:stream=codec_type,codec_name,width,height", "-of", "json", publicFile]));
  const sourceDuration = Number(JSON.parse(capture("ffprobe", ["-v", "error", "-show_entries",
    "format=duration", "-of", "json", compressed])).format.duration);
  const duration = Number(media.format.duration);
  const video = media.streams.find((stream) => stream.codec_type === "video");
  const audio = media.streams.find((stream) => stream.codec_type === "audio");
  if (video?.codec_name !== "h264" || audio?.codec_name !== "aac") throw new Error(`${publicFile}: codecs`);
  if (Math.abs(duration - sourceDuration) > 0.1 || !audio) throw new Error(`${publicFile}: duration/audio`);
  if (cues.some((cue) => cue.end > duration + 0.05)) throw new Error(`${publicFile}: cue past duration`);

  // Arial 24, alignment 2, and MarginV 52 place even two-line boxes well below y=504.
  const topY = 720 - 52 - (cues.some((cue) => cue.lines.length === 2) ? 2 : 1) * 29 - 4;
  if (topY < 504) throw new Error(`${publicFile}: subtitle placement y=${topY}`);
  console.log(JSON.stringify({ id, cues: cues.length, y: topY, duration, audio: audio.codec_name,
    bytes: Number(media.format.size) }));
}
