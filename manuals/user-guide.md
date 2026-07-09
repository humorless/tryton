# Ordinary User 操作手冊

給「日常操作 ERP」的人看：下單、出入庫、開發票、收付款。對照 [`admin-guide.md`](admin-guide.md)（admin 設定）與 [`../docs/business_flow.md`](../docs/business_flow.md)（整體課程）服用。

> ✅ （2026-07-06 更新，已實測＋查證）`aaa` 帳號已建立（`res_user` id=3，見 [`admin-guide.md`](admin-guide.md) Step 6）。查了 `ir_model_access` 表發現：`party.party` 完全沒有限制規則（預設全開放，`aaa` 可正常新增/編輯 Party），但 `product.template` 有規則：無 Group 的基礎權限是 `read only`，只有 **Product Administration** 群組才有 create/write/delete。**目前已把 `aaa` 加進 Product Administration 群組**（`res_user-res_group` 查到 user=3／group=8 一筆），所以 Step 2（Party）與 Step 3（Product）現在都可以直接用 `aaa` 操作，不會卡權限。

## 前置需求檢查表

跑這份文件前，對照 [`admin-guide.md`](admin-guide.md) 確認以下已完成，否則會卡關：

| 前置條件 | 狀態 |
|---------|------|
| Company 已建立且設為 Current Company | ✅ 已完成（REPLWARE Co., Ltd., id=1） |
| Chart of Accounts 已建立 | ✅ 已完成（Universal 範本，135 筆科目） |
| Fiscal Year + Period 已建立 | ✅ 已完成（2026 全年 12 個月 Period） |
| ordinary user 帳號已建立 | ✅ 已完成（`aaa`，已加入 Product Administration 群組，已實測登入可見 Parties/Products 選單） |
| `aaa` 加入 **Stock** 群組（Day 3 前）| ✅ 已完成（2026-07-07，psql 複查，見 [`admin-guide.md`](admin-guide.md) 「Day 3 前置」） |
| `purchase` 模組（Day 2 前）/ `sale` 模組（Day 4 前）已啟用 | ⬜ 待 admin 完成 |

> **順序更正（2026-07-07）**：原本 Day 2 是庫存盤點、Day 3 是採購，現在對調——Day 2 改採購到入庫、Day 3 改庫存盤點。原因：一個全新環境裡 Day 1 建的 Product 只是型錄資料，沒有真實庫存；庫存操作（Internal Shipment）要「搬東西」，但沒有先跑過採購入庫的話，Input Zone 是空的，實測時會在 Assign 這步卡關（"Unable to assign these products"）。對調後 Day 3 開始操作時，Input Zone 已經有 Day 2 採購入庫的真實庫存，不用另外想辦法生出庫存數字，也更貼近真實商業邏輯（先進貨才有貨可以搬/盤）。

---

## Day 1｜介面導覽 + 建立 Party / Product

### Step 1：介面導覽（1hr）

- 狀態：✅ 完成（2026-07-06）——List View ↔ Form View 切換、排序/篩選、breadcrumb 多層導覽都實測過一輪，沒有卡關
- 目標：搞懂 Menu、Form View、List View 長什麼樣子
- 已實測：`aaa` 登入後左側選單可見 **Parties**（Parties/Identifiers/Addresses/Contact Mechanisms/Categories）、**Hello World**（自訂模組）、**Products**（Products/Categories/Reporting），確認一般使用者不需要掛 Group 就能看到這些基礎選單（見上方前置需求檢查表的說明）
- 📸 `day1-user-01-aaa-login-menu.png`（aaa 登入後的選單全貌）
- **狀態機（draft → confirmed → done）延後到 Day 2／Day 4 處理**：查了 `party_party`、`product_template` 兩張表都**沒有 `state` 欄位**，代表 Day 1 這兩個 model 本來就沒有工作流程狀態可以練習；等 Day 2（Purchase Order，2026-07-07 已將原 Day 3 對調到 Day 2）／Day 4（Sale Order）建出真正的單據，才有 draft/confirmed/done 這類狀態機可以實際操作觀察，屆時再補這部分的說明與截圖

**實測發現（2026-07-08，補充）：工具列圖示看不出來的操作，去麵包屑下拉選單找**

- 現象：工具列上一整排小圖示（New／Save／Reload／Duplicate／Delete...）只有圖示沒有文字，特別是 **Delete**（垃圾桶圖示）夾在中間很容易漏看，一度以為某些 entity 沒有刪除功能
- **解法：點畫面左上角麵包屑最後一段旁邊的小箭頭**（例如 `Products / Configuration / Units of Measure / Categories ⌄`）——這會展開一個**完整文字版選單**，把工具列圖示全部重複列一次、外加文字說明：Switch／Previous／Next／Search／New／Save／Reload/Undo／Duplicate／**Delete**／View Logs／Attachment／Note／Action／Relate／Print／Email／Export／Import／Close Tab
- 📸 `day1-user-06-breadcrumb-dropdown-menu.png`（Categories 清單，麵包屑下拉選單展開，紅框標出 Delete 位置）
- **這是通用操作，任何 model 的 List／Form 畫面都適用**——不管是 Party、Product、之後的 Purchase／Sale／Shipment，只要找不到工具列上的圖示對應什麼功能，就點這個下拉選單看文字版，比用眼睛在小圖示堆裡辨認可靠很多
- 這也解釋了 Day 3 卡關的「風車圖示」：那其實也是同一個下拉選單機制裡的 **Action** 項目（查 `tab.js` 的 `menu_def()`，`icon: 'tryton-launch', label: 'Action'`），只是碰巧圖示長得像四色風車；有工作流程狀態的 model（例如 Shipment）點開後，選單內容會換成該狀態能做的動作（Cancel／Wait／Assign 之類）

**實測發現（2026-07-08，補充）：有工作流程狀態的表單，狀態機按鈕其實直接顯示在表單最下方，比 Action 選單更好找**

- 現象：Day 2 建 Purchase Order（Draft 狀態）時發現，表單最下方除了 Shipments／Invoices／Returns 這種關聯統計數字，還有一排**文字＋圖示的按鈕**：Cancel／Modify Header／Quote——不用點開任何下拉選單，直接就看得到、點得到
- 📸 `day2-user-03-purchase-quote-button.png`（Purchase Order Draft 表單下方按鈕列，紅框標出 Quote）
- **這才是找狀態機動作更直覺的地方**：Day 3 Internal Shipment 那次是靠點開風車圖示（Action 選單）才找到 Cancel／Wait，但其實同一組按鈕，很多有狀態機的表單（Purchase／Sale／Shipment...）會**直接把目前狀態下可以按的按鈕，用文字按鈕的形式放在表單最下方**，Action 選單裡的版本只是備援／不佔表單版面的另一種呈現方式而已——**以後遇到有狀態機的單據，先往表單最下面看，通常比點開 Action 選單快**

**實測發現（2026-07-08，補充）：反覆新增/刪除 Category，新記錄的 id 一直增加、不會重複利用**

- 現象：練習新增/刪除 Units of Measure 的 Category 時，發現新建記錄的 `id` 越來越大，刪掉的號碼沒有被回收再利用
- **查證（psql）**：`product_uom_category` 表目前只剩 7 筆（id 1~7），但底層自動遞增序列 `product_uom_category_id_seq` 的 `last_value` 已經是 10——代表 8、9、10 這幾個號碼已經被用掉（含練習時建立又刪除的 `Box`），刪除並不會把號碼還給序列
- **本質**：這裡的 `id` 是 PostgreSQL 的 **identity/serial 遞增序列**，設計哲學是「只往前走，永不回頭」——不管記錄後來有沒有被刪除、甚至有沒有真的存檔成功，序列的計數器都不會倒退。這是資料庫層級保證「id 一定唯一」最簡單的做法，回收號碼反而複雜且沒必要，因為 `id` 本來就只是給機器用的技術性主鍵，從來沒打算給人看、也沒打算連續無缺口
- **跟 `ir.sequence` 的對比（呼應 Day 1／Day 3 學過的概念）**：`ir.sequence`（Shipment number、Invoice number 那些）目的完全不同——它是刻意設計成「業務單據的人類可讀編號」，因為要給人看、要對外溝通，才特別設計成「離開 Draft 才給號」這種避免產生解釋不了的缺口的機制；`id` 從來不追求這個目標，出現缺口是正常且無害的。這次親眼看到的現象，正是「`id` 只是技術主鍵、可以有缺口」這個概念的具體實例

**概念筆記（2026-07-08，Day 2 討論後回填）：Tryton 的 `state`／`Workflow` 到底在對應什麼商業概念？是不是所有 ERP 都有這個？**

這幾則是 Day 2 建 Purchase Order、卡在 Quote／Confirm／Process 這幾個狀態機按鈕時討論出來的，但概念是通用的，先寫在 Day 1 這裡，之後每個有 `state` 的 model 都可以回頭參照。

- **核心心智模型：`state` 欄位＝「這個 model 是不是一份會隨時間推進的商業文件」**。看到一個 model 有 `state` 欄位，就代表它在模擬某種「商業文件的生命週期」（草稿 → 提案 → 正式生效 → 執行 → 完成）；沒有 `state` 的 model（例如 Party／Product），通常代表它是靜態的主檔資料——「誰是誰、這是什麼商品」本身沒有生命週期可言，不會過期、不會走完流程
- **這個對應解釋了我們一路查到的好幾個細節，不是巧合**：
  - 單號（`ir.sequence` 給的 `number`）通常在離開 Draft 那一刻才出現——草稿階段這東西還不算「真正存在的文件」，要送出去（Quote）或正式生效才算文件誕生，才需要可追溯的編號
  - 欄位的 readonly／required 會隨狀態改變（例如 Purchase 的 Payment Term 在 Confirmed 後鎖死）——對應「文件生效後，關鍵條款不能再改」的現實合約概念
  - Party／Product 沒有 `state` 欄位——因為它們是主檔資料，不是文件
