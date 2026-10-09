from __future__ import annotations

import argparse
import base64
import math
import random
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).parent / "rendered"
WIDTH, HEIGHT, ART_WIDTH, FPS = 1280, 720, 720, 24
VOICE_NAME = "Microsoft David Desktop"


@dataclass(frozen=True)
class Scene:
    title: str
    text: str
    reference: str
    motif: str


@dataclass(frozen=True)
class Episode:
    slug: str
    title: str
    chapters: str
    scenes: tuple[Scene, ...]


EPISODES = (
    Episode("01-king-benjamin", "A KING WHO SERVED", "MOSIAH 1-6", (
        Scene("Records carried forward", "As King Benjamin neared the end of his reign, he taught his sons to preserve their language, their history, and the records of their people. He entrusted the sacred records and other treasured objects to Mosiah, preparing him to lead. In Mosiah, memory is more than the past: it is a responsibility passed from one generation to the next.", "Mosiah 1", "records"),
        Scene("A gathering at the temple", "Benjamin's people gathered to hear their king. He reminded them that leadership meant service, not privilege. He had worked with his own hands and had not placed heavy demands on the people. He urged them to care for one another, especially those who were poor or in need, and to remember the goodness of God in every part of their lives.", "Mosiah 2-4", "assembly"),
        Scene("A people take a new name", "Benjamin testified of Jesus Christ and invited the people to make a covenant. They described a change within themselves and took upon them the name of Christ. Benjamin recorded their names and appointed teachers to help them remember. His address leaves a simple pattern: receive, remember, and serve. Mosiah then began to reign in Zarahemla.", "Mosiah 3-6", "covenant"),
    )),
    Episode("02-the-prophet-and-the-king", "THE PROPHET AND THE KING", "MOSIAH 7-17", (
        Scene("Ammon finds a separated people", "Years earlier, Zeniff had led a group from Zarahemla south to reclaim the land of Lehi-Nephi. His son Noah later ruled there, while a smaller group remained under Noah's son Limhi. When Ammon's search party finally reached them, Limhi's people were living under Lamanite control. Their meeting joined two histories that had unfolded far apart.", "Mosiah 7-10", "journey"),
        Scene("Abinadi speaks before Noah", "Before Ammon arrived, the prophet Abinadi had warned Noah's court that injustice and pride would bring suffering. He returned in disguise, was recognized, and was brought before the king. There he challenged the priests to understand the teachings they claimed to uphold. The court could silence a messenger, but it could not make his warning disappear.", "Mosiah 11-13", "palace"),
        Scene("A testimony remembered", "Abinadi taught from scripture and testified that redemption would come through Jesus Christ. Alma, one of Noah's priests, believed him and began to record his words. The king condemned Abinadi, who died for his testimony. Alma escaped with the record of what he had heard. One listener's decision would shape the lives of many people.", "Mosiah 14-17", "fire"),
    )),
    Episode("03-waters-and-wilderness", "WATERS AND WILDERNESS", "MOSIAH 18-25", (
        Scene("A covenant beside the water", "Away from Noah's court, Alma gathered those who believed Abinadi. At the waters of Mormon, they made covenants, were baptized, and formed a community of faith. When the king's forces discovered them, Alma and his people left by night and traveled into the wilderness. Their new community had begun with a promise to support one another.", "Mosiah 18", "water"),
        Scene("Limhi's people seek a way out", "In Lehi-Nephi, Limhi's people endured repeated hardship and looked for a way to escape bondage. They met Ammon and learned that Zarahemla still stood. With Gideon's careful plan, they left the city and traveled through the wilderness. Their deliverance reunited them with a larger people and brought new records to Mosiah.", "Mosiah 19-22", "escape"),
        Scene("Burdened, yet not abandoned", "Alma's people found safety, built a settlement, and tried to live in peace. Later, a Lamanite force brought them under the rule of Amulon, one of Noah's former priests. Their burdens grew heavy, but they continued to pray and help each other. In time they too escaped and found their way to Zarahemla.", "Mosiah 23-24", "mountain"),
        Scene("Two histories meet", "The people of Limhi and the people of Alma arrived in Zarahemla, where their stories could finally be heard together. Alma taught and baptized, and Mosiah gave him authority to organize the Church. Records, memories, and communities once scattered across the wilderness were gathered into one account of struggle, faith, and deliverance.", "Mosiah 25", "gathering"),
    )),
    Episode("04-a-change-of-heart", "A CHANGE OF HEART", "MOSIAH 26-27", (
        Scene("Questions in the growing church", "As a new generation grew up, some questioned the teachings they had inherited. Alma brought difficult concerns to the Lord and received guidance about repentance, forgiveness, and how the community should respond when people turned away. The account makes room for both accountability and a way back: those who repent can be forgiven and welcomed again.", "Mosiah 26", "assembly"),
        Scene("An unexpected interruption", "Alma the Younger and the sons of Mosiah opposed the Church and tried to lead people away. An angel appeared and called them to stop. Alma could not speak or move for a time; his friends carried him to his father. The interruption became a turning point, forcing him to confront the harm he had caused and the mercy he now needed.", "Mosiah 27", "light"),
        Scene("From opposition to witness", "After days of weakness, Alma stood and spoke of being changed through faith in Christ. The sons of Mosiah also repented. Rather than claim authority over others, they chose to travel and teach among the Lamanites. Their story turns on a choice: a past mistake need not decide what a person does next.", "Mosiah 27", "road"),
    )),
    Episode("05-a-new-kind-of-government", "A NEW KIND OF GOVERNMENT", "MOSIAH 28-29", (
        Scene("A mission and an ancient record", "The sons of Mosiah asked to take their message to the Lamanites. Mosiah let them go, while he used the seer stones to translate an ancient Jaredite record brought from the wilderness. One generation turned outward to teach; another gift opened a window into an older people's rise and fall.", "Mosiah 28", "records"),
        Scene("The people choose judges", "With no heir willing to take the throne, Mosiah proposed a system of judges chosen by the people. He warned that a bad king could draw a whole nation into harm, while laws and shared responsibility could check concentrated power. The people accepted the change, and Alma the Younger became the first chief judge. Mosiah closes as a book of records and leadership passes into a new form.", "Mosiah 29", "judges"),
        Scene("The story continues", "Mosiah follows families, prophets, and communities through separation, reunion, deliverance, and change. Its people carry records so later generations can weigh the choices that shaped them. The book ends with a new government, but not a finished story: its central question remains how a people can live with justice, faith, and care for one another.", "Mosiah 1-29", "horizon"),
    )),
)


