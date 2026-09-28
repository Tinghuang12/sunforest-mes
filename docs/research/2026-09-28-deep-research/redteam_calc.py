#!/usr/bin/env python3
"""紅隊計算：用交接包自己的數字，檢驗「檢驗單元售價 ≤90 萬、毛利 ≥40%」與 AI 驗收時程。

只用 Python 標準庫。執行：python3 redteam_calc.py
輸入全部來自交接包（3.2、4.2、5.1、6 節）與研究查核結果；【估算】另標。
"""

WAGE = {"交接包 9 萬": 9.0, "研究 11.8 萬（M3-1 區間中點）": 11.8}   # 萬元／人年
PAYBACK_YEARS = 1.5                                                  # 交接包 6 節定價公式

# 交接包 3.2 與 4.2：每千片日產人數
INSPECT = {"現況": 4.0, "第 0 層": 2.0, "第 1 層": 1.0, "第 2 層": 0.5}
NEEDLE_SAVED = 2.5     # 檢針 2.50 → 0（隧道檢針機，交接包 4.1、5.1 列為外購）
TRIM_SAVED = 1.24      # 剪線 1.54 → 0.3（機台自動剪線，交接包 4.1 列為零成本製程改造）

# 交接包 4.2 各層設備估算（萬元）；T1 規格 BOM（第 1 層整台硬體）
LAYER_COST = {"第 0 層": (5, 10), "第 1 層": (15, 25), "第 2 層": (20, 30)}
T1_BOM = (15.45, 40.65)


def fmt(a, b, nd=1):
    return f"{a:.{nd}f}–{b:.{nd}f}"


def decomposition():
    layer0 = INSPECT["現況"] - INSPECT["第 0 層"]
    layer1 = INSPECT["第 0 層"] - INSPECT["第 1 層"]
    total = layer0 + layer1 + NEEDLE_SAVED + TRIM_SAVED
    rows = [("機械燈箱台（第 0 層，無 AI）", layer0, "可外購：HCW SA-CIM-3300 等 [V1-N2]"),
            ("相機輔助判定（第 1 層，需要我方視覺）", layer1, "我方技術"),
            ("隧道檢針機", NEEDLE_SAVED, "標準品：Hashima 等 [V3-N5]"),
            ("機台自動剪線", TRIM_SAVED, "機台功能：中日本ジューキ窗簾縫製機已含自動剪線 [V1-N6]；交接包 4.1 零成本製程改造")]
    out = ["| 省人來源（每千片日） | 省幾人 | 占 6.7 人 | 取得方式 |", "|---|---:|---:|---|"]
    for name, v, how in rows:
        out.append(f"| {name} | {v:.2f} | {v/total:.0%} | {how} |")
    out.append(f"| **合計** | **{total:.2f}** | 100% | 交接包 6 節寫 6.7 |")
    return "\n".join(out), layer1 / total


def marginal_payback():
    out = ["| 層 | 這一層多省幾人（每千片日） | 設備成本 萬元（交接包 4.2） | 回收年（9 萬） | 回收年（11.8 萬） |",
           "|---|---:|---:|---:|---:|"]
    prev = INSPECT["現況"]
    for layer in ("第 0 層", "第 1 層", "第 2 層"):
        saved = prev - INSPECT[layer]
        lo, hi = LAYER_COST[layer]
        p9 = (lo / (saved * 9.0), hi / (saved * 9.0))
        p118 = (lo / (saved * 11.8), hi / (saved * 11.8))
        out.append(f"| {layer} | {saved:.1f} | {lo}–{hi} | {fmt(*p9, 2)} | {fmt(*p118, 2)} |")
        prev = INSPECT[layer]
    return "\n".join(out)


