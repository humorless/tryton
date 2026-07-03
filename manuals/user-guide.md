# Ordinary User 操作手冊

給「日常操作 ERP」的人看：下單、出入庫、開發票、收付款。對照 [`admin-guide.md`](admin-guide.md)（admin 設定）與 [`../tryton_business_flow.md`](../tryton_business_flow.md)（整體課程）服用。

> ✅ （2026-07-03 更新，已實測＋查證）`aaa` 帳號已建立（`res_user` id=3，見 [`admin-guide.md`](admin-guide.md) Step 6），Access Permissions 沒勾任何 Group，實際登入後選單確認可見 **Parties**、**Products** 等選單。**但選單看得到不代表能建立資料**——查了 `ir_model_access` 表發現：`party.party` 完全沒有限制規則（預設全開放，`aaa` 可正常新增/編輯 Party），但 `product.template` 有規則：無 Group 的基礎權限是 `read only`，只有 **Product Administration** 群組才有 create/write/delete。所以 **Step 2（Party）可以直接用 `aaa`，Step 3（Product）要先把 `aaa` 加進 Product Administration 群組**，否則存檔會跳權限錯誤。

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

- 狀態：🔄 進行中
- 目標：搞懂 Menu、Form View、List View、狀態機（draft → confirmed → done）長什麼樣子
- 沒有固定「操作步驟」，就是點過一輪主要選單，感受一下 breadcrumb 跟畫面切換方式，卡關直接截圖記錄
- 已實測：`aaa` 登入後左側選單可見 **Parties**（Parties/Identifiers/Addresses/Contact Mechanisms/Categories）、**Hello World**（自訂模組）、**Products**（Products/Categories/Reporting），確認一般使用者不需要掛 Group 就能看到這些基礎選單（見上方前置需求檢查表的說明）
- 📸 `day1-user-01-aaa-login-menu.png`（aaa 登入後的選單全貌）

### Step 2：建立 Party（廠商＋客戶）

- 狀態：⬜ 待做
- 選單路徑：Party ‣ Parties → New
- 建議建 2 筆：一筆當供應商（Day 3 採購用）、一筆當客戶（Day 4 銷售用）
- 📸 截圖建議：`day1-user-02-party-form.png`

### Step 3：建立 Product（含 UoM）

- 狀態：⬜ 待做
- **前置**：先回 Administration ‣ User ‣ Users → `aaa` → Access Permissions 分頁，勾選 **Product Administration** 群組並存檔（查過 `ir_model_access`，`product.template` 對「無 Group」的預設權限是唯讀，沒有這個群組會建立失敗）
- 選單路徑：Products ‣ Products → New（UoM／Category 若清單裡沒有需要的，先去對應選單建)
- `account_product` 已啟用，記得在 Product 表單把 Account Category（會對應到收入/費用科目）設好，不然 Day 7 開發票時系統找不到科目會卡關
- 📸 截圖建議：`day1-user-03-product-form.png`

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
