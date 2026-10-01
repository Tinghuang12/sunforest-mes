// Markdown → 排版 HTML → Chromium PDF（繁中字型、表格、頁碼）
import fs from 'node:fs'
import path from 'node:path'
import { marked } from 'marked'
import { chromium } from 'playwright-core'

const HERE = path.dirname(new URL(import.meta.url).pathname)
const REPO = path.resolve(HERE, '../../..')
const R = `${REPO}/docs/research/2026-09-28-deep-research`
const T1 = `${REPO}/docs/engineering/T1-inspection-station`
const PLAN = `${REPO}/docs/plan`
const OUT = `${REPO}/docs/pdf`
const FONT = `file://${HERE}/node_modules/@fontsource/noto-sans-tc`

const DOCS = [
  {
    file: '01_執行摘要.pdf',
    title: '窗簾自動化事業<br>五面向深度研究・執行摘要',
    plainTitle: '五面向深度研究・執行摘要',
    parts: [[`${R}/00-executive-summary.md`, null]],
  },
  {
    file: '02_五面向深度研究_完整報告.pdf',
    title: '窗簾自動化事業<br>五面向深度研究報告',
    plainTitle: '五面向深度研究報告',
    toc: true,
    parts: [
      [`${R}/00-executive-summary.md`, '執行摘要'],
      [`${R}/01-talent.md`, '第 1 章　人才'],
      [`${R}/02-engineering.md`, '第 2 章　工程技術'],
      [`${R}/03-market.md`, '第 3 章　市場分析'],
      [`${R}/04-competitors.md`, '第 4 章　競爭對手分析'],
      [`${R}/05-already-built.md`, '第 5 章　是否已有人做出來'],
    ],
  },
  {
    file: '03_T1_成品窗簾檢驗台規格.pdf',
    title: 'T1 成品窗簾檢驗台<br>光機電規格・BOM・節拍・缺陷分類',
    plainTitle: 'T1 成品窗簾檢驗台規格',
    toc: true,
    parts: [
      [`${T1}/README.md`, '規格本文'],
      [`${T1}/results.md`, '附錄 A　計算結果（inspection_calc.py 輸出）', '# 附錄 A　計算結果\n\n> 以下為 `inspection_calc.py` 的完整輸出。改參數可重算。\n\n'],
      [`${T1}/components-verification.md`, '附錄 B　元件查核紀錄'],
    ],
  },
  {
    file: '05_紅隊_嘗試推翻我們的想法.pdf',
    title: '窗簾自動化事業<br>紅隊報告：嘗試推翻我們的想法',
    plainTitle: '紅隊報告：嘗試推翻我們的想法',
    toc: true,
    parts: [
      [`${R}/06-red-team.md`, '紅隊整合報告（判決、反駁、定案衝突、90 天驗證）'],
      [`${R}/redteam/buyer.md`, '附錄 A　買方紅隊全文', null, '附錄 A　買方紅隊'],
      [`${R}/redteam/investor.md`, '附錄 B　投資人紅隊全文', null, '附錄 B　投資人紅隊'],
      [`${R}/redteam/engineer.md`, '附錄 C　工程紅隊全文', null, '附錄 C　工程紅隊'],
      [`${R}/redteam/calc-output.md`, '附錄 D　計算輸出（redteam_calc.py）', '# 附錄 D　計算輸出\n\n> 以下為 `redteam_calc.py` 的完整輸出，只用交接包數字與已查核論點；改參數可重算。\n\n'],
      [`${R}/redteam/verify_new.md`, '附錄 E　新搜尋事實的獨立查核表', null, '附錄 E　新搜尋事實的獨立查核表'],
    ],
  },
  {
    file: '06_Texpa查核_是不是虛的.pdf',
    title: '補充查核<br>Texpa 是不是虛的？宏華的窗簾機是什麼？',
    plainTitle: '補充查核：Texpa 是不是虛的',
    parts: [
      [`${R}/07-texpa-check.md`, null],
      [`${R}/texpa/verify_texpa.md`, null, null, '附錄　Texpa 獨立查核表（T1–T11）'],
      [`${R}/texpa/verify_curtain_machine.md`, null, null, '附錄　宏華「窗簾機」獨立查核表（S1–S6）'],
    ],
  },
  {
    file: '07_招募作戰表.pdf',
    title: '招募作戰表<br>招誰、去哪找、怎麼招',
    plainTitle: '招募作戰表',
    parts: [
      [`${R}/08-recruiting-playbook.md`, null],
      [`${R}/talent/verify_channels.md`, null, null, '附錄　招募管道獨立查核表（P1–P14）'],
    ],
  },
  {
    file: '08_紅隊第二輪_狀況分析.pdf',
    title: '窗簾自動化事業<br>紅隊第二輪：更深、更廣的攻擊與狀況分析',
    plainTitle: '紅隊第二輪：狀況分析',
    date: '2026 年 9 月 29 日',
    toc: true,
    parts: [
      [`${R}/09-red-team-2.md`, '紅隊第二輪整合報告（狀況圖、四種做法、判決、定案衝突、90 天清單）'],
      [`${R}/redteam2/competitor.md`, '附錄 A　競爭對手兵推全文', null, '附錄 A　競爭對手兵推'],
      [`${R}/redteam2/cfo.md`, '附錄 B　集團財務長＋家族股東全文', null, '附錄 B　集團財務長＋家族股東'],
      [`${R}/redteam2/policy.md`, '附錄 C　法規、政策與地緣全文', null, '附錄 C　法規、政策與地緣'],
      [`${R}/redteam2/demand.md`, '附錄 D　需求與產品趨勢全文', null, '附錄 D　需求與產品趨勢'],
      [`${R}/redteam2/calc-output.md`, '附錄 E　做法比較試算輸出（redteam2_calc.py）', null, '附錄 E　做法比較試算輸出'],
      [`${R}/redteam2/verify_policy.md`, '附錄 F　法規組新事實查核表', null, '附錄 F　法規組新事實查核表（Q-P1–Q-P17）'],
      [`${R}/redteam2/verify_market.md`, '附錄 G　競爭與需求組新事實查核表', null, '附錄 G　競爭與需求組新事實查核表（Q-C、Q-D）'],
      [`${R}/redteam2/verify_cfo.md`, '附錄 H　財務長組新事實查核表', null, '附錄 H　財務長組新事實查核表（Q-F1–Q-F9）'],
      [`${R}/redteam2/verify_fob.md`, '附錄 I　每片 FOB 補查', null, '附錄 I　每片 FOB 補查（Q-FOB）'],
    ],
  },
  {
    file: '09_NewTech_第一年活動計劃表.pdf',
    title: 'New Tech<br>第一年活動計劃表<br><span style="font-size:15pt;font-weight:500">2026 年 10 月至 2027 年 9 月</span>',
    plainTitle: 'New Tech 第一年活動計劃表',
    date: '2026 年 10 月 1 日',
    basis: '交接包【定案】＋研究第 1–9 章',
    idNote: '<b>引用</b>　「第 N 章」指五面向研究與兩輪紅隊報告（PDF 02、05、08）；「財務長組」指 PDF 08 附錄 B；「反向驗證」指 PDF 11。',
    parts: [[`${PLAN}/01-newtech-year1-plan.md`, null]],
  },
  {
    file: '10_上市計劃_2026至2031.pdf',
    title: '集團上市計劃<br><span style="font-size:15pt;font-weight:500">2026 年第 4 季至 2031 年上櫃</span>',
    plainTitle: '集團上市計劃',
    date: '2026 年 10 月 1 日',
    basis: '交接包【定案】＋研究第 1–9 章＋上櫃規定查核',
    idNote: '<b>方括號小標籤</b>是查核編號：IP-x（例如 <span class="cid">IP-4</span>）見附錄一，IL-x 見附錄三；「第 N 章」指研究與紅隊報告（PDF 02、05、08）；「反向驗證」指 PDF 11。',
    parts: [
      [`${PLAN}/02-ipo-roadmap.md`, null],
      [`${PLAN}/verify_listing_rules.md`, null],
      [`${PLAN}/funding_calc_output.md`, null, null, '附錄二　每一期要到位的資金：試算輸出'],
      [`${PLAN}/verify_ipo_leadtimes.md`, null, null, '附錄三　上市前置時間的獨立查核（IL-1 至 IL-8）'],
    ],
  },
  {
    file: '11_反向驗證_計劃可行性.pdf',
    title: '反向驗證<br><span style="font-size:15pt;font-weight:500">第一年活動計劃表與集團上市計劃<br>做不做得到</span>',
    plainTitle: '反向驗證',
    date: '2026 年 10 月 1 日',
    basis: '交接包【定案】＋PDF 09、10＋上市前置時間查核',
    idNote: '<b>方括號小標籤</b>（例如 <span class="cid">IL-7</span>）是查核編號：IL-x 見本文件附錄二，IP-x 見 PDF 10 附錄一。「第 N 節」指本文件。',
    parts: [
      [`${PLAN}/03-backward-check.md`, null],
      [`${PLAN}/backward_check_output.md`, null, null, '附錄一　反向驗證：試算輸出'],
      [`${PLAN}/verify_ipo_leadtimes.md`, null, null, '附錄二　上市前置時間的獨立查核（IL-1 至 IL-8）'],
    ],
  },
  {
    file: '04_研究查核附錄_282條論點.pdf',
    title: '五面向深度研究<br>查核附錄（282 條論點與來源）',
    plainTitle: '研究查核附錄',
    parts: [[`${R}/appendix-verification-log.md`, null]],
  },
]

