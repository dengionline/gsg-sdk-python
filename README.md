Клиент GSG API на Python
==================

Описание протокола:
* [RU] http://dengionline.com/dev/protocol/gsg_protocol
* [EN] http://dengionline.com/eng/dev/protocol/gsg_protocol

Требуемые модули:
* Python 2.7
  * calendar
  * time
  * json
  * requests
  * hashlib
  * requests

Пример использования:

```
from gsgclient.client import GSGClient

client = GSGClient()

response = client.check(
	txn_id = 0,
	paysystem = 7,
	account = '9522771693',
	amount = 1,
	currency = 'RUB'
)

print(response)
```
