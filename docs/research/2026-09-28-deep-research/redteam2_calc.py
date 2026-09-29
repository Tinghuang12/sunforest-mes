#!/usr/bin/env python3
"""紅隊第二輪：把幾種「做法」的錢算清楚。

只用 Python 標準庫。執行：python3 redteam2_calc.py
輸入全部來自交接包（3.1、3.2、4.1、4.2、5.1、5.3、6 節）、研究第 3 章 [M2-1]、第一輪紅隊、
T1 規格，以及第二輪財務長組的 24 個月現金表（redteam2/cfo_calc.py）；【假設】另標。
金額單位：萬元人民幣，另有註明者除外。
"""

WAGE = 9.0            # 萬元／人年，交接包 6 節；第一輪紅隊認為檢驗工比 11.8 萬更接近 9 萬
NTD_PER_RMB = 4.4     # 【假設】匯率，1 人民幣＝4.4 新台幣
FULL_LINE_SAVE = 13.3 # 交接包 3.2：整線每千片日 18.6 → 5.3 人

# ── 做法 A：不自研，只買現成設備與改製程（每千片日）──────────────────────
# (項目, 省幾人, 設備成本下限, 上限, 情境)；省人取自交接包 3.2，成本取自交接包 4.2、5.1
# 情境與第二輪財務長組一致：S1 最保守；S2 加縫製卷邊與送料改造；S3 再加摺疊機
BUY_EXISTING = [
    ("封口改順序（零成本）",        0.63, 0,  0,  "S1"),
    ("機台自動剪線（零成本）",      1.24, 0,  0,  "S1"),
    ("燈箱台（第 0 層）",           2.00, 5,  20, "S1"),   # 4.2 寫 5–10、5.1 寫自建 10–20，取全距
    ("隧道檢針機",                  2.50, 3,  5,  "S1"),   # 前提：非鐵環（交接包 4.2 紅線）
    ("套袋機",                      1.27, 8,  15, "S1"),
    ("封箱機",                      0.18, 1,  3,  "S1"),
    ("打孔上環一體機",              0.50, 5,  10, "S1"),
    ("自動卷邊與送料改造（3 台）",  1.76, 9,  24, "S2"),   # 包小邊 1.02＋上擺 0.4＋下擺 0.34；3 × 3–8 萬
    ("摺疊機（帶環簾，未驗證）",    2.24, 15, 30, "S3"),   # 12/15 打樣成功才成立
]
AI_LAYER1 = (0.5, 1.0)  # 相機比燈箱台多省的人：3.2 口徑 0.5、4.2 口徑 1.0
AI_LAYER1_COST = (15, 25)   # 交接包 4.2
OWN_LINE_KPCS = 0.5     # 自家昆山線 500 片/日（交接包 3.1）

# ── New Tech 現金（萬元新台幣）──────────────────────────────────────────
FIRST_YEAR_HANDOFF_NTD = (1800 + 150 + 1000, 2400 + 250 + 1600)  # 交接包 5.3、5.1 只列的三項
CASH24_A_NTD = (6362, 10536)   # 財務長組：只做檢驗＋後段，24 個月
CASH24_B_NTD = (8107, 15052)   # 財務長組：照交接包串整線，24 個月
TRANCHE1_NTD = (1094, 1914)    # 財務長組：精簡版第 1 段，9 個月

# ── 對外賣 AI 檢驗層的市場（研究第 3 章分析一；第一輪紅隊）──────────────
KPCS_UNITS = (1267, 3378)      # 出口成品簾「千片日單位」[M2-1]
ADOPT_PER_YEAR = 0.03          # 交接包自己的 30% ÷ 10 年
STATION_CAP = 2990             # 雙夾桿單台片/日（T1 5.2）
STATION_PRICE = (40, 60)       # 買方紅隊：AI 層按台 40 萬開價、上限約 60 萬
GM = (0.35, 0.40)              # 實現毛利：投資人紅隊第二期門檻 35%；交接包 40%

# ── 法規組：遣散對客戶回收期的影響 ──────────────────────────────────────
SOCIAL = (1.30, 1.35)          # 交接包 5.3 社保係数
BASE_PAYBACK = 1.5             # 交接包 6 節：省人 × 人年成本 × 1.5 年


def rng(a, b, nd=1):
    x, y = f"{a:,.{nd}f}", f"{b:,.{nd}f}"
    return x if x == y else f"{x}–{y}"


