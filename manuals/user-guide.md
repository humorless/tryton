# Ordinary User 操作手冊

給「日常操作 ERP」的人看：下單、出入庫、開發票、收付款。對照 [`admin-guide.md`](admin-guide.md)（admin 設定）與 [`../tryton_business_flow.md`](../tryton_business_flow.md)（整體課程）服用。

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
- **Account Category 更正**：原本寫「不設會在開發票時卡關」講得太重了——查了 `product_category` 表目前是空的（0 筆，這環境還沒建過任何 Category），但 `account_configuration_default_account` 已經有公司層級的預設收入/費用科目（`default_category_account_revenue`=99、`default_category_account_expense`=112，Chart of Accounts 精靈時設定的）。所以 **Account Category 這欄可以先留空**，Tryton 找不到 Product 專屬科目時會退回用這組公司預設值；除非要讓「這個商品線用專屬的收入/費用科目」做更細的財務分類，才需要先去 Products ‣ Categories 建 Category、勾 Accounting、指定科目
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
- 用表單裡的 **+ ADD PRODUCTS** 按鈕把已建立的 `bk001` 掛進這個分類（精靈視窗選好後要先存精靈，再存 Category 本身，兩層都要存）
- 📸 `day1-user-04-category-form.png`（Category 表單，Name/Accounting/Parent）
- 📸 `day1-user-05-category-add-products.png`（Add products 精靈，`bk001` 已加入清單）

**執行結果（psql 複查，2026-07-06）**

| 表 | 欄位 | 值 |
|---|---|---|
| `product_category` | id / name / code / accounting / parent | 1 ／ 書籍 ／ book ／ false ／ NULL（頂層） |
| `product_template-product_category` | category / template | 1 ／ 1（`bk001` 已掛進「書籍」分類），create_uid=3（`aaa`） |

---

## Day 2｜採購到入庫

- 狀態：⬜ 待做，前置：admin 先啟用 `purchase` 模組
- **順序更正（2026-07-07）**：這裡原本排在 Day 3，現在對調到 Day 2——先跑通採購入庫，Day 3 的庫存操作（Internal Shipment）才有真實庫存可以搬，詳見上方前置需求檢查表下的說明

## Day 3｜庫存盤點

- 狀態：🔄 進行中（2026-07-07）
- **前置**：✅ 已完成——`aaa` 已加入 **Stock** 群組（見 [`admin-guide.md`](admin-guide.md)「Day 3 前置」）

### Step 1：看懂預設 Warehouse／Location 結構（不用重建）

- 狀態：✅ 完成（2026-07-07，psql＋UI 雙重查證）
- 選單路徑（已實測）：左側選單 **Inventory & Stock** ‣ **Locations** ‣ **Locations**（子項目，跟上一層同名，點下去才是真正的清單）
- **與原課程規劃的差異**：`tryton_business_flow.md` 原本寫「建立 Warehouse、Location 結構」，但查了 `stock_location` 表發現這個環境的 `stock` 模組一啟用，Tryton 就已經自動產生一組堪用的預設結構，**不需要從零建**。書店這種單一門市情境直接沿用即可，只有要練習「開第二間分店/第二個倉庫」時才需要手動加 Location
- 已知的預設結構（psql 複查，2026-07-07）：

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

### Step 2：手動建立 Internal Shipment

- 狀態：🔄 進行中（2026-07-07）——單據已建好存檔在 Draft，推進到 Waiting 後在 Assign 卡關（見下方「實測發現」），待 Day 2 採購入庫完成、Input Zone 有真實庫存後回來重試
- 選單路徑（已實測）：**Inventory & Stock ‣ Shipments ‣ Internal Shipments** → 清單畫面上方有一排狀態分頁（Requests / Draft / Waiting / Partially Assigned / Assigned / Packed / Shipped），建立前全部是 0
- 📸 `day3-user-02-internal-shipments-list.png`（Internal Shipments 清單，狀態分頁全 0）
- 填寫內容：From Location=Input Zone、To Location=Storage Zone、Company=REPLWARE Co., Ltd.（自動帶出）；Moves 分頁新增一筆：Product=`bk001`（從試算表到資料平台）、Quantity=5
- 📸 `day3-user-03-internal-shipment-draft-form.png`（存檔後畫面，Moves 顯示 `[bk001] 從試算表到資料平台 / 5 u / Draft`）

**執行結果（psql 複查，2026-07-07）**

| 表 | 欄位 | 值 |
|---|---|---|
| `stock_shipment_internal` | id / number / state / from_location / to_location | 1 ／ `NULL` ／ `draft` ／ 1（Input Zone）／ 3（Storage Zone） |
| `stock_move` | id / shipment / product / quantity / state / effective_date | 1 ／ `stock.shipment.internal,1` ／ 2（bk001 變體）／ 5 ／ `draft` ／ `NULL` |

**概念筆記：這一步在做什麼？對應到書店的什麼實體動作？**

