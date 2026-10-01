# 計劃文件

依交接包【定案】的上市目標（5 年內上市；2031 上櫃）排出的兩份計劃，以及對這兩份計劃的反向驗證。兩份日期互相對齊。

| 檔案 | 內容 | PDF |
|---|---|---|
| [01-newtech-year1-plan.md](01-newtech-year1-plan.md) | New Tech 第一年活動計劃表（2026-10 至 2027-09）：年度交付、風險、甘特圖、關卡與決策日曆、各季明細、花費、人員、與【定案】衝突待裁決 | `docs/pdf/09_NewTech_第一年活動計劃表.pdf` |
| [02-ipo-roadmap.md](02-ipo-roadmap.md) | 集團上市計劃（2026Q4 至 2031 上櫃）：時程總表、上櫃條件與集團最晚何時要做到、各階段計劃、New Tech 的三個決定、延後觸發點、與【定案】衝突待裁決 | `docs/pdf/10_上市計劃_2026至2031.pdf` |
| [verify_listing_rules.md](verify_listing_rules.md) | 上櫃相關規定的獨立查核（IP-1 至 IP-10），附來源 | PDF 10 附錄一 |
| [funding_calc.py](funding_calc.py)、[funding_calc_output.md](funding_calc_output.md) | 每一期要到位的資金水位試算（按季、按半年、三種走向、30% 規則） | PDF 10 附錄二 |
| [03-backward-check.md](03-backward-check.md) | 反向驗證：從關卡一、關卡二、2031 上櫃往回推，兩份計劃表做不做得到；已改的地方與成立條件 | `docs/pdf/11_反向驗證_計劃可行性.pdf` |
| [backward_check.py](backward_check.py)、[backward_check_output.md](backward_check_output.md) | 反向驗證試算（最晚日期、餘裕、錢的前提、兩份文件的一致性檢查） | PDF 11 附錄一 |
| [verify_ipo_leadtimes.md](verify_ipo_leadtimes.md) | 上市前置時間的獨立查核（IL-1 至 IL-8），附來源 | PDF 10 附錄三；PDF 11 附錄二 |

重建：先跑 `python3 docs/plan/funding_calc.py > docs/plan/funding_calc_output.md` 與 `python3 docs/plan/backward_check.py > docs/plan/backward_check_output.md`，再在 `docs/pdf/build` 執行 `node render.mjs 09 10 11`。
