from __future__ import annotations

from pathlib import Path
from typing import Any

ORACLE_SCHEMA_VERSION = "1.0.0"
ORACLE_MODEL_VERSION = "three-coin-change-rules-v1"

TRIGRAMS = {
    "111": {"key": "qian", "zh": "乾", "en": "Heaven", "image": "天", "motion": "initiative and creative force"},
    "110": {"key": "dui", "zh": "兑", "en": "Lake", "image": "泽", "motion": "exchange, openness, and persuasion"},
    "101": {"key": "li", "zh": "离", "en": "Fire", "image": "火", "motion": "clarity, visibility, and discernment"},
    "100": {"key": "zhen", "zh": "震", "en": "Thunder", "image": "雷", "motion": "activation, surprise, and movement"},
    "011": {"key": "xun", "zh": "巽", "en": "Wind", "image": "风", "motion": "gradual influence, entry, and adaptation"},
    "010": {"key": "kan", "zh": "坎", "en": "Water", "image": "水", "motion": "risk, depth, and repeated testing"},
    "001": {"key": "gen", "zh": "艮", "en": "Mountain", "image": "山", "motion": "limits, stillness, and deliberate stopping"},
    "000": {"key": "kun", "zh": "坤", "en": "Earth", "image": "地", "motion": "receptivity, support, and patient development"},
}