const CSS = `
@import url('${FONT}/400.css');
@import url('${FONT}/500.css');
@import url('${FONT}/700.css');
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
html { font-family: 'Noto Sans TC', 'WenQuanYi Zen Hei', sans-serif; font-size: 10.2pt; color: #1f2328; }
body { margin: 0; line-height: 1.7; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
h1 { font-size: 20pt; color: #0b3d63; border-bottom: 3px solid #0b3d63; padding-bottom: 6px; margin: 0 0 14px; line-height: 1.35; }
h2 { font-size: 14pt; color: #0b3d63; border-left: 5px solid #2f7fb8; padding-left: 9px; margin: 22px 0 10px; line-height: 1.4; break-after: avoid; }
h3 { font-size: 11.5pt; color: #174a70; margin: 16px 0 6px; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 12px 0 4px; break-after: avoid; }
p { margin: 5px 0 8px; }
ul, ol { margin: 4px 0 8px; padding-left: 20px; }
li { margin: 2px 0; }
li > ul, li > ol { margin: 2px 0; }
strong { color: #0b2540; }
th strong { color: #fff; }
blockquote { margin: 10px 0 14px; padding: 10px 14px; background: #eef5fb; border-left: 5px solid #2f7fb8; border-radius: 4px; }
blockquote p { margin: 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 14px; font-size: 8.6pt; line-height: 1.5; page-break-inside: auto; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: #0b3d63; color: #fff; font-weight: 500; text-align: left; padding: 5px 6px; border: 1px solid #0b3d63; }
td { padding: 4px 6px; border: 1px solid #c9d3dd; vertical-align: top; }
tbody tr:nth-child(even) td { background: #f5f8fb; }
code { font-family: 'WenQuanYi Zen Hei Mono', monospace; font-size: 8.8pt; background: #f1f3f5; padding: 0 3px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #d8dee4; padding: 10px; border-radius: 4px; overflow: hidden; break-inside: avoid; }
pre code { background: none; font-size: 8.4pt; line-height: 1.35; white-space: pre; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 18px 0; }
a { color: #1f5f99; text-decoration: none; word-break: break-all; }
.cid { font-size: 7.2pt; color: #6e7781; background: #eef1f4; border-radius: 3px; padding: 0 3px; margin: 0 1px; white-space: nowrap; vertical-align: 1px; }
.chapter { break-before: page; }
.chapter:first-of-type { break-before: auto; }
/* 甘特圖 */
table.gantt { table-layout: fixed; font-size: 7.4pt; line-height: 1.3; }
table.gantt th, table.gantt td { text-align: center; padding: 4px 1px; }
table.gantt th:first-child, table.gantt td:first-child { text-align: left; width: 31%; padding-left: 5px; font-size: 7.8pt; }
table.gantt td.w { background: #a9cbe8 !important; }
table.gantt td.d { background: #2f7fb8 !important; color: #fff; }
table.gantt td.k { background: #c0392b !important; color: #fff; font-weight: 700; }
table.gantt td.p { background: #e3e8ee !important; color: #6e7781; }
table.gantt.wide th:first-child, table.gantt.wide td:first-child { width: 22%; }
table.gantt td.m { background: #fff3d1 !important; font-size: 6.6pt; color: #5a4300; line-height: 1.25; }
table.gantt tr.mh td { background: #f1e2ae !important; font-weight: 700; text-align: left; font-size: 7.4pt; color: #4a3800; padding-left: 5px; }
.pb { break-before: page; height: 0; }
p.legend { font-size: 8pt; color: #444; margin: -6px 0 10px; }
.lg { display: inline-block; width: 12px; height: 9px; border-radius: 2px; margin: 0 3px 0 10px; vertical-align: -1px; }
.lg.w { background: #a9cbe8; } .lg.d { background: #2f7fb8; } .lg.k { background: #c0392b; } .lg.p { background: #e3e8ee; border: 1px solid #c9d3dd; } .lg.m { background: #fff3d1; border: 1px solid #e0c97a; }
/* 封面 */
.cover { height: 250mm; display: flex; flex-direction: column; break-after: page; }
.cover .band { background: #0b3d63; color: #fff; padding: 34mm 14mm 16mm; border-radius: 6px; }
.cover .org { font-size: 11pt; letter-spacing: 2px; opacity: .85; }
.cover .title { font-size: 25pt; font-weight: 700; line-height: 1.4; margin-top: 10mm; }
.cover .meta { margin-top: 14mm; font-size: 11pt; line-height: 2; }
.cover .legend { margin-top: auto; font-size: 9.5pt; color: #333; border-top: 1px solid #c9d3dd; padding-top: 8px; line-height: 1.9; }
.cover .note { font-size: 8.8pt; color: #555; margin-top: 6px; }
.toc { break-after: page; }
.toc h1 { font-size: 16pt; }
.toc ol { font-size: 11.5pt; line-height: 2.1; }
`

