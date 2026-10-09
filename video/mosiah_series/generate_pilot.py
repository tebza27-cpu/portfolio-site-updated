from __future__ import annotations

import argparse
import base64
import json
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "rendered" / "pilot-abinadi"
WIDTH, HEIGHT, FPS = 1280, 720, 12
VOICE_NARRATOR = "Microsoft Zira Desktop"
VOICE_CHARACTER = "Microsoft David Desktop"


LINES = (
    {"speaker": "Narrator", "voice": VOICE_NARRATOR, "scene": "city", "visible": ["Abinadi"], "text": "During King Noah's reign, Abinadi came among the people with a warning."},
    {"speaker": "Abinadi", "voice": VOICE_CHARACTER, "scene": "city", "visible": ["Abinadi"], "text": "The Lord sent me to warn you. Repent, or your people will be brought into bondage."},
    {"speaker": "Narrator", "voice": VOICE_NARRATOR, "scene": "court", "visible": ["Abinadi", "Noah", "Priest", "Alma"], "text": "Noah rejected the warning. Abinadi escaped, then returned in disguise."},
    {"speaker": "Noah", "voice": VOICE_CHARACTER, "scene": "court", "visible": ["Abinadi", "Noah", "Priest", "Alma"], "text": "Bring this man before me. Let the priests question him."},
    {"speaker": "Priest", "voice": VOICE_CHARACTER, "scene": "court", "visible": ["Abinadi", "Noah", "Priest", "Alma"], "text": "We teach the law. Explain the words of the prophet Isaiah."},
    {"speaker": "Abinadi", "voice": VOICE_CHARACTER, "scene": "court", "visible": ["Abinadi", "Noah", "Priest", "Alma"], "text": "You teach the law, but your lives deny what it teaches. The law cannot save without redemption through Christ."},
    {"speaker": "Noah", "voice": VOICE_CHARACTER, "scene": "court", "visible": ["Abinadi", "Noah", "Priest", "Alma"], "text": "You speak against me and my priests. What defense have you?"},
    {"speaker": "Abinadi", "voice": VOICE_CHARACTER, "scene": "court", "visible": ["Abinadi", "Noah", "Priest", "Alma"], "text": "I will answer what the Lord commands. I will not deny my testimony."},
    {"speaker": "Narrator", "voice": VOICE_NARRATOR, "scene": "study", "visible": ["Alma"], "text": "Alma believed Abinadi. He wrote the words and escaped the king's servants."},
    {"speaker": "Alma", "voice": VOICE_CHARACTER, "scene": "study", "visible": ["Alma"], "text": "I have heard the truth. I must preserve his words."},
    {"speaker": "Narrator", "voice": VOICE_NARRATOR, "scene": "study", "visible": ["Alma"], "text": "Abinadi was condemned, but his testimony lived on through Alma and the people he later taught."},
)


