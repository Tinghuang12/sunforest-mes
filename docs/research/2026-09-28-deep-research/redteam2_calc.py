#!/usr/bin/env python3
"""紅隊第二輪：把幾種「做法」的錢算清楚。

只用 Python 標準庫。執行：python3 redteam2_calc.py
輸入全部來自交接包（3.2、4.1、4.2、5.1、5.3、6 節）、研究第 3 章 [M2-1]、第一輪紅隊與 T1 規格；
【假設】另標。金額單位：萬元人民幣，另有註明者除外。
"""

WAGE = 9.0            # 萬元／人年，交接包 6 節；第一輪紅隊認為檢驗工比 11.8 萬更接近 9 萬
NTD_PER_RMB = 4.4     # 【假設】匯率，1 人民幣＝4.4 新台幣

# ── 做法 A：不自研，只買現成設備與改製程（每千片日）──────────────────────
# (項目, 省幾人, 設備成本下限, 上限, 備註)；省人取自交接包 3.2，成本取自交接包 4.2、5.1
BUY_EXISTING = [
    ("燈箱台（第 0 層）",       2.00, 5, 10, "交接包 4.2；5.1 寫自建 10–20 萬"),
    ("隧道檢針機",              2.50, 3, 5,  "前提：非鐵環（交接包 4.2 紅線）"),
    ("機台自動剪線",            1.24, 0, 0,  "交接包 4.1 列為零成本製程改造；若現有平車沒有此功能要另買"),
    ("封口改順序",              0.63, 0, 0,  "交接包 4.1 零成本製程改造"),
    ("套袋機",                  1.27, 8, 15, "包裝 1.67→0.4"),
    ("封箱機",                  0.18, 1, 3,  "入箱 0.38→0.2"),
    ("打孔上環一體機",          0.50, 5, 10, "打孔 0.37→0.3、打環 0.73→0.3"),
    ("自動卷邊（包小邊）",      1.02, 3, 8,  "包小邊 1.52→0.5；交接包 1.3：買現成單元改造"),
]
FOLDING = ("摺疊機（帶環簾，未驗證）", 2.24, 15, 30, "摺疊 2.74→0.5；帶環塗層簾能否自動摺疊，第 5 章列為先驗證")
AI_LAYER1 = 1.0       # 第 1 層相機輔助判定多省的人（交接包 4.2）
OWN_LINE_KPCS = 0.5   # 自家昆山線 500 片/日（交接包 3.1、4.2）

# ── New Tech 首年預算（交接包 5.1、5.3；萬元新台幣）──────────────────────
TEAM_FULL_COST_NTD = (1800, 2400)   # 首批 10 人全成本
RECRUIT_NTD = (150, 250)
RND_CENTER_NTD = (1000, 1600)       # 台中研發中心首年基礎建設

# ── 對外賣 AI 檢驗層的市場（研究第 3 章分析一；第一輪紅隊）──────────────
KPCS_UNITS = (1267, 3378)           # 出口成品簾「千片日單位」[M2-1]
ADOPT_PER_YEAR = 0.03               # 交接包自己的 30% ÷ 10 年
STATION_CAP = 2990                  # 雙夾桿單台片/日（T1 5.2）
STATION_PRICE = (40, 60)            # 買方紅隊：AI 層按台 40 萬開價、上限約 60 萬
GM = (0.35, 0.40)                   # 實現毛利：投資人紅隊第二期門檻 35%；交接包 40%


def rng(a, b, nd=1):
    return f"{a:,.{nd}f}–{b:,.{nd}f}"


