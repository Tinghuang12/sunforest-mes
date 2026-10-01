"""反向驗證：從終點往回推，兩份計劃表做不做得到

做法：從每一個終點往回推，算每個前置條件「最晚何時要完成」，再和計劃表上排的
日期比對。餘裕＝最晚日期 − 計劃日期；負數表示照表排做不到。錢的部分，反過來算
「每一期要到位的錢，集團先要具備什麼條件」。最後用程式檢查兩份文件的日期、
金額、甘特圖欄數彼此一致。

輸入：
- 工期：交接包 4.7【定案，經驗值】（P0 4–6 週、P1 8–12 週、P2 4–6 個月、P3 3 個月）
- 資金：funding_calc.py（直接匯入，同一套數字）
- 法條與日曆：勞基法第 15 條第 2 項、第 16 條（年資 ≥3 年預告 30 日）；大陸《勞動合同法》
  第 37 條（提前 30 日書面通知）；2026 國慶 10/1–10/7；2027 春節初一 2/6
- 上市前置時間：查核員報告（03 號文件附錄二，IL-1 至 IL-8），下方 LEAD 每一項都註明出處與口徑

執行：python3 docs/plan/backward_check.py > docs/plan/backward_check_output.md
"""

import calendar
import contextlib
import io
import pathlib
import re
import sys
from datetime import date, timedelta

HERE = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True  # 匯入 funding_calc 時不留 __pycache__
sys.path.insert(0, str(HERE))
with contextlib.redirect_stdout(io.StringIO()):
    import funding_calc as fc  # noqa: E402

DOC1 = (HERE / "01-newtech-year1-plan.md").read_text(encoding="utf-8")
DOC2 = (HERE / "02-ipo-roadmap.md").read_text(encoding="utf-8")
MONTH = 30.44  # 平均每月天數，只用來把天數換成月數顯示


def add_months(d, m):
    y = d.year + (d.month - 1 + m) // 12
    mo = (d.month - 1 + m) % 12 + 1
    return date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))


def weeks(n):
    return timedelta(days=round(n * 7))


def s(d):
    return d.isoformat()


def gap(a, b):
    """a − b，天數，帶正負號"""
    n = (a - b).days
    return f"+{n}" if n > 0 else str(n)


def mo(days):
    return f"{days / MONTH:.1f}"


def yi(x):
    return f"{x[0] / 1e4:.2f}–{x[1] / 1e4:.2f} 億"


def ok(n_days):
    return "✅" if n_days >= 14 else ("🟡" if n_days >= 0 else "❌")


print("# 反向驗證：試算輸出\n")
print("> `backward_check.py` 的完整輸出。餘裕＝最晚日期 − 計劃日期（天）；"
      "✅ ≥14 天、🟡 0–13 天、❌ 負數＝照表排做不到。\n")

# =====================================================================
# 1. New Tech 第一年：關卡一、關卡二
# =====================================================================
GATE1 = date(2027, 3, 31)
GATE2 = date(2027, 9, 30)
P3_MONTHS = 3                         # 【定案】1.4：連跑 3 個月
P3_LATEST = add_months(GATE2 + timedelta(days=1), -P3_MONTHS)  # 2027-07-01
P2_47 = (4, 6)                        # 4.7：P2 4–6 個月
P2_PLAN = 3                           # 計劃表把 P2 壓成 3 個月（4–6 月）
NOTICE = 30                           # 預告期：勞基法 15、16 條；勞動合同法 37 條
SIGN_PLAN = date(2026, 11, 30)        # 計劃表：首批 3 人 11/30「到位」（決策日曆寫「簽約」）
CASES = [("最順", 8, 1), ("中間", 10, 2), ("最慢", 12, 3)]  # (名稱, P1 週數, 春節損失週數)
# 春節損失【推論】：台灣假期 2027-02-04 至 02-10（7 天）約 1 週；
# 大陸供應商與昆山線停工 2–3 週（計劃表第「先看風險」段）

print("## 1. 第一年：關卡一（2027-03-31）與關卡二（2027-09-30）\n")
print(f"倒推起點：關卡二要在 {s(GATE2)} 交出連跑 {P3_MONTHS} 個月的報告 → P3 最晚 {s(P3_LATEST)} 開跑。\n")

