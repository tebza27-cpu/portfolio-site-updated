from __future__ import annotations

import argparse
import base64
import math
import random
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

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
    caption: str = ""


@dataclass(frozen=True)
class Episode:
    slug: str
    title: str
    chapters: str
    scenes: tuple[Scene, ...]


EPISODES = (
    Episode("01-king-benjamin", "KING BENJAMIN'S ADDRESS", "MOSIAH 2-5", (
        Scene("A call to gather", "King Benjamin sent a proclamation throughout the land, asking his people to come to the temple in Zarahemla. The gathering had a purpose beyond ceremony. Benjamin wanted the people to hear his counsel, to witness the transfer of the kingdom to his son Mosiah, and to understand what kind of people they were choosing to become. Families prepared for the journey, carrying food and belongings and making camp near the temple. The summons reached rich and poor alike. Each household came to hear the same message, and each person would have to decide what to do with it.", "Mosiah 2:1", "journey", "The people are called to gather"),
        Scene("Tents around the temple", "The people arrived in large numbers and pitched their tents with their doors facing the temple. The arrangement turned the whole encampment toward a shared center. Parents settled children, neighbors greeted one another, and the camp filled with the small sounds of a community preparing to listen. This was not only a royal announcement. Benjamin's people came as families and as a covenant people, bringing their lives and questions with them. They would hear about government, faith, service, mercy, and the Savior. The message began with a simple act: set aside time, come together, and listen with an open heart.", "Mosiah 2:1-4", "gathering", "Families gather around the temple"),
        Scene("A message carried to every tent", "Because the crowd was so large, Benjamin spoke from a tower where more people could see and hear him. Even then, he arranged for his words to be written and carried to those beyond the reach of his voice. The detail matters: the address was not meant only for those closest to the king. It was to reach every tent. Benjamin wanted the people to hear clearly, consider carefully, and remember. A written record would also carry the address beyond that day, giving later generations a chance to reflect on the choices made in Zarahemla.", "Mosiah 2:5-8", "records", "His words are written and shared"),
        Scene("Mosiah is presented as king", "Benjamin spoke of his son Mosiah and the transition of the kingdom. The moment could have centered on inheritance and power, but Benjamin used it to teach accountability. He called the people to open their ears and their hearts, not because the speaker was a king, but because the message deserved honest consideration. Mosiah would lead after his father, yet neither title could replace the people's own responsibility before God. A government could be transferred in a public gathering; a faithful life had to be chosen by each person, one decision at a time.", "Mosiah 2:8-9", "palace", "Mosiah is named as the next king"),
        Scene("A clear conscience", "Benjamin began by asking the people to listen with attention and to judge his words fairly. He did not claim perfection. Instead, he described the work he had done and invited the people to speak if he had wronged them or taken anything unfairly. He wanted to stand before them with a clear conscience, having served rather than used them. That invitation made the king answerable to the people he governed. Authority did not place him beyond correction. Benjamin's first example was humility: before instructing others, he was willing to account for his own conduct.", "Mosiah 2:9-11", "assembly", "A king answers for his service"),
        Scene("Power used for service", "Benjamin reminded the people that he had not sought wealth, praise, or control for himself. He had not burdened them with taxes to support a life of ease, and he had worked with his own hands. He described leadership as labor carried for the benefit of others. These details made his counsel concrete. Service was not an attractive word placed over privilege; it was what a ruler did with his time and strength. Benjamin's years on the throne could now become a lesson for Mosiah and for everyone listening: leadership is trustworthy when it is joined to restraint, honesty, and care.", "Mosiah 2:12-14", "assembly", "Benjamin describes a life of service"),
        Scene("No one stands above a neighbor", "Benjamin said he did not wish to boast, even though the people could speak for the work he had done. He asked them to learn from his example and not to suppose that one person was better than another. Their lives were connected. Families depended on one another, and the community's strength came from people keeping faith and helping each other. A title might place someone in a particular duty, but it did not make that person's life more precious. Benjamin urged the people to set aside pride and envy and to see their neighbors as fellow children of God.", "Mosiah 2:15-18", "gathering", "Neighbors are equal in worth"),
        Scene("Serving God by serving people", "Benjamin taught that when people served one another, they were also serving God. He asked them to consider how much they depended on God for life, food, and the ability to act. Gratitude was not meant to remain a private feeling. It could become patience with a child, help for a neighbor, or a fair decision made by someone in authority. The service did not need to be dramatic. It needed to be real. In Benjamin's address, love of God and responsibility to people were joined together: faith became visible in how a person treated those nearby.", "Mosiah 2:17-20", "gathering", "Faith becomes visible in service"),
        Scene("Remember the source of every blessing", "Benjamin asked the people to remember that life itself was a gift. Even if they spent every day serving God, they could not place God in their debt. That truth was not meant to make service feel pointless. It was meant to loosen the grip of pride. No one could claim that every success had been earned alone, or that receiving blessings made them superior. The people could choose gratitude instead: accept what they had been given, acknowledge their dependence, and use their strength to lift someone else. Humility, for Benjamin, began with an honest view of where life comes from.", "Mosiah 2:20-25", "light", "Gratitude replaces pride"),
        Scene("The danger of turning away", "Benjamin warned that a people who had received so much also carried responsibility. If they knowingly rebelled and turned away from God, their choices would bring sorrow and separation. He did not offer easy reassurance that a covenant made once would excuse every later action. Their conduct mattered. A person who had learned what was right could not treat that knowledge casually. Benjamin's warning was serious, but it was given before the message of hope, not instead of it. The people were asked to understand the consequences of their choices so they could choose a better path while there was time.", "Mosiah 2:26-41", "palace", "Choices carry consequences"),
        Scene("An angel brings a message", "Benjamin told the people that an angel had appeared to him with glad tidings of great joy. The message looked far beyond the king's lifetime. A Savior would be born among humankind, and his name would be Jesus Christ. The angel's words shifted the gathering from the record of Benjamin's rule to a promise of divine deliverance. The people were not asked to trust in a king's strength alone. They were invited to look toward Christ, whose coming would bring healing and hope. Benjamin shared the message carefully so the people could remember both the promise and the path it opened.", "Mosiah 3:1-8", "light", "Benjamin shares the angel's message"),
        Scene("The Savior ministers among people", "The angel described the life of Jesus Christ: his mother, his birth, the miracles he would perform, and the care he would give to the sick and afflicted. The Savior would teach with authority and show compassion through action. His path would also include rejection and suffering. Benjamin's people heard that the Redeemer was not distant from human pain. He would enter mortal life, meet people in their weakness, and minister among them. The account invited listeners to imagine a Savior whose power was expressed not as domination, but as teaching, healing, sacrifice, and love.", "Mosiah 3:5-10", "assembly", "Christ's ministry brings healing"),
        Scene("A message of redemption", "The angel's message included the suffering and death of Jesus Christ, as well as his resurrection. The good news did not pretend that sin, grief, or death were unreal. It taught that God had prepared a way to redeem and raise his children. Benjamin asked the people to believe this witness and to remember the name of Christ, for salvation came through him. That belief would call for more than agreement with an idea. It would ask each listener to trust, repent, and allow the Savior's teachings to shape everyday choices.", "Mosiah 3:10-18", "light", "Hope reaches beyond suffering"),
        Scene("The natural person can change", "Benjamin taught that people could yield to the influence of the Holy Spirit and become more patient, humble, gentle, and full of love. This was not a claim that change came instantly or without effort. The change was a direction: turn away from selfishness and learn to follow God. A person could choose not to be ruled by anger or pride, and could practice kindness even when it was difficult. The Savior's grace offered hope, while each person still had choices to make. The address connected spiritual conversion to recognizable qualities that could be seen in family life and community.", "Mosiah 3:19", "covenant", "A heart learns patience and love"),
        Scene("The people ask for mercy", "After hearing Benjamin's words, the people fell to the ground. They recognized their need for forgiveness and cried out for mercy through Jesus Christ. Their response was shared, but it was also personal: each one felt the weight of their own life and reached toward God. The gathering grew quiet as they sought a change within themselves. The record describes their hearts as being filled with joy and peace when they received forgiveness. Benjamin's message had moved from a tower and a written record into the inner life of the people who had listened.", "Mosiah 4:1-3", "assembly", "A people seek forgiveness together"),
        Scene("Keep the change alive", "Benjamin asked whether the people could claim credit for the change they had felt. He taught them to remember their dependence on God, to remain humble, and to keep faith. A moment of peace could become the beginning of a lasting practice. They could pray, watch their words, and turn away from contention. They could remember how it felt to seek mercy and show mercy to others. Benjamin's counsel made conversion practical: keep turning toward God, and let the memory of forgiveness change the way you respond to the people around you.", "Mosiah 4:4-12", "covenant", "Remember mercy in daily life"),
        Scene("Care begins at home", "Benjamin described what a faithful community might look like in ordinary households. Parents would teach children to care for one another, to walk honestly, and to serve God. Children would learn through words and through the example of adults. Homes could become places where people practiced patience instead of cruelty and honesty instead of deception. These small choices mattered because a community was made of families and neighbors. A covenant was not only something spoken in a large assembly; it continued at home, in the way people treated those closest to them when no crowd was watching.", "Mosiah 4:13-15", "gathering", "Faith is taught at home"),
        Scene("Give what you are able", "Benjamin turned to people in need. He taught that a person who had only a little could still give, and that those who had more could share according to what they were able. The amount was not the only measure of generosity. What mattered was a willing heart and an honest effort to relieve another person's hardship. No one should be sent away simply because the giver could not solve everything. Even listening, offering what was possible, or treating a person with dignity could be part of compassionate service.", "Mosiah 4:16-21", "assembly", "Generosity is measured by willingness"),
        Scene("Do not judge the one who asks", "The king cautioned the people not to condemn someone who asked for help. A person might need food, clothing, shelter, or relief from a burden that others could not see. If the giver could not provide everything, they could still respond with kindness rather than accusation. Benjamin asked the people to remember their own dependence on God before looking down on a neighbor. The lesson challenged quick judgments. It encouraged the community to ask what help was possible and to treat a person in need as a neighbor, not as a problem to dismiss.", "Mosiah 4:17-23", "gathering", "Meet a request with compassion"),
        Scene("Wisdom and order in giving", "Benjamin did not ask the people to give recklessly or pretend that every need could be met at once. He taught them to act in wisdom and order, caring for families while also sharing with others. Some people had means to help; others had little to give. Each could contribute according to their circumstances. The point was to keep a willing heart and avoid using hardship as an excuse for indifference. A community could plan, share responsibility, and respond steadily. Compassion and good judgment belonged together.", "Mosiah 4:24-28", "records", "Give with both compassion and wisdom"),
        Scene("A covenant changes a people", "Benjamin asked the people whether they believed his words. They answered that they did and described a mighty change in their hearts. They no longer felt inclined to do evil, but wanted to do good continually. Their words marked a turning point. They were not simply moved by a speech; they had begun to choose a new identity and direction. They entered a covenant to do God's will and to keep his commandments. Their commitment joined faith in Christ with the daily work of becoming a more loving people.", "Mosiah 5:1-5", "covenant", "The people describe a change of heart"),
        Scene("They take upon them the name of Christ", "Benjamin taught the people that through faith they could become children of Christ and take upon them his name. The name represented belonging, but also responsibility. They would be recognized by their loyalty to Christ and by the good they chose to do. Benjamin urged them to remember the covenant, remain steadfast, and not let pride or wrongdoing pull them away. The gathering would end, and the people would return to their homes, but the name they had accepted was meant to travel with them into every part of their lives.", "Mosiah 5:6-15", "covenant", "A name becomes a lifelong commitment"),
        Scene("A charge to remember", "Benjamin recorded the names of those who had made the covenant and appointed teachers to help them remember. His address had moved through service, humility, the promise of Christ, repentance, generosity, and a new covenant. Now each person would return to familiar work and relationships carrying the message with them. Benjamin's final counsel was not to admire the gathering from a distance, but to live what had been heard. Remember the Lord, help one another, and remain steadfast in good works. The story of this assembly ended with a beginning for the people who had listened.", "Mosiah 5:15", "assembly", "Return home ready to serve"),
    )),
    Episode("02-the-prophet-and-the-king", "THE PROPHET AND THE KING", "MOSIAH 7-17", (
        Scene("A search beyond Zarahemla", "Some time after Mosiah became king, a group led by Ammon traveled south to learn what had happened to people who had left Zarahemla years earlier. The journey was uncertain. They did not know whether Zeniff's colony still lived, or what kind of welcome they would receive. At last they reached the land of Lehi-Nephi and were taken before King Limhi.", "Mosiah 7", "journey"),
        Scene("Limhi tells of bondage", "Limhi explained that his people were paying tribute to the Lamanites and had suffered defeat in battle. Their hardship had not begun in a single day. His grandfather Zeniff had led the original settlement, and later rulers had made choices that left the people vulnerable. Limhi now hoped the newcomers could help him find a way back to Zarahemla.", "Mosiah 7", "palace"),
        Scene("A record without a translator", "Limhi also showed Ammon twenty-four plates found in the wilderness. The people wanted to know who had made them and what had happened to the civilization they described. Ammon explained that Mosiah had the gift to interpret such records. The discovery opened a second story inside the first: the present people were not the only ones whose history needed preserving.", "Mosiah 8", "records"),
        Scene("The story turns back to Zeniff", "The account then returns to Zeniff, whose record explains how the colony began. He had first joined a group sent to explore the land, but rejected a plan to destroy its inhabitants. Later he led another migration and made an agreement with the Lamanite king. His intentions included peace and rebuilding, yet the settlement depended on the promises of a ruler whose interests could change.", "Mosiah 9", "journey"),
        Scene("A fragile peace gives way", "Zeniff's people planted crops, raised flocks, and rebuilt their communities. But conflict returned, and they had to defend their homes. Zeniff taught his people to prepare and to trust God rather than assume that a treaty would keep them safe forever. After Zeniff died, his son Noah took the throne and moved the people in a very different direction.", "Mosiah 9-10", "escape"),
        Scene("Noah's court and Abinadi's warning", "Noah taxed the people heavily while his court lived lavishly. Priests were appointed, but their conduct did not match the faith they professed. Abinadi came with a warning that injustice would bring bondage. The message was dangerous to a ruler who wanted praise, not correction. Noah's servants searched for the prophet, but Abinadi escaped and later returned in disguise.", "Mosiah 11", "palace"),
        Scene("Before the priests", "Recognized and arrested, Abinadi stood before Noah and the priests. They questioned him about scripture, but he challenged them to live what they taught. He spoke of commandments, the law of Moses, and the need for redemption. His words did not flatter the court. Alma, one of the priests, listened closely and began to believe.", "Mosiah 12-15", "palace"),
        Scene("One listener preserves the testimony", "Abinadi testified of Jesus Christ and the hope of resurrection. Noah ordered him to be killed, but Alma spoke in his defense and was forced to flee. Alma wrote down what he had heard. The testimony passed out of the courtroom with him. A king could sentence the messenger, but could not prevent the words from shaping a new community.", "Mosiah 16-17", "fire"),
    )),
    Episode("03-waters-and-wilderness", "WATERS AND WILDERNESS", "MOSIAH 18-25", (
        Scene("A community forms at Mormon", "After escaping Noah's court, Alma gathered people who believed Abinadi. At the waters of Mormon, he taught them and invited them to make a covenant: bear one another's burdens, mourn with those who mourn, and comfort those who needed comfort. They were baptized and became a community that tried to practice the faith they had heard.", "Mosiah 18", "water"),
        Scene("The people leave by night", "Noah's servants discovered the gathering, and Alma's people had to move quickly. They left the area and traveled into the wilderness, carrying families and whatever supplies they could manage. Their journey was not a triumphant march. They had left homes behind because worship and community had become dangerous, and they had to build a new life in unfamiliar country.", "Mosiah 18", "journey"),
        Scene("Limhi inherits a hard kingdom", "Meanwhile in Lehi-Nephi, Limhi had become king after the death of his father Noah. The people were under Lamanite control, and their attempts to fight their way free had brought more suffering. Limhi asked them to face the choices that had led there, while also urging them to look to God for deliverance and not give up hope.", "Mosiah 19-21", "palace"),
        Scene("A plan to escape bondage", "Gideon proposed a careful plan rather than another direct battle. The people prepared provisions and waited for a moment when they could leave without alerting their captors. Their departure required trust in one another and restraint. When the opportunity came, families traveled through the wilderness toward Zarahemla, carrying their records and the memory of what they had endured.", "Mosiah 22", "escape"),
        Scene("Alma's people face new rulers", "Alma's people had built a peaceful settlement, but their safety did not last. Lamanite forces found them, and Amulon, once one of Noah's priests, became their overseer. The people were placed under burdens and forbidden to pray aloud. Even then they found ways to support one another and hold to the covenant they had made at the water.", "Mosiah 23-24", "mountain"),
        Scene("A burden made bearable", "The people asked for relief, and the account describes God strengthening them so their burdens could be borne. They worked, watched over families, and waited for a chance to leave. Their faith did not remove every hardship at once; it gave them courage while they continued through it. At last they gathered their belongings and escaped into the wilderness.", "Mosiah 24", "journey"),
        Scene("The journeys converge", "Alma's people reached Zarahemla and found the people of Limhi there as well. The two groups had traveled different roads, but both carried the experience of bondage and deliverance. Their stories were told publicly, allowing the wider community to understand what had happened and how each group had survived.", "Mosiah 25", "gathering"),
        Scene("One people, many memories", "Mosiah allowed Alma to organize the Church, and Alma began teaching and baptizing among the people. The reunions did not erase their different histories; they placed those histories beside one another. The record of Mosiah shows a people learning to belong together by listening, remembering, and taking responsibility for how they treat one another.", "Mosiah 25", "covenant"),
    )),
    Episode("04-a-change-of-heart", "A CHANGE OF HEART", "MOSIAH 26-27", (
        Scene("A new generation asks questions", "After the people reunited in Zarahemla, the Church grew. Some young people did not understand or accept the teachings they had inherited, and arguments began to unsettle the community. Alma, now serving as high priest, had to respond to questions that could not be solved by simply repeating old rules. He sought guidance about justice, repentance, and mercy.", "Mosiah 26", "assembly"),
        Scene("Alma seeks an answer", "Alma prayed about people who had turned away and about the responsibility of those who led the Church. The answer he received joined accountability with the possibility of change. People who repented, confessed, and sought forgiveness could be forgiven. The community was not asked to pretend harm had not happened; it was asked to make room for sincere return.", "Mosiah 26", "light"),
        Scene("A conflict led by Alma the Younger", "Alma's own son, also named Alma, opposed the Church with the sons of Mosiah. They tried to persuade people to abandon their faith. Their family connections did not make the situation easy, and their actions affected the whole community. The story names the conflict plainly before showing what interrupted it.", "Mosiah 27", "road"),
        Scene("The angel's interruption", "As the young men traveled, an angel appeared and called Alma to account. The encounter shook him so deeply that he could not speak or move. His companions carried him to his father and described what had happened. The silence that followed gave him time to face the consequences of what he had done and consider what he believed.", "Mosiah 27", "light"),
        Scene("A father's prayer", "Alma the Elder gathered others and fasted and prayed for his son. For two days and two nights, Alma the Younger remained unable to speak or move. His friends and family waited with him. The change did not arrive as a quick public speech; it began in a private struggle, surrounded by people who hoped he could recover.", "Mosiah 27", "assembly"),
        Scene("Alma remembers mercy", "When Alma regained his strength, he told those around him that he had been changed through faith in Jesus Christ. He remembered his wrongs, but he also remembered the mercy he had received. His repentance did not erase his past; it changed what he chose to do with the rest of his life.", "Mosiah 27", "covenant"),
        Scene("A different direction", "The sons of Mosiah also repented. They could have used their family status to seek comfort or influence, but instead asked permission to teach among the Lamanites. The people worried for their safety, yet Mosiah allowed them to go. A story that began with opposition ended with a difficult decision to serve those they had once resisted.", "Mosiah 27", "journey"),
        Scene("A testimony becomes a beginning", "Alma and the sons of Mosiah began teaching with new purpose. Their changed lives became part of their message, though the work ahead would be long and uncertain. Mosiah's record presents conversion not as a single dramatic moment only, but as a turning toward repair, humility, and continued service after harm has been done.", "Mosiah 27", "road"),
    )),
    Episode("05-a-new-kind-of-government", "A NEW KIND OF GOVERNMENT", "MOSIAH 28-29", (
        Scene("A mission chosen freely", "The sons of Mosiah asked to leave Zarahemla and teach among the Lamanites. Their request worried their father, because the journey would be dangerous and the people might reject them. But the brothers wanted to share what they had come to believe. Mosiah considered their choice and let them go, trusting them to take responsibility for their own calling.", "Mosiah 28", "journey"),
        Scene("An older record comes to light", "At the same time, Mosiah used the interpreters to translate the twenty-four plates found by Limhi's people. The record described an ancient civilization and its history. Translation brought the past into the present: the people could learn not only where their own families had traveled, but what earlier societies had built and lost.", "Mosiah 28", "records"),
        Scene("The throne has no successor", "As Mosiah grew old, none of his sons wanted to become king. They had chosen a mission instead. Mosiah faced a question larger than his household: what should happen to the government when there was no heir prepared to rule? He did not treat the throne as something the family must keep at any cost.", "Mosiah 29", "palace"),
        Scene("Mosiah warns about unchecked power", "Mosiah explained the danger of an unrighteous king. A ruler who sought wealth, praise, or power could lead an entire people into suffering. Even a good ruler could not guarantee that every successor would govern fairly. The people needed a way to judge actions and hold leaders accountable rather than rely only on the character of one person.", "Mosiah 29", "judges"),
        Scene("The people choose a system of judges", "Mosiah proposed that judges be chosen by the voice of the people and that laws apply to everyone. Different levels of responsibility would make it harder for one person to control every decision. This system did not promise perfect justice, but it gave the people a role in choosing leaders and responding when those leaders acted wrongly.", "Mosiah 29", "assembly"),
        Scene("A choice, and its responsibility", "The people accepted the change and selected Alma the Younger as chief judge. The record stresses that freedom to choose brings responsibility: people must understand the laws, resist manipulation, and seek leaders who care for the common good. A new government could help, but it could not replace the character and judgment of the people themselves.", "Mosiah 29", "judges"),
        Scene("Two generations move forward", "The sons of Mosiah traveled toward a difficult mission. Alma began serving as chief judge and high priest. Mosiah and Alma the Elder approached the end of their lives, while younger leaders took on new responsibilities. The story of Mosiah closes not with every conflict solved, but with institutions and testimonies passed forward.", "Mosiah 29", "horizon"),
        Scene("A record for those who come after", "Mosiah brings together records of kings, prophets, families, and communities in crisis. It asks readers to notice the effects of leadership, the cost of pride, the possibility of repentance, and the strength people find in keeping covenants. The final change from kings to judges leaves a question for each generation: how will we use the choices we have been given?", "Mosiah 1-29", "records"),
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
    for line in lines_for(d, scene.caption or scene.text, body, maxw):
        d.text((x,y), line, font=body, fill="#f1eddf")
        y += 34
    d.line((x,HEIGHT-80,WIDTH-48,HEIGHT-80), fill="#67877b", width=2)
    d.text((x,HEIGHT-58), scene.reference, font=face(18,True), fill="#dfbd72")
    d.text((x+165,HEIGHT-58), "INDEPENDENT STORY SUMMARY", font=face(13), fill="#c8d4c8")
    image.save(path)


def powershell(script: str) -> None:
    command = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", command], check=True)


def narrate(scenes: tuple[Scene, ...], target: Path) -> None:
    spoken_scenes = "<break time='500ms'/>".join(escape(scene.text) for scene in scenes)
    ssml = (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        f"<voice name={quoteattr(VOICE_NAME)}><prosody rate='-8%'>{spoken_scenes}</prosody></voice></speak>"
    )
    ssml_path = target.with_suffix(".ssml")
    ssml_path.write_text(ssml, encoding="utf-8")
    destination = str(target).replace("'", "''")
    ssml_source = str(ssml_path).replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.SelectVoice('{VOICE_NAME}'); $s.SetOutputToWaveFile('{destination}'); "
        f"$ssml = [IO.File]::ReadAllText('{ssml_source}'); "
        "try { $s.SpeakSsml($ssml) } finally { $s.Dispose() }"
    )
    try:
        powershell(script)
    finally:
        ssml_path.unlink(missing_ok=True)


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
    narrate(episode.scenes, wav)
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
    parser.add_argument("--episode", choices=[episode.slug for episode in EPISODES], help="Render only one episode.")
    args = parser.parse_args()
    ffmpeg = find_ffmpeg()
    if args.check:
        print(f"FFmpeg: {ffmpeg}\nPillow: {Image.__version__ if hasattr(Image, '__version__') else 'available'}\nVoice: {VOICE_NAME}")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    episodes = [episode for episode in EPISODES if args.episode is None or episode.slug == args.episode]
    for episode in episodes:
        print(f"Rendering {episode.title}...")
        folder = OUT / episode.slug
        folder.mkdir(parents=True, exist_ok=True)
        for index, scene in enumerate(episode.scenes):
            make_card(episode, scene, index, folder / f"scene-{index+1:02}.png")
        render(episode, ffmpeg)
    print(f"Finished: {OUT}")


if __name__ == "__main__":
    main()