const ID_RE = /\[((?:[A-Z]{1,2}\d{0,2}|ML)-N?\d+)\]/g

function prep(md) {
  // 連到其他檔案的連結（.md／.py／.csv）在 PDF 裡點不到，只留文字
  md = md.replace(/\[([^\]]+)\]\((?!https?:)[^)]+\)/g, '$1')
  // claim id 做成小標籤
  md = md.replace(ID_RE, '<span class="cid">$1</span>')
  // 中文標點緊貼 ** 時 CommonMark 不會轉成粗體，直接改成 <strong>
  md = md.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>')
  return md
}

function cover(doc) {
  return `<section class="cover">
  <div class="band">
    <div class="org">晨森 NEW TECH ・ 窗簾自動化事業</div>
    <div class="title">${doc.title}</div>
    <div class="meta">呈：黃悟庭 社長<br>日期：${doc.date || '2026 年 9 月 28 日'}<br>依據：${doc.basis || '2026-09-28 研究交接包'}</div>
  </div>
  <div class="legend">
    <b>查核狀態圖例</b>　✅ 已驗證　🟡 部分驗證（使用查核後修正版）　⚪ 無法驗證（不作決策依據）　❌ 已推翻<br>
    <b>標記</b>　【估算】自行計算，附算式　【推論】工程或商業判斷　【假設】待實測或詢價更新<br>
    ${doc.idNote || '<b>方括號小標籤</b>（例如 <span class="cid">C1-3</span>）是論點編號，可在「研究查核附錄」查到來源與查核說明。'}
    <div class="note">限制：本研究環境無法直接開啟網頁，所有查核依據搜尋結果摘要；放入對外文件的重要數字，請再人工打開原文核對。</div>
  </div>
</section>`
}