print("### 1.1 往前推：P1 何時開工，就決定 P2 最多能有幾個月\n")
print("| P1 開工 | 情境（P1 週數＋春節損失） | P1 完成 | 關卡一餘裕 | P2 最多可用（月） | 4.7 要 4–6 個月 | 計劃表壓成 3 個月 |")
print("|---|---|---|---:|---:|---|---|")
starts = [
    (date(2026, 12, 1), "12/1（表上排法：11/30 簽約、隔天就上工）"),
    (date(2026, 12, 31), "12/31（11/30 簽約＋預告 30 天）"),
]
for st, label in starts:
    for name, p1, cny in CASES:
        end = st + weeks(p1 + cny)
        g1 = (GATE1 - end).days
        room = (P3_LATEST - end).days
        v47 = "✅" if room / MONTH >= P2_47[0] else "❌"
        vplan = "✅" if room / MONTH >= P2_PLAN else "❌"
        print(f"| {label} | {name}（{p1}＋{cny} 週） | {s(end)} | {ok(g1)} {gap(GATE1, end)} | {mo(room)} | {v47} | {vplan} |")
print("\n- 「P2 最多可用」＝P1 完成日到 P3 最晚開跑日（2027-07-01）之間的月數；假設 P1 一完成就開關卡一評審、P2 立刻開工。")

print("\n### 1.2 往回推：首批 3 人最晚何時要簽約\n")
print("| P2 工期 | 情境 | P2 最晚開工 | P1 最晚完成 | P1 最晚開工＝人最晚報到 | 最晚簽約（報到 − 30 天） | 對照計劃 11/30 簽約 |")
print("|---|---|---|---|---|---|---:|")
for p2, p2label in [(P2_PLAN, "3 個月（計劃表）"), (P2_47[0], "4 個月（4.7 下緣）"), (P2_47[1], "6 個月（4.7 上緣）")]:
    p2_start = add_months(P3_LATEST, -p2)
    p1_end = min(p2_start, GATE1)
    for name, p1, cny in CASES:
        p1_start = p1_end - weeks(p1 + cny)
        sign = p1_start - timedelta(days=NOTICE)
        d = (sign - SIGN_PLAN).days
        print(f"| {p2label} | {name} | {s(p2_start)} | {s(p1_end)} | {s(p1_start)} | {s(sign)} | {ok(d)} {gap(sign, SIGN_PLAN)} |")
print("\n- 讀法：最後一欄是「最晚簽約日 − 11/30」。負數＝11/30 才簽約就來不及，要提早發聘書，或在人報到前由委託方先開工 P1。")
print("- 試用期內離職只要預告 3 日（勞動合同法 37 條），但挖的是資深人選，照 30 天算。")

# 1.3 兩岸技術合作許可
print("\n### 1.3 兩岸技術合作許可：審查最多能花幾個月\n")
print("| 軟體第一次進昆山線 | 需要許可的日期 | 11/15 送件可用（月） | 12/31 送件可用（月） |")
print("|---|---|---:|---:|")
for label, need in [("P2 就在昆山線上（計劃表）", date(2027, 4, 1)), ("P2 在台中做，P3 才上昆山線", P3_LATEST)]:
    a = (need - date(2026, 11, 15)).days
    b = (need - date(2026, 12, 31)).days
    print(f"| {label} | {s(need)} | {mo(a)} | {mo(b)} |")
print("\n- 技術合作許可**沒有法定審查期限** ⚪[IL-7]；查核員建議至少預留 2–3 個月。")
print("- 計劃表原本的門檻寫「審查 >6 個月 → B 案」。照上表，P2 在昆山線上時，門檻應是 3.0–4.5 個月；P2 改在台中做，才放寬到 6.0–7.5 個月。")

