# 故障排除

## 無法連接資料庫

檢查 PostgreSQL 是否正確啟動：
```bash
docker compose logs postgres
```

確保密碼和連接設定符合 `docker-compose.yml` 和 `trytond.conf`。

## 無法存取 Web 介面

1. 檢查 Tryton 伺服器是否執行中：
   ```bash
   docker compose logs trytond
   ```

2. 檢查連接埠 8000 是否被佔用

3. 嘗試重啟服務：
   ```bash
   docker compose restart trytond
   ```

## 資料庫初始化失敗

1. 確保 PostgreSQL 已完全啟動：
   ```bash
   docker compose logs postgres
   ```
2. 檢查 PostgreSQL 連接：
   ```bash
   docker compose exec postgres pg_isready -U tryton
   ```
3. 重新運行初始化命令：
   ```bash
   docker compose run -it --rm trytond trytond-admin -d tryton --all
   ```
