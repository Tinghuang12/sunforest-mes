"""每一期要到位的資金水位（萬元新台幣）

輸入全部取自紅隊第二輪財務長組 `redteam2/cfo_calc.py` 的燒錢曲線與分段撥款提案，
以及交接包 4.1、6 節。這支程式只做「把 6 個月區塊攤到季、半年」與「累計」，
另加三個標明【假設】的延伸：

1. 每個 6 個月區塊內平均攤提（不前重後輕）。
2. 第 25 個月（2028-10）以後，New Tech 維持第 2 年規模：第 2 年 A 路費用扣掉
   關卡三 3 台試點料件（一次性），沒有營收、也沒有擴編。
3. 營運資金照交接包 6 節「做 500 萬美元營收約要墊 200–300 萬美元」，即營收的
   40–60%；營收用交接包 2.5 基準路徑（人民幣）。

執行：python3 docs/plan/funding_calc.py > docs/plan/funding_calc_output.md
"""

FX = 4.4  # 台幣 / 人民幣【假設】，和研究試算一致

# ---- 財務長組燒錢曲線（A 路：只做檢驗＋後段），萬台幣 ----
P1 = (1973, 3303)   # 第 0–6 個月：2026-10 至 2027-03
P2 = (1645, 2761)   # 第 6–12 個月：2027-04 至 2027-09
YA = (2744, 4472)   # 第 2 年（第 12–24 個月：2027-10 至 2028-09）
PILOT = (204, 537)  # 第 2 年內含：關卡三 3 台試點料件（一次性）
B_EXTRA = (1745, 4516)  # B 路（整線）第 12–24 個月另加
B_HIRE = (900, 2400)    # B 路裡「加招 5–10 人」的年費用（第 25 個月起照算）
TRANCHES = [("第 1 段", "2026-10", 1800), ("第 2 段", "2027-05", 2200), ("第 3 段", "2027-11", 2500)]
S_BIZ_RMB = (50, 90)    # 交接包 4.1 標竿線現成設備，萬人民幣（本業帳）
MAINT = (4 * 180, 4 * 240)  # 維持模式 ≤4 人，每人全成本 180–240 萬/年（交接包 5.3：10 人 1,800–2,400）
REV_PATH = {2028: 1.0, 2029: 2.0, 2030: 3.5, 2031: 5.0}  # 億人民幣，交接包 2.5 基準【估算】
WC = (0.40, 0.60)       # 交接包 6 節：營運資金 ≈ 營收 40–60%


def half(x):
    return (x[0] / 2, x[1] / 2)


def add(*xs):
    return (sum(x[0] for x in xs), sum(x[1] for x in xs))


def rnd(v):
    return int(v + 0.5)  # 四捨五入（不用銀行家捨入）


def f(x):
    return f"{rnd(x[0]):,}–{rnd(x[1]):,}"


run_rate_half = half((YA[0] - PILOT[0], YA[1] - PILOT[1]))  # 第 25 個月起每半年
quarter_p1 = half(P1)
quarter_p2 = half(P2)
block = {  # 每 3 個月
    "26Q4": quarter_p1, "27Q1": quarter_p1, "27Q2": quarter_p2, "27Q3": quarter_p2,
    "27Q4": half(half(YA)), "28Q1": half(half(YA)), "28Q2": half(half(YA)), "28Q3": half(half(YA)),
}

print("# 每一期要到位的資金：試算輸出\n")
print("> `funding_calc.py` 的完整輸出，單位萬元新台幣（另註明者除外）。改參數可重算。\n")

print("## 1. 第一年，按季（照【定案】人數，A 路）\n")
print("| 季 | 期間 | 本季支出 | 累計（季末） |")
print("|---|---|---:|---:|")
cum = (0, 0)
for q, label in [("26Q4", "2026-10 至 12"), ("27Q1", "2027-01 至 03"), ("27Q2", "2027-04 至 06"), ("27Q3", "2027-07 至 09")]:
    cum = add(cum, block[q])
    print(f"| {q} | {label} | {f(block[q])} | {f(cum)} |")
print(f"\n- 本業標竿線現成設備（記本業帳）：{S_BIZ_RMB[0]}–{S_BIZ_RMB[1]} 萬人民幣 ＝ {f((S_BIZ_RMB[0]*FX, S_BIZ_RMB[1]*FX))} 萬台幣，2026 年第 4 季。")
y1 = add(P1, P2)
print(f"- 第一年合計 {f(y1)}；要讓它 ≤ 集團前一年稅前利潤的 30%【提案】，集團 2026 年稅前要 ≥ {f((y1[0]/0.3, y1[1]/0.3))}。")