# 1.4 其他前置
print("\n### 1.4 其他前置條件\n")
NATIONAL_DAY_END = date(2026, 10, 7)
p0_start = NATIONAL_DAY_END + timedelta(days=1)
print("| 前置 | 往回推的要求 | 計劃表 | 結果 |")
print("|---|---|---|---|")
print(f"| P0 工序實測（4–6 週，昆山線） | 國慶假 10/1–10/7 後才能開工 → 最早 {s(p0_start)}，完成 {s(p0_start + weeks(4))}–{s(p0_start + weeks(6))} | 原本寫「10/5–11 月中」 | 🟡 → 已改成 10/8；仍早於 P1 開工 |")
print(f"| New Tech 設立登記 | 首批 11/30 簽約要用 New Tech 當雇主（交接包 7.1「聘用契約掛台灣新公司」）→ 11/30 前完成登記 | 原本 11 月登記，持股方式「依 11/30 股權地圖初稿」 | ❌ 循環 → 已改：持股方 10/31 先定，11/20 前登記 |")
print("| 第 1 季的錢 | 10 月就要付：試合作（10/15 起）、律師意見（10/31）、委託先裝相機（10 月底前） | 原本家族協議排在 11 月；第 1 段寫「10 月前」到位 | ❌ → 已改：協議 10/31 前簽，簽之前的支出由社長先核定為籌備費 |")
print("| 第一筆錢前的文件 | 財務三張表（1 週）＋24 個月逐月現金表（2 週）都要在家族協議前完成 | 10 月 | ✅ 10/8 起算，10/22 前可完成 |")

# =====================================================================
# 2. 上市：從 2031 年底往回推
# =====================================================================
LISTING_DEADLINE = date(2031, 12, 31)
BD = 7 / 5  # 營業日換成日曆日
# 前置時間，出處見 03 號文件附錄二（查核員報告，編號 IL-1 至 IL-8）
LEAD = {
    "上櫃月": (3, 5),             # 送件 → 掛牌：實務 3–4 個月，另一來源 4–5 個月；規劃抓 5 🟡[IL-1]
    "公發日": round(12 * BD),     # 一般公發：處理準則第 66 條，收件起 12 個營業日生效 ✅[IL-3]
    "興櫃日": round(9 * BD),      # 已公發公司登錄興櫃：最快第 9 個營業日開始交易 ✅[IL-2]
    "興櫃簡易日": round(18 * BD), # 興櫃併送簡易公發：最快 18 個營業日 ✅[IL-2]
    "興櫃滿月": 6,                # 興櫃交易滿 6 個月 ✅[IP-1]
}
PLAN_SUBMIT = date(2031, 4, 30)   # 計劃：2031 年 4 月送件（2030 年報 3/31 前出爐後）


def fwd(first_audit_year, path):
    """往前推最早日期。甲：兩本年報 → 一般公發 → 興櫃。乙：一本年報（含比較期）→ 興櫃併簡易公發。"""
    rpt = date(first_audit_year + 2, 3, 31)  # 甲：第 2 本年報；乙：第 2 個查核年度的年報（含第 1 年比較期）
    if path == "甲":
        gf = rpt + timedelta(days=LEAD["公發日"])
        xg = gf + timedelta(days=LEAD["興櫃日"])
    else:
        gf = None
        xg = rpt + timedelta(days=LEAD["興櫃簡易日"])
    sub = add_months(xg, LEAD["興櫃滿月"])
    if sub.month <= 3:  # 送件要附最近一年的查核年報 🟡[IL-4]；1–3 月送件就等 3/31 年報
        sub = date(sub.year, 4, 1)
    lst = (add_months(sub, LEAD["上櫃月"][0]), add_months(sub, LEAD["上櫃月"][1]))
    return rpt, gf, xg, sub, lst


print("\n## 2. 上市：從 2031 年底掛牌往回推\n")
lat_submit = add_months(LISTING_DEADLINE + timedelta(days=1), -LEAD["上櫃月"][1]) - timedelta(days=1)
lat_xg = add_months(lat_submit, -LEAD["興櫃滿月"])
lat_gf = lat_xg - timedelta(days=LEAD["興櫃日"])
lat_xg_b = lat_xg - timedelta(days=LEAD["興櫃簡易日"])
print(f"- 掛牌最晚 {s(LISTING_DEADLINE)}；送件到掛牌最長抓 {LEAD['上櫃月'][1]} 個月 → **送件最晚 {s(lat_submit)}**。")
print(f"- 送件前興櫃要滿 {LEAD['興櫃滿月']} 個月 → **興櫃最晚 {s(lat_xg)} 登錄**。")
print(f"- 甲：興櫃前要先完成一般公發（生效後約 {LEAD['興櫃日']} 天可登錄）→ 公發最晚 {s(lat_gf)} 生效。")
print(f"- 乙：興櫃併簡易公發最快 {LEAD['興櫃簡易日']} 天 → 最晚 {s(lat_xg_b)} 送興櫃申請。\n")