def ntd2rmb(x):
    return (x[0] / NTD_PER_RMB, x[1] / NTD_PER_RMB)


def option_a():
    rows = ["| 項目 | 每千片日省幾人 | 設備 萬元 | 情境 |", "|---|---:|---:|---|"]
    for name, p, a, b, s in BUY_EXISTING:
        rows.append(f"| {name} | {p:.2f} | {rng(a, b, 0)} | {s} 起 |")
    table = "\n".join(rows)
    scen = {}
    for s in ("S1", "S2", "S3"):
        keep = [x for x in BUY_EXISTING if x[4] <= s]
        ppl = sum(x[1] for x in keep)
        lo = sum(x[2] for x in keep)
        hi = sum(x[3] for x in keep)
        scen[s] = (ppl, lo, hi)
    s_rows = ["| 情境 | 每千片日省幾人 | 占整線 13.3 人 | 年省 萬元 | 設備 萬元 | 回本 月 | 昆山線（500 片/日）年省 萬元 |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for s, (ppl, lo, hi) in scen.items():
        save = ppl * WAGE
        s_rows.append(f"| {s} | {ppl:.2f} | {ppl / FULL_LINE_SAVE:.0%} | {save:.1f} | {lo:.0f}–{hi:.0f} | "
                      f"{rng(lo / save * 12, hi / save * 12)} | {save * OWN_LINE_KPCS:.1f} |")
    a_lo, a_hi = AI_LAYER1
    s_rows.append(f"| 對照：AI 第 1 層（相機比燈箱台多省） | {a_lo:.1f}–{a_hi:.1f} | {a_lo / FULL_LINE_SAVE:.0%}–{a_hi / FULL_LINE_SAVE:.0%} | "
                  f"{a_lo * WAGE:.1f}–{a_hi * WAGE:.1f} | {AI_LAYER1_COST[0]}–{AI_LAYER1_COST[1]} | "
                  f"{rng(AI_LAYER1_COST[0] / (a_hi * WAGE) * 12, AI_LAYER1_COST[1] / (a_lo * WAGE) * 12, 0)} | "
                  f"{a_lo * WAGE * OWN_LINE_KPCS:.2f}–{a_hi * WAGE * OWN_LINE_KPCS:.1f} |")
    return table, "\n".join(s_rows), scen


def external_market():
    st_total = (KPCS_UNITS[0] * 1000 / STATION_CAP, KPCS_UNITS[1] * 1000 / STATION_CAP)
    st_year = (st_total[0] * ADOPT_PER_YEAR, st_total[1] * ADOPT_PER_YEAR)
    rev = (st_year[0] * STATION_PRICE[0], st_year[1] * STATION_PRICE[1])
    gp = (rev[0] * GM[0], rev[1] * GM[1])
    orig = (KPCS_UNITS[0] * ADOPT_PER_YEAR * 90, KPCS_UNITS[1] * ADOPT_PER_YEAR * 90)
    rows = ["| 定價口徑 | 每年可賣 | 每年營收 萬元 | 每年毛利 萬元 |", "|---|---:|---:|---:|",
            f"| 交接包原公式（每千片日 90 萬，含燈箱台、檢針、剪線） | {rng(KPCS_UNITS[0] * ADOPT_PER_YEAR, KPCS_UNITS[1] * ADOPT_PER_YEAR, 0)} 個千片日單位 | "
            f"{rng(*orig, 0)} | {rng(orig[0] * GM[0], orig[1] * GM[1], 0)} |",
            f"| 紅隊版（只賣 AI 層，按台 40–60 萬，雙夾桿單台 2,990 片/日） | {rng(*st_year)} 台 | {rng(*rev, 0)} | {rng(*gp, 0)} |"]
    return "\n".join(rows), st_total, gp


def severance():
    rows = ["| 被替代員工平均年資 | 每人經濟補償 N 萬元 | 回收期：N | 回收期：違法解除 2N |", "|---:|---:|---:|---:|"]
    m = (WAGE / SOCIAL[1] / 12, WAGE / SOCIAL[0] / 12)   # 萬元/月，全成本扣社保
    for yrs in (3, 5, 8):
        n = (yrs * m[0], yrs * m[1])
        rows.append(f"| {yrs} 年 | {rng(*n, 2)} | {rng(BASE_PAYBACK + n[0] / WAGE, BASE_PAYBACK + n[1] / WAGE, 2)} 年 | "
                    f"{rng(BASE_PAYBACK + 2 * n[0] / WAGE, BASE_PAYBACK + 2 * n[1] / WAGE, 2)} 年 |")
    return "\n".join(rows), m


def main():
    table, summ, scen = option_a()
    print("## 1. 做法 A：不自研，只買現成設備與改製程（交接包 3.2、4.1、4.2、5.1）\n")
    print(table, "\n")
    print(summ, "\n")
    s1 = scen["S1"][0]
    print(f"- S1 每千片日省 {s1:.2f} 人，是 AI 第 1 層（{AI_LAYER1[0]}–{AI_LAYER1[1]} 人）的 "
          f"{s1 / AI_LAYER1[1]:.1f}–{s1 / AI_LAYER1[0]:.1f} 倍【估算】。")
    lo, hi = scen["S1"][1], scen["S1"][2]
    own = s1 * WAGE * OWN_LINE_KPCS
    print(f"- 自家昆山線只有 {OWN_LINE_KPCS} 個千片日，但每種機器至少要買 1 台，設備不會減半【推論】；"
          f"S1 回本約 {rng(lo / own * 12, hi / own * 12)} 個月【估算：{lo}–{hi} ÷ {own:.1f} × 12】。\n")

    print("## 2. New Tech 要花多少（萬元新台幣；24 個月數字取自財務長組 cfo_calc.py）\n")
    fy = FIRST_YEAR_HANDOFF_NTD
    print(f"- 交接包只列的首年三項（10 人、招募、台中研發中心）：{fy[0]:,}–{fy[1]:,} 萬台幣，約 {rng(*ntd2rmb(fy), 0)} 萬人民幣。")
    for label, c in (("只做檢驗＋後段（A 路）", CASH24_A_NTD), ("照交接包串整線（B 路）", CASH24_B_NTD)):
        r = ntd2rmb(c)
        print(f"- 24 個月，{label}：{c[0]:,}–{c[1]:,} 萬台幣，約 {rng(*r, 0)} 萬人民幣。")
    t = TRANCHE1_NTD
    print(f"- 財務長組精簡版第 1 段（9 個月）：{t[0]:,}–{t[1]:,} 萬台幣，約 {rng(*ntd2rmb(t), 0)} 萬人民幣。\n")
    s1_lo, s1_hi = scen["S1"][1], scen["S1"][2]
    fyr = ntd2rmb(fy)
    print(f"- 交接包首年三項，夠買 S1 設備 {fyr[0] / s1_hi:.0f}–{fyr[1] / s1_lo:.0f} 個千片日【估算：{rng(*fyr, 0)} ÷ S1 設備 {s1_lo}–{s1_hi} 萬】。\n")

    t, st_total, gp = external_market()
    print("## 3. 對外賣檢驗單元：每年能賣多少（中國出口成品簾口徑）\n")
    print(t, "\n")
    a24 = ntd2rmb(CASH24_A_NTD)
    print(f"- 出口成品簾全部裝滿，約需雙夾桿檢驗台 {rng(*st_total, 0)} 台【估算：千片日單位 × 1,000 ÷ 2,990】。")
    print(f"- 紅隊版定價下，**全市場**每年毛利 {rng(*gp, 0)} 萬。就算全部拿下，要 {rng(a24[0] / gp[1], a24[1] / gp[0])} 年"
          f"才抵得過 A 路 24 個月的現金 {rng(*a24, 0)} 萬【估算】。")
    print("- 這只算中國出口成品簾，年採用率 3% 沿用交接包；若檢驗台也能用在國內簾、床單、被套等平幅家紡，市場會放大，但目前沒有算式。\n")

    t, m = severance()
    print("## 4. 客戶要裁人時，遣散把回收期拉長多少（法規組 P2）\n")
    print(f"- 月工資＝{WAGE} 萬 ÷ {SOCIAL[0]}–{SOCIAL[1]} ÷ 12 ≈ {m[0] * 1e4:,.0f}–{m[1] * 1e4:,.0f} 元；N＝年資 × 月工資；回收期＝{BASE_PAYBACK} 年 ＋ 遣散 ÷ {WAGE} 萬。\n")
    print(t, "\n")
    print("- 平均年資 ≥5 年而且違法解除（2N），就超過關卡二的 2 年；8 年時，合法協商（N）也剛好碰線。")


if __name__ == "__main__":
    main()
