# Admin User 操作手冊

給「設定 ERP」的人看。對照 [`user-guide.md`](user-guide.md)（ordinary user 操作）與 [`../docs/business_flow.md`](../docs/business_flow.md)（整體課程）服用。

> 版本：`tryton/tryton:8.0-office`（docker-compose.yml）。網路上 Tryton 教學多半是 6.0 時代寫的，選單文字/位置在 8.0 大致沿用但偶有差異，本文件的選單路徑以**實際跑過並截圖確認**為準；還沒實測的步驟會標註「⬜ 待做（未驗證選單路徑）」。

## 環境現況（2026-07-02 用 psql 直查資料庫確認）

已啟用模組：

| 模組 | 狀態 |
|------|------|
| `company` | ✅ activated |
| `currency` | ✅ activated |
| `party` | ✅ activated |
| `account` | ✅ activated |
| `account_invoice` | ✅ activated |
| `account_product` | ✅ activated |
| `stock` | ✅ activated |
| `sale` | ✅ activated（2026-07-09） |
| `purchase` | ✅ activated（2026-07-08，Day 2 完成時已啟用，此表格先前未同步更新） |
| `hello_world` | ✅ activated（自訂模組，見 [`../docs/custom-modules.md`](../docs/custom-modules.md)） |

> **化簡（2026-07-07）**：原本這裡還列了 `production`（Day 5 前需要），但這份計劃鎖定「進書、庫存、賣書」的純貿易情境，不需要製造模組，已從模組清單與 Day 5–6 拿掉，見 [`../docs/business_flow.md`](../docs/business_flow.md)。

使用者：

| login | name | 狀態 |
|-------|------|------|
| `admin` | Administrator | ✅ 已可登入 |
| `aaa` | — | ⬜ **`id_pw.md` 裡有帳密規劃，但 `res_user` 表裡還不存在** → 這是 Day 1 admin 任務之一：建立專屬的 ordinary user 帳號，不要一直用 admin 測操作流程 |

`company_company` / `party_party`：（2026-07-02 更新）已各有 1 筆——`REPLWARE Co., Ltd.`（Party id=1）／Company id=1（currency=TWD），並已設為 admin 的 Current Company。

---

## Day 1｜地基（admin 部分）

對應 [`business_flow.md`](../docs/business_flow.md) Day 1 的「建立基礎資料」時段。

### Step 1：Admin 登入 Web

- 狀態：✅ 完成
- URL：`http://localhost:8000/`
- 帳密：見 `id_pw.md`（已加入 `.gitignore`，不會進版控，本文件不重複寫密碼明文）

### Step 2：確認已啟用模組

- 狀態：✅ 完成（見上方「環境現況」表）
- UI 對應路徑：Administration ‣ Modules（或 8.0 選單若改名，實際點過後回來更新這裡）

### Step 3：建立 Party（公司本身）、Currency、Company、設定 Current Company

- 狀態：✅ 完成
- **修正**：一開始誤以為 Company 表單會直接內嵌 Party 欄位（同一張表）。用 `psql` 查 `company_company` schema 後確認：`company_company.party` 是 `NOT NULL` + `UNIQUE` 的 FK，指向獨立的 `party_party` 表。Tryton 沒有 Odoo 那種 delegation inheritance，Company 是靠 Many2One 關聯到一筆真正獨立的 Party 記錄，**不是同一筆資料**。
- 實際走的路徑：先建 Party，再建 Currency，再建 Company，最後設定 Current Company

**執行記錄**

