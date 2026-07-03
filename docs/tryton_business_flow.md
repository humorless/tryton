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

以下是本文件 Day 1–8 實際會用到的完整清單：

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
production
```

> **注意**：`production` 在這裡是為了跑通製造流程（Day 5–6）而裝，不代表它是所有場景的 minimum set。真實客戶的 minimum set 應該從業務需求反推，而不是預先全裝。
 
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
 
## Day 2｜Use Case 3：庫存盤點（3 hr）
 
**目標：理解 Stock Move 是 Tryton 庫存的核心**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 建立 Warehouse、Location 結構（Storage, Input, Output, Lost & Found） |
| 1 hr | 手動建立 Internal Shipment，感受 Stock Move 怎麼產生 |
| 1 hr | 跑一次完整盤點：建盤點單 → 輸入實際數 → 確認 → 看庫差 Move |
 
**關鍵概念：** 所有庫存異動本質上都是 `Stock Move`（from location → to location），盤點只是其中一種觸發方式。
 
---
 
## Day 3｜Use Case 1：採購到入庫（3 hr）
 
**目標：跑通 Purchase → Supplier Shipment → Stock**
 
| 時間 | 內容 |
|------|------|
| 0.5 hr | 設定廠商的 Payment Term、幣別 |
| 1.5 hr | 建採購單 → 確認 → 系統產生 Supplier Shipment → 驗收 → 確認入庫 |
| 1 hr | 查庫存數量確認有變動、看自動產生的 Stock Move 明細 |
 
**關鍵概念：** Tryton 的採購不會直接異動庫存，中間一定經過 Shipment，這個設計是刻意的。
 
---
 
## Day 4｜Use Case 2：銷售到出庫（3 hr）
 
**目標：跑通 Sale → Customer Shipment → Stock**
 
| 時間 | 內容 |
|------|------|
| 0.5 hr | 設定客戶資料、Price List（用最簡單的固定價） |
| 1.5 hr | 建銷售單 → 確認 → 系統產生 Customer Shipment → 出貨確認 |
| 1 hr | 對照 Day 3，觀察採購與銷售流程的對稱性，加深記憶 |
 
**關鍵概念：** Sale 和 Purchase 流程幾乎對稱，學完採購後銷售會快很多。刻意比較兩者差異。
 
---
 
## Day 5｜Use Case 4：製造流程 Part 1（3 hr）
 
**目標：建立 BOM 與工單，理解製造資料結構**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 建立成品 Product、原料 Product，設定正確的 Product Type |
| 1 hr | 建立 Bill of Materials（BOM）：指定用料與數量 |
| 1 hr | 建立 Production Order → 確認 → 觀察系統自動帶入的用料清單 |
 
**關鍵概念：** BOM 是製造的規格書，Production Order 是執行實例，兩者分開是刻意設計。
 
---
 
## Day 6｜Use Case 4：製造流程 Part 2（3 hr）
 
**目標：跑通用料記錄到庫存異動**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 對 Production Order 執行 Assign（分配庫存）→ 確認原料夠用 |
| 1 hr | 記錄實際用料（可以與 BOM 不同）→ 完工確認 |
| 1 hr | 查看系統產生的所有 Stock Move，對照原料消耗與成品入庫 |
 
**關鍵概念：** 製造完工會同時產生兩筆 Move：原料出庫 + 成品入庫，這是 Tryton 製造模組的核心動作。
 
---
 
## Day 7｜整合與會計閉環（3 hr）
 
**目標：補上發票與收付款，讓商業循環完整閉合**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 從採購單產生廠商發票 → 確認 → 登錄付款 |
| 1 hr | 從銷售單產生客戶發票 → 確認 → 登錄收款 |
| 1 hr | 跑損益表、資產負債表，確認數字有反映所有交易 |
 
**關鍵概念：** 會計是所有流程的終點。發票不確認，損益表就不會動。這一天讓整個 MVP ERP 閉合。
 
---
 
## Day 8｜整合與除錯（3 hr）
 
**目標：建立系統性理解，準備獨立探索**
 
| 時間 | 內容 |
|------|------|
| 1 hr | 從頭跑一次最複雜的流程（製造），不看筆記 |
| 1 hr | 刻意製造錯誤（庫存不足、狀態不對）→ 看錯誤訊息 → 學會除錯 |
| 1 hr | 看 Tryton 的 Model 結構（用 `ir.model` 查），建立「資料在哪裡」的直覺 |
 
**關鍵概念：** 最後一小時的 `ir.model` 探索，是從使用者轉向顧問／開發者視角的第一步。
 
---
 
## 核心概念總整理
 
### 庫存是所有流程的交匯點
 
```
採購入庫  →  ＋庫存
製造領料  →  －庫存（原料）＋庫存（成品）
銷售出庫  →  －庫存
盤點調整  →  ±庫存（修正誤差）
```
### MVP ERP 完整循環
 
```
採購 → 入庫 → 廠商發票 → 付款 → 反映應付／現金
銷售 → 出庫 → 客戶發票 → 收款 → 反映應收／現金
製造 → 成本自動帶入發票
```
### Stock Move 是底層機制
 
不管是採購、銷售、製造、盤點，最終都落地到 `Stock Move`（from location → to location）。
`purchase`、`sale`、`production` 都只是觸發庫存異動的不同原因。
 
---
 
## 學習原則
 
1. **每個流程都要跑通才算完成**，看懂不算
2. **遇到卡關先截圖記下來**，繼續往前，回頭再查
3. **Day 1 的基礎資料建好就不要亂動**，後面所有 Use Case 都會用到
4. **不要跳著學**，每個 Use Case 都建立在前一個的概念上