def ai_price_ceiling():
    """T1 整台（第 0＋1 層）客戶願付的價＝自己買燈箱台的價（交接包 4.2：5–10 萬）＋視覺增量價值。
    視覺增量價值＝第 1 層多省的 1.0 人／千片日 × 日產 ÷ 1,000 × 人年成本 × 1.5 年（交接包 6 節公式）。
    40% 毛利所需售價＝T1 硬體 BOM ÷ 0.6（BOM 為 T1 規格 8.1 節【估算】，多數未詢價）。"""
    saved = INSPECT["第 0 層"] - INSPECT["第 1 層"]
    alt = LAYER_COST["第 0 層"]
    need = (T1_BOM[0] / 0.6, T1_BOM[1] / 0.6)
    out = ["| 單台日產（片） | 客戶願付上限 萬元（9 萬） | 客戶願付上限 萬元（11.8 萬） | 40% 毛利所需售價 萬元 |",
           "|---:|---:|---:|---:|"]
    for v, label in ((500, "500（自家線現況）"), (1000, "1,000"), (1688, "1,688（單夾桿滿載）"), (2990, "2,990（雙夾桿滿載）")):
        c9 = (alt[0] + saved * v / 1000 * 9.0 * PAYBACK_YEARS, alt[1] + saved * v / 1000 * 9.0 * PAYBACK_YEARS)
        c118 = (alt[0] + saved * v / 1000 * 11.8 * PAYBACK_YEARS, alt[1] + saved * v / 1000 * 11.8 * PAYBACK_YEARS)
        out.append(f"| {label} | {fmt(*c9)} | {fmt(*c118)} | {fmt(*need)} |")

    def breakeven(wage):  # 最有利：BOM 低、燈箱台替代價高；最不利：BOM 高、替代價低
        return ((need[0] - alt[1]) / (saved * wage * PAYBACK_YEARS) * 1000,
                (need[1] - alt[0]) / (saved * wage * PAYBACK_YEARS) * 1000)
    b9, b118 = breakeven(9.0), breakeven(11.8)
    note = (f"要讓 T1 在 1.5 年回收下仍有 40% 毛利，單台日產需約 {b9[0]:,.0f}–{b9[1]:,.0f} 片（9 萬）"
            f"或 {b118[0]:,.0f}–{b118[1]:,.0f} 片（11.8 萬）【估算】；雙夾桿單台上限約 2,990 片/日（T1 5.2）。")
    return "\n".join(out), note


