      const appBuildVersion = "123";
      const appUrl = new URL(window.location.href);
      if (appUrl.searchParams.get("v") !== appBuildVersion) {
        appUrl.searchParams.set("v", appBuildVersion);
        window.history.replaceState(null, "", appUrl);
      }
      const form = document.querySelector("#form");
      const statusEl = document.querySelector("#status");
      const generateButton = document.querySelector("#generate-button");
      const appState = window.MING_STATE;
      const historyStorageKey = appState.storageKeys.history;
      const profileStorageKey = appState.storageKeys.profile;
      const productEventStorageKey = appState.storageKeys.productEvents;
      const oracleJournalStorageKey = appState.storageKeys.oracleJournal;
      const dailyCheckInStorageKey = appState.storageKeys.dailyCheckins;
      const fetchJson = window.MINGApi.fetchJson;
      const releaseMode = new URLSearchParams(window.location.search).get("release") || "storekit";
      const isFreeFirstRelease = releaseMode === "free_first";
      const ritualState = appState.ritualState;
      const oracleState = appState.oracleState;
      const resultState = appState.resultState;
      let currentLang = navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
      let ritualReturnFocus = null;
      const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const copy = window.MING_COPY || { zh: {}, en: {} };
      const elementLabels = {
        zh: { wood: "木", fire: "火", earth: "土", metal: "金", water: "水" },
        en: { wood: "木", fire: "火", earth: "土", metal: "金", water: "水" }
      };
      const dailyStemCycle = [
        { char: "甲", element: "wood", yinYang: "yang" },
        { char: "乙", element: "wood", yinYang: "yin" },
        { char: "丙", element: "fire", yinYang: "yang" },
        { char: "丁", element: "fire", yinYang: "yin" },
        { char: "戊", element: "earth", yinYang: "yang" },
        { char: "己", element: "earth", yinYang: "yin" },
        { char: "庚", element: "metal", yinYang: "yang" },
        { char: "辛", element: "metal", yinYang: "yin" },
        { char: "壬", element: "water", yinYang: "yang" },
        { char: "癸", element: "water", yinYang: "yin" }
      ];
      const dailyBranchCycle = [
        { char: "子", element: "water", yinYang: "yang" },
        { char: "丑", element: "earth", yinYang: "yin" },
        { char: "寅", element: "wood", yinYang: "yang" },
        { char: "卯", element: "wood", yinYang: "yin" },
        { char: "辰", element: "earth", yinYang: "yang" },
        { char: "巳", element: "fire", yinYang: "yin" },
        { char: "午", element: "fire", yinYang: "yang" },
        { char: "未", element: "earth", yinYang: "yin" },
        { char: "申", element: "metal", yinYang: "yang" },
        { char: "酉", element: "metal", yinYang: "yin" },
        { char: "戌", element: "earth", yinYang: "yang" },
        { char: "亥", element: "water", yinYang: "yin" }
      ];
      const elementGenerates = { wood: "fire", fire: "earth", earth: "metal", metal: "water", water: "wood" };
      const elementControls = { wood: "earth", earth: "water", water: "fire", fire: "metal", metal: "wood" };
      const dailyThemeKeys = ["career", "wealth", "relationship", "stability"];
      const stemRomanization = {
        "甲": "Jia",
        "乙": "Yi",
        "丙": "Bing",
        "丁": "Ding",
        "戊": "Wu",
        "己": "Ji",
        "庚": "Geng",
        "辛": "Xin",
        "壬": "Ren",
        "癸": "Gui"
      };
      const branchRomanization = {
        "子": "Zi",
        "丑": "Chou",
        "寅": "Yin",
        "卯": "Mao",
        "辰": "Chen",
        "巳": "Si",
        "午": "Wu",
        "未": "Wei",
        "申": "Shen",
        "酉": "You",
        "戌": "Xu",
        "亥": "Hai"
      };
      const tenGodLabels = {
        zh: {
          peer: "比肩",
          rob_wealth: "劫财",
          eating_god: "食神",
          hurting_officer: "伤官",
          direct_wealth: "正财",
          indirect_wealth: "偏财",
          direct_officer: "正官",
          seven_killings: "七杀",
          direct_resource: "正印",
          indirect_resource: "偏印"
        },
        en: {
          peer: "比肩",
          rob_wealth: "劫财",
          eating_god: "食神",
          hurting_officer: "伤官",
          direct_wealth: "正财",
          indirect_wealth: "偏财",
          direct_officer: "正官",
          seven_killings: "七杀",
          direct_resource: "正印",
          indirect_resource: "偏印"
        }
      };
      const archetypes = {
        zh: {
          peer: { name: "独立建造者", gift: "从自己的判断出发并持续推进", tension: "在坚持主见时仍为合作留下空间" },
          rob_wealth: { name: "大胆协作者", gift: "快速进入竞争与资源流动", tension: "在机会变多前先讲清归属和边界" },
          eating_god: { name: "创造型匠人", gift: "把能力转成别人能体验的成果", tension: "让灵感进入稳定交付而不只停留在兴趣" },
          hurting_officer: { name: "规则挑战者", gift: "看见旧方法的问题并提出新解法", tension: "让锋利表达真正推动改变而非制造阻力" },
          direct_wealth: { name: "务实经营者", gift: "管理现实资源并追求可验证结果", tension: "避免为了稳定而错过必要的试验" },
          indirect_wealth: { name: "机会侦察者", gift: "捕捉市场、人脉和非标准机会", tension: "少开几个窗口，把最好的一项做深" },
          direct_officer: { name: "责任架构师", gift: "建立规则、承担责任并维持秩序", tension: "别让高标准变成对自己和他人的持续压力" },
          seven_killings: { name: "压力导航者", gift: "在挑战和紧迫环境中快速行动", tension: "分清真正的紧急与自己制造的紧急" },
          direct_resource: { name: "系统学习者", gift: "吸收可信知识并建立稳定理解", tension: "在准备充分之前也允许自己开始行动" },
          indirect_resource: { name: "战略观察者", gift: "发现别人忽略的联系和隐藏模式", tension: "把复杂判断及时翻译成一个可执行动作" }
        },
        en: {
          peer: { name: "The Independent Builder", gift: "moving from your own judgment with steady conviction", tension: "leaving room for collaboration without abandoning your center" },
          rob_wealth: { name: "The Bold Collaborator", gift: "moving quickly through competition and shared resources", tension: "clarifying ownership before opportunity gets crowded" },
          eating_god: { name: "The Creative Maker", gift: "turning ability into something other people can experience", tension: "giving inspiration a delivery date" },
          hurting_officer: { name: "The Rule Challenger", gift: "spotting what no longer works and proposing a sharper answer", tension: "making bold expression useful rather than merely loud" },
          direct_wealth: { name: "The Practical Steward", gift: "managing real resources toward tangible outcomes", tension: "letting stability support experimentation instead of replacing it" },
          indirect_wealth: { name: "The Opportunity Scout", gift: "noticing markets, people, and unconventional openings", tension: "closing a few tabs and developing the best one" },
          direct_officer: { name: "The Responsible Architect", gift: "building standards, roles, and dependable structure", tension: "keeping high standards from becoming permanent pressure" },
          seven_killings: { name: "The Pressure Navigator", gift: "acting decisively when the stakes rise", tension: "separating a real emergency from an internally produced one" },
          direct_resource: { name: "The Patient Scholar", gift: "building understanding from trusted knowledge", tension: "beginning before every instruction manual has been read" },
          indirect_resource: { name: "The Strategic Observer", gift: "seeing hidden connections others tend to miss", tension: "translating twelve mental steps into one timely action" }
        }
      };
      const traditionalTenGodLabels = {
        peer: "Bi Jian · 比肩",
        rob_wealth: "Jie Cai · 劫财 · Rob Wealth",
        eating_god: "Shi Shen · 食神 · Eating God",
        hurting_officer: "Shang Guan · 伤官 · Hurting Officer",
        direct_wealth: "Zheng Cai · 正财 · Direct Wealth",
        indirect_wealth: "Pian Cai · 偏财 · Indirect Wealth",
        direct_officer: "Zheng Guan · 正官 · Direct Officer",
        seven_killings: "Qi Sha · 七杀 · Seven Killings",
        direct_resource: "Zheng Yin · 正印 · Direct Resource",
        indirect_resource: "Pian Yin · 偏印 · Indirect Resource"
      };
      const rootExplanations = {
        peer: {
          body: "A same-element relationship associated with autonomy, identity, and acting from your own center.",
          aside: "In modern terms: your inner project manager has opinions."
        },
        rob_wealth: {
          body: "A traditional pattern describing competition, shared resources, and the need to clarify ownership and boundaries.",
          aside: "No one is literally stealing your wallet. The name had a flair for drama."
        },
        eating_god: {
          body: "An output pattern connected with creativity, enjoyment, craft, and turning ability into something others can experience.",
          aside: "Despite the name, lunch remains entirely optional."
        },
        hurting_officer: {
          body: "An expressive pattern linked to questioning rules, independent thinking, critique, and unconventional solutions.",
          aside: "No actual officer was harmed in the making of this chart."
        },
        direct_wealth: {
          body: "A resource pattern associated with practical value, steady management, commitments, and tangible results.",
          aside: "Less lottery ticket, more spreadsheet that actually gets opened."
        },
        indirect_wealth: {
          body: "A resource pattern associated with opportunity, markets, flexibility, networks, and non-routine possibilities.",
          aside: "Opportunity radar is useful. Fifteen open tabs, somewhat less so."
        },
        direct_officer: {
          body: "A structure pattern connected with responsibility, standards, roles, and working within clear expectations.",
          aside: "Your calendar may feel strangely validated."
        },
        seven_killings: {
          body: "A pressure-and-action pattern associated with challenge, urgency, courage, and functioning under demanding conditions.",
          aside: "It sounds dramatic. Your chart is not plotting a crime documentary."
        },
        direct_resource: {
          body: "A learning pattern connected with trusted knowledge, support, patient study, and organized understanding.",
          aside: "The part of you that reads the instructions before assembling the shelf."
        },
        indirect_resource: {
          body: "A learning pattern connected with intuition, synthesis, unconventional insight, and recognizing hidden connections.",
          aside: "Pattern recognition: excellent. Explaining all twelve mental steps: negotiable."
        }
      };
      const traitFactorLabels = {
        zh: {
          structured_output: "稳定产出能力",
          expressive_output: "表达与突破能力",
          responsibility: "责任承担",
          challenge_drive: "挑战驱动力",
          analysis_delay: "分析过久带来的延迟",
          independent_expression: "独立表达",
          self_direction: "自主推进",
          support_dependence: "对外部支持的依赖",
          rule_awareness: "规则意识",
          practical_follow_through: "现实执行与跟进",
          steady_output: "持续输出",
          rule_friction: "与规则产生摩擦",
          priority_competition: "优先级与资源竞争",
          structured_learning: "系统学习",
          pattern_learning: "模式识别与洞察",
          knowledge_expression: "知识转化与表达",
          premature_conclusion: "过早形成判断",
          stable_opportunity: "稳定机会获取",
          market_opportunity: "市场与项目机会",
          value_creation: "价值创造",
          commercial_expression: "商业表达",
          budget_awareness: "预算与成本意识",
          financial_rules: "财务规则",
          resource_buffer: "资源缓冲",
          resource_competition: "资源竞争与分散",
          opportunity_expansion: "机会扩张冲动",
          impulse_expression: "即时冲动",
          stable_support: "稳定支持",
          adaptive_support: "灵活支持",
          practical_care: "实际投入与照顾",
          boundary_competition: "边界与责任竞争",
          high_expectation: "高期待与强压力",
          role_pressure: "角色责任压力",
          communication_friction: "沟通摩擦"
        },
        en: {
          structured_output: "consistent output",
          expressive_output: "expressive breakthrough",
          responsibility: "responsibility",
          challenge_drive: "challenge drive",
          analysis_delay: "analysis delay",
          independent_expression: "independent expression",
          self_direction: "self-direction",
          support_dependence: "support dependence",
          rule_awareness: "rule awareness",
          practical_follow_through: "practical follow-through",
          steady_output: "steady output",
          rule_friction: "rule friction",
          priority_competition: "priority competition",
          structured_learning: "structured learning",
          pattern_learning: "pattern recognition",
          knowledge_expression: "knowledge expression",
          premature_conclusion: "premature conclusions",
          stable_opportunity: "stable opportunities",
          market_opportunity: "market opportunities",
          value_creation: "value creation",
          commercial_expression: "commercial expression",
          budget_awareness: "budget awareness",
          financial_rules: "financial rules",
          resource_buffer: "resource buffer",
          resource_competition: "resource competition",
          opportunity_expansion: "opportunity expansion",
          impulse_expression: "impulsive expression",
          stable_support: "stable support",
          adaptive_support: "adaptive support",
          practical_care: "practical care",
          boundary_competition: "boundary competition",
          high_expectation: "high expectations",
          role_pressure: "role pressure",
          communication_friction: "communication friction"
        }
      };
      const elementInsights = {
        wood: {
          tone: "成长、规划、表达和主动开拓",
          caution: "持续性和边界感需要被稳定下来",
          advice: "适合把想法拆成阶段计划，用固定节奏推进。"
        },
        fire: {
          tone: "表达、判断、热情和被看见",
          caution: "容易受情绪、节奏或外部反馈影响",
          advice: "适合先明确目标，再决定何时展示和推进。"
        },
        earth: {
          tone: "承载、稳定、整合和落地",
          caution: "变化速度过快时，容易出现消化和取舍压力",
          advice: "适合建立预算、流程和边界，让事情更稳地落地。"
        },
        metal: {
          tone: "规则、效率、判断和取舍",
          caution: "标准强时容易显得紧，合作中要留出沟通弹性",
          advice: "适合做筛选、制定规则、优化结构，但要避免过早否定。"
        },
        water: {
          tone: "洞察、学习、流动和风险感知",
          caution: "想得多时容易延迟行动，需要清晰的决策触发点",
          advice: "适合用信息优势做判断，同时给行动设置明确期限。"
        }
      };
      const tenGodInsights = {
        peer: "自我驱动和独立意识较明显，适合在清晰规则中发挥主见。",
        rob_wealth: "竞争感和资源流动感较强，合作时要提前讲清边界。",
        eating_god: "表达、产出和创造性较容易被看见，适合稳定输出。",
        hurting_officer: "突破和质疑精神较明显，适合创新，但要注意表达方式。",
        direct_wealth: "对现实资源、效率和结果较敏感，适合做具体目标管理。",
        indirect_wealth: "机会嗅觉和灵活性较强，适合探索，但要控制分散。",
        direct_officer: "规则意识、责任感和秩序感较强，适合制度化推进。",
        seven_killings: "压力驱动和行动强度较高，适合挑战型任务，但要控制风险。",
        direct_resource: "学习、吸收和获得支持的能力较明显，适合深度积累。",
        indirect_resource: "洞察、联想和非线性思考较强，适合研究和策略判断。"
      };
      const classicByElement = {
        wood: {
          hexagram: "震 / 巽",
          line: "洊雷，震；君子以恐惧修省。随风，巽；君子以申命行事。",
          meaning: "木象对应生发、启动、传播。结构里木旺时，适合用作行动力和扩展力；木弱时，要补足规划、学习和持续表达。"
        },
        fire: {
          hexagram: "离",
          line: "明两作，离；大人以继明照于四方。",
          meaning: "火象对应显现、判断、表达和被看见。火旺时利于展示与决断；火弱时，目标感和外部表达需要被点亮。"
        },
        earth: {
          hexagram: "坤 / 艮",
          line: "地势坤，君子以厚德载物。兼山，艮；君子以思不出其位。",
          meaning: "土象对应承载、边界、稳定和消化。土旺时适合建制度与承接资源；土弱时，要注意稳定性、节奏和落地能力。"
        },
        metal: {
          hexagram: "乾 / 兑",
          line: "天行健，君子以自强不息。丽泽，兑；君子以朋友讲习。",
          meaning: "金象对应规则、判断、效率和取舍。金旺时利于标准化与决策；金弱时，要补足边界、纪律和筛选能力。"
        },
        water: {
          hexagram: "坎",
          line: "习坎，有孚，维心亨。",
          meaning: "水象对应流动、风险、智慧和适应。水旺时善于洞察变化；水弱时，要补足信息收集、弹性和风险预案。"
        }
      };
      const elementInsightsEn = {
        wood: {
          tone: "growth, planning, expression, and active expansion",
          caution: "consistency and boundaries need extra support",
          advice: "Break ideas into staged plans and move forward with a steady rhythm."
        },
        fire: {
          tone: "expression, judgment, enthusiasm, and visibility",
          caution: "mood, pace, or external feedback may affect momentum",
          advice: "Clarify the goal first, then choose when to present and push forward."
        },
        earth: {
          tone: "stability, integration, responsibility, and execution",
          caution: "fast changes may create pressure around digestion and prioritization",
          advice: "Use budgets, processes, and boundaries to make things land steadily."
        },
        metal: {
          tone: "rules, efficiency, judgment, and selection",
          caution: "strong standards can feel rigid; leave room for communication",
          advice: "Use structure and standards, but avoid rejecting options too early."
        },
        water: {
          tone: "insight, learning, adaptability, and risk awareness",
          caution: "too much thinking may delay action; define decision triggers",
          advice: "Use information advantage, while setting clear deadlines for action."
        }
      };
      const tenGodInsightsEn = {
        peer: "Independent drive is more visible. It works best inside clear rules.",
        rob_wealth: "Competition and resource movement are more visible. Set partnership boundaries early.",
        eating_god: "Expression, output, and creativity are easier to notice. Stable production suits this pattern.",
        hurting_officer: "A questioning and breakthrough tendency is stronger. It supports innovation, but expression needs care.",
        direct_wealth: "Practical resources, efficiency, and results matter more. Concrete goal management suits this pattern.",
        indirect_wealth: "Opportunity sensing and flexibility are stronger. Exploration is useful, but dispersion needs control.",
        direct_officer: "Responsibility, order, and rule awareness are stronger. Institutional execution suits this pattern.",
        seven_killings: "Pressure-driven action is stronger. Challenge suits this pattern, but risk control matters.",
        direct_resource: "Learning, absorption, and support are more visible. Deep accumulation suits this pattern.",
        indirect_resource: "Insight, association, and non-linear thinking are stronger. Research and strategy suit this pattern."
      };
      const classicByElementEn = {
        wood: {
          hexagram: "Zhen / Xun",
          line: "Repeated thunder: Zhen. Following wind: Xun.",
          meaning: "Wood points to growth, activation, and propagation. When strong, it supports initiative; when weak, planning and sustained expression need support."
        },
        fire: {
          hexagram: "Li",
          line: "Brightness doubled: Li. The great person continues the light.",
          meaning: "Fire points to visibility, judgment, and expression. When strong, it supports presentation and decision; when weak, direction and visibility need to be lit up."
        },
        earth: {
          hexagram: "Kun / Gen",
          line: "Earth's condition is receptive. Mountain over mountain: Gen.",
          meaning: "Earth points to stability, boundaries, and digestion. When strong, it supports systems and responsibility; when weak, pace and grounding need attention."
        },
        metal: {
          hexagram: "Qian / Dui",
          line: "Heaven moves vigorously. Joined lakes: Dui.",
          meaning: "Metal points to rules, judgment, efficiency, and selection. When strong, it supports standards; when weak, discipline and boundaries need support."
        },
        water: {
          hexagram: "Kan",
          line: "Repeated abyss: with sincerity, the heart succeeds.",
          meaning: "Water points to flow, risk, wisdom, and adaptation. When strong, it supports sensing change; when weak, information gathering and flexibility need support."
        }
      };
      const locationData = {
        CN: {
          label: "中国",
          label_en: "China",
          regions: {
            "北京市": { label: "北京市", cities: { "北京市": { label: "北京市", timezone: "Asia/Shanghai", longitude: 116.4074, latitude: 39.9042 } } },
            "天津市": { label: "天津市", cities: { "天津市": { label: "天津市", timezone: "Asia/Shanghai", longitude: 117.2009, latitude: 39.0842 } } },
            "河北省": { label: "河北省", cities: { "石家庄市": { label: "石家庄市", timezone: "Asia/Shanghai", longitude: 114.5149, latitude: 38.0428 }, "唐山市": { label: "唐山市", timezone: "Asia/Shanghai", longitude: 118.1802, latitude: 39.6309 }, "保定市": { label: "保定市", timezone: "Asia/Shanghai", longitude: 115.4646, latitude: 38.8744 } } },
            "山西省": { label: "山西省", cities: { "太原市": { label: "太原市", timezone: "Asia/Shanghai", longitude: 112.5492, latitude: 37.8706 }, "大同市": { label: "大同市", timezone: "Asia/Shanghai", longitude: 113.3001, latitude: 40.0768 } } },
            "内蒙古自治区": { label: "内蒙古自治区", cities: { "呼和浩特市": { label: "呼和浩特市", timezone: "Asia/Shanghai", longitude: 111.7492, latitude: 40.8426 }, "包头市": { label: "包头市", timezone: "Asia/Shanghai", longitude: 109.8404, latitude: 40.6582 } } },
            "辽宁省": { label: "辽宁省", cities: { "沈阳市": { label: "沈阳市", timezone: "Asia/Shanghai", longitude: 123.4315, latitude: 41.8057 }, "大连市": { label: "大连市", timezone: "Asia/Shanghai", longitude: 121.6147, latitude: 38.914 } } },
            "吉林省": { label: "吉林省", cities: { "长春市": { label: "长春市", timezone: "Asia/Shanghai", longitude: 125.3235, latitude: 43.8171 }, "吉林市": { label: "吉林市", timezone: "Asia/Shanghai", longitude: 126.5494, latitude: 43.8378 } } },
            "黑龙江省": { label: "黑龙江省", cities: { "哈尔滨市": { label: "哈尔滨市", timezone: "Asia/Shanghai", longitude: 126.5349, latitude: 45.8038 }, "齐齐哈尔市": { label: "齐齐哈尔市", timezone: "Asia/Shanghai", longitude: 123.9182, latitude: 47.3543 } } },
            "上海市": { label: "上海市", cities: { "上海市": { label: "上海市", timezone: "Asia/Shanghai", longitude: 121.4737, latitude: 31.2304 } } },
            "江苏省": { label: "江苏省", cities: { "南京市": { label: "南京市", timezone: "Asia/Shanghai", longitude: 118.7969, latitude: 32.0603 }, "苏州市": { label: "苏州市", timezone: "Asia/Shanghai", longitude: 120.5853, latitude: 31.2989 }, "无锡市": { label: "无锡市", timezone: "Asia/Shanghai", longitude: 120.3119, latitude: 31.4912 } } },
            "浙江省": { label: "浙江省", cities: { "杭州市": { label: "杭州市", timezone: "Asia/Shanghai", longitude: 120.1551, latitude: 30.2741 }, "宁波市": { label: "宁波市", timezone: "Asia/Shanghai", longitude: 121.5503, latitude: 29.8739 }, "温州市": { label: "温州市", timezone: "Asia/Shanghai", longitude: 120.6994, latitude: 27.9949 } } },
            "安徽省": { label: "安徽省", cities: { "合肥市": { label: "合肥市", timezone: "Asia/Shanghai", longitude: 117.2272, latitude: 31.8206 }, "芜湖市": { label: "芜湖市", timezone: "Asia/Shanghai", longitude: 118.4331, latitude: 31.3525 } } },
            "福建省": { label: "福建省", cities: { "福州市": { label: "福州市", timezone: "Asia/Shanghai", longitude: 119.2965, latitude: 26.0745 }, "厦门市": { label: "厦门市", timezone: "Asia/Shanghai", longitude: 118.0894, latitude: 24.4798 }, "泉州市": { label: "泉州市", timezone: "Asia/Shanghai", longitude: 118.6759, latitude: 24.8741 } } },
            "江西省": { label: "江西省", cities: { "南昌市": { label: "南昌市", timezone: "Asia/Shanghai", longitude: 115.8582, latitude: 28.6829 }, "赣州市": { label: "赣州市", timezone: "Asia/Shanghai", longitude: 114.935, latitude: 25.8311 } } },
            "山东省": { label: "山东省", cities: { "济南市": { label: "济南市", timezone: "Asia/Shanghai", longitude: 117.1201, latitude: 36.6512 }, "青岛市": { label: "青岛市", timezone: "Asia/Shanghai", longitude: 120.3826, latitude: 36.0671 }, "烟台市": { label: "烟台市", timezone: "Asia/Shanghai", longitude: 121.4479, latitude: 37.4638 } } },
            "河南省": { label: "河南省", cities: { "郑州市": { label: "郑州市", timezone: "Asia/Shanghai", longitude: 113.6254, latitude: 34.7466 }, "洛阳市": { label: "洛阳市", timezone: "Asia/Shanghai", longitude: 112.454, latitude: 34.6197 } } },
            "湖北省": { label: "湖北省", cities: { "武汉市": { label: "武汉市", timezone: "Asia/Shanghai", longitude: 114.3055, latitude: 30.5928 }, "宜昌市": { label: "宜昌市", timezone: "Asia/Shanghai", longitude: 111.2864, latitude: 30.6919 } } },
            "湖南省": { label: "湖南省", cities: { "长沙市": { label: "长沙市", timezone: "Asia/Shanghai", longitude: 112.9388, latitude: 28.2282 }, "株洲市": { label: "株洲市", timezone: "Asia/Shanghai", longitude: 113.1338, latitude: 27.8278 } } },
            "广东省": { label: "广东省", cities: { "广州市": { label: "广州市", timezone: "Asia/Shanghai", longitude: 113.2644, latitude: 23.1291 }, "深圳市": { label: "深圳市", timezone: "Asia/Shanghai", longitude: 114.0579, latitude: 22.5431 }, "佛山市": { label: "佛山市", timezone: "Asia/Shanghai", longitude: 113.1214, latitude: 23.0215 }, "东莞市": { label: "东莞市", timezone: "Asia/Shanghai", longitude: 113.7518, latitude: 23.0207 } } },
            "广西壮族自治区": { label: "广西壮族自治区", cities: { "南宁市": { label: "南宁市", timezone: "Asia/Shanghai", longitude: 108.3669, latitude: 22.817 }, "桂林市": { label: "桂林市", timezone: "Asia/Shanghai", longitude: 110.2902, latitude: 25.2736 } } },
            "海南省": { label: "海南省", cities: { "海口市": { label: "海口市", timezone: "Asia/Shanghai", longitude: 110.1983, latitude: 20.0442 }, "三亚市": { label: "三亚市", timezone: "Asia/Shanghai", longitude: 109.5119, latitude: 18.2528 } } },
            "重庆市": { label: "重庆市", cities: { "重庆市": { label: "重庆市", timezone: "Asia/Shanghai", longitude: 106.5516, latitude: 29.563 } } },
            "四川省": { label: "四川省", cities: { "成都市": { label: "成都市", timezone: "Asia/Shanghai", longitude: 104.0665, latitude: 30.5728 }, "绵阳市": { label: "绵阳市", timezone: "Asia/Shanghai", longitude: 104.6796, latitude: 31.4675 } } },
            "贵州省": { label: "贵州省", cities: { "贵阳市": { label: "贵阳市", timezone: "Asia/Shanghai", longitude: 106.6302, latitude: 26.6477 }, "遵义市": { label: "遵义市", timezone: "Asia/Shanghai", longitude: 106.9373, latitude: 27.7066 } } },
            "云南省": { label: "云南省", cities: { "昆明市": { label: "昆明市", timezone: "Asia/Shanghai", longitude: 102.8329, latitude: 24.8801 }, "大理市": { label: "大理市", timezone: "Asia/Shanghai", longitude: 100.2676, latitude: 25.6065 } } },
            "西藏自治区": { label: "西藏自治区", cities: { "拉萨市": { label: "拉萨市", timezone: "Asia/Shanghai", longitude: 91.1322, latitude: 29.6604 } } },
            "陕西省": { label: "陕西省", cities: { "西安市": { label: "西安市", timezone: "Asia/Shanghai", longitude: 108.9398, latitude: 34.3416 }, "咸阳市": { label: "咸阳市", timezone: "Asia/Shanghai", longitude: 108.7088, latitude: 34.3299 } } },
            "甘肃省": { label: "甘肃省", cities: { "兰州市": { label: "兰州市", timezone: "Asia/Shanghai", longitude: 103.8343, latitude: 36.0611 }, "天水市": { label: "天水市", timezone: "Asia/Shanghai", longitude: 105.7249, latitude: 34.5809 } } },
            "青海省": { label: "青海省", cities: { "西宁市": { label: "西宁市", timezone: "Asia/Shanghai", longitude: 101.7782, latitude: 36.6171 } } },
            "宁夏回族自治区": { label: "宁夏回族自治区", cities: { "银川市": { label: "银川市", timezone: "Asia/Shanghai", longitude: 106.2309, latitude: 38.4872 } } },
            "新疆维吾尔自治区": { label: "新疆维吾尔自治区", cities: { "乌鲁木齐市": { label: "乌鲁木齐市", timezone: "Asia/Shanghai", longitude: 87.6168, latitude: 43.8256 }, "喀什市": { label: "喀什市", timezone: "Asia/Shanghai", longitude: 75.9898, latitude: 39.4704 } } },
            "香港特别行政区": { label: "香港特别行政区", cities: { "香港": { label: "香港", timezone: "Asia/Hong_Kong", longitude: 114.1694, latitude: 22.3193 } } },
            "澳门特别行政区": { label: "澳门特别行政区", cities: { "澳门": { label: "澳门", timezone: "Asia/Macau", longitude: 113.5439, latitude: 22.1987 } } },
            "台湾省": { label: "台湾省", cities: { "台北市": { label: "台北市", timezone: "Asia/Taipei", longitude: 121.5654, latitude: 25.033 }, "高雄市": { label: "高雄市", timezone: "Asia/Taipei", longitude: 120.3014, latitude: 22.6273 } } }
          }
        },
        US: {
          label: "美国",
          label_en: "United States",
          regions: {
            "California": {
              label: "California",
              cities: {
                "Los Angeles": { label: "Los Angeles", timezone: "America/Los_Angeles", longitude: -118.2437, latitude: 34.0522 },
                "San Francisco": { label: "San Francisco", timezone: "America/Los_Angeles", longitude: -122.4194, latitude: 37.7749 },
                "San Diego": { label: "San Diego", timezone: "America/Los_Angeles", longitude: -117.1611, latitude: 32.7157 }
              }
            },
            "New York": {
              label: "New York",
              cities: {
                "New York City": { label: "New York City", timezone: "America/New_York", longitude: -74.006, latitude: 40.7128 },
                "Buffalo": { label: "Buffalo", timezone: "America/New_York", longitude: -78.8784, latitude: 42.8864 }
              }
            },
            "Texas": {
              label: "Texas",
              cities: {
                "Austin": { label: "Austin", timezone: "America/Chicago", longitude: -97.7431, latitude: 30.2672 },
                "Dallas": { label: "Dallas", timezone: "America/Chicago", longitude: -96.797, latitude: 32.7767 },
                "Houston": { label: "Houston", timezone: "America/Chicago", longitude: -95.3698, latitude: 29.7604 }
              }
            },
            "Illinois": {
              label: "Illinois",
              cities: {
                "Chicago": { label: "Chicago", timezone: "America/Chicago", longitude: -87.6298, latitude: 41.8781 }
              }
            },
            "Florida": {
              label: "Florida",
              cities: {
                "Miami": { label: "Miami", timezone: "America/New_York", longitude: -80.1918, latitude: 25.7617 },
                "Orlando": { label: "Orlando", timezone: "America/New_York", longitude: -81.3792, latitude: 28.5383 }
              }
            },
            "Washington": {
              label: "Washington",
              cities: {
                "Seattle": { label: "Seattle", timezone: "America/Los_Angeles", longitude: -122.3321, latitude: 47.6062 }
              }
            },
            "Massachusetts": {
              label: "Massachusetts",
              cities: {
                "Boston": { label: "Boston", timezone: "America/New_York", longitude: -71.0589, latitude: 42.3601 }
              }
            },
            "Colorado": {
              label: "Colorado",
              cities: {
                "Denver": { label: "Denver", timezone: "America/Denver", longitude: -104.9903, latitude: 39.7392 }
              }
            },
            "Arizona": {
              label: "Arizona",
              cities: {
                "Phoenix": { label: "Phoenix", timezone: "America/Phoenix", longitude: -112.074, latitude: 33.4484 }
              }
            },
            "Hawaii": {
              label: "Hawaii",
              cities: {
                "Honolulu": { label: "Honolulu", timezone: "Pacific/Honolulu", longitude: -157.8583, latitude: 21.3069 }
              }
            }
          }
        }
      };

      const chinaLocationLabelsEn = {
        "北京市": "Beijing",
        "天津市": "Tianjin",
        "河北省": "Hebei",
        "石家庄市": "Shijiazhuang",
        "唐山市": "Tangshan",
        "保定市": "Baoding",
        "山西省": "Shanxi",
        "太原市": "Taiyuan",
        "大同市": "Datong",
        "内蒙古自治区": "Inner Mongolia",
        "呼和浩特市": "Hohhot",
        "包头市": "Baotou",
        "辽宁省": "Liaoning",
        "沈阳市": "Shenyang",
        "大连市": "Dalian",
        "吉林省": "Jilin",
        "长春市": "Changchun",
        "吉林市": "Jilin City",
        "黑龙江省": "Heilongjiang",
        "哈尔滨市": "Harbin",
        "齐齐哈尔市": "Qiqihar",
        "上海市": "Shanghai",
        "江苏省": "Jiangsu",
        "南京市": "Nanjing",
        "苏州市": "Suzhou",
        "无锡市": "Wuxi",
        "浙江省": "Zhejiang",
        "杭州市": "Hangzhou",
        "宁波市": "Ningbo",
        "温州市": "Wenzhou",
        "安徽省": "Anhui",
        "合肥市": "Hefei",
        "芜湖市": "Wuhu",
        "福建省": "Fujian",
        "福州市": "Fuzhou",
        "厦门市": "Xiamen",
        "泉州市": "Quanzhou",
        "江西省": "Jiangxi",
        "南昌市": "Nanchang",
        "赣州市": "Ganzhou",
        "山东省": "Shandong",
        "济南市": "Jinan",
        "青岛市": "Qingdao",
        "烟台市": "Yantai",
        "河南省": "Henan",
        "郑州市": "Zhengzhou",
        "洛阳市": "Luoyang",
        "湖北省": "Hubei",
        "武汉市": "Wuhan",
        "宜昌市": "Yichang",
        "湖南省": "Hunan",
        "长沙市": "Changsha",
        "株洲市": "Zhuzhou",
        "广东省": "Guangdong",
        "广州市": "Guangzhou",
        "深圳市": "Shenzhen",
        "佛山市": "Foshan",
        "东莞市": "Dongguan",
        "广西壮族自治区": "Guangxi",
        "南宁市": "Nanning",
        "桂林市": "Guilin",
        "海南省": "Hainan",
        "海口市": "Haikou",
        "三亚市": "Sanya",
        "重庆市": "Chongqing",
        "四川省": "Sichuan",
        "成都市": "Chengdu",
        "绵阳市": "Mianyang",
        "贵州省": "Guizhou",
        "贵阳市": "Guiyang",
        "遵义市": "Zunyi",
        "云南省": "Yunnan",
        "昆明市": "Kunming",
        "大理市": "Dali",
        "西藏自治区": "Tibet",
        "拉萨市": "Lhasa",
        "陕西省": "Shaanxi",
        "西安市": "Xi'an",
        "咸阳市": "Xianyang",
        "甘肃省": "Gansu",
        "兰州市": "Lanzhou",
        "天水市": "Tianshui",
        "青海省": "Qinghai",
        "西宁市": "Xining",
        "宁夏回族自治区": "Ningxia",
        "银川市": "Yinchuan",
        "新疆维吾尔自治区": "Xinjiang",
        "乌鲁木齐市": "Urumqi",
        "喀什市": "Kashgar",
        "香港特别行政区": "Hong Kong",
        "香港": "Hong Kong",
        "澳门特别行政区": "Macao",
        "澳门": "Macao",
        "台湾省": "Taiwan",
        "台北市": "Taipei",
        "高雄市": "Kaohsiung"
      };

      function localizedLocationLabel(item, value) {
        if (currentLang !== "en") return item.label;
        return item.label_en || chinaLocationLabelsEn[value] || item.label;
      }

      function t(key) {
        return copy[currentLang][key] || copy.zh[key] || key;
      }

      function activeElementLabels() {
        return elementLabels[currentLang] || elementLabels.zh;
      }

      function activeTenGodLabels() {
        return tenGodLabels[currentLang] || tenGodLabels.zh;
      }

      function activeArchetypes() {
        return archetypes[currentLang] || archetypes.zh;
      }

      function activeElementInsights() {
        return currentLang === "en" ? elementInsightsEn : elementInsights;
      }

      function activeTenGodInsights() {
        return currentLang === "en" ? tenGodInsightsEn : tenGodInsights;
      }

      function activeClassicByElement() {
        return currentLang === "en" ? classicByElementEn : classicByElement;
      }

      function applyLanguage(lang) {
        currentLang = lang;
        document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
        document.title = t("pageTitle");
        document.querySelectorAll("[data-i18n]").forEach((node) => {
          node.textContent = t(node.dataset.i18n);
        });
        document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
          node.placeholder = t(node.dataset.i18nPlaceholder);
        });
        document.querySelector("#display_name").placeholder = t("displayNamePlaceholder");
        document.querySelector("#birth_date").setAttribute("aria-label", t("birthDateAria"));
        document.querySelector("#birth_period").setAttribute("aria-label", t("birthPeriodAria"));
        document.querySelector("#birth_hour").setAttribute("aria-label", t("birthHourAria"));
        document.querySelector("#birth_minute").setAttribute("aria-label", t("birthMinuteAria"));
        document.querySelector("#country").setAttribute("aria-label", t("countryAria"));
        document.querySelector("#region").setAttribute("aria-label", t("regionAria"));
        document.querySelector("#city").setAttribute("aria-label", t("cityAria"));
        document.querySelector("#birth_period option[value='AM']").textContent = t("am");
        document.querySelector("#birth_period option[value='PM']").textContent = t("pm");
        document.querySelector("#gender option[value='male']").textContent = t("genderMale");
        document.querySelector("#gender option[value='female']").textContent = t("genderFemale");
        document.querySelector("#gender option[value='unknown']").textContent = t("genderUnknown");
        Array.from(form.country.options).forEach((option) => {
          const country = locationData[option.value];
          option.textContent = currentLang === "en" ? (country.label_en || country.label) : country.label;
        });
        const selectedCountry = form.country.value;
        const selectedRegion = form.region.value;
        const selectedCity = form.city.value;
        if (selectedCountry && locationData[selectedCountry]) {
          populateRegions(selectedCountry, selectedRegion, selectedCity);
        }
        document.querySelectorAll("[data-lang]").forEach((button) => {
          button.classList.toggle("active", button.dataset.lang === lang);
        });
        refreshTimeOptionLabels();
        updateAccuracyNote();
        if (!generateButton.disabled) generateButton.textContent = t("generate");
        document.querySelector("#ritual-skip").textContent = t("ritualSkip");
        if (resultState.payload) {
          render(resultState.payload);
          statusEl.textContent = `${t("updated")}, ${resultState.generatedAt} ${t("schemaPassed")}`;
        }
        renderRecentCharts();
        renderOracleLines();
        renderOracleJournal();
        if (oracleState.result) renderOracleResult(oracleState.result);
        updateOracleButton();
        updateProAccessState();
      }

      function setMobilePane(pane, { scroll = true } = {}) {
        document.body.dataset.activeMobilePane = pane;
        if (pane === "oracle") document.body.dataset.oracleAssets = "ready";
        document.querySelectorAll("[data-mobile-pane]").forEach((section) => {
          section.classList.toggle("mobile-pane-active", section.dataset.mobilePane === pane);
        });
        document.querySelectorAll("[data-mobile-target]").forEach((button) => {
          const active = button.dataset.mobileTarget === pane;
          button.classList.toggle("active", active);
          button.setAttribute("aria-current", active ? "page" : "false");
        });
        if (!scroll || !window.matchMedia("(max-width: 640px)").matches) return;
        window.requestAnimationFrame(() => {
          const target = pane === "me"
            ? document.querySelector(".hero")
            : document.querySelector(`[data-mobile-pane="${pane}"]`);
          if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }

      initTimeSelectors();
      initAnnualStartYear();
      applyLanguage(currentLang);
      setMobilePane("me", { scroll: false });

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await generate({ animate: true });
      });

      document.querySelectorAll("[data-lang]").forEach((button) => {
        button.addEventListener("click", () => applyLanguage(button.dataset.lang));
      });

      document.querySelectorAll("[data-mobile-target]").forEach((button) => {
        button.addEventListener("click", () => setMobilePane(button.dataset.mobileTarget));
      });

      form.country.addEventListener("change", () => populateRegions(form.country.value));
      form.region.addEventListener("change", () => populateCities(form.country.value, form.region.value));
      form.city.addEventListener("change", updateLocationMetadata);
      document.querySelector("#birth_time_accuracy").addEventListener("change", updateAccuracyNote);
      document.querySelector("#oracle-cast-button").addEventListener("click", castOracleLine);
      document.querySelector("#oracle-reset-button").addEventListener("click", resetOracle);
      document.querySelector("#oracle-pro-unlock").addEventListener("click", async () => {
        try {
          await updateDemoEntitlement(true);
          setMobilePane("oracle");
        } catch (error) {
          const message = document.querySelector("#oracle-message");
          message.textContent = error.message;
          message.classList.add("error");
        }
      });
      document.querySelector("#oracle-journal-list").addEventListener("click", (event) => {
        const viewButton = event.target.closest("[data-oracle-view]");
        const deleteButton = event.target.closest("[data-oracle-delete]");
        if (viewButton) viewOracleJournalItem(viewButton.dataset.oracleView);
        if (deleteButton) deleteOracleJournalItem(deleteButton.dataset.oracleDelete);
      });
      document.querySelector("#history-list").addEventListener("click", (event) => {
        const loadButton = event.target.closest("[data-history-load]");
        const deleteButton = event.target.closest("[data-history-delete]");
        if (loadButton) loadRecentChart(loadButton.dataset.historyLoad);
        if (deleteButton) deleteRecentChart(deleteButton.dataset.historyDelete);
      });

      document.querySelectorAll(".tab").forEach((tab) => {
        tab.addEventListener("click", () => selectTab(tab.dataset.tab));
      });

      document.querySelector("#ritual-skip").addEventListener("click", () => {
        ritualState.skip = true;
        hideCalculationRitual();
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && ritualState.active) {
          ritualState.skip = true;
          hideCalculationRitual();
        }
      });

      async function loadEntitlement() {
        try {
          const { payload } = await fetchJson("/api/entitlement", { credentials: "same-origin" });
          if (!payload.ok) throw new Error("entitlement_unavailable");
          resultState.isPro = !isFreeFirstRelease && Boolean(payload.entitlement.is_pro);
          resultState.canDemoUnlock = !isFreeFirstRelease && Boolean(payload.entitlement.can_demo_unlock);
        } catch {
          resultState.isPro = false;
          resultState.canDemoUnlock = false;
        } finally {
          resultState.entitlementReady = true;
          updateProAccessState();
        }
      }

      function updateProAccessState() {
        const node = document.querySelector("#pro-access-state");
        if (node) node.textContent = resultState.isPro ? t("proUnlockedState") : t("proLockedState");
        updateOracleAccessState();
      }

      function updateOracleAccessState() {
        const section = document.querySelector(".theme-oracle");
        const unlockButton = document.querySelector("#oracle-pro-unlock");
        if (!section) return;
        section.classList.toggle("oracle-locked", !resultState.isPro);
        section.setAttribute("data-pro-access", resultState.isPro ? "unlocked" : "locked");
        if (unlockButton) {
          unlockButton.classList.toggle("hidden", resultState.isPro || !resultState.canDemoUnlock);
        }
        updateOracleButton();
      }

      async function updateDemoEntitlement(unlock) {
        if (isFreeFirstRelease) {
          throw new Error(t("proFreeFirstNote"));
        }
        statusEl.textContent = t("proUnlocking");
        const endpoint = unlock ? "/api/entitlement/demo-unlock" : "/api/entitlement/demo-lock";
        const { payload } = await fetchJson(endpoint, { method: "POST", credentials: "same-origin" });
        if (!payload.ok) throw new Error(payload.error || "entitlement_update_failed");
        trackProductEvent(unlock ? "test_report_unlocked" : "test_report_locked");
        resultState.isPro = Boolean(payload.entitlement.is_pro);
        resultState.canDemoUnlock = Boolean(payload.entitlement.can_demo_unlock);
        updateProAccessState();
        if (!resultState.isPro) {
          resultState.activePro = "";
          document.querySelector("#pro-report-view").innerHTML = "";
          resetOracle();
        } else if (resultState.requestedPro && resultState.payload) {
          resultState.activePro = resultState.requestedPro;
        }
        if (resultState.payload) render(resultState.payload);
        statusEl.textContent = resultState.isPro ? t("premiumPending") : t("proLockedStatus");
      }

      async function generate({ animate = false } = {}) {
        generateButton.disabled = true;
        generateButton.textContent = t("generating");
        statusEl.textContent = t("calculating");
        statusEl.classList.remove("error");
        let data;
        let ritualPromise = Promise.resolve();
        try {
          resultState.displayName = document.querySelector("#display_name").value.trim();
          data = buildRequestData();
          if (!shouldReplaceActiveProfile(data)) {
            statusEl.textContent = "";
            return;
          }
          ritualPromise = animate && !prefersReducedMotion ? playCalculationRitual() : Promise.resolve();
          const { payload } = await fetchJson("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
          });
          if (!payload.ok) throw new Error(payload.error || "生成失败");
          resultState.payload = payload.result;
          resultState.traits = payload.traits;
          resultState.annualOutlook = null;
          resultState.monthlyCompass = null;
          resultState.selectedMonthIndex = 0;
          resultState.activePro = "";
          resultState.requestedPro = "";
          resultState.proReports = {};
          resultState.generatedAt = new Date().toLocaleTimeString();
          await ritualPromise;
          if (animate && !prefersReducedMotion && !ritualState.skip) await completeCalculationRitual(payload.result, payload.traits);
          render(payload.result, payload.traits);
          trackProductEvent("reading_generated", {
            language: currentLang,
            country: data.country,
            time_accuracy: document.querySelector("#birth_time_accuracy").value,
            true_solar_time: Boolean(data.use_true_solar_time)
          });
          if (document.querySelector("#save_on_device").checked) {
            saveRecentChart(data);
          }
          const profileSaved = writeActiveProfile(data);
          document.body.dataset.hasReading = "true";
          statusEl.textContent = `${t("updated")}, ${resultState.generatedAt} ${t("schemaPassed")}${profileSaved ? ` ${t("profileSaved")}` : ""}`;
          if (animate) setMobilePane("today");
        } catch (error) {
          hideCalculationRitual();
          statusEl.textContent = error instanceof TypeError ? t("serviceUnavailable") : error.message;
          statusEl.classList.add("error");
        } finally {
          generateButton.disabled = false;
          generateButton.textContent = t("generate");
        }
      }

      async function playCalculationRitual() {
        ritualState.skip = false;
        ritualState.active = true;
        const overlay = document.querySelector("#calculation-ritual");
        ritualReturnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
        const phases = t("ritualPhases");
        const steps = t("ritualSteps");
        const location = locationData[form.country.value].regions[form.region.value].cities[form.city.value];
        document.querySelector("#ritual-context").textContent = t("ritualContext")(
          `${form.birth_date.value} ${String(form.birth_hour.value).padStart(2, "0")}:${String(form.birth_minute.value).padStart(2, "0")}`,
          localizedLocationLabel(location, form.city.value)
        );
        document.querySelector("#ritual-result-pillars").classList.add("hidden");
        document.querySelector("#ritual-result-pillars").innerHTML = "";
        document.querySelector("#ritual-stats").textContent = "";
        updateRitualProgress(0);
        document.querySelector("#ritual-steps").innerHTML = steps
          .map((step, index) => `<span class="ritual-step" data-ritual-step="${index}">${step}</span>`)
          .join("");
        overlay.classList.add("active");
        overlay.setAttribute("aria-hidden", "false");
        overlay.focus({ preventScroll: true });
        document.body.style.overflow = "hidden";
        for (let index = 0; index < phases.length; index += 1) {
          if (ritualState.skip) return;
          setRitualPhase(index, phases[index]);
          await ritualWait(390);
        }
      }

      function setRitualPhase(index, phase) {
        const symbol = document.querySelector("#ritual-symbol");
        symbol.classList.add("changing");
        window.setTimeout(() => {
          symbol.textContent = phase.symbol;
          symbol.classList.remove("changing");
        }, 150);
        document.querySelector("#ritual-title").textContent = phase.title;
        document.querySelector("#ritual-description").textContent = phase.body;
        updateRitualProgress((index + 1) * 18);
        document.querySelectorAll("[data-ritual-step]").forEach((step, stepIndex) => {
          step.classList.toggle("active", stepIndex === index);
          step.classList.toggle("done", stepIndex < index);
        });
      }

      async function completeCalculationRitual(core, traitOutput) {
        const chart = core.chart;
        const names = t("pillarNames");
        const keys = ["year", "month", "day", "hour"];
        document.querySelector("#ritual-symbol").textContent = "命";
        document.querySelector("#ritual-title").textContent = t("ritualComplete");
        document.querySelector("#ritual-description").textContent = "";
        const resultView = document.querySelector("#ritual-result-pillars");
        resultView.innerHTML = keys.map((key) => `<div class="ritual-result-pillar">
          <span>${names[key]}</span>
          <strong>${chart[key].stem.char}${chart[key].branch.char}</strong>
        </div>`).join("");
        resultView.classList.remove("hidden");
        document.querySelectorAll("[data-ritual-step]").forEach((step) => {
          step.classList.remove("active");
          step.classList.add("done");
        });
        const pillarNodes = Array.from(resultView.querySelectorAll(".ritual-result-pillar"));
        for (const pillar of pillarNodes) {
          if (ritualState.skip) return;
          pillar.classList.add("visible");
          await ritualWait(110);
        }
        document.querySelector("#ritual-stats").textContent = t("ritualStats")(
          core.evidence.length,
          Object.keys(traitOutput.traits).length
        );
        updateRitualProgress(100);
        await ritualWait(520);
        hideCalculationRitual();
      }

      function updateRitualProgress(value) {
        const percent = Math.max(0, Math.min(100, Math.round(value)));
        document.querySelector("#ritual-progress-fill").style.width = `${percent}%`;
        document.querySelector("#ritual-progress-value").textContent = `${percent}%`;
      }

      function ritualWait(ms) {
        return new Promise((resolve) => window.setTimeout(resolve, ms));
      }

      function hideCalculationRitual() {
        ritualState.active = false;
        const overlay = document.querySelector("#calculation-ritual");
        overlay.classList.remove("active");
        overlay.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        if (ritualReturnFocus && document.contains(ritualReturnFocus)) {
          ritualReturnFocus.focus({ preventScroll: true });
        }
        ritualReturnFocus = null;
      }

      function buildRequestData() {
        const data = Object.fromEntries(new FormData(form).entries());
        data.annual_start_year = document.querySelector("#annual_start_year").value;
        data.birth_datetime = buildBirthDateTime();
        data.use_true_solar_time = form.use_true_solar_time.checked;
        return data;
      }

      function updateAccuracyNote() {
        const accuracy = document.querySelector("#birth_time_accuracy").value;
        const keys = {
          exact: "accuracyExactNote",
          approximate: "accuracyApproximateNote",
          unknown: "accuracyUnknownNote"
        };
        document.querySelector("#accuracy-note").textContent = t(keys[accuracy]);
      }

      function initTimeSelectors() {
        document.querySelector("#birth_hour").innerHTML = Array.from({ length: 12 }, (_, index) => {
          const hour = index + 1;
          return `<option value="${hour}">${String(hour).padStart(2, "0")} ${t("hourUnit")}</option>`;
        }).join("");
        document.querySelector("#birth_minute").innerHTML = Array.from({ length: 60 }, (_, minute) => {
          return `<option value="${minute}">${String(minute).padStart(2, "0")} ${t("minuteUnit")}</option>`;
        }).join("");
        setBirthTime("", "AM", 8, 30);
      }

      function refreshTimeOptionLabels() {
        Array.from(document.querySelector("#birth_hour").options).forEach((option) => {
          option.textContent = `${String(option.value).padStart(2, "0")} ${t("hourUnit")}`;
        });
        Array.from(document.querySelector("#birth_minute").options).forEach((option) => {
          option.textContent = `${String(option.value).padStart(2, "0")} ${t("minuteUnit")}`;
        });
      }

      function initLocationSelectors() {
        form.country.innerHTML = Object.entries(locationData)
          .sort(([, left], [, right]) => {
            const leftLabel = currentLang === "en" ? (left.label_en || left.label) : left.label;
            const rightLabel = currentLang === "en" ? (right.label_en || right.label) : right.label;
            return leftLabel.localeCompare(rightLabel, currentLang === "en" ? "en" : "zh-CN");
          })
          .map(([value, item]) => `<option value="${value}">${currentLang === "en" ? (item.label_en || item.label) : item.label}</option>`)
          .join("");
        if (currentLang === "en") {
          setLocation("US", "New York", "New York City");
        } else {
          setLocation("CN", "上海市", "上海市");
        }
      }

      function initAnnualStartYear() {
        document.querySelector("#annual_start_year").value = String(new Date().getFullYear());
      }

      function setLocation(country, region, city) {
        form.country.value = country;
        populateRegions(country, region);
        populateCities(country, region, city);
        updateLocationMetadata();
      }

      function populateRegions(country, selectedRegion, selectedCity) {
        const regions = locationData[country].regions;
        const regionValue = selectedRegion && regions[selectedRegion] ? selectedRegion : Object.keys(regions)[0];
        form.region.innerHTML = Object.entries(regions)
          .map(([value, item]) => `<option value="${value}">${localizedLocationLabel(item, value)}</option>`)
          .join("");
        form.region.value = regionValue;
        populateCities(country, regionValue, selectedCity);
      }

      function populateCities(country, region, selectedCity) {
        const cities = locationData[country].regions[region].cities;
        const cityValue = selectedCity && cities[selectedCity] ? selectedCity : Object.keys(cities)[0];
        form.city.innerHTML = Object.entries(cities)
          .map(([value, item]) => `<option value="${value}">${localizedLocationLabel(item, value)}</option>`)
          .join("");
        form.city.value = cityValue;
        updateLocationMetadata();
      }

      function updateLocationMetadata() {
        const city = locationData[form.country.value].regions[form.region.value].cities[form.city.value];
        form.timezone.value = city.timezone;
        form.longitude.value = city.longitude;
        form.latitude.value = city.latitude;
      }

      async function loadWorldLocations() {
        try {
          const response = await fetch("/assets/world-locations-v1.json", { cache: "no-store" });
          if (!response.ok) throw new Error("world_locations_unavailable");
          const worldLocations = await response.json();
          Object.entries(worldLocations).forEach(([countryCode, country]) => {
            if (!locationData[countryCode]) locationData[countryCode] = country;
          });
        } catch (error) {
          console.warn("Global birthplace directory could not be loaded.", error);
        }
      }

      function setBirthTime(date, period, hour, minute) {
        form.birth_date.value = date;
        form.birth_period.value = period;
        form.birth_hour.value = String(hour);
        form.birth_minute.value = String(minute);
      }

      function buildBirthDateTime() {
        const date = form.birth_date.value;
        if (!date) throw new Error(t("birthDateRequired"));
        const hour12 = Number(form.birth_hour.value);
        const minute = Number(form.birth_minute.value);
        const period = form.birth_period.value;
        let hour24 = hour12 % 12;
        if (period === "PM") hour24 += 12;
        return `${date}T${String(hour24).padStart(2, "0")}:${String(minute).padStart(2, "0")}:00`;
      }

      function profileSignatureFromInput(input) {
        return [
          input.birth_datetime,
          input.timezone,
          input.gender,
          input.country,
          input.region,
          input.city,
          input.longitude,
          input.latitude,
          Boolean(input.use_true_solar_time),
          input.birth_time_accuracy || ""
        ].join("|");
      }

      function readActiveProfile() {
        try {
          const profile = JSON.parse(localStorage.getItem(profileStorageKey) || "null");
          return profile?.setup_complete && profile.input ? profile : null;
        } catch {
          return null;
        }
      }

      function writeActiveProfile(data) {
        const profile = {
          setup_complete: true,
          saved_at: new Date().toISOString(),
          display_name: resultState.displayName,
          input: {
            birth_datetime: data.birth_datetime,
            timezone: data.timezone,
            gender: data.gender,
            country: data.country,
            region: data.region,
            city: data.city,
            longitude: data.longitude,
            latitude: data.latitude,
            use_true_solar_time: Boolean(data.use_true_solar_time),
            birth_time_accuracy: document.querySelector("#birth_time_accuracy").value
          }
        };
        try {
          localStorage.setItem(profileStorageKey, JSON.stringify(profile));
          resultState.setupComplete = true;
          hideOnboardingPanel();
          return true;
        } catch {
          return false;
        }
      }

      function hideOnboardingPanel() {
        const panel = document.querySelector("#onboarding-panel");
        if (panel) panel.classList.toggle("hidden", resultState.setupComplete);
      }

      function applyProfile(profile) {
        const input = profile.input || {};
        const dateTime = String(input.birth_datetime || "");
        const [date, clock = "08:30:00"] = dateTime.split("T");
        const hour24 = Number(clock.slice(0, 2));
        const minute = Number(clock.slice(3, 5));
        const period = hour24 >= 12 ? "PM" : "AM";
        const hour12 = hour24 % 12 || 12;
        setBirthTime(date, period, hour12, Number.isFinite(minute) ? minute : 30);
        if (
          locationData[input.country]
          && locationData[input.country].regions[input.region]
          && locationData[input.country].regions[input.region].cities[input.city]
        ) {
          setLocation(input.country, input.region, input.city);
        }
        form.gender.value = input.gender || "unknown";
        form.use_true_solar_time.checked = Boolean(input.use_true_solar_time);
        document.querySelector("#birth_time_accuracy").value = input.birth_time_accuracy || "exact";
        updateAccuracyNote();
        document.querySelector("#display_name").value = profile.display_name || "";
        resultState.displayName = profile.display_name || "";
        resultState.setupComplete = true;
        hideOnboardingPanel();
      }

      function shouldReplaceActiveProfile(data) {
        const profile = readActiveProfile();
        if (!profile?.input) return true;
        const next = { ...data, birth_time_accuracy: document.querySelector("#birth_time_accuracy").value };
        if (profileSignatureFromInput(profile.input) === profileSignatureFromInput(next)) return true;
        return window.confirm(t("profileChangeConfirm"));
      }

      function readRecentCharts() {
        try {
          const parsed = JSON.parse(localStorage.getItem(historyStorageKey) || "[]");
          return Array.isArray(parsed) ? parsed.slice(0, 5) : [];
        } catch {
          return [];
        }
      }

      function writeRecentCharts(charts) {
        try {
          localStorage.setItem(historyStorageKey, JSON.stringify(charts.slice(0, 5)));
        } catch {
          return false;
        }
        return true;
      }

      function trackProductEvent(name, metadata = {}) {
        window.MINGAnalytics.record(name, metadata, productEventStorageKey);
      }

      function saveRecentChart(data) {
        const record = {
          id: `${Date.now()}`,
          saved_at: new Date().toISOString(),
          display_name: resultState.displayName,
          birth_time_accuracy: document.querySelector("#birth_time_accuracy").value,
          input: {
            birth_datetime: data.birth_datetime,
            timezone: data.timezone,
            gender: data.gender,
            country: data.country,
            region: data.region,
            city: data.city,
            longitude: data.longitude,
            latitude: data.latitude,
            use_true_solar_time: Boolean(data.use_true_solar_time)
          }
        };
        const signature = [
          record.display_name,
          record.birth_time_accuracy,
          record.input.birth_datetime,
          record.input.gender,
          record.input.country,
          record.input.region,
          record.input.city,
          record.input.use_true_solar_time
        ].join("|");
        const charts = readRecentCharts().filter((item) => {
          const itemSignature = [
            item.display_name,
            item.birth_time_accuracy,
            item.input?.birth_datetime,
            item.input?.gender,
            item.input?.country,
            item.input?.region,
            item.input?.city,
            Boolean(item.input?.use_true_solar_time)
          ].join("|");
          return itemSignature !== signature;
        });
        writeRecentCharts([record, ...charts]);
        renderRecentCharts();
      }

      function renderRecentCharts() {
        const container = document.querySelector("#history-list");
        if (!container) return;
        const charts = readRecentCharts();
        if (!charts.length) {
          container.innerHTML = `<div class="history-empty">${t("historyEmpty")}</div>`;
          return;
        }
        container.innerHTML = charts.map((record) => {
          const input = record.input || {};
          const name = record.display_name || input.city || input.region || input.country || t("recentCharts");
          const date = String(input.birth_datetime || "").slice(0, 16).replace("T", " ");
          const place = [input.region, input.city].filter(Boolean).join(" · ");
          return `<article class="history-item">
            <div class="history-copy">
              <strong>${escapeHtml(name)}</strong>
              <span>${escapeHtml(`${date} · ${place}`)}</span>
            </div>
            <div class="history-controls">
              <button type="button" data-history-load="${escapeHtml(record.id)}" title="${t("historyLoad")}">${t("historyLoad")}</button>
              <button type="button" data-history-delete="${escapeHtml(record.id)}" title="${t("historyDelete")}">×</button>
            </div>
          </article>`;
        }).join("");
      }

      function loadRecentChart(id) {
        const record = readRecentCharts().find((item) => item.id === id);
        if (!record?.input) return;
        const input = record.input;
        const dateTime = String(input.birth_datetime || "");
        const [date, clock = "00:00:00"] = dateTime.split("T");
        const hour24 = Number(clock.slice(0, 2));
        const minute = Number(clock.slice(3, 5));
        const period = hour24 >= 12 ? "PM" : "AM";
        const hour12 = hour24 % 12 || 12;
        setBirthTime(date, period, hour12, minute);
        if (
          locationData[input.country]
          && locationData[input.country].regions[input.region]
          && locationData[input.country].regions[input.region].cities[input.city]
        ) {
          setLocation(input.country, input.region, input.city);
        }
        form.gender.value = input.gender || "unknown";
        form.use_true_solar_time.checked = Boolean(input.use_true_solar_time);
        document.querySelector("#birth_time_accuracy").value = record.birth_time_accuracy || "exact";
        updateAccuracyNote();
        document.querySelector("#display_name").value = record.display_name || "";
        resultState.displayName = record.display_name || "";
        statusEl.textContent = t("historyLoaded");
      }

      function deleteRecentChart(id) {
        writeRecentCharts(readRecentCharts().filter((item) => item.id !== id));
        renderRecentCharts();
      }

      function escapeHtml(value) {
        return String(value)
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#039;");
      }

      function render(payload, traitOutput = resultState.traits) {
        document.querySelector("#chart-title").textContent = resultState.displayName ? t("userFourPillars")(resultState.displayName) : t("fourPillars");
        const productMetrics = deriveProductMetrics(payload, traitOutput);
        renderQualityStrip(payload, traitOutput);
        renderHighlight(productMetrics);
        renderDailyFocus(productMetrics, payload);
        renderRadar(productMetrics);
        renderBriefSummary(productMetrics);
        renderInsightSummary(payload, productMetrics);
        renderPremiumModules(productMetrics, payload);
        if (resultState.isPro && resultState.activePro) {
          if (resultState.activePro === "annual") {
            if (resultState.annualOutlook) {
              renderAnnualReport(resultState.annualOutlook);
            } else {
              requestAnnualReport();
            }
          } else if (resultState.activePro === "monthly") {
            if (resultState.monthlyCompass) {
              renderMonthlyCompass(resultState.monthlyCompass);
            } else {
              requestMonthlyCompass();
            }
          } else {
            const cachedReport = resultState.proReports[resultState.activePro];
            if (cachedReport) {
              renderServerProReport(cachedReport);
            } else {
              requestProReport(resultState.activePro);
            }
          }
        } else if (!resultState.isPro) {
          document.querySelector("#pro-report-view").innerHTML = "";
        }
        renderPillars(payload.chart);
        renderBars("#elements", payload.elements, activeElementLabels());
        renderBars("#ten-gods", payload.ten_gods, activeTenGodLabels());
        renderClassicReferences(payload.elements);
        renderChineseRoots(payload);
        renderTiming(payload);
        document.querySelector("#json-view").textContent = JSON.stringify({ core: payload, traits: traitOutput }, null, 2);
        renderEvidence(payload.evidence);
        renderLuck(payload.luck_cycles, payload.annual_flows);
        const warningCount = payload.warnings ? payload.warnings.length : 0;
        document.querySelector("#warning-count").textContent = warningCount ? t("warningsDetected")(warningCount) : t("valid");
      }

      function renderQualityStrip(payload, traitOutput) {
        const warningCount = payload.warnings ? payload.warnings.length : 0;
        const location = payload.input.location;
        const city = location.city || location.region || location.country;
        const birthTime = payload.input.birth_datetime.slice(0, 16).replace("T", " ");
        const timeEvidence = payload.evidence.find((item) => item.id === "input.time_basis");
        const correction = Number(timeEvidence?.weight || 0);
        const formattedCorrection = `${correction >= 0 ? "+" : ""}${correction.toFixed(0)}`;
        const accuracy = document.querySelector("#birth_time_accuracy").value;
        const accuracyLabels = {
          exact: t("accuracyExact"),
          approximate: t("accuracyApproximate"),
          unknown: t("accuracyUnknown")
        };
        const items = [
          { label: t("qualityInput"), value: `${city} / ${birthTime}` },
          { label: t("qualitySchema"), value: warningCount ? t("warningsDetected")(warningCount) : t("checked") },
          { label: t("qualityEvidence"), value: t("evidenceCount")(payload.evidence.length) },
          { label: t("qualityTraits"), value: t("traitModelReady")(Object.keys(traitOutput.traits).length) },
          {
            label: t("timeBasisLabel"),
            value: payload.input.use_true_solar_time
              ? t("trueSolarTimeBasis")(formattedCorrection)
              : t("civilTimeBasis")
          },
          { label: t("accuracyQuality"), value: accuracyLabels[accuracy] }
        ];
        document.querySelector("#quality-strip").innerHTML = items
          .map((item) => `<article class="quality-item"><span>${item.label}</span><strong>${item.value}</strong></article>`)
          .join("");
      }

      function deriveProductMetrics(payload, traitOutput) {
        if (!traitOutput?.traits) {
          throw new Error("TraitOutput v1 is required for interpretation.");
        }
        const elementEntries = Object.entries(payload.elements).sort((a, b) => b[1].adjusted - a[1].adjusted);
        const tenGodEntries = Object.entries(payload.ten_gods).sort((a, b) => b[1].adjusted - a[1].adjusted);
        const strongestElement = elementEntries.find(([key]) => key === traitOutput.context.strongest_element) || elementEntries[0];
        const strongestTenGod = tenGodEntries.find(([key]) => key === traitOutput.context.strongest_ten_god) || tenGodEntries[0];
        const trait = (key) => traitOutput.traits[key];
        const outputScore = trait("career_momentum").score;
        const ruleScore = trait("execution_stability").score;
        const wealthScore = trait("wealth_generation").score;
        const retentionPressure = 100 - trait("wealth_retention").score;
        const supportScore = trait("relationship_support").score;
        const relationshipPressure = trait("relationship_pressure").score;
        const careerStyle = trait("leadership_drive").score > ruleScore ? t("active") : t("disciplined");
        const wealthTag = wealthScore >= retentionPressure ? t("supportive") : t("risk");
        const relationTag = supportScore >= relationshipPressure ? t("supportive") : t("risk");
        const reminderTopics = {
          wealth_retention: t("wealth"),
          relationship_pressure: t("relationship"),
          execution_stability: t("career")
        };
        const mainReminderTopic = reminderTopics[traitOutput.context.main_reminder];
        const traitEvidenceCount = (...keys) => new Set(keys.flatMap((key) => trait(key).evidence_ids)).size;
        const traitConfidenceLabel = (key) => {
          const confidence = trait(key).confidence;
          if (confidence >= 0.8) return t("confidenceStrong");
          if (confidence >= 0.62) return t("confidenceMedium");
          return t("confidenceInitial");
        };
        const level = (value) => describeTraitLevel(Math.max(0, Math.min(100, value)));
        return {
          traitOutput,
          trait,
          strongestElement,
          strongestTenGod,
          outputScore,
          ruleScore,
          wealthScore,
          retentionPressure,
          supportScore,
          relationshipPressure,
          careerStyle,
          wealthTag,
          relationTag,
          mainReminderTopic,
          traitEvidenceCount,
          traitConfidenceLabel,
          level
        };
      }

      function describeTraitLevel(score) {
        if (currentLang === "en") {
          if (score >= 82) return "very prominent";
          if (score >= 62) return "relatively strong";
          if (score >= 38) return "moderate";
          if (score >= 18) return "relatively weak";
          return "very weak";
        }
        if (score >= 82) return "很突出";
        if (score >= 62) return "较强";
        if (score >= 38) return "中等";
        if (score >= 18) return "偏弱";
        return "很弱";
      }

      function positiveMod(value, divisor) {
        return ((value % divisor) + divisor) % divisor;
      }

      function localDateKey(date = new Date()) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
      }

      function buildDailyPillar(date = new Date()) {
        const localYear = date.getFullYear();
        const localMonth = date.getMonth();
        const localDay = date.getDate();
        const currentDayNumber = Math.floor(Date.UTC(localYear, localMonth, localDay) / 86400000);
        const anchorDayNumber = Math.floor(Date.UTC(2024, 1, 10) / 86400000);
        const cycleIndex = positiveMod(currentDayNumber - anchorDayNumber + 40, 60);
        const stem = dailyStemCycle[cycleIndex % 10];
        const branch = dailyBranchCycle[cycleIndex % 12];
        return {
          dateKey: localDateKey(date),
          cycleIndex,
          stem,
          branch,
          pillar: `${stem.char}${branch.char}`
        };
      }

      function dailyRelationKey(dayMasterElement, todayElement) {
        if (dayMasterElement === todayElement) return "same";
        if (elementGenerates[todayElement] === dayMasterElement) return "support";
        if (elementGenerates[dayMasterElement] === todayElement) return "output";
        if (elementControls[dayMasterElement] === todayElement) return "manage";
        if (elementControls[todayElement] === dayMasterElement) return "pressure";
        return "same";
      }

      function stableDailySeed(value) {
        return String(value).split("").reduce((hash, char) => {
          return positiveMod(hash * 31 + char.charCodeAt(0), 1000003);
        }, 7);
      }

      function selectDailyTheme(metrics, payload, relation, today) {
        const reminderTheme = {
          wealth_retention: "wealth",
          relationship_pressure: "relationship",
          execution_stability: "career"
        }[metrics.traitOutput.context.main_reminder] || "stability";
        if (relation === "pressure") return reminderTheme;
        if (relation === "output") return "career";
        if (relation === "manage") return "wealth";
        if (relation === "support") return "stability";
        const seed = stableDailySeed(`${payload.input.birth_datetime}|${metrics.strongestTenGod[0]}|${today.dateKey}`);
        return dailyThemeKeys[positiveMod(seed + today.cycleIndex, dailyThemeKeys.length)];
      }

      function buildDailyBoost(metrics, payload, today, themeKey) {
        const candidates = [
          { key: "career", score: metrics.trait("career_momentum").score },
          { key: "wealth", score: metrics.trait("wealth_generation").score },
          { key: "relationship", score: metrics.trait("relationship_support").score },
          { key: "stability", score: metrics.trait("execution_stability").score }
        ];
        const themeBonus = {
          career: "career",
          wealth: "wealth",
          relationship: "relationship",
          stability: "stability"
        }[themeKey];
        const seed = stableDailySeed(`${payload.input.birth_datetime}|${today.dateKey}|boost`);
        const ranked = candidates
          .map((item, index) => ({
            ...item,
            adjusted: item.score + (item.key === themeBonus ? 8 : 0) + positiveMod(seed + index * 13, 7)
          }))
          .sort((a, b) => b.adjusted - a.adjusted);
        const top = ranked[0];
        const score = Math.max(72, Math.min(94, Math.round(70 + top.adjusted * 0.24)));
        return {
          key: top.key,
          score,
          angle: `${Math.round(score * 3.6)}deg`
        };
      }

      function formatDailyDate(date = new Date()) {
        const locale = currentLang === "en" ? "en-US" : "zh-CN";
        return new Intl.DateTimeFormat(locale, {
          weekday: "short",
          month: "short",
          day: "numeric"
        }).format(date);
      }

      function formatDailyPillarLabel(today) {
        if (currentLang !== "en") return today.pillar;
        return `${stemRomanization[today.stem.char] || today.stem.char}-${branchRomanization[today.branch.char] || today.branch.char}`;
      }

      function elementIcon(element) {
        const icons = {
          wood: `
            <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
              <path class="icon-stroke" d="M16 26V12" />
              <path class="icon-fill" d="M15 13C9 7 5 8 4 14c6 1 9-1 11-1Z" />
              <path class="icon-fill" d="M17 15c4-6 9-7 12-2-4 4-8 4-12 2Z" />
              <path class="icon-stroke" d="M16 22c-3-4-6-6-10-7M17 19c3-3 6-4 10-5" />
            </svg>`,
          fire: `
            <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
              <path class="icon-fill" d="M16 29c6-3 9-7 8-12-1-5-5-7-6-13-4 3-4 7-3 10-3-2-5-5-5-8-5 5-7 11-5 16 2 4 6 6 11 7Z" />
              <path class="icon-soft" d="M16 26c3-2 5-4 5-7 0-3-2-4-3-7-3 3-2 5-2 7-2-1-3-2-4-4-2 3-2 6 0 8 1 2 2 3 4 3Z" />
              <path class="icon-stroke" d="M16 29c6-3 9-7 8-12-1-5-5-7-6-13-4 3-4 7-3 10-3-2-5-5-5-8-5 5-7 11-5 16 2 4 6 6 11 7Z" />
            </svg>`,
          earth: `
            <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
              <path class="icon-fill" d="M3 24 13 9l5 7 3-4 8 12H3Z" />
              <path class="icon-soft" d="M4 24h24v4H4z" />
              <path class="icon-stroke" d="M3 24 13 9l5 7 3-4 8 12H3ZM8 24h17M11 20h12" />
            </svg>`,
          metal: `
            <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
              <path class="icon-fill" d="M16 3 26 12 21 28H11L6 12 16 3Z" />
              <path class="icon-soft" d="M16 3v25l10-16L16 3Z" />
              <path class="icon-stroke" d="M16 3 26 12 21 28H11L6 12 16 3ZM6 12h20M16 3v25M11 28l5-16 5 16" />
            </svg>`,
          water: `
            <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
              <path class="icon-fill" d="M16 4c5 6 8 10 8 15a8 8 0 0 1-16 0c0-5 3-9 8-15Z" />
              <path class="icon-stroke" d="M16 4c5 6 8 10 8 15a8 8 0 0 1-16 0c0-5 3-9 8-15Z" />
              <path class="icon-stroke" d="M7 26c3 2 15 2 18 0M10 29c3 1 9 1 12 0" />
            </svg>`
        };
        return icons[element] || "";
      }

      function shiftLocalDate(date, offset) {
        const next = new Date(date);
        next.setDate(next.getDate() + offset);
        return next;
      }

      function readDailyCheckins() {
        try {
          const parsed = JSON.parse(localStorage.getItem(dailyCheckInStorageKey) || "[]");
          return Array.isArray(parsed)
            ? parsed.filter((item) => item && item.date && item.optionKey).slice(-80)
            : [];
        } catch {
          return [];
        }
      }

      function writeDailyCheckins(records) {
        try {
          localStorage.setItem(dailyCheckInStorageKey, JSON.stringify(records.slice(-80)));
          return true;
        } catch {
          return false;
        }
      }

      function recommendedDailyCheckin(themeKey, relation) {
        const byTheme = {
          career: "focus",
          wealth: "ground",
          relationship: "connect",
          stability: "restore"
        };
        const byRelation = {
          output: "spark",
          pressure: "restore",
          support: "restore",
          manage: "ground",
          same: "focus"
        };
        return byTheme[themeKey] || byRelation[relation] || "focus";
      }

      const motionAllowed = !window.matchMedia || !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      function dailySealImageSrc(key) {
        const icons = {
          focus: "/assets/daily-seals/image5/focus-image5.png",
          spark: "/assets/daily-seals/image5/spark-image5.png",
          ground: "/assets/daily-seals/image5/ground-image5.png",
          connect: "/assets/daily-seals/image5/connect-image5.png",
          restore: "/assets/daily-seals/image5/restore-image5.png"
        };
        return icons[key] || icons.focus;
      }

      const dailySealEffectMarkup = {
        focus: `<i class="seal-fx halo"></i><i class="seal-fx core"></i>`,
        spark: `<i class="seal-fx flame"></i><i class="seal-fx sparks"></i>`,
        ground: `<i class="seal-fx mountain"></i><i class="seal-fx settle"></i>`,
        connect: `<i class="seal-fx link-left"></i><i class="seal-fx heart"></i><i class="seal-fx link-right"></i>`,
        restore: `<i class="seal-fx sprout"></i><i class="seal-fx ripple"></i>`
      };

      function dailySealEffects(key, animated = true) {
        if (!animated || !motionAllowed) return "";
        return dailySealEffectMarkup[key] || dailySealEffectMarkup.focus;
      }

      function checkInIcon(key, options = {}) {
        const safeKey = String(key || "focus").replace(/[^a-z0-9_-]/gi, "") || "focus";
        const animated = options.animated !== false;
        const src = dailySealImageSrc(safeKey);
        return `<span class="daily-seal-scene seal-scene-${safeKey} ${animated && motionAllowed ? "is-motion" : "is-static"}"><img class="daily-seal-art" src="${src}?v=${appBuildVersion}" alt="" aria-hidden="true" loading="lazy" decoding="async">${dailySealEffects(safeKey, animated)}</span>`;
      }

      function sealKeyForTenGod(key) {
        const map = {
          peer: "focus",
          rob_wealth: "connect",
          eating_god: "spark",
          hurting_officer: "spark",
          direct_wealth: "ground",
          indirect_wealth: "ground",
          direct_officer: "focus",
          seven_killings: "spark",
          direct_resource: "restore",
          indirect_resource: "restore"
        };
        return map[key] || "focus";
      }

      function dailyCheckinStats(records, todayDate = new Date()) {
        const dates = new Set(records.map((item) => item.date));
        const todayKey = localDateKey(todayDate);
        const checkedToday = dates.has(todayKey);
        let streak = 0;
        let offset = checkedToday ? 0 : -1;
        while (dates.has(localDateKey(shiftLocalDate(todayDate, offset)))) {
          streak += 1;
          offset -= 1;
        }
        return {
          checkedToday,
          streak,
          todayRecord: records.find((item) => item.date === todayKey) || null
        };
      }

      function dailyCheckinTrail(records, todayDate = new Date()) {
        const byDate = new Map(records.map((item) => [item.date, item]));
        return Array.from({ length: 7 }, (_, index) => {
          const date = shiftLocalDate(todayDate, index - 6);
          const key = localDateKey(date);
          return {
            key,
            record: byDate.get(key) || null,
            isToday: index === 6,
            label: new Intl.DateTimeFormat(currentLang === "en" ? "en-US" : "zh-CN", {
              weekday: "short"
            }).format(date)
          };
        });
      }

      function saveDailyCheckin(optionKey, context) {
        const todayKey = localDateKey();
        const record = {
          date: todayKey,
          optionKey,
          pillar: context.pillarLabel,
          relation: context.relation,
          theme: context.themeKey,
          elements: context.todayElements,
          savedAt: new Date().toISOString()
        };
        const next = [...readDailyCheckins().filter((item) => item.date !== todayKey), record];
        writeDailyCheckins(next);
        trackProductEvent("daily_checkin_collected", { language: currentLang, module: optionKey });
      }

      function renderDailyCheckin(container, context) {
        const widget = container.querySelector("#daily-checkin-widget");
        if (!widget) return;
        const options = t("dailyCheckinOptions");
        const records = readDailyCheckins();
        const stats = dailyCheckinStats(records);
        const todayRecord = stats.todayRecord;
        const selectedKey = widget.dataset.selectedCheckin || todayRecord?.optionKey || recommendedDailyCheckin(context.themeKey, context.relation);
        const selectedOption = options.find((item) => item.key === selectedKey) || options[0];
        widget.dataset.selectedCheckin = selectedOption.key;
        const trail = dailyCheckinTrail(records);
        widget.innerHTML = `
          <div class="daily-checkin-header">
            <div>
              <span class="daily-checkin-kicker">${t("dailyCheckinEyebrow")}</span>
              <strong class="daily-checkin-title">${t("dailyCheckinTitle")}</strong>
            </div>
            <span class="daily-checkin-streak">${escapeHtml(t("dailyCheckinStreak")(stats.streak))}</span>
          </div>
          <div class="daily-checkin-options" role="group" aria-label="${escapeHtml(t("dailyCheckinTitle"))}">
            ${options.map((option) => `<button class="daily-checkin-option ${escapeHtml(option.key)} ${option.key === selectedOption.key ? "is-selected" : ""} ${todayRecord?.optionKey === option.key ? "is-saved" : ""}" type="button" data-checkin-option="${escapeHtml(option.key)}" aria-pressed="${option.key === selectedOption.key ? "true" : "false"}">
              <span class="daily-checkin-orb">${checkInIcon(option.key)}</span>
              <span>${escapeHtml(option.label)}</span>
            </button>`).join("")}
          </div>
          <div class="daily-checkin-action">
            <p class="daily-checkin-prompt">${escapeHtml(t("dailyCheckinPrompt")(selectedOption.label))}</p>
            <button class="daily-checkin-save" type="button" data-checkin-save="1">${todayRecord ? t("dailyCheckinSaved") : t("dailyCheckinSave")}</button>
          </div>
          <div class="daily-stamp-rail">
            <div class="daily-stamp-label">
              <span>${t("dailyCheckinTrail")}</span>
              <span>${t("dailyCheckinPrivacy")}</span>
            </div>
            <div class="daily-stamp-row">
              ${trail.map((item) => `<span class="daily-stamp-wrap" title="${escapeHtml(item.record ? item.record.optionKey : t("dailyCheckinEmpty"))}">
                <span class="daily-stamp ${item.record ? `is-filled ${escapeHtml(item.record.optionKey)}` : ""} ${item.isToday ? "is-today" : ""}">
                  ${item.record ? checkInIcon(item.record.optionKey, { animated: false }) : ""}
                </span>
                <span class="daily-stamp-day">${escapeHtml(item.label)}</span>
              </span>`).join("")}
            </div>
          </div>`;
        widget.onclick = (event) => {
          const optionButton = event.target.closest("[data-checkin-option]");
          if (optionButton) {
            widget.dataset.selectedCheckin = optionButton.dataset.checkinOption;
            renderDailyCheckin(container, context);
            return;
          }
          if (event.target.closest("[data-checkin-save]")) {
            saveDailyCheckin(widget.dataset.selectedCheckin || selectedOption.key, context);
            renderDailyCheckin(container, context);
          }
        };
      }

      function publicShareUrl() {
        const host = window.location.hostname;
        if (!host || host === "127.0.0.1" || host === "localhost") return "";
        return `${window.location.origin}/app`;
      }

      async function copyShareText(text) {
        if (navigator.clipboard?.writeText) {
          await navigator.clipboard.writeText(text);
          return true;
        }
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.top = "-1000px";
        document.body.appendChild(textarea);
        textarea.select();
        const copied = document.execCommand("copy");
        textarea.remove();
        return copied;
      }

      function bindShareButton(button, options) {
        if (!button) return;
        button.addEventListener("click", async () => {
          const shareUrl = publicShareUrl();
          const shareText = shareUrl ? `${options.text}\n${shareUrl}` : options.text;
          button.disabled = true;
          try {
            if (navigator.share) {
              await navigator.share({
                title: options.title,
                text: options.text,
                ...(shareUrl ? { url: shareUrl } : {})
              });
              if (options.feedback) options.feedback.textContent = t("shareDone");
            } else {
              const copied = await copyShareText(shareText);
              if (options.feedback) options.feedback.textContent = copied ? t("shareCopied") : t("shareUnavailable");
            }
            trackProductEvent(options.eventName, { language: currentLang });
          } catch (error) {
            if (error?.name !== "AbortError") {
              const copied = await copyShareText(shareText).catch(() => false);
              if (options.feedback) options.feedback.textContent = copied ? t("shareCopied") : t("shareUnavailable");
            }
          } finally {
            button.disabled = false;
            if (options.feedback) {
              window.setTimeout(() => {
                options.feedback.textContent = "";
              }, 2600);
            }
          }
        });
      }

      function renderDailyFocus(metrics, payload) {
        const container = document.querySelector("#daily-card-view");
        if (!container) return;
        const labels = activeElementLabels();
        const tenLabels = activeTenGodLabels();
        const today = buildDailyPillar();
        const dayMasterElement = payload.chart.day_master?.element || metrics.strongestElement[0];
        const relation = dailyRelationKey(dayMasterElement, today.stem.element);
        const themeKey = selectDailyTheme(metrics, payload, relation, today);
        const relationCopy = t("dailyRelations")[relation];
        const themeCopy = t("dailyThemes")[themeKey];
        const oracleLine = t("dailyOracleLines")[relation];
        const dailyBoost = buildDailyBoost(metrics, payload, today, themeKey);
        const boostTopic = t("dailyBoostTopics")[dailyBoost.key];
        const todayElements = `${labels[today.stem.element]} → ${labels[today.branch.element]}`;
        const pillarLabel = formatDailyPillarLabel(today);
        const dateStamp = t("dailyDateStamp")(formatDailyDate(), pillarLabel);
        const dailySealKey = recommendedDailyCheckin(themeKey, relation);
        container.innerHTML = `<article class="daily-card">
          <img class="daily-card-spirit" src="${dailySealImageSrc(dailySealKey)}" alt="" aria-hidden="true" loading="lazy" decoding="async">
          <div class="daily-card-header">
            <div>
              <span class="daily-card-kicker">${t("dailyFocusEyebrow")}</span>
              <h3>${escapeHtml(relationCopy.title)}</h3>
            </div>
            <span class="daily-card-date">${escapeHtml(dateStamp)}</span>
          </div>
          <div class="daily-ritual-strip">
            <div class="daily-seal" aria-label="${escapeHtml(today.pillar)}">
              <div><strong>${escapeHtml(today.pillar)}</strong><small>${t("dailySealLabel")}</small></div>
            </div>
            <div class="daily-flow-panel">
              <div class="daily-flow-title">
                <span>${t("dailyFlowTitle")}</span>
                <span class="daily-flow-icons" aria-label="${escapeHtml(todayElements)}">
                  <span class="element-orb ${today.stem.element}" title="${escapeHtml(labels[today.stem.element])}">${elementIcon(today.stem.element)}</span>
                  <span class="daily-flow-arrow">→</span>
                  <span class="element-orb ${today.branch.element}" title="${escapeHtml(labels[today.branch.element])}">${elementIcon(today.branch.element)}</span>
                </span>
              </div>
              <p class="daily-flow-copy">${escapeHtml(t("dailyFlowBody")(labels[today.stem.element], labels[today.branch.element]))}</p>
            </div>
          </div>
          <div class="daily-oracle-line">
            <span>${t("dailyOracleLineLabel")}</span>
            <strong>${escapeHtml(oracleLine)}</strong>
          </div>
          <div class="daily-boost" style="--boost-angle:${dailyBoost.angle}">
            <div class="daily-boost-score">
              <div><strong>${dailyBoost.score}</strong><span>${t("dailyBoostUnit")}</span></div>
            </div>
            <div class="daily-boost-copy">
              <span>${t("dailyBoostLabel")}</span>
              <strong>${escapeHtml(t("dailyBoostTitle")(boostTopic, dailyBoost.score))}</strong>
              <p>${t("dailyBoostBody")}</p>
            </div>
          </div>
          <p class="daily-card-body">${escapeHtml(relationCopy.body)}</p>
          <div class="daily-card-grid">
            <div class="daily-card-item">
              <span>${t("dailyActionLabel")}</span>
              <p>${escapeHtml(themeCopy.action)}</p>
            </div>
            <div class="daily-card-item">
              <span>${t("dailyDrainLabel")}</span>
              <p>${escapeHtml(themeCopy.drain)}</p>
            </div>
            <div class="daily-card-item">
              <span>${t("dailyQuestionLabel")}</span>
              <p>${escapeHtml(themeCopy.question)}</p>
            </div>
          </div>
          <div class="daily-card-evidence">
            <span>${escapeHtml(t("dailyEvidenceDayMaster")(labels[dayMasterElement]))}</span>
            <span>${escapeHtml(t("dailyEvidenceCore")(tenLabels[metrics.strongestTenGod[0]]))}</span>
            <span>${escapeHtml(t("dailyEvidenceToday")(pillarLabel))}</span>
            <span>${escapeHtml(t("dailyEvidenceReminder")(metrics.mainReminderTopic))}</span>
          </div>
          <p class="daily-card-note">${t("dailyNote")}</p>
          <section id="daily-checkin-widget" class="daily-checkin" aria-live="polite"></section>
          <div class="share-actions">
            <button class="share-button" type="button" data-share-card="daily">${t("shareDailyButton")}</button>
            <span class="share-feedback" data-share-feedback="daily"></span>
          </div>
        </article>`;
        renderDailyCheckin(container, {
          pillarLabel,
          relation,
          themeKey,
          todayElements
        });
        const dailyShareText = t("shareDailyText")(
          relationCopy.title,
          oracleLine,
          t("dailyBoostTitle")(boostTopic, dailyBoost.score),
          themeCopy.action,
          themeCopy.drain,
          themeCopy.question
        );
        bindShareButton(container.querySelector('[data-share-card="daily"]'), {
          title: t("shareDailyTitle"),
          text: dailyShareText,
          feedback: container.querySelector('[data-share-feedback="daily"]'),
          eventName: "daily_card_shared"
        });
      }

      function renderHighlight(metrics) {
        const elementLabels = activeElementLabels();
        const tenGodLabels = activeTenGodLabels();
        const element = elementLabels[metrics.strongestElement[0]];
        const tenGod = tenGodLabels[metrics.strongestTenGod[0]];
        const archetype = activeArchetypes()[metrics.strongestTenGod[0]];
        const coreSealKey = sealKeyForTenGod(metrics.strongestTenGod[0]);
        document.querySelector("#highlight-view").innerHTML = `
          <article class="highlight-card">
            <div class="highlight-content">
              <span class="archetype-kicker">${t("highlightEyebrow")}</span>
              <h3 class="archetype-name">${t("highlightTitle")(archetype.name)}</h3>
              <p>${t("highlightBody")(metrics.careerStyle, metrics.mainReminderTopic)}</p>
              <div class="archetype-tension">${t("highlightTension")(archetype.gift, archetype.tension)}</div>
              <div class="highlight-chips">
                <span class="highlight-chip"><span>${t("dominantElementLabel")}</span>${element}</span>
                <span class="highlight-chip"><span>${t("dominantPatternLabel")}</span>${tenGod}</span>
                <span class="highlight-chip"><span>${t("currentStrategyLabel")}</span>${metrics.careerStyle}</span>
              </div>
              <div class="highlight-action">${t("highlightAction")}</div>
              <div class="share-actions">
                <button class="share-button" type="button" data-share-card="core">${t("shareCoreButton")}</button>
                <span class="share-feedback" data-share-feedback="core"></span>
              </div>
            </div>
            <div class="highlight-symbol ${escapeHtml(coreSealKey)}" aria-hidden="true">
              ${checkInIcon(coreSealKey)}
              <span class="highlight-symbol-caption">${escapeHtml(element)} · ${escapeHtml(tenGod)}</span>
            </div>
          </article>`;
        const coreShareText = t("shareCoreText")(
          archetype.name,
          element,
          tenGod,
          t("highlightAction")
        );
        bindShareButton(document.querySelector('[data-share-card="core"]'), {
          title: t("shareCoreTitle"),
          text: coreShareText,
          feedback: document.querySelector('[data-share-feedback="core"]'),
          eventName: "core_card_shared"
        });
      }

      function renderBriefSummary(metrics) {
        const labels = activeElementLabels();
        const tenLabels = activeTenGodLabels();
        const items = [
          {
            title: t("strengthPath"),
            body: t("strengthPathBody")(labels[metrics.strongestElement[0]], tenLabels[metrics.strongestTenGod[0]])
          },
          {
            title: t("mainReminder"),
            body: t("mainReminderBody")(metrics.mainReminderTopic)
          },
          {
            title: t("nextMove"),
            body: t("nextMoveBody")
          }
        ];
        document.querySelector("#brief-view").innerHTML = items
          .map((item) => `<article class="brief-item"><strong>${item.title}</strong><span>${item.body}</span></article>`)
          .join("");
      }

      function renderRadar(metrics) {
        const axisLabels = t("radarAxes");
        const axisColors = {
          career: ["#35c8ff", "#6f7cff"],
          wealth: ["#ffd166", "#ff9f1c"],
          relationship: ["#28f5be", "#13d8ff"],
          decision: ["#ff5f7e", "#ff2bd6"],
          support: ["#9dff6e", "#44d7a8"],
          pressure: ["#b967ff", "#6d5dfc"]
        };
        const axes = [
          { key: "career", score: metrics.trait("career_momentum").score },
          { key: "wealth", score: metrics.trait("wealth_generation").score },
          { key: "relationship", score: metrics.trait("relationship_support").score },
          { key: "decision", score: metrics.trait("execution_stability").score },
          { key: "support", score: metrics.trait("resource_integration").score },
          { key: "pressure", score: metrics.trait("relationship_pressure").score }
        ].map((item) => ({
          ...item,
          color: axisColors[item.key][0],
          glow: axisColors[item.key][1]
        }));
        const center = 120;
        const radius = 74;
        const point = (index, percent = 100) => {
          const angle = -Math.PI / 2 + (Math.PI * 2 * index) / axes.length;
          const r = radius * (percent / 100);
          return {
            x: center + Math.cos(angle) * r,
            y: center + Math.sin(angle) * r
          };
        };
        const polygon = axes.map((axis, index) => point(index, axis.score)).map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
        const rings = [25, 50, 75, 100]
          .map((percent) => `<polygon points="${axes.map((_, index) => {
            const p = point(index, percent);
            return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
          }).join(" ")}" fill="none" stroke="rgba(170,180,177,0.18)" stroke-width="1" />`)
          .join("");
        const spokes = axes
          .map((_, index) => {
            const p = point(index, 100);
            return `<line x1="${center}" y1="${center}" x2="${p.x.toFixed(1)}" y2="${p.y.toFixed(1)}" stroke="rgba(170,180,177,0.18)" stroke-width="1" />`;
          })
          .join("");
        const labels = axes
          .map((axis, index) => {
            const p = point(index, 118);
            const anchor = Math.abs(p.x - center) < 8 ? "middle" : p.x > center ? "start" : "end";
            return `<text class="radar-axis" x="${p.x.toFixed(1)}" y="${p.y.toFixed(1)}" text-anchor="${anchor}" dominant-baseline="middle">${axisLabels[axis.key]}</text>`;
          })
          .join("");
        const rows = axes
          .map((axis) => `<div class="radar-row" style="--axis-color:${axis.color};--axis-glow:${axis.glow}">
            <span class="radar-name"><span class="axis-dot"></span>${axisLabels[axis.key]}</span>
            <span class="track"><span class="fill" style="width:${axis.score}%"></span></span>
            <strong>${axis.score}</strong>
          </div>`)
          .join("");
        document.querySelector("#radar-view").innerHTML = `
          <svg class="radar-chart" viewBox="0 0 240 240" role="img" aria-label="${t("radarTitle")}">
            <defs>
              <linearGradient id="radarFillGradient" x1="42" y1="42" x2="198" y2="198" gradientUnits="userSpaceOnUse">
                <stop offset="0" stop-color="#35c8ff" stop-opacity="0.42" />
                <stop offset="0.52" stop-color="#28f5be" stop-opacity="0.32" />
                <stop offset="1" stop-color="#ff2bd6" stop-opacity="0.28" />
              </linearGradient>
              <filter id="radarGlow" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            ${rings}
            ${spokes}
            <polygon points="${polygon}" fill="url(#radarFillGradient)" stroke="#28f5be" stroke-width="2.4" filter="url(#radarGlow)" />
            ${labels}
          </svg>
          <div>
            <h3 style="margin: 0 0 8px; font-size: 15px;">${t("radarTitle")}</h3>
            <p style="margin: 0 0 12px; color: var(--muted); font-size: 13px; line-height: 1.65;">${t("radarSubtitle")}</p>
            <div class="radar-list">${rows}</div>
          </div>`;
      }

      function renderInsightSummary(payload, metrics) {
        const labels = activeElementLabels();
        const tenLabels = activeTenGodLabels();
        const cards = [
          {
            key: "career",
            title: t("career"),
            tag: metrics.careerStyle,
            body: t("careerBody")(metrics.careerStyle, metrics.level(metrics.outputScore), metrics.level(metrics.ruleScore)),
            evidence: metrics.traitEvidenceCount("career_momentum"),
            confidence: metrics.traitConfidenceLabel("career_momentum")
          },
          {
            key: "wealth",
            title: t("wealth"),
            tag: metrics.wealthTag,
            body: t("wealthBody")(metrics.level(metrics.wealthScore), metrics.level(metrics.retentionPressure)),
            evidence: metrics.traitEvidenceCount("wealth_generation", "wealth_retention"),
            confidence: metrics.traitConfidenceLabel("wealth_retention")
          },
          {
            key: "relationship",
            title: t("relationship"),
            tag: metrics.relationTag,
            body: t("relationshipBody")(metrics.level(metrics.supportScore), metrics.level(metrics.relationshipPressure)),
            evidence: metrics.traitEvidenceCount("relationship_support", "relationship_pressure"),
            confidence: metrics.traitConfidenceLabel("relationship_pressure")
          },
          {
            key: "decision",
            title: t("decisionStyle"),
            tag: `${labels[metrics.strongestElement[0]]} / ${tenLabels[metrics.strongestTenGod[0]]}`,
            body: t("decisionBody")(labels[metrics.strongestElement[0]], tenLabels[metrics.strongestTenGod[0]]),
            evidence: metrics.traitEvidenceCount("execution_stability"),
            confidence: metrics.traitConfidenceLabel("execution_stability")
          }
        ];
        const cardColors = {
          career: "#35c8ff",
          wealth: "#ffd166",
          relationship: "#28f5be",
          decision: "#ff5f7e"
        };
        document.querySelector("#insight-view").innerHTML = cards
          .map((card) => `<article class="insight-card" style="--card-color: ${cardColors[card.key]}">
            <div class="insight-head">
              <span class="insight-tag">${card.tag}</span>
              <div class="insight-title-row">
                <h3>${card.title}</h3>
                <div class="insight-icon" aria-hidden="true">${insightIcon(card.key)}</div>
              </div>
            </div>
            <div>
              <p>${card.body}</p>
              <div class="confidence-line">${card.confidence} · ${t("evidenceShort")(card.evidence)}</div>
            </div>
          </article>`)
          .join("");
      }

      function insightIcon(key) {
        const attrs = `viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"`;
        const common = `stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"`;
        const soft = `stroke="currentColor" stroke-opacity="0.32" stroke-width="1.6"`;
        const icons = {
          career: `<svg ${attrs}><circle cx="32" cy="32" r="22" ${soft}/><path d="M18 42L28 32l7 6 12-17" ${common}/><path d="M41 21h6v6" ${common}/><path d="M20 48h25" ${soft}/></svg>`,
          wealth: `<svg ${attrs}><circle cx="32" cy="32" r="22" ${soft}/><path d="M22 39c4 5 16 5 20 0" ${common}/><path d="M23 29c2-7 16-7 18 0" ${common}/><path d="M32 18v28" ${common}/><path d="M25 25h14M25 35h14" ${common}/></svg>`,
          relationship: `<svg ${attrs}><circle cx="32" cy="32" r="22" ${soft}/><circle cx="22" cy="28" r="5" ${common}/><circle cx="42" cy="28" r="5" ${common}/><circle cx="32" cy="43" r="5" ${common}/><path d="M26.5 30.5l11 0M24.5 32.5l5.5 7M39.5 32.5l-5.5 7" ${common}/></svg>`,
          decision: `<svg ${attrs}><circle cx="32" cy="32" r="22" ${soft}/><path d="M32 17v6M32 41v6M17 32h6M41 32h6" ${soft}/><path d="M25 39l5-14 9 9-14 5Z" ${common}/><path d="M30 25l9-4-4 9" ${common}/></svg>`
        };
        return icons[key] || icons.decision;
      }

      function renderPremiumModules(metrics, payload) {
        const modules = [
          {
            key: "career",
            title: t("careerPremiumTitle"),
            body: t("careerPremiumBody")(metrics.careerStyle, metrics.level(metrics.outputScore), metrics.level(metrics.ruleScore)),
            points: t("careerPremiumPoints")
          },
          {
            key: "wealth",
            title: t("wealthPremiumTitle"),
            body: t("wealthPremiumBody")(metrics.level(metrics.wealthScore), metrics.level(metrics.retentionPressure)),
            points: t("wealthPremiumPoints")
          },
          {
            key: "relationship",
            title: t("relationshipPremiumTitle"),
            body: t("relationshipPremiumBody")(metrics.level(metrics.supportScore), metrics.level(metrics.relationshipPressure)),
            points: t("relationshipPremiumPoints")
          },
          {
            key: "annual",
            title: t("annualPremiumTitle"),
            body: t("annualPremiumBody"),
            points: t("annualPremiumPoints")
          },
          {
            key: "monthly",
            title: t("monthlyPremiumTitle"),
            body: t("monthlyPremiumBody"),
            points: t("monthlyPremiumPoints")
          }
        ];
        document.querySelector("#premium-view").innerHTML = modules
          .map((item) => `<article class="premium-card ${resultState.activePro === item.key && resultState.isPro ? "active" : ""} ${resultState.isPro ? "" : "locked"}">
            <span class="insight-tag">${t("premiumLayer")}</span>
            <h3>${item.title}</h3>
            <div class="premium-preview"><strong>${t("premiumPreviewLabel")}</strong><br>${item.body}</div>
            <ul class="premium-points">
              ${item.points.map((point) => `<li>${point}</li>`).join("")}
            </ul>
            ${resultState.isPro ? "" : `<div class="premium-lock-note">
              <span>${t("premiumLockedIncludes")}</span>
              <strong class="premium-price">${isFreeFirstRelease ? t("proComingSoonBadge") : t("premiumOneTimePrice")}</strong>
            </div>`}
            <button class="premium-button" type="button" data-premium="${item.key}">${resultState.isPro ? t("premiumCta") : (isFreeFirstRelease ? t("proComingSoonCta") : t("premiumLockedCta"))}</button>
          </article>`)
          .join("");
        document.querySelectorAll("[data-premium]").forEach((button) => {
          button.addEventListener("click", () => {
            resultState.requestedPro = button.dataset.premium;
            trackProductEvent("paid_module_opened", {
              language: currentLang,
              module: resultState.requestedPro
            });
            if (!resultState.isPro) {
              resultState.activePro = "";
              renderProPaywall();
              trackProductEvent("paywall_viewed", {
                language: currentLang,
                module: resultState.requestedPro
              });
              statusEl.textContent = t("proLockedStatus");
              document.querySelector("#pro-report-view").scrollIntoView({ behavior: "smooth", block: "start" });
              return;
            }
            resultState.activePro = resultState.requestedPro;
            renderPremiumModules(metrics, payload);
            if (resultState.activePro === "annual") {
              requestAnnualReport();
            } else if (resultState.activePro === "monthly") {
              requestMonthlyCompass();
            } else {
              requestProReport(resultState.activePro);
              statusEl.textContent = t("premiumPending");
            }
            document.querySelector("#pro-report-view").scrollIntoView({ behavior: "smooth", block: "start" });
          });
        });
      }

      async function requestProReport(moduleKey) {
        const reportView = document.querySelector("#pro-report-view");
        reportView.innerHTML = `<article class="pro-report-card"><p>${t("annualLoading")}</p></article>`;
        statusEl.textContent = t("proUnlocking");
        try {
          const { response, payload } = await fetchJson("/api/pro/report", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ...buildRequestData(), module: moduleKey, language: currentLang })
          });
          if (response.status === 403) {
            resultState.isPro = false;
            resultState.activePro = "";
            updateProAccessState();
            renderProPaywall();
            throw new Error(t("proLockedStatus"));
          }
          if (!payload.ok) throw new Error(payload.error || "pro_report_failed");
          resultState.proReports[moduleKey] = payload.report;
          renderServerProReport(payload.report);
          statusEl.textContent = t("premiumPending");
        } catch (error) {
          statusEl.textContent = error instanceof TypeError ? t("serviceUnavailable") : error.message;
          statusEl.classList.add("error");
        }
      }

      function renderServerProReport(report) {
        const badges = Array.isArray(report.badges) ? report.badges : [t("proFixedBadge"), t("proNoPredictionBadge")];
        const summary = Array.isArray(report.summary) ? report.summary : [];
        const evidence = report.evidence || {};
        document.querySelector("#pro-report-view").innerHTML = `<article class="pro-report-card">
          <div class="report-badges">
            ${badges.map((badge) => `<span class="report-badge">${escapeHtml(badge)}</span>`).join("")}
          </div>
          <span class="insight-tag">${t("premiumLayer")}</span>
          <h3 style="margin: 8px 0 8px; font-size: 18px;">${escapeHtml(report.title || t("premiumTitle"))}</h3>
          <p style="margin: 0; color: var(--muted); font-size: 13px; line-height: 1.75;">${escapeHtml(report.intro || "")}</p>
          <div class="pro-summary-panel">
            <div class="pro-summary-header">
              <h4>${t("proSummaryTitle")}</h4>
              <span>${t("proSummarySubtitle")}</span>
            </div>
            <div class="pro-summary-grid">
              ${summary.map((card, index) => `<section class="pro-summary-card" style="--summary-color: ${["#c9a65b", "#77b8a0", "#d87863", "#73a8d8"][index % 4]};" data-mark="${index + 1}">
                <span class="pro-summary-kicker">${escapeHtml(card.label || "")}</span>
                <strong>${escapeHtml(card.title || "")}</strong>
                <p>${escapeHtml(card.body || "")}</p>
              </section>`).join("")}
            </div>
          </div>
          <div class="report-grid">
            ${(report.blocks || []).map((block) => `<section class="report-block"><h4>${escapeHtml(block.title)}</h4><p>${escapeHtml(block.body)}</p></section>`).join("")}
            <section class="report-block">
              <h4>${t("actionChecklistTitle")}</h4>
              <ul class="report-actions">
                ${(report.actions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
              </ul>
            </section>
            <section class="report-block">
              <h4>${t("proEvidenceTitle")}</h4>
              <p>${escapeHtml(evidence.body || "")}</p>
            </section>
          </div>
          ${reportActionButtons()}
        </article>`;
        bindReportActions();
      }

      async function requestMonthlyCompass() {
        const now = new Date();
        const reportView = document.querySelector("#pro-report-view");
        reportView.innerHTML = `<article class="pro-report-card"><p>${t("monthlyLoading")}</p></article>`;
        statusEl.textContent = t("monthlyLoading");
        try {
          const { response, payload } = await fetchJson("/api/pro/monthly-compass", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              ...buildRequestData(),
              monthly_start_year: now.getFullYear(),
              monthly_start_month: now.getMonth() + 1,
              monthly_count: 6
            })
          });
          if (response.status === 403) {
            resultState.isPro = false;
            resultState.activePro = "";
            updateProAccessState();
            renderProPaywall();
            throw new Error(t("proLockedStatus"));
          }
          if (!payload.ok) throw new Error(payload.error || "monthly_compass_failed");
          resultState.monthlyCompass = payload.compass;
          resultState.selectedMonthIndex = 0;
          renderMonthlyCompass(payload.compass);
          statusEl.textContent = t("premiumPending");
        } catch (error) {
          statusEl.textContent = error instanceof TypeError ? t("serviceUnavailable") : error.message;
          statusEl.classList.add("error");
        }
      }

      function renderMonthlyCompass(compass) {
        const selected = compass.months[resultState.selectedMonthIndex] || compass.months[0];
        const elementNames = activeElementLabels();
        const axes = t("annualAxes");
        const focusCopy = t("monthlyFocus");
        const boundaryCopy = t("monthlyBoundary");
        const experimentCopy = t("monthlyExperiment");
        const reflectionCopy = t("monthlyReflection");
        const markMeanings = t("markMeanings");
        const palette = {
          jade: "#28f5be",
          coral: "#ff5f7e",
          gold: "#ffd166",
          silver: "#b9d7df",
          cyan: "#35c8ff"
        };
        const scoreColors = {
          career: "#35c8ff",
          wealth: "#ffd166",
          relationship: "#28f5be",
          stability: "#ff5f7e"
        };
        const markColor = palette[selected.mark.palette_key];
        const markAngle = selected.mark.pattern_key === "expanding" ? "45deg" : "-45deg";
        document.querySelector("#pro-report-view").innerHTML = `<article class="pro-report-card">
          <div class="report-badges">
            <span class="report-badge">${t("proNoPredictionBadge")}</span>
            <span class="report-badge">${escapeHtml(compass.model_version)}</span>
          </div>
          <span class="insight-tag">${t("premiumLayer")}</span>
          <h3 style="margin: 8px 0; font-size: 18px;">${t("monthlyCompassTitle")}</h3>
          <p style="margin: 0; color: var(--muted); font-size: 13px; line-height: 1.75;">${t("monthlyCompassIntro")}</p>
          <div class="monthly-selector">
            ${compass.months.map((item, index) => `<button type="button" class="monthly-option ${index === resultState.selectedMonthIndex ? "active" : ""}" data-month-index="${index}">
              <strong>${item.year}.${String(item.month).padStart(2, "0")}</strong>
              <span>${item.pillar} · ${elementNames[item.branch_element]}</span>
            </button>`).join("")}
          </div>
          <div class="monthly-compass-layout">
            <section class="monthly-mark-panel" style="--mark-color:${markColor};--mark-angle:${markAngle}">
              <div>
                <div class="monthly-mark"><strong>${selected.mark.glyph}</strong></div>
                <div class="monthly-mark-meta">
                  <strong>${t("monthlyMarkLabel")}</strong><br>
                  ${t("monthlyMarkMeaningLabel")}：${markMeanings[selected.mark.meaning_key]}<br>
                  ${t("monthlyCollectionLabel")}：${escapeHtml(selected.mark.collection_id)}
                </div>
              </div>
            </section>
            <section class="monthly-detail">
              <h4>${selected.year}.${String(selected.month).padStart(2, "0")} · ${selected.pillar}</h4>
              <div class="annual-score-grid">
                ${Object.entries(selected.scores).map(([key, score]) => `<div class="annual-score" style="--axis-color:${scoreColors[key]}">
                  <span>${axes[key]}</span>
                  <strong>${describeTraitLevel(score)}</strong>
                </div>`).join("")}
              </div>
              <div class="monthly-copy-grid">
                <div class="monthly-copy-item" style="--item-color:#35c8ff">
                  <strong>${t("monthlyFocusLabel")}</strong>
                  <p>${focusCopy[selected.focus_key]}</p>
                </div>
                <div class="monthly-copy-item" style="--item-color:#ff5f7e">
                  <strong>${t("monthlyBoundaryLabel")}</strong>
                  <p>${boundaryCopy[selected.boundary_key]}</p>
                </div>
                <div class="monthly-copy-item" style="--item-color:#28f5be">
                  <strong>${t("monthlyExperimentLabel")}</strong>
                  <p>${experimentCopy[selected.experiment_key]}</p>
                </div>
                <div class="monthly-copy-item" style="--item-color:#ffd166">
                  <strong>${t("monthlyReflectionLabel")}</strong>
                  <p>${reflectionCopy[selected.reflection_key]}</p>
                </div>
              </div>
              <div class="confidence-line">${confidenceFromValue(selected.confidence)} · ${t("evidenceShort")(selected.evidence_ids.length)}</div>
            </section>
          </div>
          ${reportActionButtons()}
        </article>`;
        document.querySelectorAll("[data-month-index]").forEach((button) => {
          button.addEventListener("click", () => {
            resultState.selectedMonthIndex = Number(button.dataset.monthIndex);
            renderMonthlyCompass(compass);
          });
        });
        bindReportActions();
      }

      async function requestAnnualReport() {
        const reportView = document.querySelector("#pro-report-view");
        reportView.innerHTML = `<article class="pro-report-card"><p>${t("annualLoading")}</p></article>`;
        statusEl.textContent = t("annualLoading");
        try {
          const { response, payload } = await fetchJson("/api/pro/annual-report", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ...buildRequestData(), annual_report_years: 5 })
          });
          if (response.status === 403) {
            resultState.isPro = false;
            resultState.activePro = "";
            updateProAccessState();
            renderProPaywall();
            throw new Error(t("proLockedStatus"));
          }
          if (!payload.ok) throw new Error(payload.error || "annual_report_failed");
          resultState.annualOutlook = payload.annual;
          renderAnnualReport(payload.annual);
          statusEl.textContent = t("premiumPending");
        } catch (error) {
          statusEl.textContent = error instanceof TypeError ? t("serviceUnavailable") : error.message;
          statusEl.classList.add("error");
        }
      }

      function renderAnnualReport(annual) {
        const elementNames = activeElementLabels();
        const axes = t("annualAxes");
        const focusCopy = t("annualFocus");
        const cautionCopy = t("annualCaution");
        const colors = {
          career: "#35c8ff",
          wealth: "#ffd166",
          relationship: "#28f5be",
          stability: "#ff5f7e"
        };
        document.querySelector("#pro-report-view").innerHTML = `<article class="pro-report-card">
          <div class="report-badges">
            <span class="report-badge">${t("proFixedBadge")}</span>
            <span class="report-badge">${t("proNoPredictionBadge")}</span>
            <span class="report-badge">${escapeHtml(annual.model_version)}</span>
          </div>
          <span class="insight-tag">${t("premiumLayer")}</span>
          <h3 style="margin: 8px 0; font-size: 18px;">${t("annualReportTitle")}</h3>
          <p style="margin: 0; color: var(--muted); font-size: 13px; line-height: 1.75;">${t("annualReportIntro")}</p>
          <div class="annual-report-grid">
            ${annual.years.map((item) => `<section class="annual-report-card">
              <div class="annual-year-mark">
                <strong>${item.year}</strong>
                <span>${item.pillar} · ${elementNames[item.theme_element]}</span>
              </div>
              <div>
                <div class="annual-score-grid">
                  ${Object.entries(item.scores).map(([key, score]) => `<div class="annual-score" style="--axis-color:${colors[key]}">
                    <span>${axes[key]}</span>
                    <strong>${describeTraitLevel(score)}</strong>
                  </div>`).join("")}
                </div>
                <div class="annual-guidance">
                  <p><strong>${t("annualFocusLabel")}${currentLang === "en" ? ": " : "："}</strong>${focusCopy[item.focus_key]}</p>
                  <p><strong>${t("annualCautionLabel")}${currentLang === "en" ? ": " : "："}</strong>${cautionCopy[item.caution_key]}</p>
                </div>
                <div class="confidence-line">${t("annualConfidenceLabel")}${currentLang === "en" ? ": " : "："}${confidenceFromValue(item.confidence)} · ${t("evidenceShort")(item.evidence_ids.length)}</div>
              </div>
            </section>`).join("")}
          </div>
          ${reportActionButtons()}
        </article>`;
        bindReportActions();
      }

      function confidenceFromValue(value) {
        if (value >= 0.68) return t("confidenceMedium");
        return t("confidenceInitial");
      }

      function renderProPaywall() {
        const includes = t("proIncludes");
        const planHtml = isFreeFirstRelease
          ? `<div class="pro-plan-grid">
              <section class="pro-plan-card recommended">
                <span class="pro-plan-label">${t("proComingSoonBadge")}</span>
                <h4>${t("proComingSoonTitle")}</h4>
                <p>${t("proComingSoonBody")}</p>
              </section>
            </div>`
          : `<div class="pro-plan-grid">
              <section class="pro-plan-card">
                <h4>${t("proMonthlyTitle")}</h4>
                <div class="pro-plan-price">${t("proMonthlyPrice")}</div>
                <p>${t("proMonthlyBody")}</p>
              </section>
              <section class="pro-plan-card recommended">
                <span class="pro-plan-label">${t("proPlanRecommended")}</span>
                <h4>${t("proYearlyTitle")}</h4>
                <div class="pro-plan-price">${t("proYearlyPrice")}</div>
                <p>${t("proYearlyBody")}</p>
              </section>
            </div>`;
        const actionHtml = isFreeFirstRelease
          ? ""
          : `<div class="pro-access-actions">
              ${resultState.canDemoUnlock ? `<button type="button" id="demo-pro-unlock">${t("proDemoUnlock")}</button>` : ""}
              <button type="button" id="restore-pro-purchase" class="pro-reset-button">${t("proRestorePurchase")}</button>
            </div>`;
        document.querySelector("#pro-report-view").innerHTML = `<article class="pro-paywall">
          <span class="insight-tag">${isFreeFirstRelease ? t("proComingSoonBadge") : t("proLockedState")}</span>
          <h3>${isFreeFirstRelease ? t("proComingSoonTitle") : t("proPaywallTitle")}</h3>
          <p>${isFreeFirstRelease ? t("proComingSoonBody") : t("proPaywallBody")}</p>
          ${planHtml}
          <h4 style="margin: 18px 0 0; font-size: 14px;">${t("proIncludesTitle")}</h4>
          <div class="pro-includes-grid">
            ${includes.map(([title, body]) => `<div class="pro-include-item"><strong>${title}</strong>${body}</div>`).join("")}
          </div>
          <p style="margin-top: 14px;">${isFreeFirstRelease ? t("proFreeFirstNote") : t("proStoreNote")}</p>
          ${actionHtml}
          <div class="pro-legal-row">
            <a href="/legal/terms.html" target="_blank" rel="noopener">${t("proTerms")}</a>
            <a href="/legal/privacy.html" target="_blank" rel="noopener">${t("proPrivacy")}</a>
            <a href="/legal/support.html" target="_blank" rel="noopener">${t("proSupport")}</a>
            <a href="/legal/methodology" target="_blank" rel="noopener">${t("proMethodology")}</a>
            <span>${t("proNoPredictionBadge")}</span>
          </div>
        </article>`;
        if (isFreeFirstRelease) return;
        const unlockButton = document.querySelector("#demo-pro-unlock");
        if (unlockButton) {
          unlockButton.addEventListener("click", async () => {
            unlockButton.disabled = true;
            try {
              await updateDemoEntitlement(true);
            } catch (error) {
              statusEl.textContent = error.message;
              statusEl.classList.add("error");
            }
          });
        }
        const restoreButton = document.querySelector("#restore-pro-purchase");
        if (restoreButton) {
          restoreButton.addEventListener("click", () => {
            statusEl.textContent = t("proRestorePlaceholder");
            trackProductEvent("restore_purchase_tapped", {
              language: currentLang,
              module: resultState.requestedPro || "unknown"
            });
          });
        }
      }

      function reportActionButtons() {
        return `<div class="pro-access-actions">
          <button type="button" id="export-pro-report">${t("exportReport")}</button>
          ${resultState.canDemoUnlock ? `<button class="pro-reset-button" type="button" id="demo-pro-reset">${t("proDemoReset")}</button>` : ""}
          <span class="disclaimer">${t("exportNote")}</span>
        </div>`;
      }

      function bindReportActions() {
        const exportButton = document.querySelector("#export-pro-report");
        if (exportButton) exportButton.addEventListener("click", exportCurrentReport);
        const resetButton = document.querySelector("#demo-pro-reset");
        if (resetButton) {
          resetButton.addEventListener("click", async () => {
            resetButton.disabled = true;
            try {
              await updateDemoEntitlement(false);
            } catch (error) {
              statusEl.textContent = error.message;
              statusEl.classList.add("error");
            }
          });
        }
      }

      function exportCurrentReport() {
        const report = document.querySelector("#pro-report-view .pro-report-card");
        if (!report || !resultState.isPro) return;
        const timestamp = new Date().toLocaleString(currentLang === "en" ? "en-US" : "zh-CN");
        const content = [
          t("exportFileTitle"),
          `${timestamp}`,
          "",
          report.innerText,
          "",
          currentLang === "en"
            ? "This structural interpretation is informational and is not a fixed prediction."
            : "本报告为结构化倾向参考，不构成绝对预测。"
        ].join("\r\n");
        const blob = new Blob(["\ufeff", content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `bazi-${resultState.activePro || "report"}-${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      }

      function renderPillars(chart) {
        const names = t("pillarNames");
        document.querySelector("#pillars").innerHTML = ["year", "month", "day", "hour"]
          .map((key) => {
            const p = chart[key];
            return `<article class="pillar">
              <div class="name">${names[key]}</div>
              <div class="gz">${p.stem.char}${p.branch.char}</div>
            </article>`;
          })
          .join("");
      }

      function renderBars(selector, data, labels) {
        const max = Math.max(...Object.values(data).map((item) => item.adjusted), 1);
        document.querySelector(selector).innerHTML = Object.entries(data)
          .map(([key, item]) => {
            const width = Math.max(2, (item.adjusted / max) * 100);
            return `<div class="bar">
              <span>${labels[key] || key}</span>
              <span class="track"><span class="fill" style="width:${width}%"></span></span>
              <span>${item.adjusted.toFixed(2)}</span>
            </div>`;
          })
          .join("");
      }

      function renderEvidence(evidence) {
        const countByType = evidence.reduce((acc, item) => {
          acc[item.type] = (acc[item.type] || 0) + 1;
          return acc;
        }, {});
        const countByLayer = evidence.reduce((acc, item) => {
          const layer = item.source?.layer || "unknown";
          acc[layer] = (acc[layer] || 0) + 1;
          return acc;
        }, {});
        const cards = [
          {
            title: t("evidencePillarTitle"),
            body: t("evidencePillarBody"),
            count: countByType.calculation || 0
          },
          {
            title: t("evidenceHiddenTitle"),
            body: t("evidenceHiddenBody"),
            count: countByType.branch_hidden_stem || 0
          },
          {
            title: t("evidenceTenGodTitle"),
            body: t("evidenceTenGodBody"),
            count: countByType.ten_god_relation || 0
          },
          {
            title: t("evidenceEnergyTitle"),
            body: t("evidenceEnergyBody"),
            count: countByLayer.energy_engine || 0
          }
        ];
        document.querySelector("#evidence-view").innerHTML = `<div class="evidence-summary">
          ${cards
            .map((card) => `<article class="evidence-card">
              <h3>${card.title}</h3>
              <p>${card.body}</p>
              <span class="evidence-count">${t("evidenceCount")(card.count)}</span>
            </article>`)
            .join("")}
        </div>`;
      }

      function renderClassicReferences(elements) {
        const entries = Object.entries(elements).sort((a, b) => b[1].adjusted - a[1].adjusted);
        const strongest = entries[0];
        const weakest = entries[entries.length - 1];
        const labels = activeElementLabels();
        const classics = activeClassicByElement();
        const cards = [
          {
            title: `${t("classicDominant")}: ${labels[strongest[0]]}`,
            role: t("dominantRole"),
            ...classics[strongest[0]]
          },
          {
            title: `${t("classicSupport")}: ${labels[weakest[0]]}`,
            role: t("supportRole"),
            ...classics[weakest[0]]
          }
        ];
        document.querySelector("#classic-view").innerHTML = cards
          .map((card) => `<article class="classic-card">
            <h3>${card.title} · ${card.hexagram}</h3>
            <div class="classic-line">${card.line}</div>
            <p>${card.meaning}</p>
            <p style="margin-top: 8px;">${t("structuralRole")}: ${card.role}. ${t("classicDisclaimer")}</p>
          </article>`)
          .join("");
      }

      function renderChineseRoots(payload) {
        const strongestPatterns = Object.entries(payload.ten_gods)
          .sort((a, b) => b[1].adjusted - a[1].adjusted)
          .slice(0, 3);
        const behaviorLabels = activeTenGodLabels();
        document.querySelector("#roots-view").innerHTML = strongestPatterns
          .map(([key, bundle]) => {
            if (currentLang === "en") {
              const explanation = rootExplanations[key];
              return `<article class="root-card">
                <span class="root-origin">${traditionalTenGodLabels[key]}</span>
                <h3>${behaviorLabels[key]}</h3>
                <p>${explanation.body}</p>
                <p class="root-aside">${explanation.aside}</p>
              </article>`;
            }
            return `<article class="root-card">
              <span class="root-origin">${tenGodLabels.zh[key]}</span>
              <h3>${tenGodLabels.zh[key]} · ${describeTraitLevel(Math.min(100, Math.round(bundle.adjusted * 50)))}</h3>
              <p>${tenGodInsights[key]}</p>
              <p class="root-aside">传统名称保留在文化解释层，不直接作为人生结论。</p>
            </article>`;
          })
          .join("");
      }

      function renderTiming(payload) {
        const labels = activeElementLabels();
        const birthYear = Number(payload.input.birth_datetime.slice(0, 4));
        const currentYear = Number(document.querySelector("#annual_start_year").value) || new Date().getFullYear();
        const currentAge = currentYear - birthYear;
        const currentLuck = payload.luck_cycles.find((item) => currentYear >= item.start_year && currentYear <= item.end_year)
          || payload.luck_cycles.find((item) => currentAge >= item.start_age && currentAge < item.end_age);
        const annualItems = payload.annual_flows.slice(0, 5);
        const luckHtml = currentLuck
          ? `<article class="timing-card">
              <h3>${t("currentLuckTitle")}: ${currentLuck.pillar.stem.char}${currentLuck.pillar.branch.char}</h3>
              <p>${t("luckRange")(formatAge(currentLuck.start_age), formatAge(currentLuck.end_age), currentLuck.start_year, currentLuck.end_year)}</p>
              <p>${t("luckBody")(`${currentLuck.pillar.stem.char}${currentLuck.pillar.branch.char}`, labels[currentLuck.pillar.branch.element])}</p>
            </article>`
          : `<article class="timing-card"><h3>${t("currentLuckTitle")}</h3><p>${t("currentLuckFallback")}</p></article>`;
        const annualHtml = `<article class="timing-card">
          <h3>${t("annualFocusTitle")}</h3>
          <p>${t("annualFocusBody")}</p>
          <div class="year-list" style="margin-top: 12px;">
            ${annualItems
              .map((item) => {
                const pillar = `${item.pillar.stem.char}${item.pillar.branch.char}`;
                return `<div class="year-card">
                  <strong>${item.year}</strong>
                  <p>${t("annualYearBody")(pillar, labels[item.pillar.branch.element])}</p>
                </div>`;
              })
              .join("")}
          </div>
        </article>`;
        document.querySelector("#timing-view").innerHTML = `${luckHtml}${annualHtml}`;
      }

      function renderLuck(luckCycles, annualFlows) {
        const luckRows = luckCycles
          .map((item) => `<tr><td>${t("luckCycle")} ${item.index}</td><td>${item.pillar.stem.char}${item.pillar.branch.char}</td><td>${formatAgeRange(item.start_age, item.end_age)}</td><td>${item.start_year}-${item.end_year}</td></tr>`)
          .join("");
        const annualRows = annualFlows
          .map((item) => `<tr><td>${t("annualFlow")}</td><td>${item.pillar.stem.char}${item.pillar.branch.char}</td><td></td><td>${item.year}</td></tr>`)
          .join("");
        document.querySelector("#luck-view").innerHTML = `<p class="table-note">${t("luckAgeNote")}</p><table>
          <thead><tr><th>${t("category")}</th><th>${t("ganzhi")}</th><th>${t("age")}</th><th>${t("year")}</th></tr></thead>
          <tbody>${luckRows}${annualRows}</tbody>
        </table>`;
      }

      function resetOracle() {
        oracleState.lines = [];
        oracleState.question = "";
        oracleState.category = "general";
        oracleState.horizon = "one_month";
        oracleState.result = null;
        oracleState.casting = false;
        document.querySelector("#oracle-result").innerHTML = "";
        document.querySelector("#oracle-message").textContent = "";
        document.querySelector("#oracle-last-value").textContent = "";
        document.querySelector("#oracle-progress").textContent = t("oracleReady");
        document.querySelector(".oracle-stage").classList.remove("casting", "has-cast");
        renderOracleLines();
        updateOracleButton();
      }

      async function castOracleLine() {
        if (!resultState.isPro) {
          const message = document.querySelector("#oracle-message");
          message.textContent = t("oracleProRequired");
          message.classList.add("error");
          updateOracleAccessState();
          return;
        }
        if (oracleState.casting || oracleState.lines.length >= 6) return;
        const question = document.querySelector("#oracle_question").value.trim();
        const message = document.querySelector("#oracle-message");
        message.classList.remove("error");
        if (question.length < 8) {
          message.textContent = t("oracleQuestionRequired");
          message.classList.add("error");
          return;
        }
        if (!oracleState.lines.length) {
          const recent = findRecentOracleQuestion(question);
          if (recent) {
            oracleState.question = recent.question;
            oracleState.category = recent.category;
            oracleState.horizon = recent.horizon;
            oracleState.lines = [...recent.lines];
            oracleState.result = recent.result;
            renderOracleLines();
            renderOracleResult(recent.result);
            message.textContent = t("oracleRepeatWarning");
            updateOracleButton();
            return;
          }
          oracleState.question = question;
          oracleState.category = document.querySelector("#oracle_category").value;
          oracleState.horizon = document.querySelector("#oracle_horizon").value;
          trackProductEvent("oracle_cast_started", {
            language: currentLang,
            module: oracleState.category
          });
        }

        oracleState.casting = true;
        updateOracleButton();
        message.textContent = t("oracleCasting");
        const values = new Uint32Array(3);
        crypto.getRandomValues(values);
        const faces = Array.from(values, (value) => value % 2 === 0 ? "head" : "tail");
        const total = faces.reduce((sum, face) => sum + (face === "head" ? 3 : 2), 0);
        const coins = Array.from(document.querySelectorAll(".oracle-coin"));
        const oracleStage = document.querySelector(".oracle-stage");
        oracleStage.classList.add("casting", "has-cast");
        coins.forEach((coin, index) => {
          coin.classList.remove("tossing");
          void coin.offsetWidth;
          coin.dataset.face = faces[index];
          coin.classList.add("tossing");
        });
        if (document.querySelector("#oracle_sound").checked) playOracleCastingSound(faces);
        await ritualWait(2260);
        coins.forEach((coin) => coin.classList.remove("tossing"));
        oracleStage.classList.remove("casting");
        oracleState.lines.push(total);
        document.querySelector("#oracle-last-value").textContent = t("oracleLineResult")(total, oracleLineLabel(total));
        document.querySelector("#oracle-progress").textContent = t("oracleProgress")(oracleState.lines.length);
        renderOracleLines();
        oracleState.casting = false;
        updateOracleButton();

        if (oracleState.lines.length === 6) {
          message.textContent = t("oracleInterpreting");
          await requestOracleInterpretation();
        } else {
          message.textContent = "";
        }
      }

      function oracleLineLabel(value) {
        return {
          6: t("oracleOldYin"),
          7: t("oracleYoungYang"),
          8: t("oracleYoungYin"),
          9: t("oracleOldYang")
        }[value];
      }

      function renderOracleLines() {
        const slots = [];
        for (let position = 6; position >= 1; position -= 1) {
          const value = oracleState.lines[position - 1];
          const isYang = value === 7 || value === 9;
          const moving = value === 6 || value === 9;
          slots.push(`<div class="oracle-line-slot">
            <span>${position}</span>
            <span class="yao-line ${isYang ? "yang" : "yin"} ${moving ? "moving" : ""}">
              ${value ? "<span></span><span></span>" : ""}
            </span>
            <span>${moving ? "×" : ""}</span>
          </div>`);
        }
        document.querySelector("#oracle-lines").innerHTML = slots.join("");
        const steps = Array.from({ length: 6 }, (_, index) => {
          const position = index + 1;
          const state = position <= oracleState.lines.length
            ? "complete"
            : position === oracleState.lines.length + 1
              ? "current"
              : "";
          return `<span class="oracle-cast-step ${state}">${t("oracleCastStep")(position)}</span>`;
        });
        document.querySelector("#oracle-cast-steps").innerHTML = steps.join("");
      }

      function updateOracleButton() {
        const button = document.querySelector("#oracle-cast-button");
        button.disabled = !resultState.isPro || oracleState.casting || oracleState.lines.length >= 6;
        if (!resultState.isPro) {
          button.textContent = t("oracleProRequired");
        } else if (oracleState.casting) {
          button.textContent = t("oracleCasting");
        } else if (oracleState.lines.length >= 6) {
          button.textContent = t("oracleCastAgainLater");
        } else if (!oracleState.lines.length) {
          button.textContent = t("oracleBegin");
        } else {
          button.textContent = t("oracleCastLine")(oracleState.lines.length + 1);
        }
      }

      async function requestOracleInterpretation() {
        const message = document.querySelector("#oracle-message");
        try {
          const { payload } = await fetchJson("/api/oracle/interpret", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              lines: oracleState.lines,
              category: oracleState.category,
              horizon: oracleState.horizon
            })
          });
          if (!payload.ok) {
            if (payload.error === "pro_required") {
              resultState.isPro = false;
              updateProAccessState();
              throw new Error(t("oracleProRequired"));
            }
            throw new Error(payload.error || "oracle_interpretation_failed");
          }
          const oracle = payload.oracle;
          oracleState.result = oracle;
          renderOracleResult(oracle);
          message.textContent = t("oracleCastAgainLater");
          trackProductEvent("oracle_reading_completed", {
            language: currentLang,
            module: oracleState.category
          });
        } catch (error) {
          if (!resultState.isPro || error.message === t("oracleProRequired")) {
            message.textContent = t("oracleProRequired");
            message.classList.add("error");
            return;
          }
          message.textContent = t("oracleResultError");
          message.classList.add("error");
        }
      }

      function oracleReadingCopy(result) {
        if (currentLang === "en") return result.interpretation;
        const trigramMotion = {
          qian: "主动创造与持续推动",
          dui: "交流、开放与相互影响",
          li: "清晰、呈现与辨别",
          zhen: "启动、震动与迅速行动",
          xun: "渐进影响、进入与适应",
          kan: "风险、深度与反复考验",
          gen: "边界、停顿与适时止步",
          kun: "承接、支持与耐心发展"
        };
        const linePositions = {
          1: "起点、动机与第一步",
          2: "内部关系、支持与配合",
          3: "门槛、压力与过度推进",
          4: "外部环境、影响与接触方式",
          5: "决策中心、责任与领导",
          6: "完成、过度与何时转变"
        };
        const actions = {
          general: "选择一个可验证、可回退的小行动，不要把卦象直接变成不可逆决定。",
          career: "把卦象转成一个工作交付物、一条边界和一次需要说清楚的沟通。",
          wealth: "投入资源前先写下成本上限、验证周期和退出条件。",
          relationship: "把一个期待说成具体请求，并确认对方真正能提供什么。",
          decision: "在作出更大承诺前，先设计一个最小且可回退的试验。",
          growth: "观察卦象指出的习惯，并连续七天练习一种不同回应。"
        };
        const moving = result.moving_lines;
        return {
          current_state: `本卦为第 ${result.primary.number} 卦「${result.primary.name_zh}」。下卦体现${trigramMotion[result.primary.lower.key]}，上卦则把它带入${trigramMotion[result.primary.upper.key]}的外部情境。`,
          change_dynamic: moving.length
            ? `动爻位于第 ${moving.join("、")} 爻，重点观察：${moving.map((position) => linePositions[position]).join("；")}。`
            : "本次没有动爻，适合把本卦视为相对稳定的当下结构，不必人为制造紧迫感。",
          direction: moving.length >= 3
            ? `共有 ${moving.length} 个动爻，变化强度较高。比起寻找一句固定预言，更应观察局势如何朝「${result.relating.name_zh}」的主题转移。`
            : `变卦为第 ${result.relating.number} 卦「${result.relating.name_zh}」，表示当前行动方式继续发展时可能形成的方向，而不是必然结果。`,
          action: actions[result.category],
          boundary: "不要把卦象当作保证，也不要仅凭问卦处理医疗、法律、财务或人身安全等重大决定。"
        };
      }

      function renderOracleResult(result) {
        document.querySelector(".oracle-stage").classList.add("has-cast");
        const copy = oracleReadingCopy(result);
        const plain = oraclePlainReading(result, copy);
        const movingLabel = result.moving_lines.length
          ? t("oracleMovingLines")(result.moving_lines.join(", "))
          : t("oracleNoChange");
        document.querySelector("#oracle-result").innerHTML = `<article class="oracle-result-card">
          <div class="report-badges">
            <span class="report-badge">${t("oracleMethod")}</span>
            <span class="report-badge">${movingLabel}</span>
            <span class="report-badge">${t("oracleRuleBadge")}</span>
          </div>
          <div class="oracle-answer-hero">
            <span>${t("oraclePlainTitle")}</span>
            <h3>${escapeHtml(plain.summary)}</h3>
            <p><strong>${t("oraclePlainAction")}：</strong>${escapeHtml(plain.action)}</p>
          </div>
          <div class="oracle-reading-grid">
            ${oracleReadingItem(t("oracleCurrentState"), plain.current, "#35c8ff")}
            ${oracleReadingItem(t("oracleChangeDynamic"), plain.change, "#ffd166")}
            ${oracleReadingItem(t("oracleDirection"), plain.direction, "#28f5be")}
            ${oracleReadingItem(t("oracleAction"), plain.action, "#ff5f7e")}
            ${oracleReadingItem(t("oracleBoundaryTitle"), copy.boundary, "#b967ff")}
          </div>
          <details class="oracle-traditional-details">
            <summary>${t("oracleTraditionalDetails")}</summary>
            <div class="oracle-traditional-content">
              <div class="oracle-hexagrams">
                ${oracleHexagramCard(t("oraclePrimary"), result.primary)}
                <div class="oracle-arrow">→</div>
                ${oracleHexagramCard(t("oracleRelating"), result.relating)}
              </div>
              ${oracleReadingItem(t("oracleCurrentState"), copy.current_state, "#35c8ff")}
              ${oracleReadingItem(t("oracleChangeDynamic"), copy.change_dynamic, "#ffd166")}
              ${oracleReadingItem(t("oracleDirection"), copy.direction, "#28f5be")}
            </div>
          </details>
          <button type="button" id="oracle-save-button">${t("oracleSave")}</button>
        </article>`;
        const saveButton = document.querySelector("#oracle-save-button");
        if (saveButton) saveButton.addEventListener("click", saveOracleJournalItem);
      }

      function oraclePlainReading(result, copy) {
        const movingCount = result.moving_lines.length;
        const categoryActions = currentLang === "en"
          ? {
              general: "Choose one small, reversible action and use the result as new information.",
              career: "Define one deliverable, one deadline, and one boundary before you move.",
              wealth: "Set a spending limit, a test period, and an exit rule before committing resources.",
              relationship: "Turn one expectation into a clear request, then listen to what the other person can realistically offer.",
              decision: "Run the smallest reversible test before making the larger commitment.",
              growth: "Practice one different response for seven days and record what actually changes."
            }
          : {
              general: "先做一个可验证、可回退的小行动，再根据真实反馈调整。",
              career: "先明确一个交付结果、一个期限和一条边界，再开始推进。",
              wealth: "投入前先设成本上限、验证周期和退出条件。",
              relationship: "把一个期待说成具体请求，也确认对方实际能做到什么。",
              decision: "先做一个最小且可回退的测试，再决定是否扩大投入。",
              growth: "连续七天练习一种不同回应，并记录真实变化。"
            };
        if (currentLang === "en") {
          const summary = movingCount === 0
            ? "The situation is relatively stable. Keep the useful parts of your current approach and avoid forcing a dramatic change."
            : movingCount <= 2
              ? "A focused adjustment matters more than a total reset. Deal with the key pressure point first."
              : "Several parts of the situation are moving at once. Slow the decision down, protect your boundaries, and revise the plan in stages.";
          return {
            summary,
            current: movingCount === 0
              ? "This is a stable snapshot rather than a signal to create urgency."
              : "The current approach still has value, but it is no longer enough on its own.",
            change: movingCount
              ? `${movingCount} of 6 lines are changing. That means the reading emphasizes transition rather than a fixed outcome.`
              : "No lines are changing, so consistency and observation matter more than reinvention.",
            direction: movingCount
              ? "The next phase depends on how you respond now; it is a direction, not a prediction."
              : "The likely direction remains close to the current pattern unless you introduce a deliberate change.",
            action: categoryActions[result.category] || categoryActions.general
          };
        }
        const summary = movingCount === 0
          ? "局面相对稳定。保留当前做法中有效的部分，不必为了求变化而突然推翻原计划。"
          : movingCount <= 2
            ? "这次更适合做关键调整，而不是全部重来。先处理最影响结果的那一步。"
            : "局面中有多处同时变化。先放慢决定、守住边界，再分阶段调整计划。";
        return {
          summary,
          current: movingCount === 0
            ? "这是一个偏稳定的状态，重点是持续观察，而不是制造紧迫感。"
            : "现有做法仍有可用之处，但仅靠原来的方式已经不够。",
          change: movingCount
            ? `六爻中有 ${movingCount} 爻发生变化，说明重点在“如何过渡”，而不是一个固定结果。`
            : "没有动爻，说明此刻更需要稳定执行和验证，而不是频繁改变。",
          direction: movingCount
            ? "接下来会走向哪里，很大程度取决于你此刻的处理方式；这是趋势提示，不是命定预言。"
            : "如果没有主动改变，接下来的发展大概率会延续当前模式。",
          action: categoryActions[result.category] || categoryActions.general
        };
      }

      function oracleHexagramCard(label, item) {
        const title = currentLang === "en"
          ? escapeHtml(item.name_en)
          : `${escapeHtml(item.name_zh)}卦`;
        const structure = currentLang === "en"
          ? `${escapeHtml(item.lower.en)} below · ${escapeHtml(item.upper.en)} above`
          : `下卦：${escapeHtml(item.lower.zh)}（${escapeHtml(item.lower.image)}） · 上卦：${escapeHtml(item.upper.zh)}（${escapeHtml(item.upper.image)}）`;
        return `<section class="oracle-hexagram">
          <span class="oracle-glyph">${item.unicode}</span>
          <span class="insight-tag">${label} · ${item.number}</span>
          <h3>${title}</h3>
          <p>${structure}</p>
        </section>`;
      }

      function oracleReadingItem(title, body, color) {
        return `<div class="oracle-reading-item" style="--item-color:${color}">
          <strong>${title}</strong>
          <p>${escapeHtml(body)}</p>
        </div>`;
      }

      let oracleAudioContext = null;

      function playOracleCastingSound(faces) {
        const audio = document.querySelector("#oracle-cast-audio");
        if (audio) {
          audio.pause();
          audio.currentTime = 0;
          audio.volume = 0.72;
          document.documentElement.dataset.oracleAudio = "starting";
          const playback = audio.play();
          if (playback) {
            playback.then(() => {
              document.documentElement.dataset.oracleAudio = "playing";
            }).catch(() => {
              playOracleSynthSound(faces);
            });
          }
          audio.onended = () => {
            document.documentElement.dataset.oracleAudio = "complete";
          };
          return;
        }
        playOracleSynthSound(faces);
      }

      async function playOracleSynthSound(faces) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (!AudioContextClass) {
          document.documentElement.dataset.oracleAudio = "unsupported";
          return;
        }
        oracleAudioContext ||= new AudioContextClass();
        const context = oracleAudioContext;
        document.documentElement.dataset.oracleAudio = context.state;
        context.onstatechange = () => {
          document.documentElement.dataset.oracleAudio = context.state;
        };
        if (context.state === "suspended") {
          try {
            await context.resume();
          } catch {
            document.documentElement.dataset.oracleAudio = "blocked";
            return;
          }
        }
        document.documentElement.dataset.oracleAudio = context.state;
        const now = context.currentTime;
        const master = context.createGain();
        master.gain.setValueAtTime(0.34, now);
        master.gain.setValueAtTime(0.34, now + 1.7);
        master.gain.exponentialRampToValueAtTime(0.001, now + 2.15);
        master.connect(context.destination);

        const noiseBuffer = context.createBuffer(1, context.sampleRate * 0.92, context.sampleRate);
        const data = noiseBuffer.getChannelData(0);
        for (let index = 0; index < data.length; index += 1) {
          const pulse = 0.45 + 0.55 * Math.abs(Math.sin(index / (context.sampleRate * 0.035)));
          data[index] = (Math.random() * 2 - 1) * pulse * Math.exp(-index / (context.sampleRate * 1.2));
        }
        const noise = context.createBufferSource();
        const filter = context.createBiquadFilter();
        filter.type = "bandpass";
        filter.frequency.setValueAtTime(920, now);
        filter.frequency.linearRampToValueAtTime(1760, now + 0.7);
        filter.Q.value = 1.5;
        noise.buffer = noiseBuffer;
        noise.connect(filter).connect(master);
        noise.start(now);
        noise.stop(now + 0.92);

        const scrapeBuffer = context.createBuffer(1, context.sampleRate * 0.42, context.sampleRate);
        const scrapeData = scrapeBuffer.getChannelData(0);
        for (let index = 0; index < scrapeData.length; index += 1) {
          scrapeData[index] = (Math.random() * 2 - 1) * Math.exp(-index / (context.sampleRate * 0.11));
        }
        const scrape = context.createBufferSource();
        const scrapeFilter = context.createBiquadFilter();
        const scrapeGain = context.createGain();
        scrape.buffer = scrapeBuffer;
        scrapeFilter.type = "highpass";
        scrapeFilter.frequency.value = 1280;
        scrapeGain.gain.setValueAtTime(0.001, now + 0.7);
        scrapeGain.gain.exponentialRampToValueAtTime(0.19, now + 0.78);
        scrapeGain.gain.exponentialRampToValueAtTime(0.001, now + 1.08);
        scrape.connect(scrapeFilter).connect(scrapeGain).connect(master);
        scrape.start(now + 0.7);
        scrape.stop(now + 1.12);

        faces.forEach((face, index) => {
          const start = now + 1.62 + index * 0.085;
          const oscillator = context.createOscillator();
          const gain = context.createGain();
          oscillator.type = "triangle";
          oscillator.frequency.setValueAtTime((face === "head" ? 1420 : 1080) + index * 60, start);
          oscillator.frequency.exponentialRampToValueAtTime(360 + index * 30, start + 0.2);
          gain.gain.setValueAtTime(0.001, start);
          gain.gain.exponentialRampToValueAtTime(0.34, start + 0.009);
          gain.gain.exponentialRampToValueAtTime(0.001, start + 0.3);
          oscillator.connect(gain).connect(master);
          oscillator.start(start);
          oscillator.stop(start + 0.32);

          const impact = context.createBufferSource();
          const impactFilter = context.createBiquadFilter();
          const impactGain = context.createGain();
          impact.buffer = scrapeBuffer;
          impactFilter.type = "bandpass";
          impactFilter.frequency.value = 2100 + index * 180;
          impactFilter.Q.value = 2.4;
          impactGain.gain.setValueAtTime(0.14, start);
          impactGain.gain.exponentialRampToValueAtTime(0.001, start + 0.14);
          impact.connect(impactFilter).connect(impactGain).connect(master);
          impact.start(start);
          impact.stop(start + 0.16);
        });
      }

      function readOracleJournal() {
        try {
          const items = JSON.parse(localStorage.getItem(oracleJournalStorageKey) || "[]");
          return Array.isArray(items) ? items.slice(0, 20) : [];
        } catch {
          return [];
        }
      }

      function writeOracleJournal(items) {
        try {
          localStorage.setItem(oracleJournalStorageKey, JSON.stringify(items.slice(0, 20)));
          return true;
        } catch {
          return false;
        }
      }

      function normalizedOracleQuestion(question) {
        return question.trim().toLowerCase().replace(/\s+/g, " ");
      }

      function findRecentOracleQuestion(question) {
        const cutoff = Date.now() - 24 * 60 * 60 * 1000;
        const normalized = normalizedOracleQuestion(question);
        return readOracleJournal().find((item) =>
          normalizedOracleQuestion(item.question) === normalized
          && new Date(item.saved_at).getTime() >= cutoff
        );
      }

      function saveOracleJournalItem() {
        if (!oracleState.result) return;
        const record = {
          id: `${Date.now()}`,
          saved_at: new Date().toISOString(),
          question: oracleState.question,
          category: oracleState.category,
          horizon: oracleState.horizon,
          lines: [...oracleState.lines],
          result: oracleState.result
        };
        const items = readOracleJournal().filter((item) =>
          normalizedOracleQuestion(item.question) !== normalizedOracleQuestion(record.question)
        );
        writeOracleJournal([record, ...items]);
        renderOracleJournal();
        document.querySelector("#oracle-message").textContent = t("oracleSaved");
        trackProductEvent("oracle_reading_saved", {
          language: currentLang,
          module: oracleState.category
        });
      }

      function renderOracleJournal() {
        const container = document.querySelector("#oracle-journal-list");
        if (!container) return;
        const items = readOracleJournal();
        if (!items.length) {
          container.innerHTML = `<div class="history-empty">${t("oracleJournalEmpty")}</div>`;
          return;
        }
        container.innerHTML = items.map((item) => `<article class="oracle-journal-item">
          <div class="history-copy">
            <strong>${escapeHtml(item.question)}</strong>
            <span>${escapeHtml(currentLang === "en" ? item.result.primary.name_en : item.result.primary.name_zh)} → ${escapeHtml(currentLang === "en" ? item.result.relating.name_en : item.result.relating.name_zh)} · ${new Date(item.saved_at).toLocaleDateString()}</span>
          </div>
          <div class="history-controls">
            <button type="button" data-oracle-view="${escapeHtml(item.id)}">${t("oracleView")}</button>
            <button type="button" data-oracle-delete="${escapeHtml(item.id)}" title="${t("oracleDelete")}">×</button>
          </div>
        </article>`).join("");
      }

      function viewOracleJournalItem(id) {
        const item = readOracleJournal().find((record) => record.id === id);
        if (!item) return;
        oracleState.question = item.question;
        oracleState.category = item.category;
        oracleState.horizon = item.horizon;
        oracleState.lines = [...item.lines];
        oracleState.result = item.result;
        document.querySelector("#oracle_question").value = item.question;
        document.querySelector("#oracle_category").value = item.category;
        document.querySelector("#oracle_horizon").value = item.horizon;
        renderOracleLines();
        renderOracleResult(item.result);
        updateOracleButton();
      }

      function deleteOracleJournalItem(id) {
        writeOracleJournal(readOracleJournal().filter((item) => item.id !== id));
        renderOracleJournal();
      }

      function formatAgeRange(startAge, endAge) {
        return `${formatAge(startAge)} - ${formatAge(endAge)}`;
      }

      function formatAge(value) {
        const years = Math.floor(Number(value));
        let months = Math.round((Number(value) - years) * 12);
        let displayYears = years;
        if (months >= 12) {
          displayYears += 1;
          months = 0;
        }
        if (currentLang === "en") {
          return months ? `about ${displayYears}y ${months}m` : `about ${displayYears}y`;
        }
        return months ? `约${displayYears}岁${months}个月` : `约${displayYears}岁`;
      }

      function selectTab(name) {
        document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === name));
        document.querySelector("#json-view").classList.toggle("hidden", name !== "json");
        document.querySelector("#evidence-view").classList.toggle("hidden", name !== "evidence");
        document.querySelector("#luck-view").classList.toggle("hidden", name !== "luck");
      }

      function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, (char) => ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;"
        })[char]);
      }

      async function initialize() {
        await loadWorldLocations();
        initLocationSelectors();
        applyLanguage(currentLang);
        await loadEntitlement();
        const profile = readActiveProfile();
        if (profile) {
          applyProfile(profile);
          document.body.dataset.hasReading = "true";
          await generate({ animate: false });
          setMobilePane("today", { scroll: false });
          return;
        }
        resultState.setupComplete = false;
        document.body.dataset.hasReading = "false";
        hideOnboardingPanel();
        statusEl.textContent = t("onboardingStatus");
      }

      initialize();
