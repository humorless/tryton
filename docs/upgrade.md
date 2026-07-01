# 升級 Tryton

1. 停止所有服務：
   ```bash
   docker compose down
   ```
2. 更新 docker-compose.yml 中的 Tryton 映像版本
3. 拉取新映像：
   ```bash
   docker compose pull
   ```
4. 啟動 PostgreSQL：
   ```bash
   docker compose up -d postgres
   ```
5. 更新所有模組（臨時容器）：
   ```bash
   docker compose run -it --rm trytond trytond-admin -d tryton --all
   ```
6. 啟動新的 Tryton 伺服器：
   ```bash
   docker compose up -d trytond
   ```
