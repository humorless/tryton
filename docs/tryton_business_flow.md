## 前提假設
- 環境已架好，可以登入
- 從 UI 操作出發，遇到設定問題再往下挖
- 每個 Use Case 都要**實際跑通**，不只是看
## 必裝模組清單

啟動 Tryton 後，第一步先確認以下模組已啟用：

### 第一層：任何情境都需要的底層

| 模組 | 說明 |
|------|------|
| `company` | 公司實體，幾乎所有模組都依賴它 |
| `currency` | 幣別，company 依賴它 |
| `party` | 客戶、廠商、員工的統一實體（ERP 的 Party Model） |
| `account` | 會計核心：科目、日記帳、傳票（Move/Line） |
| `account_invoice` | 應收/應付發票，銷售和採購的財務閉環靠它 |
| `stock` | 庫存異動（Stock Move），採購、銷售、製造都依賴它 |

這六個模組是地基，缺任何一個，其他模組幾乎都跑不起來。

### 第二層：依業務流程選裝

| 模組 | 需要的情境 | 說明 |
|------|-----------|------|
| `purchase` | 有採購流程 | 採購單 → Supplier Shipment → 入庫 |
| `sale` | 有銷售流程 | 銷售單 → Customer Shipment → 出庫 |
| `production` | 有製造流程 | BOM + 工單，純貿易業不需要 |
| `account_product` | 有銷售或採購 | 讓產品自動對應收入/費用科目，沒有它開發票要手動指定科目，很快就會很痛 |

`purchase` 和 `sale` 看似必裝，但純服務業或只做一邊的公司可以只裝其中一個。

### 第三層：有需求才裝，不要預先裝

| 模組 | 需要的情境 | 說明 |
|------|-----------|------|
| `stock_lot` | 食品、藥品、電子零件等需要批次/序號追蹤 | 裝了之後每筆庫存異動都要指定 lot，沒需求反而是負擔 |
| `product_cost_fifo` | 需要先進先出成本計算 | 與 `product_cost_average`（加權平均）擇一，依會計政策決定，不是每間公司都需要 |
| `account_statement` | 需要銀行對帳單匯入與對帳 | 中小企業初期手動登帳就夠，規模大了才需要 |
| `purchase_invoice_line_standalone` | 多張採購單要合併成一張發票 | 解決「一個供應商多筆訂單，月底開一張發票」的場景 |

### 本學習計劃使用的模組

以下是本文件 Day 1–6 實際會用到的完整清單：

```
account
account_invoice
account_product
company
currency
party
purchase
sale
stock
```

> **注意（2026-07-07 更正）**：原本這裡還規劃了 `production`（Day 5–6 製造流程），但這份計劃鎖定的情境是「進書、庫存、賣書」的純貿易業務（例如書店），沒有加工/組裝的需求，所以拿掉了 `production` 與對應的 Day 5–6。真實客戶的 minimum set 應該從業務需求反推，而不是預先全裝——這裡就是一個實例：一開始規劃時把 production 放進去是預先多裝，後來確認用不到就拿掉。
 
---
 
## Day 1｜地基（3 hr）
 
**目標：搞懂 Tryton 的操作邏輯，不迷路**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 介面導覽：Menu、Form View、List View、狀態機（draft → confirmed → done） |
| 1 hr | 建立基礎資料：Company、Chart of Accounts（用內建 minimal）、Fiscal Year |
| 1 hr | 建立 Party（廠商＋客戶）、建立 Product（含 UoM） |
 
**關鍵概念：** Tryton 幾乎所有單據都有狀態機，先搞清楚「按哪個按鈕推進狀態」是最重要的操作直覺。
 
---
 
## Day 2｜Use Case 1：採購到入庫（3 hr）
 
**目標：跑通 Purchase → Supplier Shipment → Stock**
 
| 時間 | 內容 |
|------|------|
| 0.5 hr | 設定廠商的 Payment Term、幣別 |
| 1.5 hr | 建採購單 → Quote → Confirm → **Process**（此時才產生草稿 Stock Move／發票）→ 手動建立 Supplier Shipment 把 Move 收進去 → 驗收 → 確認入庫 |
| 1 hr | 查庫存數量確認有變動、看自動產生的 Stock Move 明細 |
 
**關鍵概念：** Tryton 的採購不會直接異動庫存，中間一定經過 Shipment，這個設計是刻意的。

