# Mosiah Animated Series

This standalone generator creates a narrated MP4 series covering Mosiah 1-29. The King Benjamin episode focuses on Mosiah 2-5 and runs about 15 minutes. The other overview episodes remain shorter. Narration is an original summary, not a verse-by-verse reading; chapter references appear on screen. The illustrated storybook scenes are generated locally, and Windows' built-in speech synthesis supplies distinct narration with measured pacing and brief scene pauses. No real person's voice is imitated.

This is an independent adaptation, not produced by or affiliated with The Church of Jesus Christ of Latter-day Saints. Source: [Book of Mosiah](https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah?lang=eng).

## Render

```powershell
python -m pip install -r video/mosiah_series/requirements.txt
python video/mosiah_series/generate.py
```

To render just the Mosiah 2-5 King Benjamin episode, run:

```powershell
python video/mosiah_series/generate.py --episode 01-king-benjamin
```

MP4s, editable narration WAVs, and scene cards are saved under `video/mosiah_series/rendered/`. Use `--check` to verify the local renderer without generating videos. The default narrator is Microsoft David Desktop; change `VOICE_NAME` in `generate.py` to select another installed Windows voice.

## Acted-out cartoon pilot

The Abinadi pilot uses drawn characters with animated speaking poses, acted dialogue, and captions. It covers Mosiah 11-17 and is an original dramatic paraphrase. Render it with:

```powershell
python video/mosiah_series/generate_pilot.py
```

The pilot is saved under `video/mosiah_series/rendered/pilot-abinadi/` and runs about 2:49. It uses Windows voices and local vector-style art; no external AI video service or account is needed to generate or watch it.