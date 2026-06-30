from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = ROOT / "deliverables" / "youtube-subtitles"

MANIFEST = json.loads(
    (DELIVERABLES / "manifest.json").read_text(encoding="utf-8")
)
VIDEO_FOLDERS = {
    item["youtube_id"]: DELIVERABLES / f"{item['youtube_id']}-{item['slug']}"
    for item in MANIFEST
}

CORRECTIONS: dict[str, dict[int, str]] = {
    "42r5f9uf-0U": {
        1: "hello. Eminent Hospice",
        2: "This is Kim Jeong-ah, Nurse Practitioner. today",
        3: "Let me explain about POLST.",
        14: "Power of Attorney legal representative on behalf of",
        33: "If there is a POLST, depending on its contents",
        34: "Treatment such as CPR, cardiopulmonary resuscitation, etc.",
        4: "POLST stands for Physician Orders for Life-Sustaining Treatment.",
        5: "It is a serious medical order about life-sustaining treatment.",
        11: "You can think of it as a doctor's order form,",
        25: "What is written on the POLST can be changed at any time.",
        27: "POLST forms are usually printed on bright paper so they are easy to see.",
        30: "In case of emergency, keep it in a visible place, such as on the refrigerator.",
        32: "When 911 is dispatched",
        40: "The POLST form is broadly divided into four parts: A, B, C, and D.",
        45: "It works. Part A is the patient's heart.",
        46: "Part A is about what to do if the patient's heart stops or they cannot breathe, and whether CPR should be attempted.",
        49: "Instruction CPR Cardiopulmonary Resuscitation",
        87: "You have to decide. Part B is medical",
        90: "As mentioned earlier, Full Treatment is life.",
        105: "The second is the Comfort Focused Treatment.",
        136: "Considering the Nasogastric tube for a short period of time",
        198: "I have to go. If it is an emergency, of course go to 911.",
    },
    "K0bgtz2gV40": {
        10: "I will briefly explain the most common situations.",
        20: "Hospice core services are the essential services",
        21: "that must be provided",
        22: "in hospice care.",
        25: "These core services include doctors, nurses, social workers, and spiritual counselors or chaplains, and each patient must be cared for by at least one member of each discipline.",
        55: "Nurse RN or LVN service",
        156: "Bereavement Care Service also has a spiritual counselor.",
        185: "Conti Supply Diaper Underpads Chucks",
        188: "Make sure or glucometer",
        193: "We give you Hospital Bed Overbed Table",
        194: "Air Pressure Mattress Wheelchair Walker Oxygen",
        195: "Supply suction machine nebulizer etc.",
    },
    "XeGjlf7fILA": {
        40: "Under California law,",
        41: "the deceased usually must be moved",
        42: "from the place of death",
        43: "within about four hours.",
        44: "In most cases, the deceased is taken care of at the funeral home.",
        47: "If the patient dies",
        48: "while receiving hospice care,",
        49: "you do not need to call 911;",
        50: "call the hospice office first.",
        51: "If the patient",
        52: "is not receiving hospice care,",
        53: "you should",
        54: "call 911.",
        57: "Funeral homes can be found within two hours by Americans.",
        67: "I'm calling the company. The Hospice company is",
        83: "What is Death Worksheet in the office?",
        96: "Then, this physician attestation",
        126: "Mainly called Hospice Chaplain.",
        141: "After speaking, I went to Bereavement Services.",
    },
    "SNGsCjicC8E": {
        22: "POLST is important for patients.",
        23: "It is a medical order form,",
        25: "It is a doctor's order, usually printed on pink paper.",
        27: "If your heart stops, take cardiopulmonary resuscitation.",
        45: "It means that you will do cardiopulmonary resuscitation and intubation.",
        46: "If you do not do DNR Do Not Resuscitate",
        60: "If you do this, a paramedic will come.",
        75: "The coroner is investigating County Coroner.",
        88: "Like Paramedic Fire Department or",
    },
    "3mgBE6CaI4I": {
        126: "Patient's condition while looking at vital signs",
        128: "The vital signs are blood pressure and pulse.",
    },
    "edmwae3Iglk": {
        5: "From now on, I will explain how to use the nebulizer.",
        6: "A nebulizer is a machine that turns bronchodilator medication into a fine mist.",
        9: "Connect one end of the tube to the outlet of the machine",
        13: "so that the medication can easily go into the lungs.",
    },
    "Vq5rIpelzhk": {
        3: "I will explain how to use the oxygen concentrator.",
    },
    "9g98EDnOAUI": {
        6: "First, insert the plug. Make sure the lid on the suction bottle is tightly closed.",
        7: "Unscrew and connect the tubing set Direction of flow to connect patient and machine in suction special lecture",
    },
    "qWl3XdJ4rck": {
        4: "I have been working as an assistant at Eminent Hospice for 6 months now.",
        8: "With the help of Eminent Hospice during a difficult time for about a month before his death,",
        10: "Again, the grass was consumed, this sheet was weird, and then the hospital bed, then the wheelchair walker.",
    },
    "jsPCywsMe5Y": {
        3: "Hello, I work at Eminent Hospice as a Hospice Nurse.",
        17: "This is how I started Hospice.",
        43: "We decided to move the patient to the living room so the family could be together more easily.",
    },
    "xnI28GlZwZI": {
        4: "Hello m, you are a nervous person who works in Eminent Hospice.",
        6: "Yesterday was when I first started working on the hospice.",
        25: "If you have liver disease, use Liver Disease. If you have lung disease, use Lung Disease.",
        28: "Many Korean patients have neurologic diseases such as Parkinson's disease.",
        29: "Other patients may have related neurologic conditions.",
        30: "People become hospice patients",
        73: "Hospice provides patients with the medical supplies they need.",
    },
}