| 子步驟 | 狀態 | 備註 |
|--------|------|------|
| 建立 Party | ✅ 完成 | `REPLWARE Co., Ltd.`（id=1, code=1），地址：No. 119, Sec. 1, Chongqing S. Rd, Taipei 100004。Country/Subdivision 沒填，不影響存檔，之後開統一發票／VAT 相關功能可能要補 |
| 建立 Currency | ✅ 完成 | `Taiwan Dollar` / TWD（id=1），rounding 0.01，digits 2，Numeric Code 901（ISO 4217）。已補上 base currency 慣例的 Rate：2026-07-02 / 1.000000（官方建議單一幣別時把該幣別的 Rate 設為 1，見 [Currency Usage](https://docs.tryton.org/8.0/modules-currency/usage.html)），Current rate 顯示 1.000000 |
| 建立 Company | ✅ 完成 | `company_company` id=1，party=`REPLWARE Co., Ltd.`，currency=`Taiwan Dollar`，timezone 自動帶出 `Asia/Taipei` |
| 設為 Current Company | ✅ 完成（過程中卡關一次，見下方） | `res_user.company` 已確認為 `1` |

**卡關記錄：右上角 Preferences 一開始選不到 Company**

- 現象：Administrator（右上角）→ Preferences，Company 下拉選單是空的/選不了
- 原因：User 模型有兩個欄位——`companies`（這個使用者被允許切換的公司清單，多選）跟 `company`（目前生效的那間，單選）。**Preferences 的 Company 下拉只會列出已經在 `companies` 清單裡的公司**，新建的 Company 不會自動加進任何使用者的允許清單，所以清單是空的
- 正確做法：Administration ‣ User ‣ Users → 開 `admin` 使用者 → **Companies** 分頁 → 把 `REPLWARE Co., Ltd.` 加進去 → **存檔**（這步容易漏，勾選之後沒按 Save 等於沒發生——第一次操作時就漏了這步，`res_user-company_company` 關聯表當時查出來是 0 筆）
- 補存檔後複查：`res_user-company_company` 有一筆 `user=1, company=1`
- 存檔後回到 Preferences，Company 下拉列出 `REPLWARE Co., Ltd.`，選定並存檔，複查 `res_user.company = 1` 確認生效

📸 `day1-admin-01-party-form.png`、`day1-admin-02-currency-form.png`、`day1-admin-03-company-form.png`、`day1-admin-04-user-companies-field.png`（卡關瞬間：已勾選但還沒存檔）、`day1-admin-05-preferences-current-company.png`（已存檔，見 `assets/`）

### Step 4：建立 Chart of Accounts（用內建 Universal 範本）

- 狀態：✅ 完成（2026-07-03，psql 複查）
- **選單路徑更正**：實際是 Financial（財務）‣ Configuration ‣ **Templates** ‣ **Create Chart of Accounts from Template**（不在 General Account 底下，且是 Accounts 複數；同層還有一個對稱的 "Update Chart of Accounts from Template" 是之後範本更新用的，這次不用點）
- **範本更正**：8.0 沒有叫「Minimal」的範本，可選清單裡是 **Universal Chart of Accounts**，這就是通用/最簡版，直接選這個即可
- wizard 分兩步：
  1. 選 Company（`REPLWARE Co., Ltd.`）+ Account Template（`Universal Chart of Accounts`）
  2. 選預設科目：Default Receivable Account／Default Payable Account／Default Revenue Account／Default Expense Account（此時科目表已經在背後建好，這幾個欄位是從已建好的科目裡挑出常用的設成預設值，之後開發票/建 Product 會自動帶出）
- 四個 Default Account 的挑選建議（Universal 範本內建分類科目，對應一般商品貿易情境）：

  | 欄位 | 選定 | 理由 |
  |------|------|------|
  | Default Receivable Account | 1.2.1 - Accounts, Notes And Loans Receivable | 標準應收帳款，Contracts／Nontrade 是特殊情境用 |
  | Default Payable Account | 2.1.1 - Trade Payables | 標準應付帳款，Dividends／Other Payable 不適用一般進貨 |
  | Default Revenue Account | 4.1.1 - Goods | **更正**：4.x 底下不是「商品 vs 服務」分類，查了 `account_account_template` 範本階層後確認是 **ASC 606 收入認列時間點**分類：`4.1.0 Recognized Point Of Time` vs `4.2.0 Recognized Over Time`，`4.1.1 Goods` 跟 `4.2.1 Products` 都是實體商品，差別在認列時機。一般貿易情境交貨當下就完成履約義務、認列收入，屬於 Point of Time，所以選 4.1.1（不是單純因為「賣商品」） |
  | Default Expense Account | 5.2.1 - Cost Of Sales | 對應同一批 point-of-time 認列商品的銷貨成本（COGS） |

  > 補充：`4.2.x Recognized Over Time` 是給長期生產合約、分階段驗收的情境用的（例如有 `production` 模組的製造業）；這份計劃鎖定純貿易的書店情境，用不到這類收入認列，這裡選的就是「最常見、最大量一般銷售」的預設值，不影響之後個別交易另外指定科目。

**執行結果（psql 複查，2026-07-03）**

- `account_account` 表：company=1 底下共建立 **135 筆**科目（Universal 範本全套）
- 抽查四個關鍵科目代碼確實存在：`1.2.1 Accounts, Notes And Loans Receivable`、`2.1.1 Trade Payables`、`4.1.1 Goods`、`5.2.1 Cost Of Sales`
- 四個 Default Account 實際存放位置：`account_configuration_default_account` 表（公司層級單例設定，不是掛在 Party 或 Product Category 上）：
  - `default_account_receivable` → id 39（1.2.1）
  - `default_account_payable` → id 67（2.1.1）
  - `default_category_account_revenue` → id 99（4.1.1）
  - `default_category_account_expense` → id 112（5.2.1）
  - （順帶確認：`party_party_account`／`product_category_account` 這兩張表目前是空的）
  - **更正（2026-07-08，Day 2 實測發現）**：原本以為這組公司預設值是「Party／Product Category 沒特別覆寫時的通用 fallback」，Day 2 實測 Purchase Process 時發現這個理解**對 Product Category 不成立**——查了 `account_product/product.py`，`default_category_account_revenue`／`default_category_account_expense` 這兩個 classmethod 只是「新建一個 Product Category 時，Expense/Revenue Account 欄位要不要先幫你帶一個預設值」，不是 runtime 後備方案；一旦 Product 掛了 Category，那個 Category 自己就必須勾 Accounting、填好科目，不會自動退回這裡的公司預設值（不然會直接報錯，見 [`user-guide.md`](user-guide.md) Day 2 概念筆記）。Party 層級的 Receivable／Payable 是否有一樣的落差，這裡沒有實測過，先不要照搬同一套假設

- 📸 `day1-admin-06-create-chart-wizard.png`（選單定位）、`day1-admin-07-coa-wizard-template.png`（步驟一：Company + Template）、`day1-admin-08-coa-wizard-defaults.png`（步驟二：預設科目，四個欄位當時還沒填）、`day1-admin-09-coa-search-receivable.png`／`day1-admin-10-coa-search-payable.png`／`day1-admin-11-coa-search-revenue.png`／`day1-admin-12-coa-search-expense.png`（各科目的搜尋清單）、`day1-admin-13-coa-wizard-defaults-filled.png`（四個欄位填好，尚未按 CREATE）

### Step 5：建立 Fiscal Year

- 狀態：✅ 完成（2026-07-03，psql 複查）
- 選單路徑：Financial ‣ Configuration ‣ Fiscal Years ‣ Fiscal Years
- 填寫內容：Name=`2026`（慣例：公司會計年度跟日曆年一致時直接填年度數字），Start Date=01/01/2026，End Date=12/31/2026，Company=`REPLWARE Co., Ltd.`，State=Open
- 建立 Fiscal Year 後，用 **Create Periods** wizard 產生標準的月份 Period（不建 Period，之後任何交易都記不進帳）

**卡關記錄：Pre-validation 錯誤 "Move Sequence" is required**

- 現象：存檔／按 Create Periods 時跳出「The values of "Invoice Sequences" are not valid. "Move Sequence" is required.」
- 原因：Fiscal Year 表單除了 Periods 分頁，還有一個 **Sequences** 分頁，用來指定這個會計年度的傳票／發票編號規則（`ir.sequence`）。因為 `account_invoice` 模組已啟用，Sequences 分頁下至少 Move Sequence 是必填，發票相關序號可能也需要
- 處理方式：改用獨立分頁建立，而不是表單欄位旁邊的快速新增小視窗，方便之後管理／重複使用。**選單路徑：Administration ‣ Sequences ‣ Sequences Strict**（不是旁邊的普通 "Sequences"——查過 schema，Move Sequence／Invoice Sequence 欄位的 FK 指向 `ir_sequence_strict` 表，跟一般 `ir_sequence` 是不同 model，普通 Sequences 清單建的記錄在 Fiscal Year 表單裡搜尋不到）。共需建 5 筆：

  | Sequence | Name | Sequence Type | Prefix |
  |---|---|---|---|
  | Move Sequence 用 | `Move 2026` | Account Move | `${date_Y}-` |
  | Customer Invoice Sequence 用 | `Customer Invoice 2026` | Invoice | `${date_Y}-CI-` |
  | Customer Credit Note Sequence 用 | `Customer Credit Note 2026` | Invoice | `${date_Y}-CC-` |
  | Supplier Invoice Sequence 用 | `Supplier Invoice 2026` | Invoice | `${date_Y}-SI-` |
  | Supplier Credit Note Sequence 用 | `Supplier Credit Note 2026` | Invoice | `${date_Y}-SC-` |

  （查過 `ir_sequence_type` 表，發票四種共用同一個 "Invoice" 類型，只是各自獨立命名/編號；系統原本就有的 8 筆序號是 Party／Shipment 類／Inventory／Account Move **Reconciliation**——最後這筆容易跟 Account Move 搞混，但它是沖銷專用，不能拿來當 Move Sequence 用）

  每一筆建立時的欄位設定（查過 `ir_model_field` 確認）：
  - **Type**：選 **Incremental**（另兩個選項 Decimal/Hexadecimal Timestamp 是用時間戳記算短碼，條碼/標籤用途，不適合連號記帳；系統內建 8 筆序號也都是 Incremental）
  - **Prefix**：`${date_Y}-`（Tryton 支援 `${date_Y}` 這種 strftime 格式化語法，會自動代入當下年份變成 `2026-`），四個 Invoice Sequence 可各自加識別字，例如 Customer Invoice 用 `${date_Y}-CI-`
  - **Suffix**：留空
  - **Padding**：5 或 6（決定編號補零位數，例如 5 → `00001`）
  - **Number Increment**：預設 1，不用改

  建好 5 筆後回 Fiscal Year 分頁，Move Sequence／四個 Invoice Sequence 欄位改用搜尋既有的方式選進去 → 存檔 → 再按 Create Periods

  **執行結果（psql 複查 `ir_sequence_strict`，2026-07-03）**：5 筆全數存檔成功，欄位與上表設計一致（皆為 `incremental`、padding=5、increment=1、company=1／REPLWARE）：

  | id | name | prefix | sequence_type |
  |---|---|---|---|
  | 1 | Move 2026 | `${date_Y}-` | Account Move |
  | 2 | Customer Invoice 2026 | `${date_Y}-CI-` | Invoice |
  | 3 | Customer Credit Note 2026 | `${date_Y}-CC-` | Invoice |
  | 4 | Supplier Invoice 2026 | `${date_Y}-SI-` | Invoice |
  | 5 | Supplier Credit Note 2026 | `${date_Y}-SC-` | Invoice |
- 📸 `day1-admin-17-sequences-list.png`（Administration ‣ Sequences 清單，注意：這是普通 `ir.sequence`，跟下面要用的 Sequences Strict 是不同清單，僅供對照原有 8 筆內建序號）、`day1-admin-18-move-sequence-form.png`（Move 2026 表單，Preview 欄位顯示 `2026-00001`）、`day1-admin-19-fiscal-year-sequences-filled.png`（Fiscal Year 的 Sequences 分頁，5 個欄位都已指定並存檔成功）

**執行結果（psql 複查 `account_fiscalyear` / `account_fiscalyear_invoice_sequence`，2026-07-03）**

- Fiscal Year：id=2，Name=`2026`，2026-01-01～2026-12-31，State=Open，`move_sequence` 正確指向 `Move 2026`
- Invoice Sequences：`out_invoice_sequence`→`Customer Invoice 2026`、`out_credit_note_sequence`→`Customer Credit Note 2026`、`in_invoice_sequence`→`Supplier Invoice 2026`、`in_credit_note_sequence`→`Supplier Credit Note 2026`（Tryton 命名習慣：`out_` 指開給客戶的單據，`in_` 指收到的供應商單據）
- Periods：回 Periods 分頁按 **Create Periods** wizard（Frequency=Monthly，End Day=31，皆為預設值不用改）→ psql 複查 `account_period` 表，`fiscalyear=2` 底下正確產生 12 筆，`2026-01`～`2026-12`，日期正確對齊月底（2 月 28、4/6/9/11 月 30），`type=standard`、`state=open`
- 📸 `day1-admin-20-create-periods-wizard.png`（Create Periods wizard 畫面）

**概念筆記：每個新 Fiscal Year 都要新建 Sequence 嗎？**

- 查 `account_fiscalyear` 表 schema 確認：`move_sequence` 欄位有 **UNIQUE 約束**（`account_fiscalyear_move_sequence_unique`），資料庫層級強制一個 Move Sequence 只能屬於一個 Fiscal Year
- 交叉驗證：Tryton 核心開發者 Cédric Krier 在 [tryton Google Groups 討論串](https://tryton.narkive.com/4ke4rW5t/do-we-need-to-create-new-post-move-invoice-and-credit-note-sequences-for-every-fiscal-year)（原討論發生於 2014 年，narkive 為第三方 Google Groups 封存鏡像）明確回答「Yes」，原因是 Tryton 允許在開新年度後仍對**尚未關閉**的舊年度補開發票，若兩年共用同一組序號會讓單一年度內號碼出現缺口，所以用 constraint 強制 Move Sequence 每年必須不同；8.0 額外支援同一 Fiscal Year 底下按 Period（月）再細分序號
- 四個 Invoice Sequence 沒有類似 DB 約束，技術上可以讓多個年度共用同一筆、編號跨年累加不歸零（同討論串 Guillem Barba 確認）；但 Cédric 也警告這樣做在「新年度已開始、仍補開舊年度發票」的情境下，反而會在單一年度內產生號碼缺口，兩種做法互有取捨
- Tryton 主要維護公司 B2CK 自己的實務做法（Cédric 原話）：Prefix 用年份、序號每年歸零重新從 1 開始——法國稅務單位 BOFiP 的規定也證實這樣做合法（只要求同一年內不重複，不要求跨年連續）
- 本環境採用跟 B2CK 相同的「每年新建 5 筆、Prefix 帶年份、歸零重來」，是業界最常見、最不容易踩坑的預設做法
- 📸 `day1-admin-14-fiscal-year-form.png`（表單本體）、`day1-admin-15-fiscal-year-sequence-error.png`（Pre-validation 錯誤畫面）、`day1-admin-16-fiscal-year-sequences-tab.png`（Sequences 分頁：Move Sequence + Invoice Sequences 四個子欄位，皆為必填但當時未填）

**概念筆記：Sequence 是什麼**

- `ir.sequence` 是 Tryton 通用的自動編號產生器，出貨單、採購單、發票、傳票都靠它產生連續不重複的號碼；跟台灣國稅局配發的統一發票字軌**概念類似（都要求連號）但機制不同層級**——Tryton 的 Sequence 是公司自己在系統裡定義的內部規則，統一發票號碼則是國稅局依法配發、企業不能自訂，兩者不能直接畫等號，若要讓 Tryton 開的發票號碼符合台灣電子發票規範需要另外客製/串接（待查證是否有現成在地化模組，見 [`automation-notes.md`](automation-notes.md)）
- 連號編號本身只是「其中一塊防弊積木」：它讓稽核可以事後檢查號碼有沒有缺口，但真正防止事後竄改帳目的是 Tryton 的另一個機制——分錄一旦過帳（Posted）就唯讀不可修改／刪除，只能用沖銷分錄反轉，搭配 `create_uid`/`write_uid` 異動軌跡。兩者搭配才有完整的稽核意義，單靠連號防不了假帳

**概念筆記：為什麼 Move/Invoice Sequence 一定要用 `ir.sequence.strict`，不能用一般 `ir.sequence`？**

- 查 schema 證實這是寫死的，不是選項：`account_fiscalyear.move_sequence` 跟 `account_fiscalyear_invoice_sequence` 的四個 Sequence 欄位，FK 全部指向 `ir_sequence_strict` 表，不是 `ir_sequence`，一般 Sequences 清單建的記錄在這些欄位裡搜尋不到
- 兩種 model 的差別在「取號時的鎖定強度」：
  - `ir.sequence`（用在 Shipment、Party 編號這類）：取號用比較輕量的鎖，效能好，但極端高並發下理論上有極小機率非原子操作
  - `ir.sequence.strict`：取號用更嚴格的資料庫鎖（等同 `SELECT ... FOR UPDATE`），保證就算兩個人/兩個程序同時過帳，也絕對不會兩筆分錄拿到同一個號碼或跳號
- 會計分錄跟發票號碼牽涉法規稽核，號碼重複/跳號不可接受，所以 Tryton 在 model 設計上就把這五個欄位鎖死只能用 Strict 版本，用效能換取「絕對不出錯」的保證

### Step 6（追加，原 business_flow 沒明講但實務必做）：建立 ordinary user 帳號

- 狀態：✅ 完成（2026-07-03，psql 複查）
- 選單路徑：Administration ‣ User ‣ Users → New
- 填寫內容：Name=`Test User`、Login=`aaa`、Email=`aaa@replware.dev`、Password（見 `id_pw.md`）、Companies 分頁已加入 `REPLWARE Co., Ltd.`（這次記得建立當下就加，不會重踩 Step 3 那個 Preferences 選不到公司的坑）
- **Group 指派更正**：原本以為要指派 Party/Product/Sale/Purchase 相關 Group，但查了 `res_group` 表後發現這個系統目前只有 `Party Administration`／`Product Administration` 這種「管理」版本的群組，**沒有**一般使用者版本；`sale`／`purchase` 的 Group 也還不存在（模組未啟用）。研判 Party/Product 基礎資料的一般瀏覽/建立預設不需要掛 Group，只有管理設定層級才需要——Access Permissions 分頁先不勾直接存檔，之後 Day 2 用 `aaa` 實際登入測試能不能看到 Party/Product 選單，看不到再回來查是哪個 Group／`ir.rule` 卡住
- 這樣 Day 2 之後可以真的用「ordinary user 視角」登入操作，而不是一直用 admin 假扮
- 📸 `day1-admin-21-aaa-user-form.png`（User 表單，Login/Password/Companies 已填，Access Permissions 尚未設定）

**執行結果（psql 複查，2026-07-03）**

- `res_user`：id=3，login=`aaa`，name=`Test User`，email=`aaa@replware.dev`，active=true，**company=1**（建立當下就設好 Current Company，不用像 admin 當初那樣事後補）
- `res_user-company_company`：user=3／company=1，一筆 ✅
- `res_user-res_group`：**0 筆**，跟預期一致（Access Permissions 沒勾任何 Group）——留待 Day 2 用 `aaa` 實際登入測試選單可視性，見上方「Group 指派更正」

**概念筆記：User 表單 Password 欄位的 SHOW 按鈕，為什麼按了還是顯示 `xxxxxxxx`**

- 現象：編輯既有 User（例如 `admin`、`aaa`）時，Password 欄位按 SHOW 只會看到一串 `xxxxxxxx`，不是真正的密碼
- 查 `res_user` 表結構發現有 `password` 和 `password_hash` 兩個欄位；實查資料：`password` 欄位是 **NULL**，真正存的是 `password_hash`，格式是 `$argon2id$v=19$m=655...`（Argon2id 雜湊）
- 結論：**Tryton 資料庫從未存過明碼密碼**，SHOW 按鈕不可能真的還原密碼——`xxxxxxxx` 只是固定的遮罩佔位符，不是加密後可還原的內容。連 admin 自己都無法在後台看到任何使用者（包含自己）的真實密碼，忘記密碼只能重設、不能找回
- SHOW 按鈕真正的用途：讓操作者**在這次輸入時**快速 double check 剛打的字有沒有打對（把 `type="password"` 切成 `type="text"` 顯示明文），不是拿來查詢舊密碼——這也解釋了為什麼編輯舊帳號時按 SHOW 沒有意義，只有「正在輸入新密碼」時才有用
- 呼應本文件的密碼安全規範：密碼絕不明碼寫入任何 manuals/文件，只寫「見 `id_pw.md`」——這點 Tryton 自己在資料庫層級也是同樣的設計原則

**追加動作（2026-07-06）：`aaa` 加入 Product Administration 群組**

- 原因：`user-guide.md` Step 3（建立 Product）前置要求，見 `ir_model_access` 查證結果（`product.template` 無 Group 預設唯讀）
- 選單路徑：Administration ‣ User ‣ Users → `aaa` → Access Permissions 分頁 → 勾選 **Product Administration** → 存檔
- 📸 `day1-admin-22-aaa-access-permissions.png`
- **執行結果（psql 複查）**：`res_user-res_group` 查到 1 筆，`user=3`（aaa）／`group=8`（Product Administration），確認存檔成功

---

## Day 2 前置（admin 部分）：啟用 purchase 模組

- 狀態：✅ 完成（2026-07-08，psql 複查）
- **順序更正（2026-07-07）**：`aaa` 加入 Stock 群組、Location 結構這組原本標的是「Day 2 前置」，因為原始規劃 Day 2 是庫存盤點。後來發現一個全新環境沒有 Day 2（採購入庫）先跑過的話，庫存操作會因為沒有真實庫存而卡在 Assign 這步，所以把 Day 2／Day 3 對調（Day 2 改採購、Day 3 改庫存盤點），這裡也跟著往前搬，見 [`user-guide.md`](user-guide.md)
- 實際走的路徑：Administration ‣ Modules，勾選 `purchase` → 按 **ACTIVATE**（狀態變成 `To be activated`）→ 按下方 **APPLY** → 跳出「Perform Pending Activation/Upgrade」精靈 → **START UPGRADE**
- 📸 `day2-admin-01-purchase-module-activate.png`（勾選 purchase，狀態 To be activated，尚未 Apply）、`day2-admin-02-purchase-upgrade-wizard.png`（Apply 後的確認精靈，尚未按 Start Upgrade）

**執行結果（psql 複查 `ir_module`，2026-07-08）**

- `purchase`：`activated`
- **`account_invoice_stock` 也一併變成 `activated`**——一開始沒預期到多了這個模組，查了 `ir_module_dependency` 表確認：`purchase` 本身在 `tryton.cfg` 裡就宣告依賴 `account_invoice_stock`（負責把庫存異動的實際成本連回發票金額計算），Tryton 的模組啟用會自動連鎖啟用所有依賴模組，這不是操作失誤，是 `purchase` 的正常依賴鏈
- `sale` 仍是 `not activated`（預期中，Day 4 前才啟用）

---

## Day 2 前置（續）：`aaa` 加入 Purchase 群組

- 狀態：✅ 完成（2026-07-08，psql 複查）
- 原因：查了 `ir_model_access` 表，`purchase.purchase`（採購單）有一筆 `group=NULL` 的規則把預設權限全部設成 `false`，`purchase.line`（採購單明細）也只有 `Stock` 群組的唯讀規則——`aaa` 現有的 Stock／Product Administration 群組只能**看到**採購單，無法建立或編輯，必須加掛 **Purchase** 群組（`res_group` id=14）
- 選單路徑：Administration ‣ User ‣ Users → `aaa` → Access Permissions 分頁 → 勾選 **Purchase** → 存檔

**執行結果（psql 複查，2026-07-08）**：`aaa` 現有 3 筆群組——`group=8`（Product Administration）、`group=10`（Stock）、`group=14`（Purchase）。

**概念筆記：只需要 Purchase，還是要 Purchase + Purchase Administrator？**

- 原始結論（2026-07-08 上午）：**只需要 Purchase**——查了 `ir_model_access`：`purchase.purchase`／`purchase.line` 都是靠 **Purchase** 群組拿到完整 CRUD，這是建採購單需要的核心權限；當時判斷 **Purchase Administrator** 只管 `purchase.configuration`（公司層級的採購設定單例），是 admin 才需要碰的設定層級
- 額外查證排除了兩個潛在卡點：`ir_sequence` 已經有內建的 `Purchase` 編號序列（id=9），不用手動建；`account_invoice_payment_term` 表已有 9 筆內建付款條件（Upon Receipt／Net 30 days...），Day 2 只是在供應商身上**選一個既有的**，不需要新建，所以也不用額外的 Accounting Administration 群組
- **更正（2026-07-08 下午，實測發現）**：上面的結論不完整。`aaa` 只掛 Purchase 群組時，Purchase Order 的 **Process** 按鈕（狀態 Confirmed → Processing，真正產生 Supplier Shipment／Invoice 的那一步）是 disabled 的。查了 `ir_model_button`／`ir_model_button-res_group` 這兩張表才找到原因：

  | 按鈕 | 需要的群組 |
  |---|---|
  | Quote／Confirm／Cancel／Modify Header | 無（只要有 Purchase 群組的 model 層級權限就能點） |
  | **Process** | **Purchase Administrator**（獨立限定） |

- **關鍵概念：`ir.model.access`（model 層級 CRUD）跟 `ir.model.button`（按鈕層級）是兩套分開的權限機制**——`ir_model_access` 管的是「能不能讀/寫/建/刪這個 model 的資料」，`ir_model_button`／`ir_model_button-res_group` 管的是「能不能點這個特定的狀態機按鈕」，兩者互相獨立，光查 `ir_model_access` 判斷「這個群組夠不夠」是不完整的，卡到按鈕層級的權限時要另外查 `ir_model_button` 這組表
- **最終結論**：`aaa` 要跑完整個 Day 2 流程（含 Process），需要 **Purchase + Purchase Administrator** 兩個群組都掛；查了 `group_purchase_admin` 的定義，`parent` 指向 `group_purchase`（階層上是 Purchase 的加強版），概念上比較像「有權限拍板讓採購單真正生效的人」（業務角色），不是 Stock Administration 那種偏技術性的結構管理權限

**執行結果（psql 複查，2026-07-08）**：`aaa` 現有 4 筆群組——`group=8`（Product Administration）、`group=10`（Stock）、`group=14`（Purchase）、`group=15`（Purchase Administrator）。

**概念筆記：為什麼 `admin` 帳號永遠什麼都能做？**

- 現象：這門課一路下來，每次幫 `aaa` 加群組都要手動一個一個勾，但 `admin` 從來不需要——查了 `res_user-res_group`，`admin`（id=1）現在有 **15 筆**群組，剛好等於這個環境目前存在的全部群組數量
- **不是 root 超級使用者豁免**：Tryton 有一個真正的系統內部帳號 `root`（id=**0**），程式邏輯裡（`ir/model.py` 的 `ModelAccess.get_access()`）明確寫著 `if Transaction().user == 0: return ...True`，直接跳過所有權限檢查——但這是保留給 `root`（id=0）的，`admin` 是 id=**1**，一般帳號，不吃這個豁免
- **真正機制：每個模組的 XML 資料檔都會明確把 `admin` 加進自己定義的每個群組**，例如 `purchase.xml`：

  ```xml
  <record model="res.user-res.group" id="user_admin_group_purchase_admin">
      <field name="user" ref="res.user_admin"/>
      <field name="group" ref="group_purchase_admin"/>
  </record>
  ```

  這是 Tryton 的模組作者慣例：模組一啟用，內建的 `admin` 帳號就自動被加進這個模組定義的所有群組（不只 Purchase，其他模組如 Stock／Account 也是同樣寫法），假設「裝這個模組的人，至少要能立刻把它用到底」，不需要另外手動授權自己
- **實務含義**：`admin` 的「萬能」是資料驅動的明確設定，不是程式邏輯的隱藏豁免；`aaa` 這種之後才建立的一般使用者不會被自動加進新模組的群組，這也是為什麼每次啟用新模組後，都要回來重新檢查 `aaa` 是否卡在某個群組上——這是 Tryton 設計上刻意要讓「新使用者的權限」跟「模組啟用」脫鉤，不是漏做了什麼

**概念筆記：職責分離（Segregation of Duties）——要不要拆多個使用者對應不同部門？**

- 討論脈絡：這門課一路下來，`aaa` 陸續累積了 Product Administration／Stock／Purchase／Purchase Administrator 好幾個群組，等於一個人身兼多部門職能；真實公司裡採購、庫存、銷售通常是不同人/部門負責，Tryton 的群組機制本來就是設計來支援這種「職責分離」（Segregation of Duties, SoD）——不同部門的人只掛各自需要的群組，彼此不能越界操作
- **這門課的決定（2026-07-08）**：維持單一 `aaa` 累積所有操作型群組，不拆成 `aaa_purchase`／`aaa_stock`／`aaa_sales` 等多個帳號。理由：課程目標是讓一個學習者體會「一件事怎麼串起另一件事」（採購入庫 → 庫存 → 銷售 → 發票），拆多帳號會讓學習者每個 Day 都要切換登入身份，徒增操作成本，換不到等比例的學習價值——職責分離是**組織設計選擇**，不是 Tryton 技術上非如此不可
- **未來真的要導入給客戶時的考量**：真實導入專案應該依照客戶實際的部門/職掌拆分使用者與群組，讓「建採購單的人」跟「核准/Process 讓它真正生效的人」是不同角色（甚至可以用 `ir.model.button-res.group` 這種按鈕層級的權限，把「建單」和「核准」拆給不同的人，形成內控意義上的雙簽/覆核機制），而不是像這門課一樣讓單一帳號從頭做到尾

---

## Day 3 前置（admin 部分）：`aaa` 加入 Stock 群組

- 狀態：✅ 完成（2026-07-07，psql 複查）
- 原因：查了 `ir_model_access` 表，`stock.inventory`／`stock.move`／`stock.shipment.internal` 這三個 Day 3 會用到的 model，無 Group 的預設權限是**全擋**（`perm_read/write/create/delete` 全部 `false`），必須掛 **Stock** 群組（`res_group` id=10）才能操作；`stock.location` 無 Group 預設是**唯讀**，要編輯倉庫/儲位結構才需要更高權限的 **Stock Administration** 群組（id=11）
- **不用掛 Stock Administration**：查了 `stock_location` 表，這個環境的 Warehouse／Location 結構其實在 `stock` 模組啟用時就自動產生好了（見下方「環境現況」），書店這種單一門市情境直接沿用即可，`aaa` 不需要編輯 Location，掛 **Stock** 群組（一般操作）就夠
- 選單路徑：Administration ‣ User ‣ Users → `aaa` → Access Permissions 分頁 → 勾選 **Stock** → 存檔

**環境現況（psql 複查，2026-07-07）：`stock_location` 已有預設結構，不用重建**

| id | name | code | type | parent |
|----|------|------|------|--------|
| 5 | Warehouse | WH | warehouse | — |
| 1 | Input Zone | IN | storage | 5 |
| 3 | Storage Zone | STO | storage | 5 |
| 2 | Output Zone | OUT | storage | 5 |
| 4 | Lost and Found | — | lost_found | — |
| 6 | Supplier | SUP | supplier | — |
| 7 | Customer | CUS | customer | — |
| 8 | Transit | — | storage | — |

📸 `day3-admin-01-aaa-stock-group.png`（Access Permissions 分頁，Stock 已勾選）

**執行結果（psql 複查，2026-07-07）**：`res_user-res_group` 查到 `aaa` 現有 2 筆——`group=8`（Product Administration）、`group=10`（Stock）。

---

## Day 4 前置（admin 部分）：啟用 sale 模組

- 狀態：✅ 完成（2026-07-09，psql 複查）
- 實際走的路徑：跟 Day 2 啟用 `purchase` 完全一樣：Administration ‣ Modules，勾選 `sale` → 按 **ACTIVATE**（狀態變成 `To be activated`）→ 按下方 **APPLY** → 跳出「Perform Pending Activation/Upgrade」精靈 → **START UPGRADE**
- 📸 `day4-admin-01-sale-module-activate.png`（勾選 sale，尚未按 Apply）

**執行結果（psql 複查 `ir_module`，2026-07-09）**

- `sale`：`activated`
- **這次沒有連鎖啟用任何新模組**——跟 Day 2 啟用 `purchase` 時意外多啟用 `account_invoice_stock` 不一樣。查了 `sale` 的 `tryton.cfg`，它依賴的 `account`／`account_invoice`／`account_invoice_stock`／`account_product`／`company`／`country`／`currency`／`ir`／`party`／`product`／`res`／`stock` **在啟用前就已經全部是 `activated`**（Day 2 啟用 purchase 時已經帶進 `account_invoice_stock`），所以這次啟用沒有新的依賴鏈要補
- 這也再次印證「模組依賴鏈是否連鎖啟用」純粹取決於當下環境已經裝了什麼，不是每個模組都會意外多裝東西，要實際查 `ir_module` 表才知道，不能憑經驗猜

---

## Day 4 前置（續）：`aaa` 加入 Sales／Sales Administrator 群組

- 狀態：✅ 完成（2026-07-09，psql 複查）
- 原因：查了 `ir_model_access`，`sale.sale` 有一筆 `group=NULL` 的規則把預設權限全部設成 `false`，必須掛 **Sales** 群組（`res_group` id=16）才能建立/編輯銷售單；另外查了 `ir_model_button`／`ir_model_button-res_group`，`sale.sale` 的按鈕權限跟 Day 2 的 `purchase.purchase` **完全對稱**：

  | 按鈕 | 需要的群組 |
  |---|---|
  | Cancel／Draft／Quote／Confirm／Modify Header | 無 |
  | **Process** | **Sales Administrator**（獨立限定） |
  | Manual Invoice | Sales, Accounting |
  | Manual Shipment | Sales, Stock |

  要跑完整流程（含 Process，會產生 Invoice／Customer Shipment），`aaa` 需要同時掛 **Sales**、**Sales Administrator** 兩個群組——跟 Day 2 的 Purchase／Purchase Administrator 是同一套設計模式
- 選單路徑：Administration ‣ User ‣ Users → `aaa` → Access Permissions 分頁 → 勾選 **Sales**、**Sales Administrator** → 存檔
- 📸 `day4-admin-02-aaa-sales-groups.png`（Access Permissions 分頁，Groups 清單顯示 7 筆，含 Sales／Sales Administrator）

**執行結果（psql 複查，2026-07-09）**：`res_user-res_group` 查到 `aaa` 現有 **7 筆**群組——`group=8`（Product Administration）、`group=9`（Account Product Administration）、`group=10`（Stock）、`group=14`（Purchase）、`group=15`（Purchase Administrator）、`group=16`（Sales）、`group=17`（Sales Administrator）。

---

## Day 5 前置（admin 部分）：`aaa` 加入 Accounting 群組

- 狀態：✅ 完成（2026-07-13，psql 複查）
- 原因：`aaa` 目前完全沒有 Accounting 相關群組（現有 7 筆群組是 Product Administration／Account Product Administration／Stock／Purchase／Purchase Administrator／Sales／Sales Administrator），導致兩層都卡住：
  1. **選單層級被擋**：「Financial」最上層選單（`ir_ui_menu` id=71，Invoices／Supplier Invoices／Customer Invoices 都掛在它底下）被 `ir_ui_menu-res_group` 限制成只有 **Accounting**（id=6）或 **Accounting Administration**（id=7）才看得到——這是這門課第一次遇到「權限限制掛在最上層父選單，而不是個別葉節點選單」的案例，跟 Day 2／Day 4 的 Purchase／Sales（限制直接掛在 model access，選單本身沒設限）不一樣，值得記一筆
  2. **model 層級權限也不夠**：查了 `ir_model_access`，`account.invoice` 對 Purchase（14）、Sales（16）群組都只給 `perm_read=true`（唯讀），只有 **Accounting** 群組才有完整 CRUD（`perm_read/write/create/delete` 全部 `true`）。也就是說就算選單看得到，沒有 Accounting 群組也無法 Post、無法登錄付款
- 查了 `ir_model_button`／`ir_model_button-res_group`，`account.invoice` 的按鈕權限跟 Day 2／Day 4 發現的模式一致，只有 **`process`** 這顆特別限定：

  | 按鈕 | 需要的群組 |
  |---|---|
  | Draft／Cancel／Validate／Post／Pay／Reschedule／Delegate | 無（只要有 Accounting 群組的 model 層級權限就能點） |
  | **Process** | **Accounting Administration**（獨立限定） |

- **結論**：這門課 `aaa` 只需要 Post 發票、登錄收付款，不會用到 `account.invoice` 的 Process 按鈕，所以只需要加入 **Accounting** 群組，不需要 **Accounting Administration**（那是給要設定 Chart of Accounts／Fiscal Year／Tax／Payment Term／Journal 這類公司層級會計設定的人用的，查了 `ir_model_access` 對 group=7 的規則證實這點，概念上等同 Purchase Administrator／Sales Administrator 的定位——都是「日常操作」vs「批次覆核／設定」的分工）
- 選單路徑：Administration ‣ User ‣ Users → `aaa` → Access Permissions 分頁 → 勾選 **Accounting** → 存檔
- 📸 `day5-admin-01-aaa-accounting-group.png`（Access Permissions 分頁，Groups 清單顯示 8 筆，含 Accounting）

**執行結果（psql 複查，2026-07-13）**：`res_user-res_group` 查到 `aaa` 現有 **8 筆**群組——`group=6`（Accounting）、`group=8`（Product Administration）、`group=9`（Account Product Administration）、`group=10`（Stock）、`group=14`（Purchase）、`group=15`（Purchase Administrator）、`group=16`（Sales）、`group=17`（Sales Administrator）。

---

## Day 5 前置（續）：建立 Invoice Payment Method（`aaa` 這邊 PAY 按鈕不會出現）

- 狀態：⬜ 待做
- 原因：`aaa` 把採購發票 Post 完之後，發票的 **Payment** 分頁只顯示 Payment Term 算出來的到期日／金額（`Lines to Pay`），實際登錄付款用的 **PAY** 按鈕完全沒有出現——查了 `account_invoice/invoice.py` 的 `get_has_payment_method()`：Pay 按鈕要出現，前提是 `account.invoice.payment.method` 這張表**至少要有一筆**符合條件的紀錄（`debit_account`／`credit_account` 都不等於這張發票所屬的 account）；psql 查證這個環境的 `account_invoice_payment_method` 目前是 **0 筆**，從頭到尾沒人設定過，所以 Pay 按鈕整個被隱藏，不是 aaa 權限不夠
- 查了 `ir_model_access`，`account.invoice.payment.method` 只有 **Accounting Administration** 群組（id=7）能建立/編輯，**Accounting** 群組（aaa 現有的）沒有——這是繼「Chart of Accounts／Fiscal Year／Tax／Payment Term／Journal」之後，又一個歸在 Accounting Administration 底下的「公司層級會計設定」，必須由 admin 執行
- 環境現況（psql）：這個環境已經有現成的資源可以直接拿來設定，不用整個從零建：
  - `account_journal`：id=3「Cash」（type=cash）
  - `account_account`：id=35「Cash and Cash Equivalents」
- 選單路徑（psql 查 `ir_action_keyword`／`ir_ui_menu` 覆核，原先寫的「Invoices ‣ Payment Methods」是錯的，已更正）：Financial ‣ Configuration ‣ **Journals** ‣ **Invoice Payment Methods** → 新增一筆，Journal 選 **Cash**，Debit Account／Credit Account 都選 **Cash and Cash Equivalents** → 存檔
  - 📸 `day5-admin-02-financial-configuration-menu-tree.png`（admin 截圖 Configuration 選單樹，用來確認「Invoice Payments」資料夾底下只有 Payment Terms／Payment Means Rules，Invoice Payment Methods 其實在「Journals」資料夾底下）

---

## Day 5｜會計閉環（admin 視角要看的報表）

- 狀態：⬜ 待做
- 損益表 / 資產負債表選單路徑：待實測後補上

## Day 6｜`ir.model` 探索

- 狀態：⬜ 待做
- 這一段其實可以直接用 psql 查 `ir_model` / `ir_model_field` 表更快，見 [`automation-notes.md`](automation-notes.md)