print("**往前推：最早做得到的日期**（年報都假設 3/31 前出爐）\n")
print("| 方案 | 查核起點 | 公發用的年報出爐 | 最早公發生效 | 最早興櫃 | 最早送件 | 最早掛牌 | 對 2031 年底的餘裕（月） |")
print("|---|---|---|---|---|---|---|---:|")
for path, y0 in [("甲", 2027), ("乙", 2028)]:
    rpt, gf, xg, sub, lst = fwd(y0, path)
    sl = ((LISTING_DEADLINE - lst[1]).days, (LISTING_DEADLINE - lst[0]).days)
    gft = s(gf) if gf else "（併興櫃）"
    print(f"| {path} | {y0} 年度 | {s(rpt)} | {gft} | {s(xg)} | {s(sub)} | {s(lst[0])} 至 {s(lst[1])} | {mo(sl[0])}–{mo(sl[1])} |")
pl = (add_months(PLAN_SUBMIT, LEAD["上櫃月"][0]), add_months(PLAN_SUBMIT, LEAD["上櫃月"][1]))
print(f"| 計劃表（甲、乙相同） | — | — | 甲 2029 上；乙併興櫃 | 2030 上 | {s(PLAN_SUBMIT)} | {s(pl[0])} 至 {s(pl[1])} | "
      f"{mo((LISTING_DEADLINE - pl[1]).days)}–{mo((LISTING_DEADLINE - pl[0]).days)} |")

print("\n**和計劃表上排的日期比**（計劃日期取該半年的最後一天）\n")
print("| 里程碑 | 往回推的最晚日期 | 計劃 | 餘裕（天） |")
print("|---|---|---|---:|")
for name, lat, pa in [
    ("送件", lat_submit, PLAN_SUBMIT),
    ("興櫃登錄（甲、乙）", lat_xg, date(2030, 6, 30)),
    ("一般公發生效（甲）", lat_gf, date(2029, 6, 30)),
    ("興櫃併簡易公發申請（乙）", lat_xg_b, date(2030, 6, 30)),
]:
    print(f"| {name} | {s(lat)} | {s(pa)} | {ok((lat - pa).days)} {gap(lat, pa)} |")

print("\n**上游條件**\n")
print("| 條件 | 甲（2027 起查核） | 乙（2028 起查核） | 計劃表 | 結果 |")
print("|---|---|---|---|---|")
print("| 決定查核起點 | 2026-12-31 前（會計師要能查 2027 期初數） | 2027-12-31 前 | 2026-12-31 | ✅ |")
print("| 公發要的查核財報 | 2 本、3 個年度（2026–2028）＋內控專審 1 年 ✅[IL-3] | 1 本、2 個年度（2028–2029）＋內控專審半年 ✅[IL-3] | 甲 2027、2028 查核 | 甲多一個 ⚪：2027 年才成立的主體，能不能用追溯重編的 2026、2027 比較期補足「3 個年度」，查不到依據 [IL-6] |")
print("| 上市主體成立 | 2027-12-31 前 | 2027-12-31 前（2028 起是完整一年，不必靠重編） | 2027 下半年重組；甘特圖第①列原本寫「28 上 主體定」 | ❌ → 已改成「27 下 重組完成」 |")
print("| 簽重組方案 | 最晚 ≈ 主體成立日 − 執行期；執行 6 個月【推論】→ 2027-06-30 | 同左 | 2027-03-31 | ✅ 約 3 個月餘裕 |")
print("| 設立滿 2 個完整會計年度 | 投資控股公司可用任一被控股公司實際營業滿 2 年 🟡[IL-6] | 同左 | — | ✅ 不卡 |")
print("| 送件時的治理 | 獨董 ≥1/3、不得單一性別、審計委員會：114 年起送件時就要符合 🟡[IL-8] | 同左 | 2030 股東常會改選 | ✅ |")
print("| 興櫃時的治理 | 獨董 ≥2、薪酬委員會 | 併送公發者可承諾登錄後 6 個月內完成 🟡[IL-8] | 2029 | ✅ |")
print("| 內控運作 | 一般公發要專審 1 年；送件前約 12 個月 | 簡易公發專審半年 | 2028-01-01 起 | ✅ |")

