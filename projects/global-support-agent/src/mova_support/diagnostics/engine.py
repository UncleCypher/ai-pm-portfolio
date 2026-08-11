from dataclasses import dataclass

from mova_support.domain import DiagnosticStep, Hypothesis, RiskLevel, Symptom


@dataclass(frozen=True)
class DiagnosticKnowledge:
    symptom_code: str
    keywords: tuple[str, ...]
    hypotheses: tuple[Hypothesis, ...]
    next_step_zh: DiagnosticStep
    next_step_en: DiagnosticStep
    source: str


KNOWLEDGE = (
    DiagnosticKnowledge(
        symptom_code="cannot_dock",
        keywords=("回不了基站", "无法回充", "找不到基站", "充不进去", "cannot dock", "won't dock"),
        hypotheses=(
            Hypothesis(
                cause_code="dock_path_blocked",
                label="基站周围通道或红外窗口受阻",
                confidence=0.48,
                supporting_evidence=["症状与回充路径或基站识别异常一致"],
            ),
            Hypothesis(
                cause_code="charging_contact_dirty",
                label="充电触点脏污或接触不良",
                confidence=0.32,
                supporting_evidence=["无法完成充电握手时常见"],
            ),
            Hypothesis(
                cause_code="map_localization_error",
                label="地图定位状态异常",
                confidence=0.20,
                supporting_evidence=["设备可能无法计算返回路径"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="inspect_dock_area",
            instruction="请确认基站两侧及正前方无遮挡，并用干燥软布清洁基站和机器人的充电触点。",
            purpose="排除基站识别受阻和充电接触不良",
        ),
        next_step_en=DiagnosticStep(
            step_id="inspect_dock_area",
            instruction=(
                "Ensure the dock has clear space around it, then clean the charging "
                "contacts on the dock and robot with a dry soft cloth."
            ),
            purpose="Rule out blocked dock detection and poor charging contact",
        ),
        source="kb://robot-vacuum/common/cannot-dock/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="offline",
        keywords=("离线", "连不上网", "配网失败", "offline", "wifi", "wi-fi", "cannot connect"),
        hypotheses=(
            Hypothesis(
                cause_code="wifi_band_or_signal",
                label="Wi-Fi 频段或信号问题",
                confidence=0.55,
                supporting_evidence=["配网与离线问题通常先检查网络环境"],
            ),
            Hypothesis(
                cause_code="app_permission",
                label="App 网络或定位权限不足",
                confidence=0.25,
                supporting_evidence=["移动系统权限可能影响发现设备"],
            ),
            Hypothesis(
                cause_code="cloud_or_firmware",
                label="云服务或固件通信异常",
                confidence=0.20,
                supporting_evidence=["本地网络正常时需要进一步查询设备状态"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="check_wifi",
            instruction="请确认手机连接的是 2.4GHz Wi-Fi，并将设备临时移到路由器附近后重新配网。",
            purpose="排除频段不兼容和信号不足",
        ),
        next_step_en=DiagnosticStep(
            step_id="check_wifi",
            instruction=(
                "Confirm the phone is connected to a 2.4 GHz Wi-Fi network, "
                "move the device near the router, and try setup again."
            ),
            purpose="Rule out incompatible Wi-Fi band and weak signal",
        ),
        source="kb://robot-vacuum/common/offline/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="water_system",
        keywords=(
            "不出水",
            "不洗拖布",
            "污水箱",
            "轻微漏水",
            "地上有水",
            "拖地没水",
            "no water",
            "won't wash",
            "water tank",
        ),
        hypotheses=(
            Hypothesis(
                cause_code="tank_not_seated",
                label="水箱未安装到位或浮子异常",
                confidence=0.50,
                supporting_evidence=["水路异常首先检查水箱状态"],
            ),
            Hypothesis(
                cause_code="water_path_blocked",
                label="水路或过滤部件堵塞",
                confidence=0.35,
                supporting_evidence=["残留物可能影响供排水"],
            ),
            Hypothesis(
                cause_code="pump_fault",
                label="水泵或传感器故障",
                confidence=0.15,
                supporting_evidence=["完成基础检查后才能确认"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="reseat_tanks",
            instruction="请取出清水箱和污水箱，检查密封、浮子和过滤部件后重新安装到位。",
            purpose="排除水箱安装与可见堵塞问题",
        ),
        next_step_en=DiagnosticStep(
            step_id="reseat_tanks",
            instruction=(
                "Remove both water tanks, inspect the seals, float, and visible filters, "
                "then reinstall the tanks securely."
            ),
            purpose="Rule out tank seating and visible blockage issues",
        ),
        source="kb://robot-vacuum/common/water-system/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="weak_cleaning",
        keywords=(
            "扫不干净",
            "吸不干净",
            "吸力变小",
            "清洁效果差",
            "地上还有灰",
            "越扫越脏",
            "weak suction",
            "not cleaning well",
            "leaves dirt",
        ),
        hypotheses=(
            Hypothesis(
                cause_code="dust_path_blocked",
                label="尘盒、滤网或风道堵塞",
                confidence=0.46,
                supporting_evidence=["吸力下降通常先检查气流通道"],
            ),
            Hypothesis(
                cause_code="brush_worn_or_tangled",
                label="主刷磨损或被毛发缠绕",
                confidence=0.34,
                supporting_evidence=["滚刷状态会直接影响拾取能力"],
            ),
            Hypothesis(
                cause_code="cleaning_mode_mismatch",
                label="清洁模式与地面类型不匹配",
                confidence=0.20,
                supporting_evidence=["低档模式可能无法处理重污或地毯"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="inspect_air_path",
            instruction="请取出尘盒，检查滤网、吸入口和主刷是否积灰或缠绕；清理后再试一次小区域清洁。",
            purpose="排除气流堵塞和滚刷缠绕",
        ),
        next_step_en=DiagnosticStep(
            step_id="inspect_air_path",
            instruction=(
                "Remove the dustbin and inspect the filter, inlet, and main brush for "
                "blockage or tangled hair. Clean them and retry a small area."
            ),
            purpose="Rule out blocked airflow and brush tangles",
        ),
        source="kb://robot-vacuum/common/weak-cleaning/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="abnormal_noise",
        keywords=(
            "声音很大",
            "突然很吵",
            "异响",
            "咔咔响",
            "摩擦声",
            "尖叫声",
            "noisy",
            "strange noise",
            "rattling",
            "grinding sound",
        ),
        hypotheses=(
            Hypothesis(
                cause_code="brush_foreign_object",
                label="主刷或边刷卷入异物",
                confidence=0.50,
                supporting_evidence=["周期性异响通常与旋转部件相关"],
            ),
            Hypothesis(
                cause_code="wheel_foreign_object",
                label="驱动轮或万向轮卡有异物",
                confidence=0.30,
                supporting_evidence=["移动时异响可能来自轮组"],
            ),
            Hypothesis(
                cause_code="fan_or_motor_fault",
                label="风机或电机组件异常",
                confidence=0.20,
                supporting_evidence=["清除可见异物后仍异响需进一步检查"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="inspect_rotating_parts",
            instruction="请关机后检查主刷、边刷和万向轮，移除缠绕毛发或小物件，再短时试运行。",
            purpose="确认异响是否来自旋转部件异物",
        ),
        next_step_en=DiagnosticStep(
            step_id="inspect_rotating_parts",
            instruction=(
                "Power off the robot, inspect the main brush, side brush, and caster, "
                "remove tangled hair or debris, then run a short test."
            ),
            purpose="Check whether debris in rotating parts causes the noise",
        ),
        source="kb://robot-vacuum/common/abnormal-noise/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="navigation_or_map",
        keywords=(
            "地图乱了",
            "地图不对",
            "乱跑",
            "漏扫",
            "重复清扫",
            "定位错误",
            "进不了房间",
            "map is wrong",
            "random path",
            "misses rooms",
            "keeps cleaning same area",
        ),
        hypotheses=(
            Hypothesis(
                cause_code="sensor_dirty",
                label="导航传感器或雷达窗口脏污",
                confidence=0.40,
                supporting_evidence=["感知受阻可能引起定位和路径异常"],
            ),
            Hypothesis(
                cause_code="environment_changed",
                label="基站位置或室内环境发生明显变化",
                confidence=0.35,
                supporting_evidence=["环境变化可能导致地图匹配失败"],
            ),
            Hypothesis(
                cause_code="map_data_corrupted",
                label="地图数据或定位状态异常",
                confidence=0.25,
                supporting_evidence=["需在基础检查后判断是否重建地图"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="clean_navigation_sensors",
            instruction="请用干燥软布清洁雷达窗口、沿墙传感器和悬崖传感器，并确认基站没有被移动。",
            purpose="排除传感器脏污和环境变化",
        ),
        next_step_en=DiagnosticStep(
            step_id="clean_navigation_sensors",
            instruction=(
                "Clean the lidar window, wall sensor, and cliff sensors with a dry soft "
                "cloth, and confirm the dock has not been moved."
            ),
            purpose="Rule out dirty sensors and environmental changes",
        ),
        source="kb://robot-vacuum/common/navigation-map/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="stuck_or_obstacle",
        keywords=(
            "总是被卡住",
            "过不了门槛",
            "困住",
            "爬不上去",
            "卡在地毯",
            "撞家具",
            "gets stuck",
            "cannot cross threshold",
            "stuck on carpet",
            "hits furniture",
        ),
        hypotheses=(
            Hypothesis(
                cause_code="environment_threshold",
                label="门槛、地毯或家具间隙超出通行条件",
                confidence=0.48,
                supporting_evidence=["问题与特定位置重复出现时优先考虑环境因素"],
            ),
            Hypothesis(
                cause_code="sensor_obstructed",
                label="避障或悬崖传感器脏污",
                confidence=0.30,
                supporting_evidence=["传感器异常可能导致误判障碍"],
            ),
            Hypothesis(
                cause_code="wheel_mobility_issue",
                label="驱动轮活动受限",
                confidence=0.22,
                supporting_evidence=["轮组卡滞会降低越障能力"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="inspect_stuck_location",
            instruction="请检查卡住位置的门槛高度、地毯边缘和电线，并清洁底部传感器及驱动轮周围。",
            purpose="区分环境障碍、传感器误判和轮组问题",
        ),
        next_step_en=DiagnosticStep(
            step_id="inspect_stuck_location",
            instruction=(
                "Inspect the threshold, rug edge, and cables where it gets stuck, "
                "then clean the bottom sensors and areas around the drive wheels."
            ),
            purpose="Separate environmental, sensor, and wheel causes",
        ),
        source="kb://robot-vacuum/common/stuck-obstacle/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="auto_empty",
        keywords=(
            "不集尘",
            "集尘失败",
            "尘袋没反应",
            "基站不吸垃圾",
            "垃圾倒不进去",
            "won't empty",
            "auto empty failed",
            "dock not collecting dust",
        ),
        hypotheses=(
            Hypothesis(
                cause_code="dust_bag_or_lid",
                label="尘袋未安装到位或基站盖未闭合",
                confidence=0.45,
                supporting_evidence=["基站安全检测可能阻止集尘"],
            ),
            Hypothesis(
                cause_code="dust_channel_blocked",
                label="机器人或基站集尘风道堵塞",
                confidence=0.40,
                supporting_evidence=["大块垃圾可能堵住集尘通道"],
            ),
            Hypothesis(
                cause_code="dock_fan_fault",
                label="基站集尘风机异常",
                confidence=0.15,
                supporting_evidence=["基础检查后仍失败需检修"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="inspect_auto_empty_path",
            instruction="请重新安装尘袋并合紧基站上盖，再检查机器人尘盒出口和基站吸入口是否堵塞。",
            purpose="排除尘袋安装与集尘通道堵塞",
        ),
        next_step_en=DiagnosticStep(
            step_id="inspect_auto_empty_path",
            instruction=(
                "Reinstall the dust bag, close the dock lid securely, and inspect the "
                "robot outlet and dock inlet for blockage."
            ),
            purpose="Rule out dust bag installation and blocked emptying path",
        ),
        source="kb://robot-vacuum/common/auto-empty/v1",
    ),
    DiagnosticKnowledge(
        symptom_code="short_runtime",
        keywords=(
            "电量掉得快",
            "续航变短",
            "扫一会就没电",
            "充不满",
            "频繁回充",
            "battery drains fast",
            "short runtime",
            "won't fully charge",
        ),
        hypotheses=(
            Hypothesis(
                cause_code="high_power_mode",
                label="高吸力、地毯增压或高强度任务耗电",
                confidence=0.38,
                supporting_evidence=["工作模式会明显影响续航"],
            ),
            Hypothesis(
                cause_code="charging_contact_issue",
                label="充电触点接触不良导致未充满",
                confidence=0.34,
                supporting_evidence=["表面显示充电但可能未稳定充入"],
            ),
            Hypothesis(
                cause_code="battery_degradation",
                label="电池容量衰减",
                confidence=0.28,
                supporting_evidence=["使用时间较长时需要进一步核对循环次数"],
            ),
        ),
        next_step_zh=DiagnosticStep(
            step_id="verify_full_charge",
            instruction=(
                "请清洁充电触点，将设备连续充电至 App 显示 100%，再用标准模式记录一次实际运行时间。"
            ),
            purpose="区分未充满、模式耗电和电池衰减",
        ),
        next_step_en=DiagnosticStep(
            step_id="verify_full_charge",
            instruction=(
                "Clean the charging contacts, charge until the app shows 100%, "
                "then record one run in standard mode."
            ),
            purpose="Separate incomplete charging, mode consumption, and battery degradation",
        ),
        source="kb://robot-vacuum/common/short-runtime/v1",
    ),
)


def detect_symptoms(message: str) -> list[Symptom]:
    normalized = message.casefold()
    return [
        Symptom(code=item.symptom_code, original_text=message, severity=RiskLevel.LOW)
        for item in KNOWLEDGE
        if any(keyword.casefold() in normalized for keyword in item.keywords)
    ]


def symptoms_from_codes(codes: list[str], original_text: str) -> list[Symptom]:
    valid_codes = {item.symptom_code for item in KNOWLEDGE}
    return [
        Symptom(code=code, original_text=original_text, severity=RiskLevel.LOW)
        for code in dict.fromkeys(codes)
        if code in valid_codes
    ]


def find_knowledge(symptoms: list[Symptom]) -> list[DiagnosticKnowledge]:
    codes = {symptom.code for symptom in symptoms}
    return [item for item in KNOWLEDGE if item.symptom_code in codes]