GLOBAL_REPLACEMENTS = {
    "physicist for life Sust is an abbreviation for Stunning Trimman": "Physician Orders for Life-Sustaining Treatment (POLST)",
    "cardiopulmonary aquatic therapy": "cardiopulmonary resuscitation",
    "company for the disabled": "funeral home",
    "Serving service company": "answering service company",
    "serving service company": "answering service company",
    "Eminent Peace Care": "Eminent Hospice Care",
    "Death War Poetry": "death worksheet",
    "Death Worksheet": "death worksheet",
    "Death Watch": "death worksheet",
    "Death War": "death worksheet",
    "Spieth Office": "hospice office",
    "Spieth company": "hospice company",
    "disabled company": "funeral home",
    "disability company": "funeral home",
    "makeup company": "cremation company",
    "advance directive Adce Tiv": "advance directive",
    "Adce Tiv": "advance directive",
    "cardiopulmonary aquatic therapy": "cardiopulmonary resuscitation",
    "Fire Demon Police": "fire department and police",
    "County Corona": "County Coroner",
    "Kaoni Corona": "County Coroner",
    "A Eminent Spieth": "Eminent Hospice",
    "Bath nurse": "hospice aide",
    "bath nurse": "hospice aide",
    "Horses and animals": "companionship and conversation",
    "horses and animals": "companionship and conversation",
    "potion drive. Drop it with brown rice.": "It is usually given as liquid drops under the tongue using a small syringe or dropper.",
    "You can connect the key directly to the oxygen device.": "You can connect the cannula directly to the oxygen device.",
    "check the dream of the door": "check the dial that controls the amount of oxygen",
    "aspirator": "suction catheter",
    "finish the race": "complete the end-of-life journey",
    "case mini section": "case management section",
    "Chinese character referral": "patient referral",
    "DIGIZ": "diseases",
    "Hostess din rests": "hospice has improved",
    "Hostess": "Hospice",
    "hostess": "hospice",
    "Spieth": "hospice",
    "Folst's": "POLST",
    "Holst's": "POLST",
    "Folst": "POLST",
    "Holst": "POLST",
    "holst": "POLST",
    "polest": "POLST",
    "Poles": "POLST",
    "Holsts": "POLST",
    "Line One": "911",
    "not attempt search option": "the option 'Do Not Attempt Resuscitation'",
    "What is the CP and prayer incident?": "CPR and similar emergency procedures",
    "Comfort Bones at the patient’s current location": "Comfort care at the patient's current location",
    "Of Arshal": "of artificial nutrition",
    "nose line": "nasogastric tube",
    "phase tubes": "feeding tubes",
}


def parse_srt(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    entries: list[dict[str, object]] = []
    for block in re.split(r"\n{2,}", text):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        entries.append(
            {
                "number": int(lines[0]),
                "timing": lines[1].strip(),
                "text": " ".join(line.strip() for line in lines[2:] if line.strip()),
            }
        )
    return entries


def write_srt(path: Path, entries: list[dict[str, object]]) -> None:
    path.write_text(
        "\n\n".join(
            f"{entry['number']}\n{entry['timing']}\n{entry['text']}"
            for entry in entries
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    applied = 0
    for video_id, folder in VIDEO_FOLDERS.items():
        corrections = CORRECTIONS.get(video_id, {})
        path = folder / "en-subtitles.srt"
        entries = parse_srt(path)
        by_number = {int(entry["number"]): entry for entry in entries}

        missing = sorted(set(corrections) - set(by_number))
        if missing:
            raise ValueError(f"{video_id} is missing cues: {missing}")

        for cue, corrected_text in corrections.items():
            by_number[cue]["text"] = corrected_text
            applied += 1
        for entry in entries:
            text = str(entry["text"])
            for incorrect, replacement in GLOBAL_REPLACEMENTS.items():
                text = text.replace(incorrect, replacement)
            text = re.sub(r"\brace\b", "end of life", text, flags=re.IGNORECASE)
            text = re.sub(r"\brain\b", "pain", text, flags=re.IGNORECASE)
            entry["text"] = text
        write_srt(path, entries)
        print(f"{video_id}: applied {len(corrections)} cue corrections and terminology cleanup")

    print(f"Applied {applied} cue corrections and terminology cleanup across {len(VIDEO_FOLDERS)} videos")


if __name__ == "__main__":
    main()