- **Stock Move 是 Tryton 庫存的最小單位**：一筆「某個 Product、從 A 地點搬到 B 地點、搬了多少數量」的紀錄。`stock.shipment.internal` 這張單據本身不直接異動庫存，它是**包一批 Stock Move 的容器**（這次只包了 1 筆）
- **From Location=Input Zone → To Location=Storage Zone，對應書店「驗收後上架」的動作**：供應商把書送到店裡時，通常不會貨一到就直接算進可銷售庫存——會先卸在收貨暫存區（Input Zone），清點數量、檢查外觀沒問題後，才正式搬上書架/ 入庫位置（Storage Zone），變成「顧客真的看得到、可以賣」的庫存。這張單據就是在系統裡記錄這個「上架」動作
- **現在的狀態是 Draft（草稿），代表「打算這麼做」，還沒真正執行**：查 `stock_move` 表確認 `effective_date` 是空的——Tryton 是用 `effective_date` 有沒有值來判斷這筆搬移「有沒有真的發生」，**不是存檔就等於庫存變動了**，Storage Zone 現在的庫存數字還是舊的
- **單據編號（`number` 欄位）也還是空的**，這跟 Day 1 學到的 Sequence 概念呼應：Tryton 要等單據脫離 Draft、真正確認後才會跟 Sequence 要號，避免草稿被刪掉時在編號序列裡留下缺口
- 下一步：工具列上通常會有一個「狀態機動作」按鈕（例如 Wait／Assign 之類，實際名稱與圖示待下一步截圖確認），點了之後系統才會真的去檢查 Input Zone 有沒有 5 本書可以搬，是狀態機從 Draft 往下推進的入口

**實測確認（2026-07-07）：狀態機動作按鈕長怎樣**

- 工具列上那個**四色風車圖示**就是狀態機動作選單（不是普通的裝飾圖示）；點開後在 Draft 狀態下只列出 **Cancel** 和 **Wait** 兩個選項，跟清單畫面分頁順序（Draft → Waiting → Partially Assigned → Assigned → Packed → Shipped）一致——代表 Draft 這一步只能往前推進到 Wait，或整張單據作廢（Cancel），不能跳著走
- 📸 `day3-user-04-internal-shipment-wait-menu.png`（風車圖示點開後的選單，Cancel／Wait）

**實測確認（2026-07-07）：點 Wait 之後發生什麼事**

- 📸 `day3-user-05-internal-shipment-waiting-state.png`（點 Wait 後的畫面，Number 欄位變成 `1`，Moves 明細改顯示 From Location／To Location 兩欄）
- psql 複查：`stock_shipment_internal` 的 `state` 從 `draft` → `waiting`，且 **`number` 欄位從空值變成 `1`**——證實了「編號要等單據離開 Draft 才由 Sequence 產生」這個判斷，而且是在 **Wait 這一步**就發生，不是等到整張單據 Done 才給號
- 但 `stock_move`（真正的搬移紀錄）**還是 `draft`，`effective_date` 仍是空的**——代表 Waiting 只是「單據確認要執行了」，底層的實際搬移動作還沒發生，Storage Zone 的庫存數字目前還沒變化

**概念釐清（2026-07-07）：到目前為止，Day 3 這些操作有沒有連動到會計？Sequence 是不是會計專屬概念？**

- **還沒連動到會計**：查了 `account_move`（會計分錄表）目前是 **0 筆**；再查模組啟用狀態，`account_stock_continental`／`account_stock_anglo_saxon`（讓庫存異動自動產生會計分錄的「永續盤存法」模組）這個環境都**沒有啟用**。代表這裡的設計是：**Stock Move 只管實體數量，完全不動總帳**，唯一會產生會計分錄的動作是 Day 5 的「發票確認」——這也是為什麼發票被特別留到接近最後才處理，Day 2–4 的庫存流程都是先把貨物的移動搞對，錢的部分刻意分開、最後才收斂
- **Sequence 不是會計專屬概念**：查了 `ir_sequence` 表，這次 Internal Shipment 的編號規則（`Internal Shipment`，id=5）用的是一般 `ir.sequence`，**不是** Day 1 學到的 `ir.sequence.strict`。`ir.sequence` 是 Tryton 全系統共用的自動編號產生器，Party 的 Code、各種 Shipment 編號都靠它，跟會計無關；只有 Day 1 查過的、牽涉法規稽核不能重號/跳號的場景（Fiscal Year 的 Move Sequence、四種 Invoice Sequence）才會刻意用鎖更嚴格的 `ir.sequence.strict`。正確理解是「會計只是剛好也用了 Sequence、而且用了加強版」，不代表 Sequence 本身是會計專屬工具

**概念釐清（2026-07-07，直讀原始碼查證）：Sequence 給 number 的本質，以及為什麼是在「按 Wait」這個時間點冒出來**