print("\n## 2. 到上櫃，按半年\n")
halves = [
    ("26 下", "2026-10 至 12", block["26Q4"], (0, 0)),
    ("27 上", "2027-01 至 06", add(block["27Q1"], block["27Q2"]), (0, 0)),
    ("27 下", "2027-07 至 12", add(block["27Q3"], block["27Q4"]), half(half(B_EXTRA))),
    ("28 上", "2028-01 至 06", add(block["28Q1"], block["28Q2"]), half(B_EXTRA)),
    ("28 下", "2028-07 至 12", add(block["28Q3"], half(run_rate_half)), add(half(half(B_EXTRA)), half(half(B_HIRE)))),
]
for h, label in [("29 上", "2029-01 至 06"), ("29 下", "2029-07 至 12"), ("30 上", "2030-01 至 06"),
                 ("30 下", "2030-07 至 12"), ("31 上", "2031-01 至 06"), ("31 下", "2031-07 至 12")]:
    halves.append((h, label, run_rate_half, half(B_HIRE)))

print("| 半年 | 期間 | A 路本期 | A 路累計 | 做整線（B 路）另加本期 | A＋B 累計 |")
print("|---|---|---:|---:|---:|---:|")
ca = (0, 0)
cb = (0, 0)
for h, label, a, b in halves:
    ca = add(ca, a)
    cb = add(cb, a, b)
    print(f"| {h} | {label} | {f(a)} | {f(ca)} | {f(b) if b != (0, 0) else '—'} | {f(cb)} |")

print(f"\n- 第 25 個月（2028-10）起【假設】：A 路每半年 {f(run_rate_half)}＝第 2 年 A 路 {f(YA)} 扣掉試點料件 {f(PILOT)} 後除以 2；B 路另加「加招 5–10 人」每半年 {f(half(B_HIRE))}。都沒有扣營收。")
print(f"- 維持模式（≤4 人）【假設】：每半年 {f(half(MAINT))}。")
A24 = add(P1, P2, YA)
maint_39m = (MAINT[0] / 12 * 39, MAINT[1] / 12 * 39)  # 2028-10 至 2031-12 共 39 個月
print(f"- 走向比較（2031 年底累計）：維持模式＝24 個月 A 路 {f(A24)}＋39 個月維持 {f(maint_39m)}＝{f(add(A24, maint_39m))}；維持規模＝上表 A 路累計最後一列。")
print(f"- Pre-IPO 參考：2029–2031 六個半年維持規模要 {f((run_rate_half[0]*6, run_rate_half[1]*6))}。")

print("\n## 3. 分段撥款提案（財務長組）：每段要在何時到位\n")
print("| 段 | 最晚到位 | 金額 | 累計 |")
print("|---|---|---:|---:|")
c = 0
for name, when, amt in TRANCHES:
    c += amt
    print(f"| {name} | {when} | {amt:,} | {c:,} |")

print("\n## 4. 如果照交接包營收路徑真的賣出去：營運資金水位（年底）\n")
print("| 年底 | 營收（億人民幣） | 營運資金（億人民幣） | 營運資金（億台幣） |")
print("|---|---:|---:|---:|")
for y, rev in REV_PATH.items():
    wc = (rev * WC[0], rev * WC[1])
    print(f"| {y} | {rev} | {wc[0]:.1f}–{wc[1]:.1f} | {wc[0]*FX:.1f}–{wc[1]*FX:.1f} |")

print("\n## 5. 每年燒錢對集團稅前利潤的要求（30% 規則【提案】）\n")
print("| New Tech 燒錢年度 | A 路燒錢 | 集團前一年稅前至少 | A＋B 燒錢 | 集團前一年稅前至少 |")
print("|---|---:|---:|---:|---:|")
yr = {
    2027: (add(block["27Q1"], block["27Q2"], block["27Q3"], block["27Q4"]), add(half(half(B_EXTRA)))),
    2028: (add(block["28Q1"], block["28Q2"], block["28Q3"], half(run_rate_half)), add(half(B_EXTRA), half(half(B_EXTRA)), half(half(B_HIRE)))),
}
for y, (a, b) in yr.items():
    ab = add(a, b)
    print(f"| {y} | {f(a)} | {f((a[0]/0.3, a[1]/0.3))} | {f(ab)} | {f((ab[0]/0.3, ab[1]/0.3))} |")