# King Wen number, lower trigram, upper trigram, Chinese name, English title,
# modern theme. The pair mapping is deterministic; interpretation never changes
# the generated structure.
HEXAGRAM_ROWS = [
    (1, "qian", "qian", "乾", "The Creative", "initiative needs purpose and disciplined follow-through"),
    (2, "kun", "kun", "坤", "The Receptive", "progress comes through support, patience, and responsiveness"),
    (3, "zhen", "kan", "屯", "Difficulty at the Beginning", "a new beginning needs structure before speed"),
    (4, "kan", "gen", "蒙", "Youthful Learning", "uncertainty calls for questions, instruction, and humility"),
    (5, "qian", "kan", "需", "Waiting", "prepare carefully while timing develops"),
    (6, "kan", "qian", "讼", "Conflict", "clarify facts and limits before pushing the dispute"),
    (7, "kan", "kun", "师", "Collective Discipline", "coordination requires clear roles and responsible leadership"),
    (8, "kun", "kan", "比", "Holding Together", "commitment grows through trust and chosen alignment"),
    (9, "qian", "xun", "小畜", "Small Accumulating", "small restraints and steady preparation build leverage"),
    (10, "dui", "qian", "履", "Treading Carefully", "move with awareness of power, etiquette, and consequence"),
    (11, "qian", "kun", "泰", "Peace", "different forces can cooperate when exchange remains open"),
    (12, "kun", "qian", "否", "Standstill", "do not force growth where communication and alignment are blocked"),
    (13, "li", "qian", "同人", "Fellowship", "shared purpose matters more than superficial agreement"),
    (14, "qian", "li", "大有", "Great Possession", "abundance needs stewardship, visibility, and proportion"),
    (15, "gen", "kun", "谦", "Modesty", "quiet competence creates room for sustainable influence"),
    (16, "kun", "zhen", "豫", "Enthusiasm", "mobilize energy without letting excitement replace preparation"),
    (17, "zhen", "dui", "随", "Following", "adapt to what is timely without surrendering discernment"),
    (18, "xun", "gen", "蛊", "Repairing Decay", "old damage must be named, cleaned, and given a new system"),
    (19, "dui", "kun", "临", "Approach", "influence is growing; meet it with attention and responsibility"),
    (20, "kun", "xun", "观", "Contemplation", "step back and observe the pattern before intervening"),
    (21, "zhen", "li", "噬嗑", "Biting Through", "a clear obstacle needs a proportionate and decisive response"),
    (22, "li", "gen", "贲", "Grace", "presentation helps, but form must continue to serve substance"),
    (23, "kun", "gen", "剥", "Splitting Apart", "remove what can no longer support the whole"),
    (24, "zhen", "kun", "复", "Return", "a small return to the right path matters more than dramatic correction"),
    (25, "zhen", "qian", "无妄", "Innocence", "act from what is real rather than from manipulation or fantasy"),
    (26, "qian", "gen", "大畜", "Great Accumulating", "contain strength until knowledge and timing are sufficient"),
    (27, "zhen", "gen", "颐", "Nourishment", "watch what you consume, repeat, and feed in others"),
    (28, "xun", "dui", "大过", "Great Exceeding", "the load is exceptional; reinforce the structure or reduce it"),
    (29, "kan", "kan", "坎", "The Abysmal", "repeated risk rewards skill, honesty, and a reliable method"),
    (30, "li", "li", "离", "The Clinging Fire", "clarity must attach to something worthy and sustainable"),
    (31, "gen", "dui", "咸", "Influence", "mutual responsiveness works better than pressure"),
    (32, "xun", "zhen", "恒", "Duration", "lasting change depends on rhythm rather than intensity"),
    (33, "gen", "qian", "遁", "Retreat", "strategic distance can protect what matters"),
    (34, "qian", "zhen", "大壮", "Great Power", "strength is useful only when governed by restraint"),
    (35, "kun", "li", "晋", "Progress", "make constructive work visible and accept support"),
    (36, "li", "kun", "明夷", "Darkening of the Light", "protect clarity when the environment cannot receive it"),
    (37, "li", "xun", "家人", "The Family", "healthy systems begin with roles, habits, and truthful communication"),
    (38, "dui", "li", "睽", "Opposition", "difference can clarify perspective without requiring total agreement"),
    (39, "gen", "kan", "蹇", "Obstruction", "change route, seek help, and stop treating resistance as a dare"),
    (40, "kan", "zhen", "解", "Release", "resolve the binding issue, then simplify the aftermath"),
    (41, "dui", "gen", "损", "Decrease", "intentional reduction can restore balance and focus"),
    (42, "zhen", "xun", "益", "Increase", "growth is strongest when benefit is shared and well directed"),
    (43, "qian", "dui", "夬", "Breakthrough", "state the decision clearly and avoid theatrical aggression"),
    (44, "xun", "qian", "姤", "Coming to Meet", "a small influence can become powerful; examine it early"),
    (45, "kun", "dui", "萃", "Gathering Together", "concentration needs a center, a purpose, and preparation"),
    (46, "xun", "kun", "升", "Pushing Upward", "patient effort and the right support enable gradual ascent"),
    (47, "kan", "dui", "困", "Oppression", "when resources are constrained, preserve integrity and essentials"),
    (48, "xun", "kan", "井", "The Well", "renew the shared source instead of only changing the container"),
    (49, "li", "dui", "革", "Revolution", "change becomes legitimate when timing, need, and trust align"),
    (50, "xun", "li", "鼎", "The Cauldron", "transform raw material into culture, capability, and shared value"),
    (51, "zhen", "zhen", "震", "The Arousing", "shock reveals readiness; recover your center before acting"),
    (52, "gen", "gen", "艮", "Keeping Still", "stop at the right boundary and let attention settle"),
    (53, "gen", "xun", "渐", "Gradual Development", "stable progress follows sequence, fit, and patience"),
    (54, "dui", "zhen", "归妹", "The Marrying Maiden", "limited influence requires realism about role and timing"),
    (55, "li", "zhen", "丰", "Abundance", "use the bright moment fully without assuming it will remain"),
    (56, "gen", "li", "旅", "The Traveler", "when you are not at home, travel light and respect local limits"),
    (57, "xun", "xun", "巽", "The Gentle Wind", "subtle influence works through repetition and precise entry"),
    (58, "dui", "dui", "兑", "The Joyous Lake", "open exchange creates energy when sincerity anchors it"),
    (59, "kan", "xun", "涣", "Dispersion", "dissolve rigidity and reconnect around a meaningful center"),
    (60, "dui", "kan", "节", "Limitation", "use limits that protect flow rather than limits that suffocate it"),
    (61, "dui", "xun", "中孚", "Inner Truth", "credibility grows when inner intent and outward action match"),
    (62, "gen", "zhen", "小过", "Small Exceeding", "attend to details and modest corrections, not grand gestures"),
    (63, "li", "kan", "既济", "After Completion", "success still needs maintenance, vigilance, and small corrections"),
    (64, "kan", "li", "未济", "Before Completion", "the transition is not finished; sequence the final steps carefully"),
]

HEXAGRAMS = {
    (lower, upper): {
        "number": number,
        "name_zh": name_zh,
        "name_en": name_en,
        "theme": theme,
        "unicode": chr(0x4DC0 + number - 1),
    }
    for number, lower, upper, name_zh, name_en, theme in HEXAGRAM_ROWS
}

