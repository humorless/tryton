# 自動化契機記錄

操作過程中發現「這步驟很適合寫成 script / CLI / cron，不該一直用滑鼠點」的地方，邊做邊記。目標是學完 Day 1–8 之後，手上已經有一份可重複執行的 demo 環境重建腳本。

| 日期 | 情境 | 為什麼值得自動化 | 具體做法 |
|------|------|------------------|---------|
| 2026-07-02 | 確認模組啟用狀態、確認 Company/Party 是否已建立 | 登入 UI 點 Administration ‣ Modules 逐頁確認很慢，且每次重建測試環境都要重查一次 | 直接 `psql` 連 `localhost:5432`（compose 有開這個 port）查 `ir_module`（模組狀態）、`res_user`（帳號）、`company_company` / `party_party`（是否已有資料），可以寫成一支 `scripts/check-status.sh` 健康檢查腳本 |
| 2026-07-02 | Day 3/4/5 前要分別啟用 `purchase`、`sale`、`production` 模組 | UI 啟用要點 Activate → Perform Pending Actions → 手動 `docker compose restart trytond`，步驟多且容易漏做重啟這步 | 沿用 [`../docs/custom-modules.md`](../docs/custom-modules.md) 記載的 CLI：`docker compose exec trytond trytond-admin -d tryton -u <module> --activate-dependencies`，再 `docker compose restart trytond`。三個模組可以寫成一支 `scripts/activate-day345-modules.sh` |
| 待補 | Day 3–7 建立 Party / Product / 採購單 / 銷售單等重複性主檔資料 | 手動點擊建立測試資料，每次重建環境都要重打一次，且容易漏欄位 | `tryton_20hr.md` 提到的 **proteus**（官方 Python library，可用 domain 語法操作 Tryton）——之後可以寫成腳本批次建 Party/Product/Invoice，並重複執行來重建 demo 環境。等 Day 2 proteus 環境裝好後補上實際範例 |
| 待補 | 定期報表寄送（Day 8 提到的 scheduler） | 損益表/庫存報表如果要每月自動寄給人看，手動跑報表不現實 | Tryton 內建 `ir.cron` 排程機制，之後研究怎麼設定 cron job 呼叫 report + email，補在這裡 |
| 待補 | 備份/還原 | `../docs/backup-restore.md` 已經有基本的 `pg_dump`/`psql` 指令，但目前是手動下指令 | 之後可以包成 `scripts/backup.sh`，加上時間戳記檔名，避免每次都要重打指令、忘記檔名對應哪次 |
| 2026-07-08 | `docker-compose.yml` 只有 `trytond`（web）跟 `cron`（`trytond-cron`，只跑 `ir.cron`），沒有 `trytond-worker` | **更正（2026-07-08 稍晚）**：原本以為 Purchase 的 `process()` 任務卡在 `ir.queue` 裡沒人處理，後來查了 `trytond/ir/queue_.py`／`dispatcher.py` 才發現：沒設定 `[queue] worker` 時，任務其實會在 request 結束、commit 後**同步執行**，不是卡住不動——這次真正卡關的原因是 Account Category 沒設定（見 `user-guide.md` Day 2 概念筆記），跟有沒有 `trytond-worker` 無關。加 `trytond-worker` 這件事本身還是有意義（讓耗時任務改成非同步、不卡住當下請求），但**不要預期它能解決「任務沒生效」這類問題**——那通常是任務執行時真的報錯了，要去查 `ir_error` 表，不是查有沒有 worker | 在 `docker-compose.yml` 加一個新 service，`command: trytond-worker -c /etc/trytond.conf -d tryton`，跟 `cron` 服務一樣掛 `postgres`/`trytond` 的 `depends_on`；加好之後可以用 `SELECT * FROM ir_queue WHERE dequeued_at IS NULL;` 確認佇列裡的任務有沒有被消化掉，**但卡關時先查 `ir_error` 表**，不要先假設是 worker 沒開 |
| 待查證 | Fiscal Year 的 Invoice Sequence 若要符合台灣電子發票（統一發票）字軌規範 | Tryton 內建 Sequence 只是自訂連號，不等於國稅局配發的發票字軌，兩者是不同層級的機制 | 需要另外查證是否有現成的 Tryton 台灣在地化模組（或串接財政部電子發票 API），目前尚未確認，不要假設裝了 `account_invoice` 就自動合規 |

## 已有但還沒串起來的既有基礎設施

- `docs/custom-modules.md` 已經寫好 CLI 啟用模組的完整流程，本文件的模組啟用自動化直接沿用即可，不用重寫一份
- `docs/backup-restore.md` 已有備份指令雛型
