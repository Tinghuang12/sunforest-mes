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
            ("機台自動剪線", TRIM_SAVED, "標準功能：中日本ジューキ等 [V1-N6]；交接包 4.1 零成本製程改造")]
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
    """只算我方視覺真正多創造的省人（第 1 層：1.0 人／千片日），依交接包定價公式。"""
    saved = INSPECT["第 0 層"] - INSPECT["第 1 層"]
    out = ["| 客戶日產量（片） | 售價上限 萬元（9 萬） | 售價上限 萬元（11.8 萬） | 以 T1 硬體成本 15.5–40.7 萬計，40% 毛利所需售價 |",
           "|---:|---:|---:|---:|"]
    need = (T1_BOM[0] / 0.6, T1_BOM[1] / 0.6)
    for v in (500, 1000, 2000, 3000, 5000):
        c9 = saved * v / 1000 * 9.0 * PAYBACK_YEARS
        c118 = saved * v / 1000 * 11.8 * PAYBACK_YEARS
        out.append(f"| {v:,} | {c9:.1f} | {c118:.1f} | {need[0]:.1f}–{need[1]:.1f} |")
    breakeven9 = (need[0] / (saved * 9.0 * PAYBACK_YEARS) * 1000, need[1] / (saved * 9.0 * PAYBACK_YEARS) * 1000)
    breakeven118 = (need[0] / (saved * 11.8 * PAYBACK_YEARS) * 1000, need[1] / (saved * 11.8 * PAYBACK_YEARS) * 1000)
    note = (f"要讓視覺層在 1.5 年回收下仍有 40% 毛利，客戶日產需約 {breakeven9[0]:,.0f}–{breakeven9[1]:,.0f} 片（9 萬）"
            f"或 {breakeven118[0]:,.0f}–{breakeven118[1]:,.0f} 片（11.8 萬）【估算】。")
    return "\n".join(out), note


def sample_days():
    out = ["| 每類缺陷發生率（占片數） | 日產 500 片 | 日產 1,000 片 | 日產 2,000 片 |", "|---:|---:|---:|---:|"]
    for rate in (0.01, 0.005, 0.002, 0.001):
        cells = [f"{598 / (v * rate):,.0f} 天" for v in (500, 1000, 2000)]
        out.append(f"| {rate:.1%} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    t, ai_share = decomposition()
    print("## 1. 「檢驗單元省 6.7 人」的來源拆解（交接包 3.2、4.2、6）\n")
    print(t, "\n")
    print(f"需要我方視覺技術的部分只占約 {ai_share:.0%}【估算】。\n")
    print("## 2. 各層的邊際回收期（每千片日；交接包 4.2 成本）\n")
    print(marginal_payback(), "\n")
    print("## 3. 只算視覺層多創造的價值時，售價上限夠不夠（交接包 6 節公式：省人 × 人年成本 × 1.5 年）\n")
    t, note = ai_price_ceiling()
    print(t, "\n")
    print(note, "\n")
    print("## 4. 自然累積 598 個缺陷樣本（每類，漏檢 <0.5% 零失敗驗收）需要幾天\n")
    print(sample_days())


if __name__ == "__main__":
    main()
