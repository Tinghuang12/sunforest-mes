#!/usr/bin/env python3
"""T1 成品窗簾檢驗台：光學、節拍與驗收樣本量計算工具。

只用 Python 標準庫。執行：
    python3 inspection_calc.py            # 印出全部表格（markdown）
    python3 inspection_calc.py --seed 7   # 改變蒙地卡羅亂數種子

所有輸入集中在 PARAMS，改參數即可重算。數字來源見 README.md 第 1 節。
"""
import argparse
import math
import random
import statistics
import csv
import os

PARAMS = {
    # 成品簾尺寸（交接包 T1 輸入）
    "panel_width_m": (1.4, 2.0),
    "panel_height_m": (1.6, 2.7),
    # 搬送
    "scan_speed_mps": 0.30,        # 交接包 4.2
    "return_speed_mps": 1.0,       # 空桿回程速度（假設）
    "position_margin_mm": 50,      # 布位偏移 ±50 mm（交接包 4.6 粗導正口徑）
    "overlap": 0.05,               # 相鄰相機視野重疊 5%
    "working_distance_mm": 1500,
    # 感測器（研究 E1-2、E1-3：IMX541 全域快門）
    "sensor_px": (4504, 4504),      # 多數 IMX541 相機規格頁的有效解析度（Basler、TIS、FLIR）
    "pixel_um": 2.74,
    # 模糊準則（研究 E1-4：曝光期間移動宜 ≤0.5 px）
    "blur_px_max": 0.5,
    # 景深計算：容許模糊圈取 2 個像素
    "coc_px": 2,
    # 裝卸料時間分布（三角分布：最小、最可能、最大，秒）【假設，W1 實測後更新】
    "load_s": (6.0, 8.0, 12.0),
    "unload_s": (2.0, 3.0, 5.0),
    "transfer_s": 2.0,             # 雙夾桿方案中夾桿換位時間（假設）
    "shift_hours": 10,             # 交接包 3 節：10 小時制
}

MIN_DEFECTS_MM = {
    "針孔（背光）": 0.3,
    "線徑下限": 0.2,
    "線徑上限": 0.4,
    "汙漬（植入驗收樣本）": 3.0,
    "跳針缺段（針距 2.5 mm）": 2.5,
}


def fmt(x, nd=2):
    return f"{x:,.{nd}f}"


def optics_table(p):
    sw_mm = p["sensor_px"][0] * p["pixel_um"] / 1000
    rows = []
    wmin, wmax = p["panel_width_m"]
    for res in (0.30, 0.15, 0.12, 0.10):
        fov = p["sensor_px"][0] * res                      # 單機視野 mm
        span = wmax * 1000 + 2 * p["position_margin_mm"]   # 需覆蓋的寬度 mm
        eff = fov * (1 - p["overlap"])
        n_cam = math.ceil((span - fov * p["overlap"]) / eff)
        m = sw_mm / fov
        f = p["working_distance_mm"] * m / (1 + m)
        exp_ms = p["blur_px_max"] * res / (p["scan_speed_mps"] * 1000) * 1000
        rows.append((res, fov, n_cam, f, exp_ms))
    out = ["| 解析度 mm/px | 單機視野 mm | 覆蓋 2.0 m＋±50 mm 所需台數 | 焦距 mm（WD 1.5 m） | 曝光上限 ms（0.5 px 模糊） |",
           "|---:|---:|---:|---:|---:|"]
    for res, fov, n, f, e in rows:
        out.append(f"| {res:.2f} | {fmt(fov,0)} | {n} | {fmt(f,1)} | {fmt(e,2)} |")
    return "\n".join(out), sw_mm


