# Tryton Docker Setup

這個 docker compose 配置可以快速啟動完整的 Tryton ERP 系統，包含 PostgreSQL 資料庫和應用伺服器。

## 系統要求

- Docker
- Docker Compose
- 至少 2GB RAM
- 至少 1GB 磁碟空間

## 快速開始

### 1. 啟動 PostgreSQL

```bash
docker compose up -d postgres
```

### 2. 初始化資料庫（首次運行，臨時容器）

```bash
docker compose run -it --rm trytond trytond-admin -d tryton --all
```

系統會提示你輸入：
- **管理員電郵**
- **管理員密碼**（2 次確認）

  ```
  "admin" email for "tryton" (empty for none): 
  "admin" password for "tryton": 
  "admin" password confirmation: 
  ```

#### 📦 模組選擇指南

初始化過程中會詢問要激活的模組。**初學者建議激活以下基礎模組**：

| 模組 | 說明 | 激活 |
|------|------|------|
| **party** | 客戶、供應商、員工管理 | ✅ |
| **currency** | 貨幣管理 | ✅ |
| **company** | 公司管理 | ✅ |
| **account** | 會計/財務 | ✅ |
| **account_invoice** | 應收/應付發票，銷售和採購的財務閉環靠它 | ✅ |
| **stock** | 庫存/倉庫管理 | ✅ |

**系統會自動識別並升級相關依賴模組**（如 account_invoice、account_product 等），直接確認激活即可。

⚠️ **提示**：不要激活過多模組，會讓介面變得複雜。可以在 Web 登入後，從「模組管理」頁面再激活其他需要的模組。

### 3. 啟動 Tryton 伺服器

```bash
docker compose up -d trytond
```

### 4. 從 Web 登入

打開瀏覽器訪問：
```
http://localhost:8000/
```

登入帳號：
- **用戶名**: admin
- **密碼**: 初始化時設置的密碼

## 從 Web 登入後

### 🚀 初學者建議

成功登入後，你可以開始學習和探索 Tryton：

1. **熟悉基礎數據設定**
   - 建立公司資訊（Administration → Company）
   - 設定主帳戶和帳戶科目（Accounting → Charts of Accounts）
   - 建立產品類別和產品

2. **創建測試數據**
   - 新增客戶和供應商（Party）
   - 建立產品
   - 嘗試建立銷售訂單並追蹤流程

3. **探索核心功能**
   - 查看各個模組的功能和使用方式
   - 瞭解業務流程（如銷售訂單 → 發票 → 付款）
   - 查看和自訂報表

4. **激活額外模組**
   - 從「模組管理」頁面可以啟用或停用模組
   - 根據業務需求逐步啟用其他功能模組

## 配置說明

### docker-compose.yml

包含以下服務：

- **postgres**: PostgreSQL 16 資料庫伺服器
  - 連接埠: 5432
  - 預設用戶: tryton
  - 預設密碼: tryton_password
  - 資料卷: tryton-database

- **trytond**: Tryton 應用伺服器
  - 監聽連接埠: 8000
  - 資料卷: tryton-data（用於附件和上傳文件）

### trytond.conf

Tryton 配置檔，包含：
- 資料庫連接設定
- Web 伺服器設定
- Session 和 Cookie 配置
- 日誌設定

## 常用指令

### 檢視日誌

```bash
# 查看所有服務日誌
docker compose logs -f

# 只查看 Tryton 伺服器日誌
docker compose logs -f trytond

# 只查看資料庫日誌
docker compose logs -f postgres
```

### 停止服務

```bash
# 停止但保留卷
docker compose stop

# 停止並移除容器（卷保留）
docker compose down

# 完全清除（包括卷）
docker compose down -v
```

### 重新啟動

```bash
docker compose restart trytond
```

### 進入容器 Shell

```bash
# Tryton 伺服器
docker compose exec trytond sh

# 資料庫
docker compose exec postgres psql -U tryton -d tryton
```

## 進階文件

- [安全建議](docs/security.md) — 生產環境密碼、SSL/TLS、資料庫存取限制
- [故障排除](docs/troubleshooting.md) — 資料庫連線、Web 介面、初始化失敗
- [備份和還原](docs/backup-restore.md)
- [新增、掛載、啟動自訂模組（Custom Module）](docs/custom-modules.md)
- [升級 Tryton](docs/upgrade.md)

## 學習操作手冊

跟著 [`tryton_business_flow.md`](docs/tryton_business_flow.md) 課程實際操作的記錄，依 admin／ordinary user 角色分開寫，見 [`manuals/`](manuals/README.md)。

## 詳細資訊

- [Tryton 官方文件](https://docs.tryton.org/)
- [PostgreSQL 官方文件](https://www.postgresql.org/docs/)

## 相關討論

基於此討論: https://discuss.tryton.org/t/how-to-run-tryton-using-docker/3200
