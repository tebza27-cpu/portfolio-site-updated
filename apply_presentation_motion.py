from pathlib import Path

import win32com.client


ROOT = Path(__file__).parent
INPUT = ROOT / "static" / "Mokhele_IT_Solutions_Professional_Proposal_Images_2026.pptx"
OUTPUT = ROOT / "static" / "Mokhele_IT_Solutions_Professional_Proposal_Final_2026.pptx"

FADE = 1793
ADVANCE_ON_CLICK = 1
ADVANCE_ON_TIME = 2
SLIDESHOW_USE_TIMINGS = 2
ANIM_FADE = 10
TRIGGER_AFTER_PREVIOUS = 3


def is_picture(shape):
    return shape.Type == 13


def is_candidate_text(shape):
    if not shape.HasTextFrame:
        return False
    if not shape.TextFrame.HasText:
        return False
    text = shape.TextFrame.TextRange.Text.strip()
    if not text or len(text) < 12:
        return False
    # Keep footer and section labels static; animate meaningful slide content.
    return shape.Top < 6.6 * 72 and shape.Height > 12


def add_fade(sequence, shape, delay):
    effect = sequence.AddEffect(shape, ANIM_FADE)
    effect.Timing.TriggerType = TRIGGER_AFTER_PREVIOUS
    effect.Timing.Duration = 0.45
    effect.Timing.TriggerDelayTime = delay
    return effect


def apply_motion():
    app = win32com.client.gencache.EnsureDispatch("PowerPoint.Application")
    app.Visible = True
    presentation = app.Presentations.Open(str(INPUT), False, False, False)
    timings = [8, 12, 12, 14, 12, 14, 14, 12, 16, 14, 9]

    try:
        presentation.SlideShowSettings.AdvanceMode = SLIDESHOW_USE_TIMINGS
        for index in range(1, presentation.Slides.Count + 1):
            slide = presentation.Slides(index)
            transition = slide.SlideShowTransition
            transition.EntryEffect = FADE
            transition.Duration = 0.6
            transition.AdvanceOnClick = True
            transition.AdvanceOnTime = True
            transition.AdvanceTime = timings[index - 1]

            sequence = slide.TimeLine.MainSequence
            while sequence.Count:
                sequence.Item(sequence.Count).Delete()

            pictures = [slide.Shapes(i) for i in range(1, slide.Shapes.Count + 1) if is_picture(slide.Shapes(i))]
            text_shapes = [
                slide.Shapes(i)
                for i in range(1, slide.Shapes.Count + 1)
                if is_candidate_text(slide.Shapes(i))
            ]
            text_shapes.sort(key=lambda shape: (shape.Top, shape.Left))

            delay = 0
            if pictures:
                add_fade(sequence, pictures[0], delay)
                delay = 0.12
            for shape in text_shapes[:2]:
                add_fade(sequence, shape, delay)
                delay = 0.08

        presentation.SaveAs(str(OUTPUT))
        print(f"Created {OUTPUT}")
        print(f"Slides: {presentation.Slides.Count}")
    finally:
        presentation.Close()
        app.Quit()


if __name__ == "__main__":
    apply_motion()