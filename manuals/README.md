# 學習操作手冊（manuals/）

依角色切分的 Tryton 操作記錄，對照 [`business_flow.md`](../docs/business_flow.md) 的 Day 1–8 課程邊做邊寫。

- [`admin-guide.md`](admin-guide.md) — admin user：設定 ERP（Company、Chart of Accounts、模組、Fiscal Year…）
- [`user-guide.md`](user-guide.md) — ordinary user：日常操作 ERP（Party、Product、採購/銷售單、出入庫、發票…）
- [`automation-notes.md`](automation-notes.md) — 操作過程中發現「這步驟很適合寫成 script/CLI/cron」的契機記錄

## 記錄原則

1. **只記錄實際跑過的步驟**，還沒做的維持「待做」狀態，不預先杜撰內容（呼應 `business_flow.md` 的「每個 Use Case 都要實際跑通」原則）
2. 每個步驟標記狀態：`✅ 完成` / `🔄 進行中` / `⬜ 待做` / `⚠️ 卡關`
3. 截圖存到 [`assets/`](assets/)，命名規則：`dayN-<role>-<順序>-<簡短描述>.png`
   例：`day1-admin-01-login.png`、`day1-admin-02-create-company.png`
   截圖是手動存檔（目前沒有瀏覽器自動化工具），存好後告訴檔名，我會在對應文件補上引用與說明
4. 卡關時直接記下錯誤訊息／畫面描述，先往下走，回頭再查（呼應學習原則第 2 條）
