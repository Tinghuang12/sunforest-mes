// Markdown → 排版 HTML → Chromium PDF（繁中字型、表格、頁碼）
import fs from 'node:fs'
import path from 'node:path'
import { marked } from 'marked'
import { chromium } from 'playwright-core'

const HERE = path.dirname(new URL(import.meta.url).pathname)
const REPO = path.resolve(HERE, '../../..')
const R = `${REPO}/docs/research/2026-09-28-deep-research`
const T1 = `${REPO}/docs/engineering/T1-inspection-station`
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
  return md
}

function cover(doc) {
  return `<section class="cover">
  <div class="band">
    <div class="org">晨森 NEW TECH ・ 窗簾自動化事業</div>
    <div class="title">${doc.title}</div>
    <div class="meta">呈：黃悟庭 社長<br>日期：2026 年 9 月 28 日<br>依據：2026-09-28 研究交接包</div>
  </div>
  <div class="legend">
    <b>查核狀態圖例</b>　✅ 已驗證　🟡 部分驗證（使用查核後修正版）　⚪ 無法驗證（不作決策依據）　❌ 已推翻<br>
    <b>標記</b>　【估算】自行計算，附算式　【推論】工程或商業判斷　【假設】待實測或詢價更新<br>
    <b>方括號小標籤</b>（例如 <span class="cid">C1-3</span>）是論點編號，可在「研究查核附錄」查到來源與查核說明。
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
for (const doc of DOCS) {
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