def sample_days():
    out = ["| 每類缺陷發生率（占片數） | 日產 500 片 | 日產 1,000 片 | 日產 2,000 片 |", "|---:|---:|---:|---:|"]
    for rate in (0.01, 0.005, 0.002, 0.001):
        cells = [f"{598 / (v * rate):,.0f} 天" for v in (500, 1000, 2000)]
        out.append(f"| {rate:.1%} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def provable_bound():
    """12 週內每類能證明到的漏檢上界：零漏檢時 95% 信賴上界＝1 − 0.05^(1/n)。每週 6 天、日產 500 片【假設】。"""
    out = ["| 單一類發生率 | 只用 W9–12（12,000 片）：n／可證明上界 | 用滿 12 週（36,000 片）：n／可證明上界 |",
           "|---:|---:|---:|"]
    for rate in (0.01, 0.005, 0.002, 0.001):
        cells = []
        for pcs in (12_000, 36_000):
            n = pcs * rate
            cells.append(f"{n:,.0f}／{1 - 0.05 ** (1 / n):.1%}")
        out.append(f"| {rate:.1%} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def night_shift():
    """交接包 4.5「MTBF ≥4 小時、80% 自恢復」的兩種讀法；故障設為指數分布【假設】。"""
    import math
    out = ["| 讀法 | 需人故障平均間隔 | 一夜 8 小時不停的機率 | 夜班期望有效時間 | 全日產量（白班 16 h × OEE 65%＋夜班）片/日 | 回收年（交接包 1.2 年 × 2,800 ÷ 產量） |",
           "|---|---:|---:|---:|---:|---:|"]
    for name, m in (("A：4 h 指全部故障，需人故障 20 h 一次", 20.0), ("B：4 h 指需人故障", 4.0)):
        p = math.exp(-8 / m)
        eff = m * (1 - p) / 8
        night_oee = eff * 0.95 * 0.98
        pcs = 150 * (16 * 0.65 + 8 * night_oee)
        out.append(f"| {name} | {m:.0f} h | {p:.0%} | {eff:.0%} | {pcs:,.0f} | {1.2 * 2800 / pcs:.2f} |")
    return "\n".join(out)


def per_machine():
    """按千片定價 vs 按台：年產 300 萬片、300 天、雙夾桿每台 2,990 片/日（T1 5.2）。"""
    import math
    daily = 3_000_000 / 300
    units = math.ceil(daily / 2990)
    formula = daily / 1000 * 90
    hw = (units * T1_BOM[0], units * T1_BOM[1])
    return (f"日產 {daily:,.0f} 片：照交接包公式售價 {daily/1000:.0f} × 90＝{formula:,.0f} 萬；"
            f"實際只需雙夾桿 {units} 台，硬體 {hw[0]:.0f}–{hw[1]:.0f} 萬；"
            f"售價是硬體的 {formula/hw[1]:.1f}–{formula/hw[0]:.1f} 倍【估算】。")


def sam_gap():
    """投資人紅隊：基準情景 2036 年裝備 9 億 vs 由下而上 SAM（研究第 3 章分析一的算法 [M2-1]，不先四捨五入）。"""
    target = 9.0

    def sam(fob):  # 30.4 億美元 ÷ FOB ÷ 300 日 ÷ 1,000 × 18.6 人 × 9 萬 × 4.5%，單位億元
        return 30.4e8 / fob / 300 / 1000 * 18.6 * 9.0 * 0.045 / 1e4

    lo, hi = sam(8), sam(3)
    wide = hi * 12.2 / 9 * 2            # 第 3 章：全成本上限 × 國內等量
    out = ["| SAM 口徑 | SAM 億元/年 | 9 億是 SAM 的幾倍 | 就算拿下 100% 仍缺 |", "|---|---:|---:|---:|",
           f"| 只算出口成品簾 | {lo:.2f}–{hi:.2f} | {target/hi:.1f}–{target/lo:.1f} | {target-hi:.2f} 億（{(target-hi)/target:.0%}）以上 |",
           f"| 出口＋國內等量、工資取上限（最寬鬆） | 約 {wide:.1f} | {target/wide:.1f} | {target-wide:.2f} 億（{(target-wide)/target:.0%}） |"]
    return "\n".join(out)


def net_payback():
    """買方紅隊：年費＋維護占售價 5／10／15%【假設】時，90 萬檢驗單元的淨回收期（9 萬口徑）。"""
    gross = 6.74 * 9.0
    out = ["| 年費＋維護占售價 | 淨年省 萬元 | 淨回收年 |", "|---:|---:|---:|"]
    for r in (0.05, 0.10, 0.15):
        net = gross - 90 * r
        out.append(f"| {r:.0%} | {net:.1f} | {90/net:.2f} |")
    return "\n".join(out)


def main():
    t, ai_share = decomposition()
    print("## 1. 「檢驗單元省 6.7 人」的來源拆解（交接包 3.2、4.2、6）\n")
    print(t, "\n")
    print(f"需要我方視覺技術的部分只占約 {ai_share:.0%}【估算】。\n")
    print("## 2. 各層的邊際回收期（每千片日；交接包 4.2 成本）\n")
    print(marginal_payback(), "\n")
    print("## 3. T1 整台賣得到的價 vs 40% 毛利所需售價（客戶可改買燈箱台，所以只為視覺增量多付）\n")
    t, note = ai_price_ceiling()
    print(t, "\n")
    print(note, "\n")
    print("## 4. 自然累積 598 個缺陷樣本（每類，漏檢 <0.5% 零失敗驗收）需要幾天\n")
    print(sample_days(), "\n")
    print("## 5. 12 週內每類實際能證明到的漏檢上界（零漏檢、95% 信賴）\n")
    print(provable_bound(), "\n")
    print("## 6. 夜班無人：「MTBF ≥4 小時、80% 自恢復」兩種讀法（交接包 4.5）\n")
    print(night_shift(), "\n")
    print("## 7. 按千片定價在大廠的結果\n")
    print(per_machine(), "\n")
    print("## 8. 基準情景裝備 9 億 vs 由下而上 SAM\n")
    print(sam_gap(), "\n")
    print("## 9. 扣掉年費與維護後的淨回收期（檢驗單元 90 萬、省 6.74 人、9 萬/人年）\n")
    print(net_payback())


if __name__ == "__main__":
    main()