function build(doc) {
  let body = cover(doc)
  if (doc.toc) {
    body += `<section class="toc"><h1>目錄</h1><ol>${doc.parts.map(p => `<li>${p[1]}</li>`).join('')}</ol></section>`
  }
  for (const [file, , prefix, h1] of doc.parts) {
    let md = fs.readFileSync(file, 'utf8')
    // 附錄改用統一的「附錄 X」標題
    if (h1) md = md.replace(/^# .*$/m, `# ${h1}`)
    md = (prefix || '') + md
    body += `<section class="chapter">${marked.parse(prep(md), { gfm: true, breaks: false })}</section>`
  }
  return `<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>${doc.plainTitle}</title><style>${CSS}</style></head><body>${body}</body></html>`
}

fs.mkdirSync(OUT, { recursive: true })
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' })
const page = await browser.newPage()
// 只重建指定的檔案：node render.mjs 01 08（比對檔名開頭）；不帶參數就全部重建
const ONLY = process.argv.slice(2)
for (const doc of DOCS.filter(d => !ONLY.length || ONLY.some(k => d.file.startsWith(k)))) {
  const html = build(doc)
  const htmlPath = path.join(HERE, doc.file.replace('.pdf', '.html'))
  fs.writeFileSync(htmlPath, html)
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' })
  await page.evaluate(() => document.fonts.ready)
  await page.pdf({
    path: path.join(OUT, doc.file),
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `<div style="width:100%;font-size:7.5pt;color:#777;font-family:'WenQuanYi Zen Hei',sans-serif;padding:0 16mm;display:flex;justify-content:space-between;"><span>${doc.plainTitle}</span><span>第 <span class="pageNumber"></span> / <span class="totalPages"></span> 頁</span></div>`,
    margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' },
  })
  console.log('wrote', doc.file)
}
await browser.close()
