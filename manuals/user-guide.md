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
| ordinary user 帳號已建立 | ✅ 已完成（`aaa`，未指派任何 Group，已實測登入可見 Parties/Products 選單） |
| `purchase` 模組（Day 3 前）/ `sale` 模組（Day 4 前）/ `production` 模組（Day 5 前）已啟用 | ⬜ 待 admin 完成 |

---

## Day 1｜介面導覽 + 建立 Party / Product

### Step 1：介面導覽（1hr）

- 狀態：✅ 完成（2026-07-06）——List View ↔ Form View 切換、排序/篩選、breadcrumb 多層導覽都實測過一輪，沒有卡關
- 目標：搞懂 Menu、Form View、List View 長什麼樣子
- 已實測：`aaa` 登入後左側選單可見 **Parties**（Parties/Identifiers/Addresses/Contact Mechanisms/Categories）、**Hello World**（自訂模組）、**Products**（Products/Categories/Reporting），確認一般使用者不需要掛 Group 就能看到這些基礎選單（見上方前置需求檢查表的說明）
- 📸 `day1-user-01-aaa-login-menu.png`（aaa 登入後的選單全貌）
- **狀態機（draft → confirmed → done）延後到 Day 3／Day 4 處理**：查了 `party_party`、`product_template` 兩張表都**沒有 `state` 欄位**，代表 Day 1 這兩個 model 本來就沒有工作流程狀態可以練習；等 Day 3（Purchase Order）／Day 4（Sale Order）建出真正的單據，才有 draft/confirmed/done 這類狀態機可以實際操作觀察，屆時再補這部分的說明與截圖

### Step 2：建立 Party（廠商＋客戶）

- 狀態：✅ 完成（2026-07-06，psql 複查）
- 選單路徑：Party ‣ Parties → New
- 建了 2 筆：`test supplier`（Day 3 採購用）、`test customer`（Day 4 銷售用）
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
- **Account Category 更正**：原本寫「不設會在 Day 7 卡關」講得太重了——查了 `product_category` 表目前是空的（0 筆，這環境還沒建過任何 Category），但 `account_configuration_default_account` 已經有公司層級的預設收入/費用科目（`default_category_account_revenue`=99、`default_category_account_expense`=112，Chart of Accounts 精靈時設定的）。所以 **Account Category 這欄可以先留空**，Tryton 找不到 Product 專屬科目時會退回用這組公司預設值；除非要讓「這個商品線用專屬的收入/費用科目」做更細的財務分類，才需要先去 Products ‣ Categories 建 Category、勾 Accounting、指定科目
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

## Day 2｜庫存盤點

- 狀態：⬜ 待做（尚未開始，內容待實測後填寫，避免照抄未驗證的選單路徑）

## Day 3｜採購到入庫

- 狀態：⬜ 待做，前置：admin 先啟用 `purchase` 模組

## Day 4｜銷售到出庫

- 狀態：⬜ 待做，前置：admin 先啟用 `sale` 模組

## Day 5–6｜製造流程

- 狀態：⬜ 待做，前置：admin 先啟用 `production` 模組

## Day 7｜發票與收付款

- 狀態：⬜ 待做