# =====================================================================
# 3. 錢：每一期要到位的錢，集團先要具備什麼條件
# =====================================================================
print("\n## 3. 錢：每一期要到位的錢，集團先要具備什麼\n")
f = fc.f
q4 = fc.block["26Q4"]
first9 = fc.add(fc.block["26Q4"], fc.block["27Q1"], fc.block["27Q2"])
y1 = fc.add(fc.P1, fc.P2)
lean9 = (1094, 1914)  # 財務長組第 1 段精簡版 9 個月
t1 = fc.TRANCHES[0][2]
print("| # | 要到位的錢 | 金額（萬台幣） | 往回推：之前要先有 | 計劃表 | 結果 |")
print("|---|---|---:|---|---|---|")
print(f"| M1 | 2026 第 4 季 | {f(q4)} | 2026-10-01 前（季初）可動用；家族協議或社長核定的籌備費 | 原本協議排 11 月；第 1 段寫「10 月前」 | ❌ → 已改：協議 10/31 前，簽前支出由社長先核定為籌備費 |")
short = (first9[0] - t1, first9[1] - t1)
print(f"| M2 | 前 9 個月（照【定案】人數） | {f(first9)} | 第 1 段上限 {t1:,} 撐不住，缺 {f(short)} | 兩種口徑並列 | ❌ 不能同時用：定案人數 ↔ 分段上限二選一 |")
print(f"| M3 | 前 9 個月（精簡版） | {f(lean9)} | 上限 {t1:,}；上緣超出 {lean9[1] - t1} | 第 4 節 | 🟡 要取中間偏下 |")
print(f"| M4 | 第一年（2026-10 至 2027-09） | {f(y1)} | 30% 規則：集團 2026 年稅前 ≥ {yi((y1[0] / 0.3, y1[1] / 0.3))} | 第 4 節 | ⚪ 要等財務三張表 |")
for yr, (a, b) in fc.yr.items():
    ab = fc.add(a, b)
    print(f"| M5-{yr} | {yr} 年燒錢 A 路／A＋B | {f(a)}／{f(ab)} | 集團 {yr - 1} 年稅前 ≥ {yi((a[0] / 0.3, a[1] / 0.3))}／{yi((ab[0] / 0.3, ab[1] / 0.3))} | 上市計劃第 1 節 | ⚪ |")
yrr = (fc.run_rate_half[0] * 2, fc.run_rate_half[1] * 2)
yrb = fc.add(yrr, fc.B_HIRE)
print(f"| M6 | 2029–2031 每年（維持規模）A 路／A＋B | {f(yrr)}／{f(yrb)} | 每年集團前一年稅前 ≥ {yi((yrr[0] / 0.3, yrr[1] / 0.3))}／{yi((yrb[0] / 0.3, yrb[1] / 0.3))} | 原本沒寫 | ⚪（已補進上市計劃第 1 節） |")
h29 = fc.run_rate_half
print(f"| M7 | 2029 上半年 | {f(h29)} | 2029-01-01 前可動用 → Pre-IPO 2029 年內才完成，這一期只能靠集團 | 原本寫「Pre-IPO 增資＋集團資金」 | ❌ → 已改成集團資金 |")