CHARACTERS = {
    "Abinadi": {"robe": "#9b5945", "trim": "#d7aa64", "skin": "#9b624b", "hair": "#382d29", "kind": "beard"},
    "Noah": {"robe": "#2e5b50", "trim": "#e2b65f", "skin": "#bf8966", "hair": "#47332a", "kind": "crown"},
    "Priest": {"robe": "#d8c895", "trim": "#8d9a78", "skin": "#a96e51", "hair": "#44352e", "kind": "headwrap"},
    "Alma": {"robe": "#496b77", "trim": "#d8bd85", "skin": "#b67a59", "hair": "#382e2a", "kind": "hair"},
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = Path("C:/Windows/Fonts") / ("georgiab.ttf" if bold else "georgia.ttf")
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def draw_city() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#dfab79")
    d = ImageDraw.Draw(image)
    d.ellipse((870, 80, 1030, 240), fill="#f0d493")
    d.rectangle((0, 0, WIDTH, 380), fill="#e7c49a")
    d.polygon([(0, 305), (240, 210), (430, 305), (710, 185), (920, 300), (1280, 205), (1280, 455), (0, 455)], fill="#9b6e59")
    d.rectangle((0, 365, WIDTH, HEIGHT), fill="#b9956d")
    for x, width in ((65, 190), (310, 210), (730, 220), (1010, 210)):
        d.rectangle((x, 260, x + width, 440), fill="#d0a77d", outline="#725449", width=5)
        d.polygon([(x - 15, 265), (x + width // 2, 185), (x + width + 15, 265)], fill="#805c4d")
        d.rectangle((x + 65, 335, x + 118, 440), fill="#735247")
        d.rectangle((x + width - 44, 290, x + width - 25, 330), fill="#f0d493")
    d.polygon([(0, 625), (240, 530), (470, 630), (770, 520), (1040, 630), (1280, 535), (1280, 720), (0, 720)], fill="#9e805f")
    return image


def draw_court() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#294947")
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, WIDTH, HEIGHT), fill="#315754")
    d.rectangle((0, 0, WIDTH, 115), fill="#23413f")
    for x in range(0, WIDTH, 80):
        d.line((x, 115, x, HEIGHT), fill="#416965", width=2)
    d.rectangle((0, 430, WIDTH, HEIGHT), fill="#b38660")
    d.polygon([(0, 450), (640, 380), (1280, 450), (1280, 720), (0, 720)], fill="#98734f")
    d.ellipse((270, 458, 1010, 850), fill="#bd976a", outline="#e1c38f", width=8)
    for x in (68, 1150):
        d.rectangle((x, 92, x + 70, 480), fill="#dbc69b")
        d.rectangle((x - 18, 80, x + 88, 108), fill="#ad9168")
        d.rectangle((x - 18, 470, x + 88, 498), fill="#ad9168")
    d.rectangle((925, 235, 1150, 500), fill="#68483b", outline="#d2a861", width=8)
    d.polygon([(905, 240), (1037, 145), (1170, 240)], fill="#936144", outline="#d2a861")
    d.rectangle((960, 300, 1115, 470), fill="#815b43")
    d.rounded_rectangle((465, 105, 815, 345), radius=170, fill="#deb987", outline="#9e7757", width=8)
    d.rectangle((475, 245, 805, 350), fill="#315754")
    for x in (180, 1120):
        d.ellipse((x - 24, 190, x + 24, 245), fill="#f2c66e")
        d.polygon([(x - 30, 225), (x, 315), (x + 30, 225)], fill="#d08249")
    return image


def draw_study() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#31514b")
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, WIDTH, 445), fill="#44685e")
    d.rectangle((65, 80, 390, 405), fill="#d7c39c", outline="#9b805d", width=14)
    d.rectangle((92, 108, 363, 375), fill="#e8bd7d")
    d.line((228, 108, 228, 375), fill="#9b805d", width=8)
    d.line((92, 240, 363, 240), fill="#9b805d", width=8)
    d.ellipse((135, 155, 300, 320), fill="#f0d493")
    d.rectangle((0, 445, WIDTH, HEIGHT), fill="#8b6a4e")
    d.polygon([(300, 500), (1015, 500), (1115, 610), (200, 610)], fill="#805539")
    d.polygon([(200, 610), (1115, 610), (1085, 655), (228, 655)], fill="#694832")
    d.rectangle((440, 420, 730, 500), fill="#e4d3af", outline="#72563e", width=5)
    for y in (440, 458, 476):
        d.line((470, y, 690, y + 5), fill="#795d47", width=3)
    d.polygon([(850, 475), (870, 410), (890, 475)], fill="#dda85c")
    d.ellipse((861, 387, 879, 420), fill="#f5d482")
    d.ellipse((824, 360, 916, 452), fill="#edc477", outline="#e5d3a4", width=5)
    return image


BACKGROUNDS = {"city": draw_city(), "court": draw_court(), "study": draw_study()}
POSITIONS = {
    "city": {"Abinadi": 630},
    "court": {"Abinadi": 240, "Priest": 630, "Alma": 790, "Noah": 1040},
    "study": {"Alma": 635},
}