- **狀態機本身不是 Tryton 獨創的概念，幾乎所有正經的 ERP 都有**——SAP 有 Status Management、Odoo（跟 Tryton 同源，都源自早期 TinyERP/OpenERP）也是用 state 欄位＋按鈕驅動、NetSuite／Dynamics 也都有單據狀態的概念，這是 ERP 處理「商業文件生命週期」的業界標準做法
- **查了官方文件**（[Define workflow — Tryton server](https://docs.tryton.org/8.0/server/tutorial/module/workflow.html)）：Tryton 真正比較特別的地方，是把這個模式做成**框架層級的一等公民**——抽成一個通用的 `Workflow` mixin class，搭配 `_transitions`（明確定義哪些狀態可以轉去哪些狀態，不合法的轉換直接被擋）跟 `@Workflow.transition()` decorator，讓**每個模組都用同一套機制**，不是每個開發者各自寫一套 if/else 判斷狀態的土砲邏輯。這種**跨模組的一致性跟紀律**，才是文件強調的「特色」，而不是「狀態機」這個概念本身
- **實務上會不會太複雜／over-engineered？**：核心的多階狀態機本身不算太重——不強迫你真的花時間停留在每一階，Quote 完可以馬上接著 Confirm，操作成本沒有比一鍵下單高多少；但像 Process 需要額外的 Purchase Administrator 群組、`invoice_party` 這類服務大型/跨組織採購的彈性欄位，對小規模貿易（例如書店）確實是用不到的複雜度，這是 ERP 類通用軟體常見的取捨：通用性換來的代價是小公司要多認識幾個用不到的概念，好處是公司真的成長到需要職責分離/正式簽核時，不用換系統

### Step 2：建立 Party（廠商＋客戶）

- 狀態：✅ 完成（2026-07-06，psql 複查）
- 選單路徑：Party ‣ Parties → New
- 建了 2 筆：`test supplier`（Day 2 採購用）、`test customer`（Day 4 銷售用）
- 📸 `day1-user-02-party-list.png`（Parties 清單，`aaa` 登入下可見 3 筆：公司本身 + 新建的供應商/客戶）

**執行結果（psql 複查，2026-07-06）**

| id | code | name | create_uid |
|----|------|------|------------|
| 2 | 2 | test supplier | 3（`aaa`） |
| 3 | 3 | test customer | 3（`aaa`） |

確認兩筆都是用 `aaa` 身份建立，驗證「Party 建立不需要額外 Group」的判斷成立。

### Step 3：建立 Product（含 UoM）

- 狀態：✅ 完成（2026-07-06，psql 複查，以書店情境為例）
- **前置**：✅ 已完成（2026-07-06，psql 複查）—— `aaa` 已加入 **Product Administration** 群組（`res_user-res_group` 查到 user=3／group=8 一筆），Product 建立不會再卡權限
  - 📸 `day1-admin-22-aaa-access-permissions.png`（Users ‣ aaa ‣ Access Permissions 分頁，Groups 清單已列出 Product Administration）
- 選單路徑：Products ‣ Products → New
- 填寫欄位：Name、Type（Goods）、Default UOM（建議選 Units ‣ Unit，除非商品真的需要長度/重量單位）、Code（自訂編號，選填但建議填）
- **Account Category（2026-07-08 二次更正，這次是實測證實的）**：這裡原本寫「可以先留空，Tryton 找不到 Product 專屬科目時會退回用公司預設值」——**這個判斷是錯的**，Day 2 實測 Purchase Process 時真的踩到了（見 Day 2 Step 2 概念筆記「Day 1『Account Category 可以留空』的判斷需要更正」）。正確理解：`account_configuration_default_account` 的公司層級預設值，只是「新建 Category 時拿來預填欄位」用的，不是 runtime 後備方案；**只要 Product 掛了 Category，那個 Category 自己就必須勾 Accounting、填好 Expense/Revenue Account**，不然一旦要幫這個商品產生發票分錄就會直接報錯（`AccountError: There is no "Account Category" defined for ...`），不會自動退回公司預設
- UoM 概念：`product_uom` 依 Category 分組（Units/Length/Weight/Volume/Surface/Time/Energy），**同 Category 內的單位可以互相換算**（例如箱↔顆），這是 UoM Category 存在的意義；跨 Category 不能轉換
- 📸 `day1-user-03-product-form.png`（書店範例：`從試算表到資料平台`／Code `bk001`／List Price 680／Cost Price 240／ISBN Identifier）

**概念筆記：Template 與 Variant（product.template vs product.product）的關係**

中文怎麼翻：查了 `ir_translation` 表裡 Tryton 官方語言包的翻譯（zh_CN，`Variant` → `变体`），**Template＝模板，Variant＝變體**，這是 Tryton 官方的翻法，不是自己隨便選的用詞，以下對照表統一用「模板／變體」。

Tryton 把「一個 Product」拆成兩層資料，畫面上合併顯示成一張表單，容易誤以為只有一層：

| | 模板 Template（`product.template`） | 變體 Variant（`product.product`） |
|---|---|---|
| 存放欄位 | Name、Type、Default UOM、Account Category、**List Price（可設預設值）** | Code、Description、**List Price（留空則繼承模板）**、**Cost Price（一定要在這層填，模板層只顯示唯讀彙總）**、Identifiers（ISBN／條碼掛在這層） |
| 關係 | 一個模板可以有多個變體（`product_product.template` 是 FK） | 每個變體一定屬於一個模板 |
| 這個環境的實況 | — | `product_attribute` 模組**未啟用**，沒有顏色/尺寸這類「屬性」可以自動展開多個變體，所以目前**一個模板對應一個變體**，等於一比一 |
| 何時才需要手動加第二個變體 | — | 同一本書要分「精裝版／平裝版」這種**書名/作者共用、但 Code／ISBN／價格要分開**的情境，才手動在 Variants 面板按 ＋ 加第二筆 |

**概念筆記：為什麼 Cost Price 一定要掛在變體（Variant）上，不能掛在模板（Template）上**

查了 `stock_move`（出入庫紀錄）的 schema，關鍵證據：`stock_move.product` 這個外鍵指向的是 **`product_product`（變體）**，不是 `product_template`（模板），而且 `stock_move` 表自己還有一欄 `product_cost_price`，用來在每次出入庫當下 snapshot 那個變體的成本。

- **模板是抽象概念，變體才是「真實存在、會被搬動的那個東西」**——模板代表的是「這一款商品」的共用定義（書名/作者/出版社），本身不會被領用、不會被搬到倉庫貨架上；出入庫紀錄、進貨單、庫存數量全部都是綁在變體上
- **Cost Price 的本質，是「取得/製造這一件具體商品，實際花了多少錢」**，這個問題只有對著一個具體的、可以被搬動計價的東西才有意義。同一個模板底下如果有兩個變體（例如精裝版 vs 平裝版），製作成本本來就不一樣，硬要把成本設在模板層讓兩個變體共用，反而會算錯庫存價值跟毛利
- 相對地，**List Price 是「你打算賣多少錢」的商業決策，不是物理事實**，可以先在模板層設一個共用建議售價、各變體要覆寫再自己填——這是為什麼只有 List Price 有「模板預設、變體繼承」機制，Cost Price 沒有
- 一句話總結：**List Price 問的是「你想賣多少」，可以套模板；Cost Price 問的是「這件實體東西花了多少成本」，只能問變體本身**

**概念筆記：Category／Template／Variant 三層，到底哪一層才是「書」這個抽象概念**

容易搞混的地方：Template 感覺像是「一種商品的抽象定義」，那「書」這個抽象概念是不是該設成 Template？——**不是**，關鍵限制在於 `product_product`（Variant）的欄位：`id, code, description, position, suffix_code, template, active`，**沒有 `name` 欄位**，Variant 在畫面上顯示的名稱永遠繼承自它所屬的 Template。

這代表如果把 Template 設成「書」（抽象概念），店裡每一本具體的書都會變成同一個 Template 底下的 Variant，清單裡每一本書的 Name 都會顯示同一個字「書」，分不出哪本是哪本——這樣不對。「書」這種抽象分類，其實對應到 Tryton 裡**第三個模型：`product.category`**（Product Category），跟 Template／Variant 是分開的三層：

| 層級 | 對應到什麼 | 書店範例 |
|---|---|---|
| **Category**（`product.category`） | 抽象分類，主要拿來做財務分類/報表分組（`product_category_account` 表可以幫一個 Category 指定專屬的收入/費用科目，見 Step 3 前面的 Account Category 說明） | 「書籍」、「文具」——用來把「書籍銷售」跟「文具銷售」的營收分開記帳/報表 |
| **Template**（`product.template`） | **一本具體的書**，一個書名一個 Template | 「原子習慣」、「被討厭的勇氣」各自是一個 Template |
| **Variant**（`product.product`） | 同一本書底下真正可購買/可入庫的單位，通常 1:1；只有真的需要分開追蹤 Code/ISBN/價格時才拆多個 | 「原子習慣（精裝版）」vs「原子習慣（平裝版）」才需要兩個 Variant |

已建的 `bk001`／「從試算表到資料平台」這個 Template，設計上是對的——**Template = 某一本具體的書**，ISBN 掛在它底下的 Variant 上也是對的。如果之後想把「書籍」跟其他商品類別在財務報表上分開，才需要再去 Products ‣ Categories 建一個 Category「書籍」，然後把這些書的 Template 都指定過去。

**實測驗證（2026-07-06）**：一開始在 Variants 面板編輯 Cost Price 時，誤按到面板工具列上的**垃圾桶（刪除）圖示**，把整筆 Variant 存檔刪掉了——因為 Identifier／Cost Price 都掛在 Variant 底下（FK 對到 `product.product`，不是 `product.template`），Variant 一被刪，這兩個資料跟著 CASCADE 消失，但 **Template 本身還在**（`product_template` 沒被刪，只是底下的 Variant 空了）。這證實了「Template 是殼、Variant 才是真正掛資料的那一層」，操作 Variants 面板時要注意別點錯圖示。

**執行結果（psql 複查，2026-07-06，修復後）**

| 表 | 欄位 | 值 |
|---|---|---|
| `product_template` | id / name / code / type | 1 ／ 從試算表到資料平台 ／ bk001 ／ goods |
| `product_product`（Variant，第 2 次建立） | id / template / code | 2 ／ 1 ／ bk001 |
| `product_list_price` | template=1, product=NULL, list_price | 680（Template 預設值，Variant 留空繼承這個） |
| `product_cost_price` | product=2, cost_price | 240（只存在 Variant 層，Template 層是唯讀彙總） |
| `product_identifier` | product=2, type, code | isbn ／ 9786267757284 |

### Step 3b（延伸）：建立 Product Category（書籍）

- 狀態：✅ 完成（2026-07-06，psql 複查）
- 選單路徑：Products ‣ Categories → New
- 填寫內容：Name=`書籍`、Code=`book`、**Accounting 不勾**（走公司預設收入/費用科目，見上方「Category／Template／Variant 三層」概念筆記）、Parent 留空（頂層分類）
  > ⚠️ **更正（2026-07-08，Day 2 實測發現這個判斷是錯的）**：「不勾 Accounting 會自動走公司預設科目」並不成立，Day 2 跑 Purchase 的 Process 時就是卡在這裡（`AccountError: There is no "Account Category" defined for...`）。已經回來把這個 Category 的 **Accounting 補勾起來**，並設定 Account Expense=`5.2.1`、Account Revenue=`4.1.1`；另外 `bk001` 自己的 **Account Category** 欄位（`product.template.account_category`，是跟這裡的分類 `product_template-product_category` 不同的獨立欄位）當時也沒有一併設定，一併補上指向「書籍」。完整原因、查證過程、修正步驟見 Day 2 Step 2 的兩則概念筆記（「Day 1『Account Category 可以留空』的判斷需要更正」、「`bk001` 的『分類』跟『記帳用的 Category』其實是兩個獨立欄位」）
- 用表單裡的 **+ ADD PRODUCTS** 按鈕把已建立的 `bk001` 掛進這個分類（精靈視窗選好後要先存精靈，再存 Category 本身，兩層都要存）
- 📸 `day1-user-04-category-form.png`（Category 表單，Name/Accounting/Parent）
- 📸 `day1-user-05-category-add-products.png`（Add products 精靈，`bk001` 已加入清單）

**執行結果（psql 複查，2026-07-06）**

| 表 | 欄位 | 值 |
|---|---|---|
| `product_category` | id / name / code / accounting / parent | 1 ／ 書籍 ／ book ／ false ／ NULL（頂層） |
| `product_template-product_category` | category / template | 1 ／ 1（`bk001` 已掛進「書籍」分類），create_uid=3（`aaa`） |

**執行結果更新（psql 複查，2026-07-08，Day 2 補修正後）**

| 表 | 欄位 | 值 |
|---|---|---|
| `product_category` | id / accounting | 1 ／ **true**（原本 false，已更正） |
| `product_category_account` | category / account_expense / account_revenue | 1 ／ 112（5.2.1）／ 99（4.1.1） |
| `product_template` | id / account_category | 1（`bk001`）／ **1**（書籍，原本是 NULL，這是獨立於上面 `product_template-product_category` 之外的欄位，當時沒有一併設定） |

---

## Day 2｜採購到入庫

- 狀態：🔄 進行中（2026-07-08）
- **順序更正（2026-07-07）**：這裡原本排在 Day 3，現在對調到 Day 2——先跑通採購入庫，Day 3 的庫存操作（Internal Shipment）才有真實庫存可以搬，詳見上方前置需求檢查表下的說明
- **前置**：✅ 已完成——admin 已啟用 `purchase` 模組、`aaa` 已加入 **Purchase** 群組（見 [`admin-guide.md`](admin-guide.md)「Day 2 前置」與「Day 2 前置（續）」）

### Step 1：設定供應商（`test supplier`）的 Payment Term

- 狀態：✅ 完成（2026-07-08，psql 複查）
- 選單路徑（已實測）：Party ‣ Parties → `test supplier` → **Accounting** 分頁 → Payment Terms
- 📸 `day2-user-01-party-accounting-tab.png`（Accounting 分頁，Customer Payment Term／Supplier Payment Term 兩欄皆空，填寫前）

**執行結果（psql 複查 `party_party_payment_term`，2026-07-08）**：`test supplier`（party id=2）的 `supplier_payment_term` 已指向 `Net 30 days`。

**概念筆記：Customer Payment Term 跟 Supplier Payment Term 差在哪？**

- 查了 `trytond/modules/account_invoice/party.py` 原始碼：`party.party` 上這兩個欄位都是獨立的 `Many2One('account.invoice.payment_term', ...)`，分別代表同一個 Party **當客戶**與**當供應商**時各自適用的付款條件
- 再查 `purchase.py`／`sale.py` 怎麼用這兩個欄位：建**銷售單**選這個 Party 時，`sale.py` 會自動帶入 **Customer Payment Term**；建**採購單**選這個 Party 時，`purchase.py` 會自動帶入 **Supplier Payment Term**——兩邊各自讀各自的欄位，不會互相干擾
- 之所以分開，是因為同一個 Party 在 Tryton 裡可以**同時身兼客戶跟供應商**（例如既跟某公司進貨、又賣東西給它），而談定的付款條件本來就不對稱——可能要求客戶「收到貨 30 天內付款」，自己付供應商卻是「月結 60 天」，兩組數字沒理由要一樣，所以拆成兩個獨立欄位
- `test supplier` 目前的角色是供應商，這裡應該填 **Supplier Payment Term**（例如 `Net 30 days`），**Customer Payment Term 留空**即可（除非之後也要反過來跟它進貨/賣貨給它，但目前情境用不到）

**概念筆記：內建的 `Net 30 days` 跟 `Net 30 days End of Month` 差在哪？**

- 查了 `account_invoice_payment_term_line_delta` 表兩筆的實際定義，並對照 `trytond/modules/account_invoice/payment_term.py`（用 `dateutil.relativedelta` 算到期日）：

  | | Net 30 days | Net 30 days End of Month |
  |---|---|---|
  | `days` | 30 | 30 |
  | `day`（月中第幾天） | 空 | **31** |

- **Net 30 days**：到期日＝發票日期 **+ 30 天**，就這樣，沒有其他調整
- **Net 30 days End of Month**：先一樣 **+ 30 天**，但多套一個 `day=31` 的 `relativedelta`——這是 `dateutil` 的標準寫法：`day=31` 代表「把日期釘死在當月的第 31 天」，如果那個月沒有 31 號（例如 4 月只有 30 天），`dateutil` 會自動夾到當月的**最後一天**。所以效果是「+30 天之後，再進位到那個月的月底」
- **實務意義**：`Net 30 days` 的到期日每次都精確落在「開票日 + 30 天」那一天，可能落在月中任何一天；`Net 30 days End of Month` 是很多企業慣用的「月結」條件——不管開票日是幾號，先抓 30 天的緩衝，但真正結帳日一定統一收斂在月底，方便會計對帳（每個月固定一天處理一批到期款項，不用每天零散追蹤不同到期日）

### Step 2：建立採購單

- 狀態：🔄 進行中（2026-07-08）——已推進到 Confirmed，待 Process（見下方「執行結果」，Confirm 本身不會自動產生 Supplier Shipment）
- 選單路徑（已實測）：**Purchase ‣ Purchases ‣ Purchases** → New → Party 選 `test supplier`（Payment Term 自動帶出 `Net 30 days`，驗證了下方的原始碼判斷）→ Lines 新增一行：Product=`bk001`、Quantity=10、Unit Price=200 → 存檔
- 📸 `day2-user-02-purchase-order-draft-form.png`（存檔後畫面：Number 空白、State=Draft、Invoice State/Shipment State 皆為 None、Total=TWD 2,000.00）

**執行結果（psql 複查，2026-07-08）**

| 表 | 欄位 | 值 |
|---|---|---|
| `purchase_purchase` | id / number / state / party / payment_term / warehouse / invoice_state / shipment_state | 1 ／ `NULL` ／ `draft` ／ 2（test supplier）／ 4（Net 30 days）／ 5（Warehouse）／ `none` ／ `none` |
| `purchase_line` | id / purchase / product / quantity / unit_price | 1 ／ 1 ／ 2（bk001 變體）／ 10 ／ 200 |

`number` 仍是空值——跟 Day 3 學過的 Sequence 概念一致：離開 Draft（按 Confirm）才會跟 `ir.sequence` 要號。

**概念筆記：Purchase Line 選的 Product，是「供應商的商品」還是「本公司的商品」？**

- 查了 `trytond/modules/purchase/purchase.py:1221`：`purchase.line.product` 欄位型別是 `Many2One('product.product', ...)`——跟 Day 1 建立 `bk001` 時用的**是同一個 model**，並不存在另一個「供應商的商品」資料表
- Tryton 的 Product（Template/Variant）代表「這個公司眼中，這件可以被交易的商品本身」，不綁定任何一個特定的交易對象（客戶或供應商）；跟 `test supplier` 買的書，跟之後賣給 `test customer` 的，是**同一個物理商品**，同一筆庫存記錄要能連續追蹤「供應商進來 → Storage Zone → 賣給客戶出去」，中間商品的身分必須是同一筆，不能因為交易對象換了就變成不同商品，否則庫存數量、成本追蹤全部會斷掉
- 一句話：**Product 是「東西是什麼」，Party 是「東西跟誰交易」，這是兩個獨立的維度**
- 如果真的需要記錄「供應商自己的商品編號/報價」，Tryton 有選用的 `purchase.product_supplier` model（查了 `purchase/product.py`），可以掛在 `bk001` 底下記錄該供應商專屬代號、最小訂購量、價格級距——這是進階/選用功能，不影響基本建單流程，這次沒有用到

**實測發現（2026-07-08）：Purchase Line 的 Product 欄位找不到 `bk001`**

- 現象：建 Purchase Order、Lines 分頁新增一行，Product 下拉/搜尋找不到 `bk001`（從試算表到資料平台）
- **根本原因**：查了 `purchase.line.product` 欄位的 `domain`：

  ```python
  domain=[
      If(Eval('purchase_state').in_(['draft', 'quotation']) & ~(Eval('quantity', 0) < 0),
          ('purchasable', '=', True),
          ()),
      ...
  ]
  ```

  Purchase Line 的 Product 下拉**只列出 `purchasable = True` 的商品**。再查 `product_template` 表：`bk001`（id=1）的 `purchasable` 欄位目前是空值（等同 `False`）
- **為什麼會這樣**：`purchasable` 是 `purchase` 模組替 `product.template` 新增的欄位；`bk001` 是 Day 1（`purchase` 模組還沒啟用前）建立的，當時這個欄位根本不存在，模組啟用後舊記錄就停在預設值 `False`，沒有人主動勾選
- **解除卡關的方式**：Products ‣ Products → 開 `bk001` → 存啟用 `purchase` 模組後新出現的 **Purchase** 分頁 → 勾選 **Purchasable**（可能連動要求填 **Purchase UOM**，通常跟 Default UOM 選一樣，例如 Units）→ 存檔；回到 Purchase Line 後 `bk001` 就能選到

**執行結果（psql 複查 `product_template`，2026-07-08）**：`bk001`（id=1）`purchasable=true`，`purchase_uom` 指向 `Unit`（跟 Default UOM 一致），卡關解除。

**概念筆記：填完 Quantity，Unit Price 是不是也一定要填？系統會自動帶出來嗎？**

- **技術上，Draft 階段不填也能存檔**：查了 `purchase.line.unit_price` 欄位的 `required` 條件：

  ```python
  'required': (Eval('type') == 'line') & Eval('purchase_state').in_(['confirmed', 'processing', 'done'])
  ```

  只有**離開 Draft、按下 Confirm** 之後才會強制要求填，Draft 階段存檔不會擋
- **但實務上一定要填，而且不會自動帶出來**：查了 `Product.get_purchase_price()`（自動抓價邏輯），依序會嘗試：① `purchase.product_supplier.price`（供應商專屬報價表，這個環境沒建過）② 這個供應商歷史上最後一次成交價（`get_last_purchase_price_uom`，目前一筆採購紀錄都沒有）③ `purchase_price_list` 模組的價目表邏輯（沒安裝）——三層都沒東西可以帶，`compute_unit_price()` 最終回傳 `None`，**Unit Price 不會自動填任何值**，必須手動輸入
- **這次填多少合理**：`bk001` 的 Cost Price 當初設的是 **240**（Day 1 建 Product 時填的），可以直接拿來當這次的採購單價；之後真的談定跟 `test supplier` 的實際進貨價，也可以補建 `purchase.product_supplier` 報價資料，之後系統就會自動帶出，不用每次手動輸入

**實測發現（2026-07-08）：Action 選單只有 Return Purchase／Cancel／Modify Header／Quote，沒有 Confirm**

- 現象：存檔後的 Purchase Order（Draft 狀態）點開 Action 選單，只看到這四個選項，找不到預期中的「Confirm」
- **根本原因**：查了 `trytond/modules/purchase/purchase.py` 的 `_transitions`／`_buttons`，這個模組的狀態機比想像中多一階，不是 `Draft → Confirmed`，而是 `Draft → Quotation → Confirmed → Processing → Done`。**Confirm 按鈕的顯示條件是 `state == 'quotation'`**，人還在 Draft，看不到很正常
- **四個選項各自的來源**：

  | 按鈕 | 來源 | 說明 |
  |---|---|---|
  | **Quote** | `purchase.py` 狀態機按鈕 | Draft → Quotation 的轉換按鈕，Draft 狀態下要點的就是它 |
  | **Cancel** | `purchase.py` 狀態機按鈕 | Draft／Quotation → Cancelled |
  | **Modify Header** | `purchase.py` 狀態機按鈕 | Draft 狀態下修改表頭用，不影響狀態 |
  | **Return Purchase** | 獨立 wizard（查了 `purchase.xml` 的 `ir.action.wizard`），不是狀態機按鈕 | 對供應商辦「退貨」的功能，任何狀態都會出現在 Action 選單裡，跟目前的建單流程無關 |

- **處理方式**：先點 **Quote**，狀態變成 Quotation 之後，Action 選單才會多出 **Confirm**
- **文件更正**：`business_flow.md`／`user-guide.md` 原本把 Day 2 流程簡化寫成「建單 → 確認」，漏講了中間的 Quotation 這一階，這裡補正確

**執行結果（psql 複查，2026-07-08）：點 Quote 之後**

- `purchase_purchase`：`state` 從 `draft` → `quotation`，**`number` 從 `NULL` 變成 `1`**——查了 `quote()` 方法原始碼，`cls.set_number(purchases)` 就掛在這個轉換裡呼叫，不是 Confirm，跟「離開 Draft 就給號」的判斷一致（Quote 本身就是離開 Draft 的動作）

**實測發現（2026-07-08）：點 Confirm 之後，Shipment State 還是 None，Supplier Shipment 沒有自動出現**

- 現象：按下 Confirm，`State` 變成 `Confirmed`，`Purchase Date` 自動補上今天日期，但 `Shipment State` 欄位還是顯示 `None`；psql 複查 `stock_shipment_in` 表也是 **0 筆**，還沒有任何 Supplier Shipment 產生
- 📸 `day2-user-04-purchase-confirmed-state.png`（Confirmed 狀態，表單下方按鈕變成 DRAFT／PROCESS）
- **根本原因**：查了 `purchase.py` 的狀態機按鈕，`Confirmed` 狀態下表單最下方出現的是 **PROCESS**（不是直接產生 Shipment）。再查 `process()` 方法：

  ```python
  def process(cls, purchases):
      ...
      cls._process_invoice(purchases)
      cls._process_fulfillment(purchases)
      ...
  ```

  真正「產生 Supplier Shipment（`_process_fulfillment`）」跟「產生發票（`_process_invoice`）」的動作，是掛在 **Process** 這個按鈕裡，不是 Confirm。Confirm 只是把單據鎖定、標記為已確認，本身不觸發任何庫存/會計的下游動作
- **完整狀態機更正**：`Draft → Quotation → Confirmed → Processing → Done`，其中 **Quote 給號**、**Process 才真正產生 Supplier Shipment**，跟原本 `business_flow.md` 寫的「建單 → 確認 → 系統產生 Supplier Shipment」又更精確一階——要點完 **Process** 才會看到 Shipment 出現

**概念筆記：Quote 跟 Confirm 這兩個動作，各自對應什麼商業意義？**

- 查了 `purchase.py` 裡幾個欄位在不同狀態下的 `readonly`／`required` 設定，這些差異就是兩個動作商業意義的具體線索：

  | 欄位 | Draft／Quotation | Confirmed 之後 |
  |---|---|---|
  | `payment_term` | 可改 | **鎖死不能改** |
  | `purchase_date`（實際採購日） | 可留白 | **變必填**（`confirm()` 會自動補今天日期） |
  | `quotation_expire`（報價有效期限） | 顯示、可填 | 欄位直接隱藏 |
  | `unit_price` | 不強制填 | **變必填** |
  | `invoice_address` | 不檢查 | Confirm 前置檢查：**沒填會擋下來** |

- **Quote（Draft → Quotation）＝「這份單子從『內部草稿』變成『正式要送出去的提案』」**：有 `quotation_expire`（報價有效期限）這個只在 Draft／Quotation 顯示的欄位，對應真實採購流程裡「跟供應商要報價，報價單通常有效期限只有幾天/幾週」的概念；這一步也才會產生單號（`quote()` 呼叫 `set_number()`），代表這份文件現在**有身份、可以被追蹤/引用**了。但條件還沒鎖死：Payment Term 可以改、Unit Price 甚至可以先不填——因為報價階段本來就還在跟供應商談，數字可能還會調整
- **Confirm（Quotation → Confirmed）＝「雙方（或內部）已經拍板，這筆採購變成真正的承諾」**：Payment Term 鎖死不能再改、Unit Price 變成強制要填、Invoice Address 沒填會直接擋下——這些都是「一旦要正式生效的合約，關鍵條款不能再模糊」的具體展現；`purchase_date` 在這一步變必填且系統自動補上今天日期，對應「這是真正下訂的那一刻」，不是報價/詢價階段
- **一句話總結**：Quote 是「我要跟供應商提案／詢價」，Confirm 是「這筆單已經談定、正式成交」——中間的空窗期，正好對應現實中「報價 → 議價/等供應商回覆 → 雙方拍板」這段時間差，Tryton 用兩個獨立狀態把這個時間差具體化，而不是一鍵直接下單

**概念筆記：Process 對應的商業意義**

- 查了 `process()` 方法：

  ```python
  def process(cls, purchases):
      ...
      cls._process_invoice(purchases)       # 依 invoice_method 產生發票
      cls._process_fulfillment(purchases)   # 產生 Supplier Shipment
      ...
  ```

- **Confirm 是「拍板、鎖定合約條款」，Process 是「把這份已經拍板的合約，正式送進『執行』的流程」**：
  - `_process_fulfillment`＝通知倉庫「這批貨要來了，準備收貨」——真正建立 Supplier Shipment 的動作，對應「訂單確認後，把資訊傳給收貨/倉儲部門」
  - `_process_invoice`＝依照談定的付款方式，決定現在要不要先開發票。查了 `invoice_method` 欄位，有三個選項：**Manual**（人工決定何時開）、**On Order**（下單當下就開，對應「先付款/預付訂金」）、**On Fulfillment**（等貨真正收到才開，對應「貨到才付款」）。這張單目前是 `order`，所以 Process 這一下 Invoice 應該會跟 Shipment 一起產生，不用等收貨
- **內控意義**：`process()` 一開始呼叫 `cls.lock(purchases)`，對這筆訂單上資料庫鎖，避免同一張單被重複執行兩次（重複收貨、重複開票）
- **為什麼狀態叫「Processing」不是直接跳「Done」**：Process 只是「正式放行去執行」，不是「完成」；真正的 Done 要等 Shipment／Invoice 這些下游東西都跑完才會自動發生（Tryton 沒有手動的 Done 按鈕，見官方文件 [Purchase Module usage — 8.0](https://docs.tryton.org/8.0/modules-purchase/usage/index.html)）

**概念筆記：Process 按鈕跟 `ir.queue`／`trytond-worker` 的關係**

- 現象：`aaa` 加完 Purchase Administrator 群組後，Process 按鈕從 disabled 變成可以點——這是即時生效的，不用重新登入
- **Confirm 那一刻其實已經自動把 Process 排進非同步佇列了**，查了 `confirm()` 原始碼：

  ```python
  for process_after, sub_purchases in groupby(purchases, lambda p: p.process_after):
      with transaction.set_context(queue_scheduled_at=process_after, ...):
          cls.__queue__.process(sub_purchases)
  ```

  代表在正常/正式部署的 Tryton 裡，Process 通常是 **Confirm 之後系統自動接著做**的，不需要人工再按一次
- **更正（2026-07-08，原本的判斷錯了）**：一開始以為「這個環境沒有 `trytond-worker`，所以排進佇列的 `process()` 任務永遠不會自動執行，只能手動點 Process」——這個結論**不對**。查了 `trytond/ir/queue_.py` 的 `push()`：

  ```python
  if not config.getboolean('queue', 'worker', default=False):
      transaction.tasks.append(record.id)
  ```

  再查 `trytond/protocols/dispatcher.py`，request 處理完、`transaction.commit()` 之後緊接著：

  ```python
  while transaction.tasks:
      task_id = transaction.tasks.pop()
      run_task(pool, task_id)
  ```

  也就是說：**沒有設定 `[queue] worker`（我們的 `trytond.conf` 確實沒有這段）時，任務並不會卡在佇列裡什麼都不做，而是會在同一個 request 結束、commit 之後立刻同步執行**——`trytond-cron`／`trytond-worker` 的有無，其實跟這次卡關無關
- **真正的根本原因（psql 複查 `ir_error` 表才發現）**：那個排進去的 `process()` 任務其實**真的有自動執行**，時間戳跟 `ir_queue` 的 `enqueued_at` 完全同一秒，但執行**失敗**了，錯誤被記進 `ir_error`（不會顯示在 Confirm 當下的畫面上，因為這是巢狀執行、失敗會被獨立捕捉並記錄，不會讓外層的 Confirm 請求跟著失敗）：

  > `There is no "Account Category" defined for "[bk001] 從試算表到資料平台".`

  這牽出另一個需要更正的地方，見下面新增的「Account Category」筆記——**跟 worker 完全無關，是 Day 1 建 Product Category 時的設定缺口**
- **`trytond-cron` vs `trytond-worker` 這組知識本身沒有錯**，只是套用到「這次為什麼卡關」上是錯的：`ir.cron`／`ir.queue` 確實是兩套獨立機制，`trytond-cron` 只處理 `ir.cron`；但這次的 `process()` 任務走的是「沒有 worker 時同步執行」這條路，不是「卡在佇列裡沒人處理」那條路
- 之前 `automation-notes.md` 建議「加一個 `trytond-worker` service」也需要一併修正認知：加了 worker 只會讓這個任務改成非同步背景執行，**不會解決** Account Category 沒設定這個真正的錯誤，兩者是獨立的問題

**實測驗證（2026-07-08）：手動點 Process，果然被同一個錯誤擋下來**

- 手動點 Process，跳出跟 `ir_error` 記錄一模一樣的錯誤訊息：`There is no "Account Category" defined for "[bk001] 從試算表到資料平台".`
- 📸 `day2-user-05-process-account-category-error.png`
- psql 複查 `purchase_purchase`：`state` 仍是 `confirmed`，`stock_shipment_in` 仍是 0 筆——確認整個 transaction 回滾，沒有半吊子狀態（不會出現「發票沒建但 Shipment 建了」這種情況）

**概念筆記：Day 1「Account Category 可以留空」的判斷需要更正**

- 原本 Day 1 Step 3 寫的是：「Account Category 這欄可以先留空，Tryton 找不到 Product 專屬科目時會退回用這組公司預設值」——這個判斷**不完整/會誤導人**，實測後發現有兩層要分清楚：
  1. `account_configuration_default_account` 的 `default_category_account_expense`／`default_category_account_revenue`，查了 `account_product/product.py`，這兩個 classmethod **只是「新建一個 Product Category 時，Expense/Revenue Account 欄位要不要先幫你帶一個預設值」**，是輔助填表用的，不是 runtime 的後備方案
  2. 真正決定發票分錄科目的是 `purchase.py:1906`：`invoice_line.account = self.product.account_expense_used`，一路查到 `account_category.get_account()`——**如果 Product 掛的 Category 本身沒有勾 Accounting、沒填 Account Expense／Revenue，就直接報錯，沒有任何自動退回公司預設值的機制**
- **正確理解**：只要商品掛了一個 Category（用於記帳），這個 Category 自己就必須把 Accounting 設好，不會再退回公司層級的預設值；「留空」只在 Product 完全沒有指定 Account Category 時才會直接報錯（就是 Day 2 實際踩到的情況，見下方）

**概念筆記（2026-07-08，發現多了一層）：`bk001` 的「分類」跟「記帳用的 Category」其實是兩個獨立欄位**

- 查了 `product_template` 的 schema，跟 Category 有**兩種**關聯，容易搞混：

  | 關聯 | 資料表 | 用途 | `bk001` 現況 |
  |---|---|---|---|
  | 一般分類（Day 1 用「+ ADD PRODUCTS」設的） | `product_template-product_category`（多對多） | 商品分類/報表分組，可以掛多個 Category | 已掛「書籍」（2026-07-06 建立） |
  | **Account Category**（`account_product` 模組新增） | `product_template.account_category`（單一欄位） | **決定這個商品的發票分錄要用哪個 Category 的科目** | **當時是空的（NULL）**——這才是真正卡關的原因，不是「書籍」Category 本身沒設定 Accounting（雖然那個當時也還沒設） |
- `bk001` 雖然「分類上」屬於書籍，但「記帳上」從來沒有指定要用哪個 Category 的科目——這個欄位本身空著，是兩層獨立的缺口，要兩邊都補才行
- **權限也是獨立的**：查了 `ir_model_field_access`，`product.template.account_category` 這個欄位的寫入權限只開放給 **Account Product Administration**（`res_group` id=9）——跟編輯 `product.category` 的 Accounting 分頁需要的群組是同一個（`ir_rule_group` 對 `accounting=true` 的記錄一樣限定這個群組），所以补這一個群組能同時解決兩邊
- **完整修法（兩步都要做）**：
  1. Products ‣ Categories → 開「書籍」→ 勾選 **Accounting** → Account Expense 填 `5.2.1 Cost Of Sales`、Account Revenue 填 `4.1.1 Goods`（跟公司預設科目一致）→ 存檔
  2. Products ‣ Products → 開 `bk001` → Accounting 分頁 → **Account Category** 選「書籍」→ 存檔

**執行結果（psql 複查，2026-07-08）**

- 📸 `day2-user-06-book-category-accounting.png`（「書籍」Category 表單，Accounting 已勾選，Account Revenue=4.1.1、Account Expense=5.2.1）
- `product_category`：id=1（書籍），`accounting=true`
- `product_category_account`：`category=1`，`account_expense=112`（5.2.1）、`account_revenue=99`（4.1.1）——跟公司預設科目一致
- 📸 `day2-user-07-bk001-account-category-set.png`（`bk001` 的 Accounting 分頁，Account Category 已選「書籍」）
- `product_template`：id=1（`bk001`），`account_category=1`（書籍）——兩層缺口都補齊了

**實測驗證（2026-07-08）：兩層缺口補齊後，重新點 Process 成功**

- 📸 `day2-user-08-process-success-processing-state.png`（`State=Processing`、`Invoice State=Pending`、`Shipment State=Waiting`，下方 Invoices 徽章顯示 `1`）
- psql 複查：
  - `purchase_purchase`：`state=processing`、`invoice_state=pending`、`shipment_state=waiting`
  - `account_invoice`：新增 1 筆（id=1），`state=draft`，`party=2`（test supplier）——發票確實產生了
  - `stock_move`：新增 1 筆（id=2），`from_location=6`（Supplier）→`to_location=1`（Input Zone）、quantity=10、`state=draft`、`origin=purchase.line,1`

**概念筆記：為什麼 `Shipment State=Waiting`，但 `stock_shipment_in` 表還是 0 筆、Shipments 徽章還是 0？**

- 現象：Process 明明成功了，也真的產生了一筆 Stock Move，但這筆 Move 的 `shipment` 欄位是 `NULL`——沒有被包進任何一筆 `stock.shipment.in`（Supplier Shipment）記錄
- **查了 `purchase.py` 的 `create_move()`／`get_move()`，證實這是刻意設計，不是漏掉一步**：Process 只負責產生**未分組的草稿 Stock Move**，完全不會自動建立 Supplier Shipment 容器
- **查了官方文件**（[Purchase Module usage — 8.0，「Receiving a shipment」](https://docs.tryton.org/8.0/modules-purchase/usage/index.html)）證實了同一件事：

  > "A purchase does, however, create draft Stock Moves for any goods or assets that have been purchased... Once you receive the information about what's been shipped you create a new supplier shipment and add these moves to it."

  Supplier Shipment **要人工建立**，再把這些草稿 Move 加進去——這是刻意的設計，因為現實中供應商實際出貨的方式，不見得跟你下單的方式一樣（一張採購單可能分好幾批貨到、或好幾張採購單合成一批貨一起送達），Tryton 不能自作主張幫你決定怎麼分組，只能等你依照供應商實際出貨資訊，手動建立 Shipment、把對應的 Move 收進去
- **下一步**：去 Inventory & Stock ‣ Shipments ‣ Supplier Shipments → New，把這筆 Move 加進去，才會真的產生一張 Supplier Shipment 記錄

**概念筆記：Invoice Address 明明沒手動填，Confirm 卻沒被擋——以及 Invoice Party／Invoice Address 各自的商業意義**

- 現象：畫面上 `Invoice Party` 是空白的，但 `Invoice Address` 卻自動顯示 `test supplier`；Confirm 的前置檢查（要求 Invoice Address 有值）也順利通過，沒有手動填任何東西
- **根本原因**：查了 `purchase.py` 的 `on_change_party()`：

  ```python
  if not self.invoice_party:
      self.invoice_address = self.party.address_get(type='invoice')
  ```

  一選 `test supplier` 當 Party，Tryton 立刻呼叫 `party.address_get(type='invoice')` 找這個 Party 底下「開發票要寄到哪」的地址，自動帶進 `Invoice Address`——這個環境 `test supplier` 只有一筆地址，所以直接抓那筆。psql 複查 `purchase_purchase.invoice_address` 確實有值（不是 NULL），Confirm 的前置檢查是正常生效的，只是它要求的條件在選 Party 那一刻就已經被系統自動補好了，不需要手動處理
- **`Invoice Party`（開票對象）跟 `party`（供應商）是兩個獨立概念，正常情況下留空才是常態**：`invoice_party` 是一個**選填的覆寫欄位**，只有在「跟你買東西的供應商」跟「開發票給你的對象」是**不同 Party** 時才需要填——例如跟供應商的地區分公司進貨，但發票是總公司開的；或集團採購/代收代付的安排。大多數情況下這兩者是同一個 Party，所以留空才是正常，不是漏填
- **`Invoice Address` 一定要有值，但來源看 `invoice_party` 有沒有填**：沒填 `invoice_party` 時退回用供應商（`party`）自己的地址；填了 `invoice_party`，`on_change_invoice_party()` 就改用那個第三方 Party 的地址。一句話：**Invoice Party 空白＝「發票開給供應商自己就好，沒有第三方代收」，這是正常且最常見的情況**

### Step 3：建立 Supplier Shipment，把 Process 產生的草稿 Move 收進來

- 狀態：🔄 進行中（2026-07-08）
- 選單路徑（已實測）：Inventory & Stock ‣ Shipments ‣ Supplier Shipments → New → Supplier 選 `test supplier`（Warehouse 自動帶出 `[WH] Warehouse`）→ **Incoming Moves** 面板用「+」關聯既有的草稿 Move（`bk001` × 10，`shipment` 原本是空的那筆）→ 存檔
- 📸 `day2-user-09-supplier-shipment-draft-form.png`（存檔後 Draft 狀態，Incoming Moves 顯示 `bk001` / 10 u / Draft）

**執行結果（psql 複查，2026-07-08）**：`stock_shipment_in` 新增 id=1（`number=1`，`state=draft`），原本 `shipment=NULL` 的那筆 `stock_move`（id=2）現在指向 `stock.shipment.in,1`。

**實測確認：點 Receive 之後**

- 📸 `day2-user-10-supplier-shipment-received-state.png`（`Number=1`、`State=Received`，Incoming Moves 顯示該筆 Move 狀態變 `Done`，下方按鈕變成 CANCEL／COMPLETE）
- 查了 `stock/shipment.py` 的 `receive()`：Supplier Shipment 的狀態機比 Day 3 的 Internal Shipment 少一階——`Draft → Received → Done`，沒有 Waiting／Assigned／Packed，因為 Supplier 是抽象來源，不需要「Assign（保留庫存）」

**執行結果（psql 複查，2026-07-08）**

| 表 | 欄位 | 值 |
|---|---|---|
| `stock_shipment_in` | id / number / state | 1 ／ 1 ／ `received` |
| `stock_move`（id=2，Supplier→Input Zone） | state / effective_date | `done` ／ 2026-07-08——真正的收貨動作已發生 |
| `stock_move`（id=3，**新自動產生**，Input Zone→Storage Zone） | state | `draft`——`receive()` 自動建立的「上架」動作，還沒完成 |

- 因為這個環境 Input Zone／Storage Zone 是不同地點，狀態停在 `Received`，不會自動跳 `Done`，要再點一次 **Complete**（對應 `do()` 方法）才會把上架的 Move 也做完
- **更正（點完 Complete 之後才發現）**：原本以為「Input Zone 有真實庫存了，Day 3 卡住的 Assign 應該會成功」，這個判斷下得太早。點了 Complete 之後，「Input Zone → Storage Zone」那筆自動上架的 Move 也變成 `done`，psql 複查 Input Zone 的淨庫存**又變回 0**——貨已經被系統自動上架搬進 Storage Zone 了。Day 3 那張卡住的 Internal Shipment（要把 5 個單位從 Input Zone 搬到 Storage Zone）**重新點 Assign 預期還是會失敗**，因為來源地 Input Zone 現在是空的。完整分析與後續建議見 Day 3 Step 2 的更新說明

**概念筆記：Supplier Shipment 都 Done 了，為什麼 Purchase 本身還是卡在 `Processing`？**

- 現象：Supplier Shipment 走完 Receive → Complete，狀態是 `Done`；但回頭看 Purchase 本身，`state` 依然是 `Processing`，沒有跳到 `Done`
- **psql 複查**：`purchase_purchase` 的 `shipment_state=received`（出貨這邊已達標），但 `invoice_state=pending`（發票還沒收付款）
- **查了 `purchase.py` 的 `is_done()`**：

  ```python
  def is_done(self):
      return (
          (self.invoice_state == 'paid' or ...)
          and (self.shipment_state == 'received' or ...)
      )
  ```

  要**兩個條件同時滿足**才會判定整張 Purchase 完成：出貨要 `received`（✅ 已滿足）、發票要 `paid`（❌ 還沒，目前只是 `pending`）
- **這不是卡關，是預期中的正常現象**：呼應之前查過的「Tryton 沒有手動 Done 按鈕」——`Processing` 會一直停在這裡，直到發票也走完收付款流程。發票收付款是 **Day 5** 的範圍，Day 2（採購到入庫）這邊該做的事已經全部做完了

## Day 3｜庫存盤點

> 📦 **本節於 2026-07-09 重新整理**：原本 Day 3 的記錄反覆經歷「第一次卡關（Input Zone 沒庫存）→ Day 2/3 對調 → Day 2 做完後發現預期又落空」好幾輪修正，讀起來很亂，已整段搬到 [`user-guide-old-day3.md`](user-guide-old-day3.md) 封存。這裡從乾淨的起點重新開始，**7/9 之後的新記錄都放這裡**；需要引用舊版已查證過的原始碼／psql 證據（Sequence 給號機制、Stock Move 本質、Assign 精靈四個按鈕行為等）時，會直接連到舊檔對應段落，不重複貼一次。

- 狀態：✅ 完成（2026-07-09）
- **前置**：✅ 已完成——`aaa` 已加入 **Stock** 群組（見 [`admin-guide.md`](admin-guide.md)「Day 3 前置」）
- **環境現況（psql 複查，2026-07-09）**：Day 2 採購入庫已完成，Storage Zone（id=3）淨庫存 `bk001` 10 本，Input Zone（id=1）淨庫存 0（被 Supplier Shipment 的自動上架流程清空）。舊的 Internal Shipment（id=1，From=Input Zone→To=Storage Zone，qty=5）因為來源地已空，Assign 必然失敗，已點 **Cancel** 作廢（psql 複查 `state=cancelled`），詳細背景見 [`user-guide-old-day3.md`](user-guide-old-day3.md) 的「更新（2026-07-08）」段落

### Step 1：看懂預設 Warehouse／Location 結構（不用重建）

- 狀態：✅ 完成（2026-07-09，psql＋UI 雙重查證）
- 選單路徑（已實測）：左側選單 **Inventory & Stock** ‣ **Locations** ‣ **Locations**（子項目，跟上一層同名，點下去才是真正的清單）
- **與原課程規劃的差異**：`business_flow.md` 原本寫「建立 Warehouse、Location 結構」，但查了 `stock_location` 表發現這個環境的 `stock` 模組一啟用，Tryton 就已經自動產生一組堪用的預設結構，**不需要從零建**。書店這種單一門市情境直接沿用即可，只有要練習「開第二間分店/第二個倉庫」時才需要手動加 Location
- 已知的預設結構（psql 複查，2026-07-09）：

  | Location | Code | Type | 角色 |
  |---|---|---|---|
  | Warehouse | WH | warehouse | 整個倉庫的頂層容器 |
  | Input Zone | IN | storage | 進貨暫存區（東西進來但還沒正式入庫存） |
  | Storage Zone | STO | storage | 正式庫存區（庫存數量以這裡為準） |
  | Output Zone | OUT | storage | 出貨暫存區（要出貨但還沒真正離開倉庫） |
  | Lost and Found | — | lost_found | 盤點對不上帳時，系統用來吸收落差的地方 |
  | Supplier | SUP | supplier | 抽象的「供應商那邊」，採購入庫的來源端 |
  | Customer | CUS | customer | 抽象的「客戶那邊」，銷售出貨的目的端 |
  | Transit | — | storage | 兩個 Warehouse 間調貨時的運送中繼點 |

- **實測小發現**：Locations 清單畫面預設帶了一個 Filter「`Type: Storage;View;Warehouse`」，只顯示 5 筆（Input Zone／Output Zone／Storage Zone／Transit／Warehouse）；psql 查到的 Supplier／Customer／Lost and Found 這 3 筆因為 Type 不在這個篩選範圍內，清單上看不到（**不是資料不見了**，把 Filter 清空或改成全選就能看到全部 8 筆）
- 📸 `day3-user-01-locations-list.png`（`aaa` 登入後點開 Inventory & Stock ‣ Locations，5 筆清單畫面）

### Step 2：重新示範 Internal Shipment（已上架庫存之間搬動）

- 狀態：✅ 完成（2026-07-09，psql 複查）
- 這次改用 **From=Storage Zone、To=Output Zone**，模擬「揀貨準備出貨」的情境——兩邊都是庫存已經上架後的地點之間搬動，比舊版「Input→Storage」更貼近 Internal Shipment 實際會用到的場景，且 Storage Zone 現在有真實庫存（10 本 `bk001`）可以搬
- 填寫內容：From Location=Storage Zone、To Location=Output Zone；Moves 分頁新增一筆：Product=`bk001`、Quantity=3
- 📸 `day3-user-03-internal-shipment-draft-form.png`（存檔後畫面，From=`[STO] Storage Zone`、To=`[OUT] Output Zone`，Moves 顯示 `[bk001] 從試算表到資料平台 / 3 u / Draft`，State=Draft，下方footer直接有 CANCEL／WAIT 按鈕——再次驗證「有 state 欄位的表單，狀態機按鈕會直接出現在下方footer」這個 Day 2 就發現的模式，不用特地點風車圖示）

**執行結果（psql 複查，2026-07-09）**

| 表 | 欄位 | 值 |
|---|---|---|
| `stock_shipment_internal` | id / number / state / from_location / to_location | 2 ／ `NULL` ／ `draft` ／ 3（Storage Zone）／ 2（Output Zone） |
| `stock_move` | id / shipment / product / quantity / state / effective_date | 4 ／ `stock.shipment.internal,2` ／ 2（bk001 變體）／ 3 ／ `draft` ／ `NULL` |

**概念筆記：這一步在做什麼？對應到書店的什麼實體動作？**

- **Stock Move 是 Tryton 庫存的最小單位**：一筆「某個 Product、從 A 地點搬到 B 地點、搬了多少數量」的紀錄。`stock.shipment.internal` 這張單據本身不直接異動庫存，它是**包一批 Stock Move 的容器**（這次只包了 1 筆）
- **From Location=Storage Zone → To Location=Output Zone，對應書店「揀貨準備出貨」的動作**：書已經上架、是「顧客看得到、可以賣」的正式庫存（Storage Zone），但真正要出貨給客戶之前，通常會先從書架揀出來、集中放到出貨暫存區（Output Zone）點交打包，確認數量無誤後才真正離開店裡。這張單據就是在系統裡記錄這個「揀貨準備出貨」的動作——**跟 Day 2 那個「進貨後自動上架」的情境方向相反、性質也不同**：Day 2 是系統自動把 Input Zone 的貨搬進 Storage Zone（進貨流程的一部分，不需要手動模擬），這次是**已經上架的庫存之間**主動搬動，才是 Internal Shipment 真正常態的使用場景
- **現在的狀態是 Draft（草稿），代表「打算這麼做」，還沒真正執行**：查 `stock_move` 表確認 `effective_date` 是空的——Tryton 是用 `effective_date` 有沒有值來判斷這筆搬移「有沒有真的發生」，**不是存檔就等於庫存變動了**，Storage Zone／Output Zone 現在的庫存數字都還是舊的（Storage Zone 仍是 10，Output Zone 仍是 0）
- **單據編號（`number` 欄位）也還是空的**，這跟 Day 1 學到的 Sequence 概念呼應：Tryton 要等單據脫離 Draft、真正確認後才會跟 Sequence 要號，避免草稿被刪掉時在編號序列裡留下缺口
- 下一步：這次表單下方直接有 **CANCEL／WAIT** 的 footer 按鈕（不用像 Day 3 舊版那樣特地點風車圖示才找得到），點 **WAIT** 之後系統才會真的去檢查 Storage Zone 有沒有 3 本書可以搬，是狀態機從 Draft 往下推進的入口

**實測確認（2026-07-09）：點 WAIT 之後**

- 📸 `day3-user-04-internal-shipment-waiting-state.png`（`Number` 從空值變成 `2`，`State=Waiting`，footer 按鈕變成 CANCEL／DRAFT／WAIT／ASSIGN）
- psql 複查：`stock_shipment_internal` 的 `state` 從 `draft` → `waiting`，且 `number` 從 `NULL` → `2`——跟舊版 Step 2（見 [`user-guide-old-day3.md`](user-guide-old-day3.md)）驗證過的結論一致：離開 Draft（按 Wait）才會跟 `ir.sequence` 要號
- `stock_move`（id=4）仍是 `draft`、`effective_date` 仍空——真正的搬移還沒發生，Output Zone 的庫存數字目前還沒變化

**實測確認（2026-07-09）：點 ASSIGN 之後——這次成功了**

- 📸 `day3-user-05-internal-shipment-assigned-state.png`（`State=Assigned`，沒有跳出「Unable to assign」精靈，footer 按鈕變成 CANCEL／WAIT／COMPLETE）
- psql 複查：`stock_shipment_internal.state` → `assigned`；`stock_move`（id=4）的 `state` 也同步變成 `assigned`，但 `effective_date` 仍是空值——代表庫存已經被**保留**（避免被其他單據搶用），但實際的搬移動作還沒真正發生
- **跟舊版卡關的對比**：舊版那次失敗是因為來源地 Input Zone 沒有真實庫存；這次改用 Storage Zone（有 10 本 `bk001` 的真實庫存）當來源地，Assign 就直接成功，驗證了「Assign 本質上是在檢查來源地庫存夠不夠」這個結論
- 下一步：點 **COMPLETE**，讓這筆搬移真正執行（`stock_move` 變成 `done`，`effective_date` 補上日期，Storage Zone 庫存 -3、Output Zone 庫存 +3）

**概念筆記（2026-07-09，直讀原始碼查證）：Draft／Waiting／Assigned／Packed／Shipped／Done 各自對應什麼商業動作？**

- 直接讀了 `trytond/modules/stock/shipment.py`（`ShipmentInternal` 類）裡 `draft()`／`wait()`／`assign()`／`pack()`／`ship()`／`do()` 這幾個狀態轉換方法的實作，對照出每一步真正做的事：
  - **Draft（草稿）**：單純的搬運計劃，「打算要做」，隨時可以改 From/To Location、改數量，不鎖定任何庫存，也還沒有單號
  - **Waiting（待處理）**：按 Wait 呼叫 `set_number()` 給單號、`_sync_moves()` 同步 Move 明細——代表「這張單確定要執行了，排進待處理清單」，但**只是登記意圖，還沒有真的去檢查貨夠不夠**，對應倉管人員的待辦清單
  - **Assigned（已分配／已保留）**：按 Assign 呼叫 `Move.assign()`，這裡才**真正檢查來源地庫存夠不夠**，夠的話就把數量「預留」起來——業務意義是「已確認貨找得到，先卡位保留，不給別的單據搶走同一批貨」，但實體搬運動作**還沒發生**（`effective_date` 仍空）。這正是舊版卡在 Input Zone 沒庫存時失敗的原因：Assign 本質就是「庫存夠不夠」這個檢查
  - **Packed／Shipped（打包／已出發）**：只有跨倉庫搬運（有 `transit_location`）才會用到，對應「打包完成」「貨物離開來源倉庫、運送途中」。這次 Storage→Output 是同一個 Warehouse 內，沒有 transit location，`_transitions` 允許 `('assigned', 'done')` 直接跳過這兩步，所以 footer 只有 CANCEL／WAIT／COMPLETE，沒有 PACK/SHIP
  - **Done（完成）**：按 Complete 呼叫 `do()`，才真正呼叫 `Move.do()` 讓搬運「生效」——`effective_date` 補上日期，來源地庫存減少、目的地庫存增加，這時庫存數字才真的變動
- **一句話總結**：Wait 是「排隊登記」，Assign 是「確認有貨、先卡位」，Done 才是「貨真的搬了」——分別對應真實倉庫作業裡「登記搬運需求」「盤點/保留庫存」「實際執行搬運」三個不同動作，不是同一件事分三次點而已

**實測確認（2026-07-09）：點 COMPLETE 之後——庫存數字真的變動了**

- 📸 `day3-user-06-internal-shipment-done-state.png`（`State=Done`，`Effective Date=07/09/2026`）
- psql 複查：`stock_shipment_internal.state` → `done`、`effective_date` → `2026-07-09`；`stock_move`（id=4）同步變成 `state=done`、`effective_date=2026-07-09`
- **實際庫存變化（psql 依 done moves 加總複查）**：

  | Location | bk001 淨庫存（COMPLETE 前 → 後） |
  |---|---|
  | Storage Zone | 10 → **7** |
  | Output Zone | 0 → **3** |
  | Input Zone | 0 → 0（不受影響） |

  跟預期一致：3 本從 Storage Zone 真的搬到了 Output Zone，Input Zone 全程沒被動到

### Step 3：跑一次完整盤點（Inventory）

- 狀態：✅ 完成（2026-07-09，psql 複查）
- 目標：建盤點單 → 輸入實際數 → 確認 → 觀察系統自動產生的庫差 Stock Move（差異會被導向 Lost and Found）——這時 Storage Zone 已有 Day 2 採購入庫、Step 2 搬出 3 本之後的真實庫存，這一步是「對帳／抓差異」，不是無中生有造庫存
- 選單路徑（已實測）：**Inventory & Stock ‣ Inventories**
- 📸 `day3-user-07-inventories-empty-list.png`（Inventories 清單，`Draft` 分頁顯示 0）
- **實測小發現**：這個清單畫面本身是「過去建立過的盤點單」歷史清單，**不是「目前有哪些商品庫存」的畫面**——沒建過任何盤點單之前，清單本來就是空的，看不到任何商品是正常現象，不是卡關。要先點工具列的 `+` 新增一筆盤點單，選好要盤點的 Location 之後，系統才會依照那個地點目前的庫存，帶出該地點的商品清單讓你輸入實際盤點數

**實測確認（2026-07-09）：新增盤點單，Draft 狀態畫面**

- 📸 `day3-user-08-inventory-draft-form.png`（Location=`[STO] Storage Zone`、Date=07/09/2026、Company 自動帶出 REPLWARE Co., Ltd.、Lines 是空的，footer 有 CANCEL／COMPLETE／COUNT／CONFIRM 四個按鈕）
- 查了 `trytond/modules/stock/inventory.py`：`location` 欄位限定 `domain=[('type', '=', 'storage')]`，跟 Day 3 Step 1 學到的 Location Type 分類一致；`date`／`company` 都有 `default_*` 方法自動帶出，不用手動填
- **COMPLETE** 按鈕對應 `Inventory.complete_lines(fill=True)`：會查詢這個 Location 目前庫存不為 0 的商品，自動幫每個商品建一行，`expected_quantity` 直接帶入系統算出的目前庫存；**COUNT** 按鈕對應 `do_count()`，是另一種盤點精靈（例如搭配掃描裝置逐筆輸入）用的入口，手動盤點這裡用不到

**實測確認（2026-07-09）：點 COMPLETE 之後**

- 📸 `day3-user-09-inventory-complete-lines.png`（Lines 自動帶出一行 `[bk001] 從試算表到資料平台`，`Expected Quantity=7 u`，`Actual Quantity` 空著等填）
- psql 複查：`stock_inventory_line` 新增一筆 `expected_quantity=7`（跟 psql 算出的 Storage Zone 淨庫存一致），`quantity` 欄位仍是 `NULL`

**概念筆記（2026-07-09，實測發現＋直讀原始碼查證）：Inventory 的單號給法，跟 Shipment 不一樣**

- **現象**：psql 複查發現這張盤點單**在 `Draft` 狀態就已經有 `number=1`**，不是等到某個狀態轉換按鈕才給號
- **跟 Day 3 前面 Internal Shipment 的對比**：Internal Shipment 是在呼叫 **Wait**（離開 Draft）這個轉換方法時，才在 `wait()` 內部呼叫 `cls.set_number(shipments)`；Purchase／Invoice 也是同樣「離開 Draft 才給號」的模式，這是 Day 1、Day 3 前段歸納出來的「延後給號、避免刪草稿留下編號缺口」設計哲學
- **查了 `trytond/modules/stock/inventory.py` 的 `Inventory.preprocess_values()`**：

  ```python
  @classmethod
  def preprocess_values(cls, mode, values):
      values = super().preprocess_values(mode, values)
      if mode == 'create' and not values.get('number'):
          ...
          values['number'] = sequence.get()
      return values
  ```

  Inventory 是在 **create（新增存檔）這一刻**就直接跟 `ir.sequence` 要號，不是等某個 `Workflow.transition` 方法裡才呼叫，跟 Shipment／Purchase／Invoice 的模式不同
- **這稍微違反了先前歸納的設計哲學，但可能有其道理**：Inventory 的 `check_modification()` 允許在 `state in {'cancelled', 'draft'}` 時刪除整筆記錄——換句話說，如果一張 Draft 盤點單被刪掉，它已經拿到的編號**確實會留下缺口**，跟先前「延後給號是為了避免缺口」的推論矛盾。合理的猜測是：盤點單的編號主要是給倉管人員自己追蹤用（哪一次盤點、哪一天盤的），**不像發票／會計分錄／Shipment 那樣牽涉外部稽核或供應商/客戶溝通**，所以 Tryton 開發者在這裡沒有嚴格套用「延後給號」這個模式，兩者的稽核嚴謹度需求不同
- **這是一個好例子，說明「Tryton 裡的通用模式」不代表每個 model 都無條件套用**：`set_number`／`ir.sequence` 的呼叫時機是每個 model 的開發者自行決定的，要實際讀程式碼才能確認，不能只憑「之前查過另一個 model 是這樣」就假設全部一致

**概念筆記（2026-07-09，直讀原始碼查證）：為什麼 Internal Shipment 發生之後，還需要盤點？**

- **一般商業意義：帳面庫存 vs. 實際庫存，兩者天生會走鐘**。系統裡的庫存數字（Tryton 叫 `expected_quantity`，「系統算出來這個地點應該有多少」）只是**根據歷來所有 Stock Move 累加出來的理論值**；實體世界的貨（`quantity`，「現場實際點到多少」）可能因為搬運算錯數量、放錯位置、途中損壞遺失、還沒驗收系統就先按了 Done 等原因，跟理論值不一致。**系統不會自己發現這種落差**——它只忠實反映「你告訴它發生了什麼」，不會告訴你「實際上真的發生了什麼」。這是所有 ERP／倉儲管理共通的道理，不是 Tryton 特有設計
- **為什麼 Internal Shipment 之後特別適合盤點**：因為 Internal Shipment 是一個**人工搬運會實際介入**的環節——雖然剛才在系統裡點了 Complete、`stock_move` 也寫下「搬了 3 本」，但這只代表「單據上寫 3 本」，不代表現場的人真的精準搬了 3 本、一本不多一本不少放到正確位置。系統操作跟實體動作之間永遠有一層信任落差，盤點就是用來驗證這層落差的機制
- **Tryton 具體怎麼算差異、怎麼「平帳」**（直讀 `trytond/modules/stock/inventory.py`，`InventoryLine.get_move()`）：

  ```python
  delta_qty = self.unit.round(self.expected_quantity - qty)   # 帳面 - 實際盤點數
  from_location = self.inventory.location
  to_location = self.inventory.location.lost_found_used
  if delta_qty < 0:
      (from_location, to_location, delta_qty) = (to_location, from_location, -delta_qty)
  ```

  - `delta_qty > 0`（帳面 > 實際，**盤虧**，例如帳上寫 7 本、現場只點到 5 本）：自動產生一筆 Move，把差額**從這個地點搬到 Lost and Found**，帳面數字往下修正、對齊實際
  - `delta_qty < 0`（帳面 < 實際，**盤盈**，例如帳上寫 7 本、現場點到 9 本）：反過來，從 **Lost and Found 灌進這個地點**，帳面數字往上修正
  - **Lost and Found 不是真實地點**，是一個「吸收差異的虛擬倉」——它的存在讓每一次盤點差異都變成一筆**可追溯的 Stock Move**（有明確的 from/to/quantity/日期），而不是直接偷偷改一個數字、不留痕跡。這跟 Day 1、Day 3 前面查過的「Sequence 延後給號、確保稽核軌跡完整」是同一種設計哲學——**任何庫存數字的變動，都要有一筆對應的 Move 可以查，不能憑空修改**
- **一句話總結**：盤點不是為了「相信系統」，而是為了「驗證系統記錄有沒有跟實體現實脫節」；發現落差時也不是直接覆蓋數字，而是產生一筆走 Lost and Found 的正式 Move，讓差異本身也可以被追溯查核

**實測確認（2026-07-09）：故意填一個不同的數字，親眼看到 Lost and Found 平帳機制**

- 操作：Expected Quantity=7，Actual Quantity 故意填 **6**（模擬盤虧 1 本），存檔後點 **CONFIRM**
- 📸 `day3-user-10-inventory-actual-quantity-filled.png`（存檔後畫面，Actual Quantity=6 u，State 仍是 Draft）
- 📸 `day3-user-11-inventory-done-state.png`（點 Confirm 後，`State=Done`，COMPLETE／COUNT 按鈕變灰色不可點——這不是卡關，是離開 Draft 後正常的唯讀畫面）

**執行結果（psql 複查，2026-07-09）**

| 表 | 欄位 | 值 |
|---|---|---|
| `stock_inventory` | id / number / state | 1 ／ 1 ／ `done` |
| `stock_inventory_line` | id / expected_quantity / quantity | 1 ／ 7 ／ 6 |
| `stock_move`（自動產生，origin=`stock.inventory.line,1`） | id / product / quantity / state / effective_date / from_location / to_location | 5 ／ bk001 ／ 1 ／ `done` ／ 2026-07-09 ／ 3（Storage Zone）／ 4（Lost and Found） |

- 跟概念筆記推演的完全一致：`delta_qty = expected(7) - actual(6) = 1 > 0`（盤虧），系統自動產生一筆 **Storage Zone → Lost and Found、數量 1** 的 Move，而且直接是 `done`（不停在草稿）
- Storage Zone 的 `bk001` 淨庫存從 7 修正為 **6**，跟實際盤點到的數字對齊——這就是「帳面追上實體」的具體發生過程

至此 Day 3（庫存盤點）的三個 Step 全部走完：Step 1 看懂預設 Location 結構、Step 2 手動搬運 Internal Shipment（Draft→Waiting→Assigned→Done）、Step 3 盤點抓差異（自動產生 Lost and Found 平帳 Move）。

## Day 4｜銷售到出庫

- 狀態：⬜ 待做，前置：admin 先啟用 `sale` 模組

## Day 5｜發票與收付款

- 狀態：⬜ 待做
