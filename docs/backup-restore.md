# 備份和還原

## 備份資料庫

```bash
docker compose exec -T postgres pg_dump -U tryton tryton > backup.sql
```

## 還原資料庫

```bash
docker compose exec -T postgres psql -U tryton tryton < backup.sql
```
