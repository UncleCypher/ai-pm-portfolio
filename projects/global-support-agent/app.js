const form = document.querySelector("#diagnosisForm");
const messageInput = document.querySelector("#message");
const emptyState = document.querySelector("#emptyState");
const resultContent = document.querySelector("#resultContent");
const resultState = document.querySelector("#resultState");
const riskBanner = document.querySelector("#riskBanner");
const riskLabel = document.querySelector("#riskLabel");
const resultTitle = document.querySelector("#resultTitle");
const resultReply = document.querySelector("#resultReply");
const metaRow = document.querySelector("#metaRow");
const causeBlock = document.querySelector("#causeBlock");
const causes = document.querySelector("#causes");
const actionBlock = document.querySelector("#actionBlock");
const actionPurpose = document.querySelector("#actionPurpose");
const actionText = document.querySelector("#actionText");
const choiceBlock = document.querySelector("#choiceBlock");
const choices = document.querySelector("#choices");

const cases = [
  {
    match: ["发烫", "烫手", "过热", "冒烟", "烧焦", "电池膨胀"],
    state: "已转人工",
    risk: "紧急风险",
    tone: "danger",
    symptom: "热安全风险",
    confidence: 99,
    reply: "请立即停止使用并断开电源，将设备放在通风、远离易燃物的位置自然冷却。不要继续充电、运行或拆机。",
    causes: [],
    purpose: "安全优先，不进入普通自助诊断",
    action: "已创建模拟人工工单，并保留用户原始描述供专员处理。"
  },
  {
    match: ["乱转", "乱跑", "漏扫", "重复清扫", "不去", "地图"],
    state: "可自助排查",
    risk: "低风险",
    tone: "",
    symptom: "导航与地图异常",
    confidence: 91,
    reply: "已将模糊描述归一化为“导航与地图异常”。先验证传感器和环境变化，再考虑重建地图。",
    causes: [
      ["导航传感器或雷达窗口脏污", 40],
      ["基站位置或室内环境发生变化", 35],
      ["地图数据或定位状态异常", 25]
    ],
    purpose: "排除传感器脏污和环境变化",
    action: "用干燥软布清洁雷达窗口、沿墙传感器和悬崖传感器，并确认基站没有被移动。"
  },
  {
    match: ["没以前好用", "灰", "吸不干净", "扫不干净", "清洁效果"],
    state: "可自助排查",
    risk: "低风险",
    tone: "",
    symptom: "清洁能力下降",
    confidence: 88,
    reply: "已将“没以前好用”归一化为清洁能力下降，优先检查气流通道和旋转部件。",
    causes: [
      ["尘盒、滤网或风道堵塞", 46],
      ["主刷磨损或被毛发缠绕", 34],
      ["清洁模式与地面不匹配", 20]
    ],
    purpose: "排除气流堵塞和滚刷缠绕",
    action: "取出尘盒，检查滤网、吸入口和主刷是否积灰或缠绕；清理后再试一次小区域清洁。"
  },
  {
    match: ["回不了", "回充", "找不到基站", "充不进去"],
    state: "可自助排查",
    risk: "低风险",
    tone: "",
    symptom: "无法回充",
    confidence: 93,
    reply: "问题已归一化为无法回充，先检查基站识别条件和充电接触。",
    causes: [
      ["基站通道或红外窗口受阻", 48],
      ["充电触点脏污或接触不良", 32],
      ["地图定位状态异常", 20]
    ],
    purpose: "排除基站识别和充电接触问题",
    action: "确认基站两侧及正前方无遮挡，并用干燥软布清洁基站和机器人的充电触点。"
  },
  {
    match: ["不能集尘", "垃圾还在", "不集尘", "集尘失败"],
    state: "可自助排查",
    risk: "低风险",
    tone: "",
    symptom: "基站自动集尘异常",
    confidence: 89,
    reply: "问题已归一化为基站自动集尘异常。先排除尘袋、风道和集尘口的阻塞，再判断是否需要售后检测。",
    causes: [
      ["尘袋已满或安装不到位", 42],
      ["机器人或基站集尘风道堵塞", 38],
      ["集尘设置或基站识别异常", 20]
    ],
    purpose: "排除耗材状态和集尘通道阻塞",
    action: "断开基站电源后，检查尘袋是否装好、集尘口及风道是否堵塞；恢复供电后执行一次手动集尘。"
  },
  {
    match: ["不出水", "不清洗拖布", "不洗拖布", "没有水"],
    state: "可自助排查",
    risk: "低风险",
    tone: "",
    symptom: "基站水路或拖布清洗异常",
    confidence: 86,
    reply: "问题已归一化为基站水路或拖布清洗异常。先确认清水箱、污水箱和水路安装状态。",
    causes: [
      ["清水箱缺水或未安装到位", 44],
      ["水箱密封、滤网或水路受阻", 36],
      ["清洗任务设置或基站状态异常", 20]
    ],
    purpose: "排除水箱安装和可见水路阻塞",
    action: "确认清水箱水量充足、清污水箱均安装到位，并按说明书清理可拆卸滤网；不要拆卸内部泵体或管路。"
  },
  {
    match: ["没有通电", "没电", "指示灯不亮", "基站不亮"],
    state: "需人工确认",
    risk: "中风险",
    tone: "waiting",
    symptom: "基站供电异常",
    confidence: 82,
    reply: "问题已归一化为基站供电异常。为避免带电操作，系统只提供外部电源检查，仍无响应则转人工。",
    causes: [
      ["插座、插头或电源线连接异常", 58],
      ["基站电源模块异常", 42]
    ],
    purpose: "仅检查外部供电条件",
    action: "确认插头已完全插入，并用其他低功率电器验证插座；如电源线受损、有异味或基站仍无响应，请停止使用并联系人工。"
  }
];

