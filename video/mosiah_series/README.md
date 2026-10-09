# Mosiah Animated Series

This standalone generator creates five narrated MP4 episodes covering Mosiah 1-29. The narration is an original summary, not a verse-by-verse reading; chapter references appear on screen. The illustrated storybook scenes are generated locally, and Windows' built-in speech synthesis supplies the narration.

This is an independent adaptation, not produced by or affiliated with The Church of Jesus Christ of Latter-day Saints. Source: [Book of Mosiah](https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah?lang=eng).

## Render

```powershell
python -m pip install -r video/mosiah_series/requirements.txt
python video/mosiah_series/generate.py
```

MP4s, editable narration WAVs, and scene cards are saved under `video/mosiah_series/rendered/`. Use `--check` to verify the local renderer without generating videos. The default narrator is Microsoft David Desktop; change `VOICE_NAME` in `generate.py` to select another installed Windows voice.

## Acted-out cartoon pilot

The Abinadi pilot uses drawn characters with animated speaking poses, acted dialogue, and captions. It covers Mosiah 11-17 and is an original dramatic paraphrase. Render it with:

```powershell
python video/mosiah_series/generate_pilot.py
```

The pilot is saved under `video/mosiah_series/rendered/pilot-abinadi/`. It uses Windows voices and local vector-style art; no external AI video service is connected to this workspace.