def cameras_to_resolution_table(p, sw_mm):
    """反過來算：給定台數，兩種搬送方案各能達到多少 mm/px。"""
    o, px = p["overlap"], p["sensor_px"][0]
    spans = {
        "垂直升降（相機沿簾寬，覆蓋 2.0 m＋±50 mm）": p["panel_width_m"][1] * 1000 + 2 * p["position_margin_mm"],
        "水平輸送（相機沿簾高，覆蓋 2.7 m＋±50 mm）": p["panel_height_m"][1] * 1000 + 2 * p["position_margin_mm"],
    }
    out = ["| 搬送方案 | 台數 | 單機視野 mm | 解析度 mm/px | 0.3 mm 針孔占 px | 焦距 mm（WD 1.5 m） |",
           "|---|---:|---:|---:|---:|---:|"]
    for name, span in spans.items():
        for n in (4, 5, 6):
            fov = span / (n - (n - 1) * o)
            res = fov / px
            m = sw_mm / fov
            f = p["working_distance_mm"] * m / (1 + m)
            out.append(f"| {name} | {n} | {fmt(fov,0)} | {res:.3f} | {0.3/res:.1f} | {fmt(f,1)} |")
    return "\n".join(out)


def defect_pixels_table():
    out = ["| 缺陷特徵 | 尺寸 mm | 0.30 mm/px | 0.15 mm/px | 0.12 mm/px | 0.10 mm/px |",
           "|---|---:|---:|---:|---:|---:|"]
    for name, size in MIN_DEFECTS_MM.items():
        cells = [fmt(size / r, 1) for r in (0.30, 0.15, 0.12, 0.10)]
        out.append(f"| {name} | {size} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def dof_table(p, sw_mm):
    out = ["| 解析度 mm/px | 光圈 | 放大率 m | 景深約 mm（±一半） |", "|---:|---:|---:|---:|"]
    c_mm = p["coc_px"] * p["pixel_um"] / 1000
    for res in (0.12, 0.10):
        fov = p["sensor_px"][0] * res
        m = sw_mm / fov
        for n in (5.6, 8.0):
            dof = 2 * n * c_mm * (1 + m) / (m * m)
            out.append(f"| {res:.2f} | f/{n} | {m:.4f} | {fmt(dof,0)} |")
    return "\n".join(out)


def frames_table(p):
    out = ["| 解析度 mm/px | 每種光每台張數（簾高 2.7 m） | 每片總張數（4 台×2 種光） | 每片原圖量 GB（8-bit） | 單機需求幀率 fps |",
           "|---:|---:|---:|---:|---:|"]
    hmax = p["panel_height_m"][1] * 1000
    img_mb = p["sensor_px"][0] * p["sensor_px"][1] / 1e6
    for res in (0.12, 0.10):
        fov_along = p["sensor_px"][1] * res
        step = fov_along * (1 - p["overlap"])
        per_light = math.ceil((hmax + fov_along) / step)
        total = per_light * 2 * 4
        gb = total * img_mb / 1000
        scan_s = hmax / (p["scan_speed_mps"] * 1000)
        fps = per_light * 2 / scan_s
        out.append(f"| {res:.2f} | {per_light} | {total} | {fmt(gb,2)} | {fmt(fps,2)} |")
    return "\n".join(out)


def tri(r, a):
    return r.triangular(a[0], a[2], a[1])


def cycle_sim(p, seed, n=20000):
    r = random.Random(seed)
    v, rv = p["scan_speed_mps"], p["return_speed_mps"]
    res = {"單夾桿升降（掃描後空桿回程）": [], "雙夾桿交替（裝料與掃描重疊）": [], "水平吊掛輸送（循環夾桿）": []}
    for _ in range(n):
        h = r.uniform(*p["panel_height_m"])
        w = r.uniform(*p["panel_width_m"])
        load, unload = tri(r, p["load_s"]), tri(r, p["unload_s"])
        scan = h / v
        res["單夾桿升降（掃描後空桿回程）"].append(load + scan + unload + h / rv)
        res["雙夾桿交替（裝料與掃描重疊）"].append(max(load + unload, scan + p["transfer_s"]))
        # 水平輸送：相機沿簾高排列；片距取簾寬＋0.5 m 間隙，瓶頸是裝料或通過時間
        res["水平吊掛輸送（循環夾桿）"].append(max(load, (w + 0.5) / v))
    out = ["| 搬送方案 | 平均節拍 s | P95 節拍 s | ≤20 s 的比例 | 每小時片數（平均） | 10 小時產能 |",
           "|---|---:|---:|---:|---:|---:|"]
    for k, xs in res.items():
        xs.sort()
        mean = statistics.fmean(xs)
        p95 = xs[int(0.95 * len(xs))]
        ok = sum(1 for x in xs if x <= 20) / len(xs)
        per_h = 3600 / mean
        out.append(f"| {k} | {fmt(mean,1)} | {fmt(p95,1)} | {ok:.0%} | {fmt(per_h,0)} | {fmt(per_h*p['shift_hours'],0)} |")
    return "\n".join(out)


def deterministic_cycle(p):
    load, unload = p["load_s"][1], p["unload_s"][1]
    out = ["| 簾高 m | 掃描 s | 單夾桿：裝＋掃＋卸＋回程 s | 雙夾桿：max(裝＋卸, 掃＋換位) s | 交接包口徑：掃＋裝 s |",
           "|---:|---:|---:|---:|---:|"]
    for h in (1.6, 2.0, 2.4, 2.7):
        scan = h / p["scan_speed_mps"]
        single = load + scan + unload + h / p["return_speed_mps"]
        dual = max(load + unload, scan + p["transfer_s"])
        out.append(f"| {h} | {fmt(scan,1)} | {fmt(single,1)} | {fmt(dual,1)} | {fmt(scan+load,1)} |")
    return "\n".join(out)


def speed_sensitivity(p, res=0.121, h=2.7):
    """單夾桿升降在最高簾（2.7 m）下，提高掃描速度對節拍與曝光的影響。"""
    load, unload = p["load_s"][1], p["unload_s"][1]
    out = ["| 掃描速度 m/s | 掃描 s | 單夾桿節拍 s（2.7 m 簾） | 曝光上限 ms（0.5 px，0.121 mm/px） | 曝光上限 ms（1 px） |",
           "|---:|---:|---:|---:|---:|"]
    for v in (0.3, 0.4, 0.5, 0.6):
        scan = h / v
        cyc = load + scan + unload + h / p["return_speed_mps"]
        e05 = 0.5 * res / (v * 1000) * 1000
        e1 = res / (v * 1000) * 1000
        out.append(f"| {v:.1f} | {fmt(scan,1)} | {fmt(cyc,1)} | {e05:.3f} | {e1:.3f} |")
    return "\n".join(out)


def lens_table(p, sw_mm, fov=545.0):
    """4 台沿簾寬、單機視野約 545 mm 時，不同焦距的工作距離與量測對布面高低差的容許值。"""
    m = sw_mm / fov
    out = ["| 鏡頭焦距 mm | 工作距離 m | 視野邊緣離光軸 mm | 布面高低差容許值 mm（每邊誤差 ≤1 mm） |",
           "|---:|---:|---:|---:|"]
    for f in (25, 35):
        wd = f * (1 + m) / m
        x = fov / 2
        dz = 1.0 * wd / x
        out.append(f"| {f} | {wd/1000:.2f} | {x:.0f} | {dz:.1f} |")
    return "\n".join(out)


def bom_table(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    out = ["| 分組 | 項目 | 數量 | 單價 萬元（低–高） | 小計 萬元（低–高） |", "|---|---|---:|---:|---:|"]
    lo = hi = 0.0
    for r in rows:
        q = int(r["qty"]); a = float(r["unit_low_wan"]); b = float(r["unit_high_wan"])
        lo += q * a; hi += q * b
        out.append(f"| {r['group']} | {r['item']} | {q} | {a:g}–{b:g} | {q*a:.2f}–{q*b:.2f} |")
    out.append(f"| **合計** | 硬體（不含工程人力、整合、標註人力） | | | **{lo:.2f}–{hi:.2f}** |")
    return "\n".join(out), lo, hi


def zero_fail_n(p_max, conf=0.95):
    return math.ceil(math.log(1 - conf) / math.log(1 - p_max))


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def n_with_failures(p_max, k, conf=0.95):
    n = k + 1
    while binom_cdf(k, n, p_max) > 1 - conf:
        n += 1
    return n


def sample_size_table():
    out = ["| 驗收指標 | 允許失敗數 | 95% 信賴所需樣本數 |", "|---|---:|---:|"]
    for label, pm in (("漏檢率 <0.5%（每類缺陷樣本）", 0.005), ("漏檢率 <1%", 0.01), ("誤殺率 <3%（良品樣本）", 0.03)):
        for k in (0, 1, 2):
            n = zero_fail_n(pm) if k == 0 else n_with_failures(pm, k)
            out.append(f"| {label} | {k} | {n:,} |")
    return "\n".join(out)


def payback_table():
    # 交接包 6 節：檢驗單元省 6.7 人/千片日；人年成本依研究 M3-1、V6-N3、V6-N4
    saved = 6.7
    # 匯率假設 1 美元 = 7.2 人民幣（未驗證）；單位：萬元人民幣/人年
    costs = {
        "中國沿海（交接包 9 萬）": 9.0,
        "中國沿海（研究 11.4–12.2 萬，取 11.8）": 11.8,
        "越南（5,300–6,400 美元，取 5,850）": 5850 * 7.2 / 10000,
        "日本（1.45–1.67 萬美元，取 1.56 萬）": 15600 * 7.2 / 10000,
    }
    out = ["| 客戶所在地 | 人年成本 萬元 | 年省人工 萬元 | 售價 60 萬回收 年 | 售價 90 萬回收 年 |", "|---|---:|---:|---:|---:|"]
    for k, c in costs.items():
        saving = saved * c
        out.append(f"| {k} | {fmt(c,2)} | {fmt(saving,1)} | {fmt(60/saving,2)} | {fmt(90/saving,2)} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260928)
    a = ap.parse_args()
    p = PARAMS
    t_opt, sw = optics_table(p)
    print("## A. 解析度、台數、焦距、曝光\n")
    print(f"感測器寬 {sw:.2f} mm（{p['sensor_px'][0]} px × {p['pixel_um']} µm）；工作距離 {p['working_distance_mm']} mm；布速 {p['scan_speed_mps']} m/s。\n")
    print(t_opt, "\n")
    print("## A2. 給定台數可達到的解析度\n")
    print(cameras_to_resolution_table(p, sw), "\n")
    print("## A3. 鏡頭焦距、工作距離與量測容許的布面高低差\n")
    print(lens_table(p, sw), "\n")
    print("## B. 最小缺陷占幾個像素\n")
    print(defect_pixels_table(), "\n")
    print("## C. 景深\n")
    print(dof_table(p, sw), "\n")
    print("## D. 每片影像張數、資料量、幀率（垂直升降、4 台沿幅寬）\n")
    print(frames_table(p), "\n")
    print("## E. 節拍（確定值，裝料 8 s、卸料 3 s、回程 1.0 m/s、換位 2 s）\n")
    print(deterministic_cycle(p), "\n")
    print("## E2. 單夾桿升降：提高掃描速度的效果（最高簾 2.7 m）\n")
    print(speed_sensitivity(p), "\n")
    print(f"## F. 節拍蒙地卡羅（20,000 片；簾寬、簾高均勻分布；裝卸料三角分布；seed={a.seed}）\n")
    print(cycle_sim(p, a.seed), "\n")
    print("## G. AI 驗收所需樣本量（二項分布，95% 單尾信賴）\n")
    print(sample_size_table(), "\n")
    print("## H. 回收期（檢驗單元省 6.7 人/千片日；售價 60 萬與交接包上限 90 萬）\n")
    print(payback_table(), "\n")
    bom_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bom.csv")
    if os.path.exists(bom_path):
        t, lo, hi = bom_table(bom_path)
        print("## I. BOM 合計（bom.csv；大多數單價為【估算】，須詢價）\n")
        print(t)


if __name__ == "__main__":
    main()