const clarification = {
  state: "需要澄清",
  risk: "待判断",
  tone: "waiting",
  symptom: "基站问题（尚未分类）",
  confidence: 42,
  reply: "“基站不太正常”还不足以支持可靠诊断。请选择最接近的现象，我会继续缩小范围。",
  choices: [
    "机器找不到基站或无法回充",
    "基站不能集尘，垃圾还在机器里",
    "基站不出水或不清洗拖布",
    "基站没有通电或指示灯不亮"
  ]
};

document.querySelectorAll("[data-message]").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.message;
    messageInput.focus();
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  const selected = cases.find((item) => item.match.some((word) => text.includes(word)));
  if (selected) {
    renderResult(selected);
    return;
  }
  if (text.includes("基站") || text.length < 10) {
    renderClarification();
    return;
  }
  renderUnknown(text);
});

function renderResult(data) {
  showResult();
  setBanner(data);
  metaRow.innerHTML = [
    `型号 · ${escapeHtml(document.querySelector("#model").value)}`,
    `标准症状 · ${escapeHtml(data.symptom)}`,
    `理解 · Agent 语义`,
    `置信度 · ${data.confidence}%`
  ].map((item) => `<span>${item}</span>`).join("");

  choiceBlock.hidden = true;
  if (data.causes.length) {
    causeBlock.hidden = false;
    causes.innerHTML = data.causes.map(([label, score]) => `
      <div class="cause">
        <span>${escapeHtml(label)}</span><b>${score}%</b>
        <div class="bar"><i style="width:${score}%"></i></div>
      </div>
    `).join("");
  } else {
    causeBlock.hidden = true;
  }

  actionBlock.hidden = false;
  actionPurpose.textContent = data.purpose;
  actionText.textContent = data.action;
}

function renderClarification() {
  showResult();
  setBanner(clarification);
  metaRow.innerHTML = `<span>理解 · 信息不足</span><span>置信度 · ${clarification.confidence}%</span>`;
  causeBlock.hidden = true;
  actionBlock.hidden = true;
  choiceBlock.hidden = false;
  choices.innerHTML = "";
  clarification.choices.forEach((text) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = text;
    button.addEventListener("click", () => {
      messageInput.value = text;
      form.requestSubmit();
    });
    choices.appendChild(button);
  });
}

function renderUnknown(text) {
  showResult();
  const data = {
    state: "已转人工",
    risk: "未分类问题",
    tone: "waiting",
    reply: "这个现象暂不在演示故障库中。系统不会强行给出不可靠判断，已保留描述并进入人工确认流程。"
  };
  setBanner(data);
  metaRow.innerHTML = `<span>分类 · 体系外</span><span>原始描述 · 已保留</span>`;
  causeBlock.hidden = true;
  choiceBlock.hidden = true;
  actionBlock.hidden = false;
  actionPurpose.textContent = "开放世界分流";
  actionText.textContent = `模拟工单已创建：${text}`;
}

function showResult() {
  emptyState.hidden = true;
  resultContent.hidden = false;
}

function setBanner(data) {
  resultState.textContent = data.state;
  riskBanner.className = `risk-banner ${data.tone || ""}`.trim();
  riskLabel.textContent = data.risk;
  resultTitle.textContent = data.state;
  resultReply.textContent = data.reply;
}

function escapeHtml(value) {
  const node = document.createElement("span");
  node.textContent = value;
  return node.innerHTML;
}