def draw_person(draw: ImageDraw.ImageDraw, role: str, x: int, baseline: int, speaking: bool, phase: float) -> None:
    traits = CHARACTERS[role]
    bob = math.sin(phase * math.tau) * (2 if speaking else 1)
    y = baseline + bob
    robe, trim, skin, hair = traits["robe"], traits["trim"], traits["skin"], traits["hair"]

    if speaking:
        arm_y = y - (118 if math.sin(phase * math.tau) > 0 else 96)
        draw.line((x - 34, y - 140, x - 76, arm_y), fill=skin, width=21)
        draw.ellipse((x - 88, arm_y - 13, x - 64, arm_y + 13), fill=skin)
    else:
        draw.line((x - 35, y - 135, x - 42, y - 32), fill=skin, width=20)
    draw.line((x + 34, y - 135, x + 48, y - 36), fill=skin, width=20)
    draw.polygon([(x - 38, y - 146), (x + 38, y - 146), (x + 54, y - 18), (x + 38, y), (x - 40, y), (x - 55, y - 18)], fill=robe)
    draw.polygon([(x - 38, y - 146), (x + 38, y - 146), (x + 26, y - 119), (x, y - 103), (x - 26, y - 119)], fill=trim)
    draw.line((x, y - 104, x, y - 2), fill=trim, width=5)
    draw.ellipse((x - 38, y - 250, x + 38, y - 166), fill=skin)
    draw.ellipse((x - 41, y - 222, x - 19, y - 202), fill="#f0d0b5")
    draw.ellipse((x + 19, y - 222, x + 41, y - 202), fill="#f0d0b5")
    draw.ellipse((x - 15, y - 219, x - 7, y - 211), fill="#352d28")
    draw.ellipse((x + 7, y - 219, x + 15, y - 211), fill="#352d28")
    draw.line((x, y - 211, x - 3, y - 197, x + 2, y - 195), fill="#76513e", width=3)
    if speaking and math.sin(phase * math.tau * 2) > -0.2:
        draw.ellipse((x - 9, y - 190, x + 9, y - 179), fill="#552e2b")
        draw.arc((x - 7, y - 188, x + 7, y - 180), 10, 170, fill="#d87869", width=2)
    else:
        draw.line((x - 9, y - 184, x + 9, y - 184), fill="#633a33", width=3)

    kind = traits["kind"]
    if kind == "beard":
        draw.polygon([(x - 27, y - 192), (x + 27, y - 192), (x + 19, y - 167), (x, y - 151), (x - 19, y - 167)], fill=hair)
        draw.arc((x - 43, y - 254, x + 43, y - 178), 185, 355, fill=hair, width=11)
        draw.polygon([(x - 37, y - 238), (x + 37, y - 238), (x + 30, y - 250), (x - 28, y - 250)], fill=trim)
    elif kind == "crown":
        draw.arc((x - 39, y - 257, x + 39, y - 179), 185, 355, fill=hair, width=12)
        draw.polygon([(x - 40, y - 246), (x - 31, y - 278), (x - 8, y - 253), (x + 5, y - 280), (x + 22, y - 250), (x + 39, y - 271), (x + 40, y - 239)], fill=trim, outline="#765638")
        for dx in (-22, 0, 22):
            draw.ellipse((x + dx - 4, y - 263, x + dx + 4, y - 255), fill="#a64d42")
    elif kind == "headwrap":
        draw.arc((x - 43, y - 257, x + 43, y - 178), 185, 355, fill=hair, width=10)
        draw.rounded_rectangle((x - 40, y - 258, x + 40, y - 237), radius=9, fill=trim)
        draw.line((x - 30, y - 248, x + 28, y - 248), fill="#f0dfae", width=4)
    else:
        draw.arc((x - 41, y - 257, x + 41, y - 176), 185, 355, fill=hair, width=13)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, width: int) -> list[str]:
    result: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=face)[2] > width:
            result.append(current)
            current = word
        else:
            current = candidate
    if current:
        result.append(current)
    return result