PALETTES = {
    "records": ("#dce9dc", "#a1bd9c", "#284f49", "#d78b57"),
    "assembly": ("#d9e9e5", "#91b4a0", "#284b46", "#dda759"),
    "covenant": ("#d5e9e5", "#78b9b1", "#244e4d", "#e2b660"),
    "journey": ("#e7dfc6", "#b4a67b", "#394d3f", "#d58d56"),
    "palace": ("#e8d7bc", "#b98e63", "#4a4037", "#c76f4d"),
    "fire": ("#e4cdb5", "#947d6b", "#453b38", "#df8a43"),
    "water": ("#d9e9e4", "#7aa69a", "#294e48", "#65b5c1"),
    "escape": ("#e7e0c8", "#b9a778", "#3e5140", "#d48b51"),
    "mountain": ("#d7e1d7", "#8eaa96", "#364b43", "#d59c5b"),
    "gathering": ("#dce8dd", "#93b49a", "#284f49", "#d5a658"),
    "light": ("#e9dfc5", "#b1a276", "#39483c", "#e4ad4c"),
    "road": ("#dce7d7", "#98ad83", "#344b3c", "#d98c53"),
    "judges": ("#dde5dc", "#a0aa91", "#34483d", "#d4a654"),
    "horizon": ("#dbe8e2", "#8aa897", "#294a47", "#d7a65c"),
}