**更正（2026-07-08）**：原本這裡簡化寫成「建單 → 確認」，實測後發現 Purchase 的狀態機比想像中多兩階：`Draft → Quotation → Confirmed → Processing → Done`，不是 `Draft → Confirmed`。**Quote** 把 Draft 推進到 Quotation（同時給單據編號）；**Confirm** 把 Quotation 推進到 Confirmed（只是鎖定單據，不產生任何下游動作）；**Process** 按鈕（呼叫 `_process_fulfillment`／`_process_invoice`）會產生**草稿發票**跟**未分組的草稿 Stock Move**，但**不會**自動產生 Supplier Shipment——查了官方文件（[Purchase Module usage — 8.0](https://docs.tryton.org/8.0/modules-purchase/usage/index.html)）證實 Supplier Shipment 要人工建立、手動把這些 Move 收進去（因為現實中供應商實際出貨方式不見得跟下單方式一樣），詳見 [`user-guide.md`](../manuals/user-guide.md) Day 2 的概念筆記。

**順序更正（2026-07-07）**：原始規劃是 Day 2 先做庫存盤點／內部調撥、Day 3 才做採購，但實測發現一個全新環境裡 Day 1 建立的 Product 只是型錄資料，並不代表任何地點有真實庫存——沒有先跑過採購入庫，庫存操作（Internal Shipment）在 Assign 這步會卡關（"Unable to assign these products"）。改成 **Day 2 先採購入庫（本頁），Day 3 才做庫存盤點／內部調撥**，這樣 Day 3 開始操作時 Input Zone 已經有 Day 2 採購入庫產生的真實庫存，不用另外想辦法生出庫存數字，也更貼近真實商業邏輯（先進貨才有貨可以搬/盤）。
 
---
 
## Day 3｜Use Case 3：庫存盤點（3 hr）
 
**目標：理解 Stock Move 是 Tryton 庫存的核心**
 
| 時間 | 內容 |
|------|------|
| 1 hr | **看懂**（不是建立）預設 Warehouse／Location 結構：`stock` 模組一啟用就會自動產生一組堪用的骨架（Warehouse／Input／Output／Storage／Lost & Found／Supplier／Customer／Transit）。單一門市/單一倉庫的情境（例如書店）直接沿用這組即可，不用重建；只有真的需要第二個實體倉庫或門市，才動手加新的 Location |
| 1 hr | 手動建立 Internal Shipment，感受 Stock Move 怎麼產生（Day 2 採購入庫後 Input Zone 已有真實庫存，這裡才搬得動） |
| 1 hr | 跑一次完整盤點：建盤點單 → 輸入實際數 → 確認 → 看庫差 Move |
 
**關鍵概念：** 所有庫存異動本質上都是 `Stock Move`（from location → to location），盤點只是其中一種觸發方式。Location 結構只是「這批異動要怎麼分類」的骨架，Tryton 給的預設骨架多半就夠用，不是每個環境都要手動從零蓋。
 
---
 
## Day 4｜Use Case 2：銷售到出庫（3 hr）
 
**目標：跑通 Sale → Customer Shipment → Stock**
 
| 時間 | 內容 |
|------|------|
| 0.5 hr | 設定客戶資料、Price List（用最簡單的固定價） |
| 1.5 hr | 建銷售單 → 確認 → 系統產生 Customer Shipment → 出貨確認 |
| 1 hr | 對照 Day 2，觀察採購與銷售流程的對稱性，加深記憶 |
 
**關鍵概念：** Sale 和 Purchase 流程幾乎對稱，學完採購後銷售會快很多。刻意比較兩者差異。
 
---
 
## Day 5｜整合與會計閉環（3 hr）
 
**目標：補上發票與收付款，讓商業循環完整閉合**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 從採購單產生廠商發票 → 確認 → 登錄付款 |
| 1 hr | 從銷售單產生客戶發票 → 確認 → 登錄收款 |
| 1 hr | 跑損益表、資產負債表，確認數字有反映所有交易 |
 
**關鍵概念：** 會計是所有流程的終點。發票不確認，損益表就不會動。這一天讓整個 MVP ERP 閉合。
 
---
 
## Day 6｜整合與除錯（3 hr）
 
**目標：建立系統性理解，準備獨立探索**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 從頭跑一次完整的商業循環（採購入庫 → 銷售出庫 → 發票收付款），不看筆記 |
| 1 hr | 刻意製造錯誤（庫存不足、狀態不對）→ 看錯誤訊息 → 學會除錯 |
| 1 hr | 看 Tryton 的 Model 結構（用 `ir.model` 查），建立「資料在哪裡」的直覺 |
 
**關鍵概念：** 最後一小時的 `ir.model` 探索，是從使用者轉向顧問／開發者視角的第一步。
 
---
 
## 核心概念總整理
 
### 庫存是所有流程的交匯點
 
```
採購入庫  →  ＋庫存
銷售出庫  →  －庫存
盤點調整  →  ±庫存（修正誤差）
```
### MVP ERP 完整循環
 
```
採購 → 入庫 → 廠商發票 → 付款 → 反映應付／現金
銷售 → 出庫 → 客戶發票 → 收款 → 反映應收／現金
```
### Stock Move 是底層機制
 
不管是採購、銷售、盤點，最終都落地到 `Stock Move`（from location → to location）。
`purchase`、`sale` 都只是觸發庫存異動的不同原因。
 
---
 
## 學習原則
 
1. **每個流程都要跑通才算完成**，看懂不算
2. **遇到卡關先截圖記下來**，繼續往前，回頭再查
3. **Day 1 的基礎資料建好就不要亂動**，後面所有 Use Case 都會用到
4. **不要跳著學**，每個 Use Case 都建立在前一個的概念上
