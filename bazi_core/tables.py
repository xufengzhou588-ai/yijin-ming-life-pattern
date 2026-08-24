STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

STEM_ELEMENT = {
    "甲": "wood",
    "乙": "wood",
    "丙": "fire",
    "丁": "fire",
    "戊": "earth",
    "己": "earth",
    "庚": "metal",
    "辛": "metal",
    "壬": "water",
    "癸": "water",
}

STEM_YIN_YANG = {
    "甲": "yang",
    "乙": "yin",
    "丙": "yang",
    "丁": "yin",
    "戊": "yang",
    "己": "yin",
    "庚": "yang",
    "辛": "yin",
    "壬": "yang",
    "癸": "yin",
}

BRANCH_ELEMENT = {
    "子": "water",
    "丑": "earth",
    "寅": "wood",
    "卯": "wood",
    "辰": "earth",
    "巳": "fire",
    "午": "fire",
    "未": "earth",
    "申": "metal",
    "酉": "metal",
    "戌": "earth",
    "亥": "water",
}

BRANCH_YIN_YANG = {
    "子": "yang",
    "丑": "yin",
    "寅": "yang",
    "卯": "yin",
    "辰": "yang",
    "巳": "yin",
    "午": "yang",
    "未": "yin",
    "申": "yang",
    "酉": "yin",
    "戌": "yang",
    "亥": "yin",
}

HIDDEN_STEMS = {
    "子": [("癸", "main", 1.0)],
    "丑": [("己", "main", 0.6), ("癸", "middle", 0.3), ("辛", "residual", 0.1)],
    "寅": [("甲", "main", 0.6), ("丙", "middle", 0.3), ("戊", "residual", 0.1)],
    "卯": [("乙", "main", 1.0)],
    "辰": [("戊", "main", 0.6), ("乙", "middle", 0.3), ("癸", "residual", 0.1)],
    "巳": [("丙", "main", 0.6), ("戊", "middle", 0.3), ("庚", "residual", 0.1)],
    "午": [("丁", "main", 0.7), ("己", "middle", 0.3)],
    "未": [("己", "main", 0.6), ("丁", "middle", 0.3), ("乙", "residual", 0.1)],
    "申": [("庚", "main", 0.6), ("壬", "middle", 0.3), ("戊", "residual", 0.1)],
    "酉": [("辛", "main", 1.0)],
    "戌": [("戊", "main", 0.6), ("辛", "middle", 0.3), ("丁", "residual", 0.1)],
    "亥": [("壬", "main", 0.7), ("甲", "middle", 0.3)],
}

ELEMENTS = ["wood", "fire", "earth", "metal", "water"]
TEN_GODS = [
    "peer",
    "rob_wealth",
    "eating_god",
    "hurting_officer",
    "direct_wealth",
    "indirect_wealth",
    "direct_officer",
    "seven_killings",
    "direct_resource",
    "indirect_resource",
]

GENERATES = {
    "wood": "fire",
    "fire": "earth",
    "earth": "metal",
    "metal": "water",
    "water": "wood",
}

CONTROLS = {
    "wood": "earth",
    "earth": "water",
    "water": "fire",
    "fire": "metal",
    "metal": "wood",
}

JIE_QI_NAMES = {
    0: "冬至",
    1: "小寒",
    2: "大寒",
    3: "立春",
    4: "雨水",
    5: "惊蛰",
    6: "春分",
    7: "清明",
    8: "谷雨",
    9: "立夏",
    10: "小满",
    11: "芒种",
    12: "夏至",
    13: "小暑",
    14: "大暑",
    15: "立秋",
    16: "处暑",
    17: "白露",
    18: "秋分",
    19: "寒露",
    20: "霜降",
    21: "立冬",
    22: "小雪",
    23: "大雪",
}

JIE_INDICES = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23}
