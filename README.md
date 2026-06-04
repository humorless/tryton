# Tryton Docker Setup

這個 docker-compose 配置可以快速啟動完整的 Tryton ERP 系統，包含 PostgreSQL 資料庫和應用伺服器。

## 系統要求

- Docker
- Docker Compose
- 至少 2GB RAM
- 至少 1GB 磁碟空間

## 快速開始

### 1. 啟動服務

```bash
docker-compose up -d
```

### 2. 初始化資料庫（首次運行）

```bash
docker-compose exec trytond trytond-admin -c /etc/trytond/trytond.conf -u all -d tryton
```

或者使用以下命令一步完成：

```bash
docker-compose run --rm trytond trytond-admin -c /etc/trytond/trytond.conf -u all -d tryton
```

### 3. 存取 Tryton

打開瀏覽器訪問：
```
http://localhost:8000/
```

預設登入帳號：
- **用戶名**: admin
- **密碼**: admin（初始密碼，建議更改）

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
docker-compose logs -f

# 只查看 Tryton 伺服器日誌
docker-compose logs -f trytond

# 只查看資料庫日誌
docker-compose logs -f postgres
```

### 停止服務

```bash
# 停止但保留卷
docker-compose stop

# 停止並移除容器（卷保留）
docker-compose down

# 完全清除（包括卷）
docker-compose down -v
```

### 重新啟動

```bash
docker-compose restart trytond
```

### 進入容器 Shell

```bash
# Tryton 伺服器
docker-compose exec trytond sh

# 資料庫
docker-compose exec postgres psql -U tryton -d tryton
```

## 安全建議

### 生產環境更改

1. **更改預設密碼**
   - 編輯 `docker-compose.yml` 中的密碼
   - 執行資料庫初始化後更改 admin 用戶密碼

2. **啟用 SSL/TLS**
   - 在 `docker-compose.yml` 中取消註釋 Nginx 反向代理
   - 配置 SSL 證書

3. **限制資料庫存取**
   - 移除或更改資料庫的外部連接埠（目前為 5432）
   - 只允許 Tryton 容器連接

4. **更新預設管理員密碼**
   ```bash
   docker-compose exec trytond trytond-admin -c /etc/trytond/trytond.conf -u admin -d tryton
   ```

## 故障排除

### 無法連接資料庫

檢查 PostgreSQL 是否正確啟動：
```bash
docker-compose logs postgres
```

確保密碼和連接設定符合 `docker-compose.yml` 和 `trytond.conf`。

### 無法存取 Web 介面

1. 檢查 Tryton 伺服器是否執行中：
   ```bash
   docker-compose logs trytond
   ```

2. 檢查連接埠 8000 是否被佔用

3. 嘗試重啟服務：
   ```bash
   docker-compose restart trytond
   ```

### 資料庫初始化失敗

1. 確保 PostgreSQL 已完全啟動（檢查健康檢查）
2. 查看詳細日誌：
   ```bash
   docker-compose logs trytond
   ```
3. 嘗試手動運行初始化命令並查看輸出

## 備份和還原

### 備份資料庫

```bash
docker-compose exec postgres pg_dump -U tryton tryton > backup.sql
```

### 還原資料庫

```bash
docker-compose exec -T postgres psql -U tryton tryton < backup.sql
```

## 升級 Tryton

1. 更新 docker-compose.yml 中的 Tryton 映像版本
2. 停止現有服務：
   ```bash
   docker-compose down
   ```
3. 拉取新映像：
   ```bash
   docker-compose pull
   ```
4. 啟動新服務：
   ```bash
   docker-compose up -d
   ```
5. 更新所有模組：
   ```bash
   docker-compose exec trytond trytond-admin -c /etc/trytond/trytond.conf -u all -d tryton
   ```

## 詳細資訊

- [Tryton 官方文件](https://docs.tryton.org/)
- [Tryton Docker 映像](https://hub.docker.com/_/tryton)
- [PostgreSQL 官方文件](https://www.postgresql.org/docs/)

## 相關討論

基於此討論: https://discuss.tryton.org/t/how-to-run-tryton-using-docker/3200