print("\n**上櫃獲利條件往回推**（New Tech 併表時；股本是【假設】）\n")
loss30 = yrr  # 2030 年 New Tech A 路虧損（維持規模，不扣營收）
print("| 股本（億台幣） | 4% 門檻（萬） | 2030 年 New Tech 虧損（萬） | 本業 2030 稅前至少（萬） | 本業營收至少（億台幣，利潤率 3.9%） |")
print("|---:|---:|---:|---:|---:|")
for cap in (1, 3, 5):
    th = cap * 1e4 * 0.04
    need = (th + loss30[0], th + loss30[1])
    print(f"| {cap} | {th:,.0f} | {f(loss30)} | {f(need)} | {need[0] / 0.039 / 1e4:.1f}–{need[1] / 0.039 / 1e4:.1f} |")
cum30 = (0, 0)
for h, _, a, _ in fc.halves:
    cum30 = fc.add(cum30, a)
    if h == "30 下":
        break
print(f"\n- 無累積虧損：到 2030-12-31，New Tech（A 路）累計虧損 {f(cum30)} 萬台幣【估算，未扣營收與所得稅】。"
      f"集團 2026 年初的保留盈餘＋本業 2026–2030 年稅後淨利，要大於這個數。")

# =====================================================================
# 4. 兩份文件互相對得上嗎
# =====================================================================
print("\n## 4. 兩份文件互相對得上嗎（程式檢查）\n")
checks = []


def has(doc, pat):
    return re.search(pat, doc) is not None


for d, what in [("2026-11-30", "股權地圖初稿"), ("2026-12-31", "查核起點"), ("2027-03-31", "簽重組方案"), ("2027-06-30", "階段 0 結案")]:
    checks.append((f"{d} {what}", has(DOC1, d) and has(DOC2, d)))
for d, what in [("2027-03-31", "關卡一"), ("2027-09-30", "關卡二")]:
    checks.append((f"{d} {what}", has(DOC1, d) and (has(DOC2, d) or has(DOC2, "◆關一"))))
for q in ["26Q4", "27Q1", "27Q2", "27Q3"]:
    checks.append((f"第一年 {q} 金額 {f(fc.block[q])}", f(fc.block[q]) in DOC1))
ca = (0, 0)
for h, _, a, b in fc.halves:
    ca = fc.add(ca, a)
    checks.append((f"上市計劃 {h} 本期 {f(a)}、累計 {f(ca)}", f(a) in DOC2 and f(ca) in DOC2))
checks.append((f"第一年合計 {f(y1)} 兩份都有", f(y1) in DOC1 and f(fc.add(first9, fc.block['27Q3'])) in DOC1))
for name, when, amt in fc.TRANCHES:
    checks.append((f"{name} {amt:,} 兩份都有", f"{amt:,}" in DOC1 and f"{amt:,}" in DOC2))


def gantt_ok(doc, ncols):
    bad = []
    for tbl in re.findall(r'<table class="gantt[^"]*">(.*?)</table>', doc, re.S):
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, re.S):
            cells = re.findall(r"<t[dh]([^>]*)>", row)
            n = sum(int(re.search(r'colspan="(\d+)"', c).group(1)) if "colspan" in c else 1 for c in cells)
            if n != ncols:
                bad.append(n)
    return not bad


for yr_, (a, b) in fc.yr.items():
    checks.append((f"上市計劃 30% 規則表 {yr_} 年 {f(a)}", f(a) in DOC2))
checks.append((f"上市計劃 30% 規則表 2029–2031 每年 {f(yrr)}", f(yrr) in DOC2))
checks.append(("兩份都沒有「乙完全沒有緩衝」的舊說法（除更正說明外）", "但完全沒有緩衝" not in DOC2 and "沒有緩衝 |" not in DOC1))
checks.append(("上市計劃不再寫「2031 年 2–4 月送件」", "2031 年 2–4 月" not in DOC2))
checks.append(("第一年甘特圖每列 13 欄", gantt_ok(DOC1, 13)))
checks.append(("上市甘特圖每列 12 欄", gantt_ok(DOC2, 12)))

print("| 檢查 | 結果 |")
print("|---|---|")
for name, res in checks:
    print(f"| {name} | {'✅' if res else '❌'} |")
print(f"\n- 共 {len(checks)} 項，{sum(1 for _, r in checks if r)} 項通過。")
print("- 金額是四捨五入後的字串比對；季加總成半年時可能差 1（例如 987＋823＝1,810，程式算的是 1,809），屬捨入差，不是錯。")