def option_a():
    rows = ["| 項目 | 每千片日省幾人 | 設備 萬元 | 備註 |", "|---|---:|---:|---|"]
    ppl = lo = hi = 0.0
    for name, p, a, b, note in BUY_EXISTING:
        rows.append(f"| {name} | {p:.2f} | {a}–{b} | {note} |")
        ppl += p; lo += a; hi += b
    rows.append(f"| **小計（不含摺疊）** | **{ppl:.2f}** | **{lo:.0f}–{hi:.0f}** | |")
    name, p, a, b, note = FOLDING
    rows.append(f"| {name} | {p:.2f} | {a}–{b} | {note} |")
    ppl2, lo2, hi2 = ppl + p, lo + a, hi + b
    rows.append(f"| **合計（含摺疊）** | **{ppl2:.2f}** | **{lo2:.0f}–{hi2:.0f}** | |")
    table = "\n".join(rows)

    def summary(persons, c_lo, c_hi, label):
        save = persons * WAGE
        return (f"| {label} | {persons:.2f} | {save:.1f} | {rng(c_lo, c_hi, 0)} | "
                f"{rng(c_lo / save * 12, c_hi / save * 12)} | "
                f"{persons * OWN_LINE_KPCS:.2f} | {save * OWN_LINE_KPCS:.1f} |")
    s = ["| 範圍 | 每千片日省幾人 | 每千片日年省 萬元 | 設備 萬元 | 回本 月 | 自家線（500 片/日）省幾人 | 自家線年省 萬元 |",
         "|---|---:|---:|---:|---:|---:|---:|",
         summary(ppl, lo, hi, "不含摺疊"),
         summary(ppl2, lo2, hi2, "含摺疊"),
         f"| 對照：AI 第 1 層 | {AI_LAYER1:.2f} | {AI_LAYER1 * WAGE:.1f} | 15–25（交接包 4.2） | "
         f"{rng(15 / (AI_LAYER1 * WAGE) * 12, 25 / (AI_LAYER1 * WAGE) * 12)} | "
         f"{AI_LAYER1 * OWN_LINE_KPCS:.2f} | {AI_LAYER1 * WAGE * OWN_LINE_KPCS:.1f} |"]
    return table, "\n".join(s), ppl, ppl2


def new_tech_budget():
    lo = TEAM_FULL_COST_NTD[0] + RECRUIT_NTD[0] + RND_CENTER_NTD[0]
    hi = TEAM_FULL_COST_NTD[1] + RECRUIT_NTD[1] + RND_CENTER_NTD[1]
    return lo, hi, lo / NTD_PER_RMB, hi / NTD_PER_RMB


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
    return "\n".join(rows), st_total, st_year, rev, gp


def main():
    table, summ, ppl, ppl2 = option_a()
    print("## 1. 做法 A：不自研，只買現成設備與改製程（交接包 3.2、4.1、4.2、5.1）\n")
    print(table, "\n")
    print(summ, "\n")
    print(f"- 買現成（不含摺疊）每千片日省 {ppl:.2f} 人，是 AI 第 1 層（{AI_LAYER1:.1f} 人）的 {ppl / AI_LAYER1:.1f} 倍【估算】。\n")

    lo, hi, rlo, rhi = new_tech_budget()
    print("## 2. New Tech 首年預算（交接包 5.1、5.3）\n")
    print(f"- 首批 10 人全成本 {TEAM_FULL_COST_NTD[0]:,}–{TEAM_FULL_COST_NTD[1]:,} ＋ 招募 {RECRUIT_NTD[0]}–{RECRUIT_NTD[1]} ＋ 台中研發中心 {RND_CENTER_NTD[0]:,}–{RND_CENTER_NTD[1]:,}"
          f" ＝ {lo:,}–{hi:,} 萬新台幣，約 {rng(rlo, rhi, 0)} 萬人民幣【估算，匯率 {NTD_PER_RMB} 為假設】。\n")

    t, st_total, st_year, rev, gp = external_market()
    print("## 3. 對外賣檢驗單元：每年能賣多少（出口成品簾口徑）\n")
    print(t, "\n")
    print(f"- 出口成品簾全部裝滿，約需雙夾桿檢驗台 {rng(*st_total, 0)} 台【估算：千片日單位 × 1,000 ÷ 2,990】。")
    print(f"- 紅隊版定價下，每年毛利 {rng(*gp, 0)} 萬，New Tech 首年預算 {rng(rlo, rhi, 0)} 萬；"
          f"要 {rng(rlo / gp[1], rhi / gp[0])} 年的全市場毛利才抵得過一年預算【估算】。")
    print("- 這只算中國出口成品簾；若檢驗台也能用在國內簾、床單、被套等平幅家紡，市場會放大，但目前沒有算式。")


if __name__ == "__main__":
    main()