def make_frame(line: dict, frame_index: int, line_duration: float) -> Image.Image:
    image = BACKGROUNDS[line["scene"]].copy()
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, WIDTH, 44), fill="#1d3634")
    d.text((34, 10), "MOSIAH 11-17  |  AN ACTED-OUT CARTOON ADAPTATION", font=font(17, True), fill="#e9c77e")
    phase = frame_index / FPS

    if line["speaker"] in CHARACTERS:
        actor_x = POSITIONS[line["scene"]][line["speaker"]]
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((actor_x - 112, 290, actor_x + 112, 565), fill=(242, 198, 110, 48))
        image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")
        d = ImageDraw.Draw(image)

    for role in line["visible"]:
        x = POSITIONS[line["scene"]][role]
        draw_person(d, role, x, 558, role == line["speaker"], phase + list(CHARACTERS).index(role) * 0.13)

    panel_top = 556
    d.rectangle((0, panel_top, WIDTH, HEIGHT), fill="#183331")
    d.rectangle((0, panel_top, 12, HEIGHT), fill="#d29c58")
    d.text((42, panel_top + 16), line["speaker"].upper(), font=font(17, True), fill="#e7b865")
    caption_font = font(25)
    caption_lines = wrap(d, line["text"], caption_font, WIDTH - 86)
    line_height = 32
    caption_top = panel_top + 43
    for index, caption in enumerate(caption_lines[:3]):
        d.text((42, caption_top + index * line_height), caption, font=caption_font, fill="#f4efe1")
    return image


def synthesize_audio(folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    jobs = []
    for index, line in enumerate(LINES):
        jobs.append({
            "path": str(folder / f"line-{index:02}.wav"),
            "text": line["text"],
            "voice": line["voice"],
        })
    payload = base64.b64encode(json.dumps(jobs).encode("utf-8")).decode("ascii")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        f"$jobs = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{payload}')) | ConvertFrom-Json; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "foreach ($job in $jobs) { $s.SelectVoice($job.voice); $s.SetOutputToWaveFile($job.path); $s.Speak($job.text) }; "
        "$s.Dispose()"
    )
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded], check=True)
    return [Path(job["path"]) for job in jobs]


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def concatenate_audio(ffmpeg: str, sources: list[Path], destination: Path, temp: Path) -> None:
    listing = temp / "audio-list.txt"
    entries = [f"file '{path.as_posix()}'" for path in sources]
    listing.write_text("\n".join(entries), encoding="ascii")
    subprocess.run([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(listing), "-c:a", "pcm_s16le", str(destination),
    ], check=True)


def render_video(ffmpeg: str, audio: Path, durations: list[float], destination: Path) -> None:
    command = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}",
        "-framerate", str(FPS), "-i", "pipe:0", "-i", str(audio),
        "-vf", "fps=24", "-map", "0:v:0", "-map", "1:a:0", "-shortest",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(destination),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for line, line_duration in zip(LINES, durations):
            frame_count = max(1, math.ceil(line_duration * FPS))
            for frame_index in range(frame_count):
                frame = make_frame(line, frame_index, line_duration)
                process.stdin.write(frame.tobytes())
    except BrokenPipeError:
        process.stdin.close()
        raise RuntimeError("FFmpeg stopped while receiving cartoon frames.")
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("FFmpeg could not encode the cartoon pilot.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an acted-out 2D cartoon pilot from Mosiah 11-17.")
    parser.add_argument("--check", action="store_true", help="Check video encoding and installed narration voices.")
    args = parser.parse_args()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if args.check:
        result = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True, text=True, check=True)
        if "libx264" not in result.stdout:
            raise SystemExit("The bundled FFmpeg is missing libx264.")
        print(f"FFmpeg ready: {ffmpeg}")
        print(f"Narration voices: {VOICE_NARRATOR}, {VOICE_CHARACTER}")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mosiah-cartoon-") as temp_dir:
        temp = Path(temp_dir)
        segments = synthesize_audio(temp / "lines")
        narration = OUT / "narration.wav"
        concatenate_audio(ffmpeg, segments, narration, temp)
        durations = [wav_duration(segment) for segment in segments]
        poster = make_frame(LINES[0], 0, durations[0])
        poster.save(OUT / "scene-01.png")
        render_video(ffmpeg, narration, durations, OUT / "pilot-abinadi.mp4")
    print(f"Finished: {OUT / 'pilot-abinadi.mp4'}")


if __name__ == "__main__":
    main()