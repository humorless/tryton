# 新增、掛載、啟動自訂模組（Custom Module）

⚠️ **重要**：Tryton 8.0 的模組載入機制，只會掃描：

1. trytond 套件自己安裝目錄下的 `modules/`（image 內為
   `/usr/local/lib/python3.13/dist-packages/trytond/modules/`），或
2. 透過 pip 套件宣告的 `trytond.modules` entry point

`trytond.conf` **沒有** `[modules] path = ...` 這種設定，即使寫了也不會被讀取。
把自訂模組資料夾掛到別的路徑（例如 `/var/lib/trytond/modules`）不會被 Tryton 掃到。

## 1. 建立模組目錄

在 `modules/` 底下建立一個資料夾，**資料夾名稱必須和 `__init__.py` 裡
`Pool.register(..., module='xxx')` 的 `module` 名稱完全一致**，例如：

```
modules/hello_world/
├── __init__.py       # Pool.register(hello.HelloWorld, module='hello_world', ...)
├── hello.py
├── tryton.cfg
├── hello.xml          # 選填：定義 menu / view / action
└── view/
    ├── hello_form.xml
    └── hello_list.xml
```

`tryton.cfg` 範例：

```ini
[tryton]
version=8.0.4
depends:
    ir
    res
xml:
    hello.xml
```

若模組只有 model、沒有 `xml:` 內的 menu／view 定義，啟用後在 UI 上仍然**看不到任何入口**
（模型會存在、資料表也會建立，但沒有選單可以點進去），務必記得加上
`ir.ui.view` / `ir.action.act_window` / `menuitem` 的 XML 資料。

## 2. 在 docker-compose.yml 掛載模組

**逐一**掛進 trytond 套件安裝目錄底下對應的子目錄名稱（不要整個 `modules/` 目錄掛上去，
那樣會蓋掉裡面所有內建模組！）：

```yaml
volumes:
  - tryton-data:/var/lib/trytond
  - ./modules/hello_world:/usr/local/lib/python3.13/dist-packages/trytond/modules/hello_world
  - ./trytond.conf:/etc/trytond.conf:ro
```

新增其他模組時，比照上面格式再加一行。

## 3. 讓 container 套用新的掛載設定

**單純 `docker compose restart` 不會套用新的 `volumes:` 設定**，必須用
`up -d` 讓 compose 重新建立容器：

```bash
docker compose up -d trytond
```

確認掛載成功：

```bash
docker compose exec trytond ls /usr/local/lib/python3.13/dist-packages/trytond/modules/hello_world
```

## 4. 更新模組清單、啟用模組

```bash
# 讓 trytond 掃描新模組並寫入 ir_module 表
docker compose exec trytond trytond-admin -d tryton --update-modules-list

# 啟用模組（會自動載入 xml、建資料表、建 menu）
docker compose exec trytond trytond-admin -d tryton -u hello_world --activate-dependencies
```

也可以改用 UI：登入後到 Administration → Modules，找到模組點 Activate，
再按「Perform Pending Actions」。

## 5. 重啟 trytond 讓正在跑的 web worker 重新載入

`trytond-admin` 是獨立的一次性程序，不會讓正在運行中的 gunicorn worker
即時看到新啟用的模組，所以啟用後要重啟一次：

```bash
docker compose restart trytond
```

之後重新整理瀏覽器，應該就能在對應選單看到新模組。
