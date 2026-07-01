# 安全建議

## 生產環境更改

1. **更改預設密碼**
   - 編輯 `docker-compose.yml` 中的密碼
   - 執行資料庫初始化後更改 admin 用戶密碼

2. **啟用 SSL/TLS**
   - 在 `docker-compose.yml` 中取消註釋 Nginx 反向代理
   - 配置 SSL 證書

3. **限制資料庫存取**
   - 移除或更改資料庫的外部連接埠（目前為 5432）
   - 只允許 Tryton 容器連接

4. **重置管理員密碼**
   ```bash
   docker compose exec trytond trytond-admin -d tryton --reset-password
   ```