- **Sequence 的本質**：`id`（例如 `stock_shipment_internal.id`）是純技術用途的內部主鍵，不對人類有意義、所有 Shipment 類型共用一個序列，不是設計給人看的編號；`number` 才是給業務溝通用的單據編號，需要可自訂格式（prefix／補零／要不要帶年份）、每種單據類型各自獨立計數。Tryton 把「編號規則」獨立成 `ir.sequence` 這個模型，用 Many2One 掛到各種業務單據上，而不是直接拿資料庫的 auto-increment id 當編號
- **不是自動觸發，是寫死在按鈕背後的程式碼**：直接進 docker container 讀了 `trytond/modules/stock/shipment.py` 原始碼，`ShipmentInternal.wait()`（就是 Wait 按鈕背後對應的方法）裡面明確呼叫 `cls.set_number(shipments)`；`set_number()` 會去讀 `stock.configuration`（公司層級單例設定，跟 Day 1 查過的 `account_configuration_default_account` 同一種設計）找出這個單據類型該用哪個 Sequence（這裡是 `shipment_internal_sequence`），且**只對「目前還沒有編號」的單據**才去要新號碼，保證同一張單據重複觸發也不會重複耗用編號
- **為什麼延後到「離開 Draft」才給號**：跟 Day 1 查過的 Fiscal Year Invoice Sequence 同一套設計哲學——如果一存檔（還在 Draft）就給號，草稿被刪掉時編號會永久留下缺口，事後稽核查不出原因；延後到「單據確定要執行了」（離開 Draft）這一刻才給號，之後編號如果中斷，一定對應到一個查得到的具體原因（例如某張單被 Cancel），而不是憑空消失
- **這套模式在 Tryton 裡到處重用，不是庫存模組專屬**：Party 建立時給 Code、Shipment 在 Wait 給 number、發票在 Confirm 給號、會計分錄在 Post 給號——每個 model 的開發者自己決定「在哪個狀態轉換點」呼叫 `set_number`；只有真正牽涉法規稽核的（會計分錄、發票）才會刻意選用鎖更嚴格的 `ir.sequence.strict`

**實測發現（2026-07-07）：點下一個狀態按鈕 Assign 後卡關**

- 點風車圖示後選 **Assign**，跳出精靈「Assign Internal Shipment (1)」，顯示 **"Unable to assign these products:"**，底下列出 `[bk001] 從試算表到資料平台 / 5 u`
- **根本原因（psql 複查）**：`stock_move` 表裡目前只有這一筆紀錄，`state` 還是 `draft`——代表**從來沒有任何一筆 `bk001` 真正「完成」進到過 Input Zone**。Day 1 建立 Product 時填的 Cost Price／Identifier 只是型錄資料，**不代表任何地點有真實庫存**；Input Zone 現在庫存是 0，Assign（保留庫存）自然找不到 5 本書可以搬
- **直讀原始碼查證三個按鈕的實際行為**（`trytond/modules/stock/shipment.py`，`class Assign(Wizard)`）：

  | 按鈕 | 背後呼叫 | 實際效果 |
  |---|---|---|
  | **Cancel** | `assign_reset()` → `wait()` | 放棄這次嘗試，單據留在 Waiting，資料不變，之後可以再試 |
  | **Wait** | 直接結束精靈（無額外動作） | 單純關掉提示視窗，維持現狀 |
  | **Ignore** | `assign_ignore()` | 把搬不動的那幾筆數量**強制改成 0**，然後照樣把單據標記為 Assigned——等於「放棄搬這個商品，當作沒這回事」，資料會失真，**不建議在這裡使用** |
  | （畫面上沒出現）**Force** | `assign_force()` → `assign()` | 完全跳過庫存檢查強制指派，可能讓庫存變負數；只有掛了 **Stock Force Assignment** 群組（`res_group` id=12）的人才看得到這顆按鈕，`aaa` 沒有這個群組，刻意設計成危險操作要額外授權 |

- **處理方式**：點 **Cancel** 安全退出（不使用 Ignore，避免資料失真）。這正是促成 **Day 2／Day 3 對調**的實測發現——與其在這裡硬生一個「盤點出庫存」的權宜步驟，不如先去完成 **Day 2（採購到入庫）**，讓 Input Zone 透過真實的採購流程拿到庫存；等 Day 2 做完，再回到這張還停在 Waiting 狀態的 Internal Shipment（不用重建，同一張單據）重新點 Assign，這時就找得到真實庫存可以搬

### Step 3：跑一次完整盤點（Inventory）

- 狀態：⬜ 待做（尚未實測，選單路徑待確認後填寫，避免照抄未驗證路徑）
- 目標：建盤點單 → 輸入實際數 → 確認 → 觀察系統自動產生的庫差 Stock Move（差異會被導向 Lost and Found）——這時 Day 2 已經有採購入庫的真實庫存，這一步是「對帳／抓差異」，不是無中生有造庫存

## Day 4｜銷售到出庫

- 狀態：⬜ 待做，前置：admin 先啟用 `sale` 模組

## Day 5｜發票與收付款

- 狀態：⬜ 待做