LINE_POSITIONS = {
    1: "the beginning: motives, preparation, and the first practical step",
    2: "the inner relationship: cooperation, support, and a workable response",
    3: "the threshold: pressure, overreach, and the cost of crossing too quickly",
    4: "the outer environment: influence, access, and how the situation meets others",
    5: "the decision center: responsibility, leadership, and what should guide the whole",
    6: "the culmination: excess, completion, and knowing when the pattern must change",
}

CATEGORY_ACTIONS = {
    "general": "Choose one action that tests the reading without making the outcome irreversible.",
    "career": "Translate the pattern into one deliverable, one boundary, and one conversation at work.",
    "wealth": "Set a cost ceiling, validation period, and exit condition before committing resources.",
    "relationship": "State one expectation as a concrete request and confirm what the other person can actually offer.",
    "decision": "Define the smallest reversible test before making the larger commitment.",
    "growth": "Observe the habit the reading points to, then practice one different response for seven days.",
}


def interpret_cast(
    lines: list[int],
    *,
    category: str = "general",
    horizon: str = "one_month",
) -> dict[str, Any]:
    if len(lines) != 6 or any(value not in {6, 7, 8, 9} for value in lines):
        raise ValueError("lines must contain six values from 6, 7, 8, or 9, ordered bottom to top")
    if category not in CATEGORY_ACTIONS:
        raise ValueError("unsupported oracle category")

    primary_bits = ["1" if value in {7, 9} else "0" for value in lines]
    relating_bits = [
        "0" if value == 9 else "1" if value == 6 else primary_bits[index]
        for index, value in enumerate(lines)
    ]
    moving = [index + 1 for index, value in enumerate(lines) if value in {6, 9}]
    primary = _hexagram(primary_bits)
    relating = _hexagram(relating_bits)

    if not moving:
        change_dynamic = "No line is changing. Read the primary hexagram as a stable snapshot and avoid inventing urgency."
    else:
        positions = "; ".join(LINE_POSITIONS[position] for position in moving)
        change_dynamic = f"Changing lines {', '.join(map(str, moving))} emphasize {positions}."

    if len(moving) <= 2:
        direction = (
            f"The primary pattern remains central. The relating hexagram, "
            f"{relating['name_en']}, shows the direction created by the specific changing line or lines."
        )
    else:
        direction = (
            f"With {len(moving)} changing lines, the situation is highly transitional. "
            f"Give greater weight to the movement toward {relating['name_en']} than to a fixed prediction."
        )

    return {
        "schema_version": ORACLE_SCHEMA_VERSION,
        "model_version": ORACLE_MODEL_VERSION,
        "method": "three_coin",
        "horizon": horizon,
        "category": category,
        "lines": [
            {
                "position": index + 1,
                "value": value,
                "yin_yang": "yang" if value in {7, 9} else "yin",
                "moving": value in {6, 9},
            }
            for index, value in enumerate(lines)
        ],
        "moving_lines": moving,
        "primary": primary,
        "relating": relating,
        "interpretation": {
            "current_state": (
                f"{primary['name_en']} describes the current structure: {primary['theme']}. "
                f"The lower trigram points to {primary['lower']['motion']}; "
                f"the upper trigram frames it through {primary['upper']['motion']}."
            ),
            "change_dynamic": change_dynamic,
            "direction": direction,
            "action": CATEGORY_ACTIONS[category],
            "boundary": (
                "Treat the reading as a structured reflection on change, not a guarantee. "
                "Do not use it as the sole basis for medical, legal, financial, or safety-critical decisions."
            ),
        },
        "evidence": [
            {
                "id": "oracle.cast.lines",
                "rule_id": "three_coin_sum_6_7_8_9",
                "description": "Six three-coin totals supplied bottom to top.",
            },
            {
                "id": "oracle.hexagram.primary",
                "rule_id": "king_wen_trigram_pair_v1",
                "description": f"Primary hexagram mapped to King Wen number {primary['number']}.",
            },
            {
                "id": "oracle.hexagram.relating",
                "rule_id": "moving_lines_invert_v1",
                "description": f"Moving yin and yang lines inverted to King Wen number {relating['number']}.",
            },
        ],
    }


def _hexagram(bits: list[str]) -> dict[str, Any]:
    lower = TRIGRAMS["".join(bits[:3])]
    upper = TRIGRAMS["".join(bits[3:])]
    row = HEXAGRAMS[(lower["key"], upper["key"])]
    return {
        **row,
        "lower": lower,
        "upper": upper,
        "binary_bottom_up": "".join(bits),
    }


def oracle_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "i-ching-oracle-v1.schema.json"