def face(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "georgiab.ttf" if bold else "georgia.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def lines_for(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def person(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, color: str) -> None:
    r = 12 * scale
    draw.ellipse((x-r, y-88*scale, x+r, y-64*scale), fill=color)
    draw.polygon([(x-18*scale,y-62*scale),(x+18*scale,y-62*scale),(x+30*scale,y),(x-30*scale,y)], fill=color)


def story_art(motif: str, seed: int) -> Image.Image:
    sky, hill, dark, gold = PALETTES[motif]
    image = Image.new("RGB", (ART_WIDTH, HEIGHT), sky)
    d = ImageDraw.Draw(image)
    d.ellipse((480, 55, 615, 190), fill="#edc878")
    d.polygon([(0,380),(150,195),(315,390),(450,235),(720,430),(720,720),(0,720)], fill=hill)
    d.ellipse((-150,420,460,800), fill="#718e6c")
    d.ellipse((250,420,850,810), fill="#526f59")
    if motif == "records":
        d.rounded_rectangle((150,260,505,510), radius=25, fill="#f2e7ca", outline=dark, width=8)
        d.line((327,270,327,500), fill="#c7b58f", width=5)
        for y in (330,375,420):
            d.line((198,y,280,y+10), fill=dark, width=5)
            d.line((370,y,455,y+10), fill=dark, width=5)
        person(d, 565, 620, .95, dark)
    elif motif in {"assembly", "gathering", "covenant"}:
        d.ellipse((165,415,550,555), fill=gold)
        person(d, 355, 425, 1.1, dark)
        for x,y in ((95,600),(190,625),(275,610),(465,620),(565,590),(655,635)):
            person(d, x, y, .58, "#344b43")
        if motif == "covenant":
            d.ellipse((220,470,500,565), fill="#58aeb6")
    elif motif == "palace":
        d.rectangle((140,250,585,535), fill="#d7b783", outline=dark, width=7)
        d.polygon([(115,255),(360,115),(610,255)], fill=gold, outline=dark)
        for x in (205,325,445,530):
            d.rectangle((x,285,x+42,535), fill="#f0ddbb", outline=dark, width=4)
        person(d, 365, 505, 1.0, dark)
    elif motif == "fire":
        d.rectangle((125,260,590,520), fill="#76675a", outline=dark, width=8)
        for x in (175,270,365,460,555):
            d.rectangle((x,300,x+35,515), fill="#d0ad7d")
        d.polygon([(245,585),(285,480),(325,565),(375,455),(425,585)], fill=gold)
        person(d, 540, 630, .75, dark)
    elif motif == "water":
        d.ellipse((55,420,665,690), fill="#58aeb6", outline="#e9efd9", width=8)
        for x in (175,290,410,535): person(d, x, 610, .65, dark)
        d.arc((100,475,620,655),185,350,fill="#d8eff0",width=6)
    elif motif in {"journey", "escape", "road", "horizon"}:
        d.polygon([(0,620),(145,535),(260,600),(370,480),(510,540),(720,350),(720,720),(0,720)], fill="#536f58")
        d.line([(35,680),(210,590),(335,625),(455,510),(660,470)], fill="#e6cc91", width=36, joint="curve")
        person(d, 235, 585, .7, dark)
        person(d, 305, 600, .55, "#6d4436")
        if motif == "escape": d.ellipse((520,100,625,205), fill="#f4ddaa")
    elif motif == "mountain":
        d.polygon([(0,500),(160,170),(350,505),(480,155),(720,520)], fill="#718a80")
        d.polygon([(410,265),(480,155),(555,270),(495,235),(460,275)], fill="#e9ead9")
        d.polygon([(250,530),(365,445),(490,530)], fill=dark)
        d.rectangle((285,530,465,625), fill="#bc8d59")
        person(d, 160, 650, .6, dark)
    elif motif == "light":
        for angle in range(195,350,18):
            x2 = 360 + int(280*math.cos(math.radians(angle)))
            y2 = 300 + int(240*math.sin(math.radians(angle)))
            d.line((360,300,x2,y2), fill="#f2d47c", width=8)
        person(d,360,640,1.05,dark)
        d.ellipse((330,240,390,300), fill="#f7e8a9")
    elif motif == "judges":
        d.rectangle((240,300,500,515), fill="#c9b28b", outline=dark, width=7)
        d.polygon([(210,300),(370,200),(530,300)], fill=gold, outline=dark)
        for x in (130,200,545,630): person(d,x,625,.58,dark)
        d.line((370,365,370,475), fill=dark, width=12)
    rng = random.Random(seed)
    for _ in range(220):
        x, y = rng.randrange(ART_WIDTH), rng.randrange(HEIGHT)
        if y < 400: d.point((x,y), fill="#f4eedc" if rng.random() > .5 else "#c4d5c9")
    return image


def make_card(episode: Episode, scene: Scene, index: int, path: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#193e3d")
    image.paste(story_art(scene.motif, index + len(episode.slug)), (0,0))
    d = ImageDraw.Draw(image)
    d.rectangle((ART_WIDTH,0,WIDTH,HEIGHT), fill="#193e3d")
    d.rectangle((ART_WIDTH,0,WIDTH,12), fill="#d4a654")
    x, maxw = ART_WIDTH+48, WIDTH-ART_WIDTH-88
    d.text((x,38), episode.chapters, font=face(17), fill="#d6cda9")
    d.text((x,72), episode.title, font=face(22,True), fill="#f1e8d1")
    d.line((x,116,WIDTH-48,116), fill="#67877b", width=2)
    d.text((x,142), scene.title, font=face(30,True), fill="#f2c66e")
    body = face(23)
    y = 200
    for line in lines_for(d, scene.text, body, maxw):
        d.text((x,y), line, font=body, fill="#f1eddf")
        y += 34
    d.line((x,HEIGHT-80,WIDTH-48,HEIGHT-80), fill="#67877b", width=2)
    d.text((x,HEIGHT-58), scene.reference, font=face(18,True), fill="#dfbd72")
    d.text((x+165,HEIGHT-58), "INDEPENDENT STORY SUMMARY", font=face(13), fill="#c8d4c8")
    image.save(path)


def powershell(script: str) -> None:
    command = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", command], check=True)


def narrate(text: str, target: Path) -> None:
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    destination = str(target).replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SelectVoice('{VOICE_NAME}'); $s.SetOutputToWaveFile('{destination}'); "
        f"$text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded}')); "
        "$s.Speak($text); $s.Dispose()"
    )
    powershell(script)


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def find_ffmpeg() -> str:
    try:
        import imageio_ffmpeg
    except ImportError as error:
        raise SystemExit("Install video/mosiah_series/requirements.txt first.") from error
    binary = imageio_ffmpeg.get_ffmpeg_exe()
    result = subprocess.run([binary,"-hide_banner","-encoders"], capture_output=True, text=True, check=True)
    if "libx264" not in result.stdout:
        raise SystemExit("FFmpeg is missing libx264 support.")
    return binary


def render(episode: Episode, ffmpeg: str) -> None:
    folder = OUT / episode.slug
    folder.mkdir(parents=True, exist_ok=True)
    wav = folder / "narration.wav"
    narrate(" ".join(scene.text for scene in episode.scenes), wav)
    total = duration(wav)
    weights = [len(scene.text.split()) for scene in episode.scenes]
    lengths = [total * count / sum(weights) for count in weights]
    inputs = []
    command = [ffmpeg,"-y","-hide_banner","-loglevel","error"]
    for index, length in enumerate(lengths):
        image = folder / f"scene-{index+1:02}.png"
        command += ["-loop","1","-framerate",str(FPS),"-t",f"{length:.3f}","-i",str(image)]
        inputs.append(f"[v{index}]")
    audio_index = len(episode.scenes)
    command += ["-i",str(wav)]
    filters = []
    for index in range(audio_index):
        filters.append(f"[{index}:v]scale=1344:756,zoompan=z='min(zoom+0.00018,1.035)':x='iw/2-(ow/zoom/2)':y='ih/2-(oh/zoom/2)':d=1:s={WIDTH}x{HEIGHT}:fps={FPS},setsar=1[v{index}]")
    filters.append(f"{''.join(inputs)}concat=n={audio_index}:v=1:a=0[outv]")
    destination = folder / f"{episode.slug}.mp4"
    command += ["-filter_complex",";".join(filters),"-map","[outv]","-map",f"{audio_index}:a:0","-c:v","libx264","-preset","medium","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(destination)]
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the five-part Mosiah storybook video series.")
    parser.add_argument("--check", action="store_true", help="Check local MP4 and narration tools.")
    args = parser.parse_args()
    ffmpeg = find_ffmpeg()
    if args.check:
        print(f"FFmpeg: {ffmpeg}\nPillow: {Image.__version__ if hasattr(Image, '__version__') else 'available'}\nVoice: {VOICE_NAME}")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for episode in EPISODES:
        print(f"Rendering {episode.title}...")
        folder = OUT / episode.slug
        folder.mkdir(parents=True, exist_ok=True)
        for index, scene in enumerate(episode.scenes):
            make_card(episode, scene, index, folder / f"scene-{index+1:02}.png")
        render(episode, ffmpeg)
    print(f"Finished: {OUT}")


if __name__ == "__main__":
    main()