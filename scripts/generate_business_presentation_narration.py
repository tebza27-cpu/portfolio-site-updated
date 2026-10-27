from __future__ import annotations

import argparse
import getpass
import os
import subprocess
import tempfile
import wave
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
VOICE = "en-US-AdamMultilingualNeural"
SLIDE_SECONDS = 20
SOURCE_VIDEO = STATIC / "business_presentation_investor_31_oct_2026_autoplay.mp4"
OUTPUT_VIDEO = STATIC / "business_presentation_investor_31_oct_2026_narrated.mp4"

NARRATION = [
    "Hello, I am Sifiso Mokhele. This presentation introduces Mokhele IT Solutions, a practical support business for small companies and professionals. The goal is simple: reduce technology disruption, build trust, and help clients work with confidence.",
    "Small businesses lose time and revenue when devices fail, systems slow down, or digital processes become unreliable. Many cannot justify a full-time IT technician. They need affordable, dependable support that helps operations keep moving.",
    "The offer includes troubleshooting, setup, maintenance, cloud and file support, and guidance on digital processes. Clients can choose one-off assistance, a defined package, or a monthly support plan as their needs grow.",
    "The difference is customer-first service, clear communication, and practical solutions for people who are not technical specialists. Flexible packages and reliable follow-up can build trust, repeat business, and referrals.",
    "The first customers are small business owners without in-house IT, including freelancers, home-based businesses, small offices, and service providers. The priority is local professionals and growing businesses that value responsive, understandable support.",
    "Access matters. Proposed prices are three hundred and fifty rand for a forty-five-minute essential session, seven hundred and fifty rand monthly for a starter package, and two thousand five hundred rand monthly for a business retainer. I will test demand and affordability before finalizing prices.",
    "Customer acquisition will start with referrals, local networking, and direct outreach. A simple website, WhatsApp, and social channels will make the service easier to find. A discovery call can build trust, while consistent follow-up can turn a first job into ongoing support.",
    "The launch requires a reliable laptop, phone, internet, diagnostic tools, backup systems, and clear documentation. Simple systems for quotations, invoicing, scheduling, and service records will help keep delivery organized as the client base grows.",
    "Revenue can come from support fees, monthly retainers, troubleshooting packages, and subscriptions. Sustainable profitability depends on pricing the work carefully, controlling costs, and delivering enough value to earn recurring customer relationships.",
    "The estimated setup requirement is forty-six thousand five hundred rand. Monthly cash operations are estimated at eleven thousand rand, with an additional owner-time benchmark of seven thousand five hundred rand per month tracked separately. These estimates need confirmation against actual quotations and workload.",
    "One growth scenario is twenty active clients paying an average of fifteen hundred rand monthly. That would produce thirty thousand rand in monthly sales, or three hundred and sixty thousand rand annually, before costs. Premium services and referrals could support further growth.",
    "On a three-thousand-rand sale, owner time costs fifteen hundred rand and other variable costs are estimated at five hundred. That leaves a thousand-rand contribution, or thirty-three percent. At eleven thousand rand monthly cash overhead, break-even is eleven sales.",
    "Year-three estimate: five hundred and forty thousand rand revenue at sixty-five percent margin yields three hundred and fifty-one thousand rand gross profit. Less two hundred and twenty-two thousand rand annual costs leaves one hundred and twenty-nine thousand rand operating profit before tax. Terms remain proposed.",
    "Chapter eleven turns the plan into continual improvement: keep a clear vision, document workflows, check legal responsibilities, lead and train people thoughtfully, and set measurable goals. Progress should be reviewed regularly and adjusted as the business learns.",
    "Mokhele IT Solutions is built around trust, dependable service, and measurable value. The next steps are to validate demand, confirm prices and costs, improve the operating plan, and grow at a pace that protects customer service. Thank you. I welcome your questions and feedback.",
]


def synthesize(text: str, key: str, region: str, destination: Path) -> None:
    ssml = (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">'
        f'<voice name="{VOICE}"><mstts:express-as style="general">'
        f'<prosody rate="-5%">{escape(text)}</prosody>'
        '</mstts:express-as></voice></speak>'
    )
    request = Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
            "User-Agent": "BusinessPresentationNarration/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            destination.write_bytes(response.read())
    except HTTPError as error:
        raise RuntimeError(f"Azure Speech returned HTTP {error.code}; check the key, region, and voice access.") from None
    except URLError as error:
        raise RuntimeError(f"Could not reach Azure Speech: {error.reason}") from None


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the narrated business presentation using Azure Speech.")
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Prompt locally for missing Azure credentials; the key is entered without echo.",
    )
    args = parser.parse_args()
    key = os.environ.get("AZURE_SPEECH_KEY", "").strip()
    region = os.environ.get("AZURE_SPEECH_REGION", "").strip()
    if args.prompt:
        if not key:
            key = getpass.getpass("Azure Speech key (input hidden): ").strip()
        if not region:
            region = input("Azure Speech region: ").strip()
    if not key or not region:
        raise SystemExit(
            "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION locally, or run this script "
            "with --prompt. Do not paste the key into chat or source code."
        )
    if not SOURCE_VIDEO.is_file():
        raise FileNotFoundError(SOURCE_VIDEO)
    if len(NARRATION) != 15:
        raise RuntimeError(f"Expected 15 narration segments, found {len(NARRATION)}")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory(prefix="business-narration-") as temporary:
        work = Path(temporary)
        audio_files = []
        for index, text in enumerate(NARRATION, start=1):
            audio_path = work / f"slide-{index:02}.wav"
            synthesize(text, key, region, audio_path)
            with wave.open(str(audio_path), "rb") as audio:
                seconds = audio.getnframes() / audio.getframerate()
            if seconds > SLIDE_SECONDS:
                raise RuntimeError(
                    f"Slide {index} narration is {seconds:.1f}s, longer than its "
                    f"{SLIDE_SECONDS}s slot. Shorten that script segment before retrying."
                )
            audio_files.append(audio_path)
            print(f"Synthesized slide {index}/15 ({seconds:.1f}s)")

        inputs = []
        filters = []
        for index, audio_path in enumerate(audio_files):
            inputs.extend(("-i", str(audio_path)))
            filters.append(
                f"[{index}:a]apad=pad_dur={SLIDE_SECONDS},"
                f"atrim=duration={SLIDE_SECONDS},asetpts=PTS-STARTPTS[a{index}]"
            )
        joined = "".join(f"[a{index}]" for index in range(len(audio_files)))
        filters.append(f"{joined}concat=n={len(audio_files)}:v=0:a=1[outa]")
        audio_output = work / "narration.wav"
        subprocess.run(
            [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *inputs,
             "-filter_complex", ";".join(filters), "-map", "[outa]", str(audio_output)],
            check=True,
        )
        subprocess.run(
            [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(SOURCE_VIDEO),
             "-i", str(audio_output), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "128k", "-t", str(SLIDE_SECONDS * len(NARRATION)),
             "-movflags", "+faststart", str(OUTPUT_VIDEO)],
            check=True,
        )
    print(f"Created narrated presentation: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    main()
