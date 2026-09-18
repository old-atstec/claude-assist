# Яндекс Алиса → AI Subscription Assist → колонка

Свободный текст с Алисы попадает в агента Claude, ответ озвучивается на колонке,
с которой спросили. Пример живой конфигурации: [examples/alisa_claude.yaml](examples/alisa_claude.yaml)
(кладётся в `/config/packages/`).

## Схема

```
Алиса ─► навык Яндекс.Диалогов ─HTTPS─► /api/yandex_dialogs (HA, компонент yandex_dialogs)
              │ python-обработчик: сразу «Секунду, думаю» (лимит Яндекса ~3 c)
              ▼ event alisa_claude_request {text, application_id}
        automation ─► conversation.process (агент из input_select.alisa_claude_agent)
                  ─► media_player.play_media type=text на колонку (yandex_station)
```

Ответ приходится озвучивать асинхронно: Яндекс ждёт ответ навыка ~3 секунды,
Claude с инструментами отвечает 2–15 с.

## Что нужно

- [AlexxIT/YandexStation](https://github.com/AlexxIT/YandexStation) — колонки как `media_player`, TTS.
- [AlexxIT/YandexDialogs](https://github.com/AlexxIT/YandexDialogs) — приём вебхука навыка.
- Публичный HTTPS-URL до `/api/yandex_dialogs`. Достаточно опубликовать только этот path
  (в примере — reverse-туннель frp до traefik в k3s).
- Агенту, который отвечает Алисе, включить **Assist API** (`llm_hass_api`), иначе он не
  сможет управлять устройствами.
- **HA ≥ 2026.9**: секция `http:` в YAML игнорируется; `use_x_forwarded_for` и
  `trusted_proxies` задаются в UI (Настройки → Система → Сеть). Без этого HA отвечает
  `400 Bad Request` на запросы через прокси.

## Настройка

1. Скопировать `examples/alisa_claude.yaml` в `/config/packages/`, поправить:
   - `agents:` — свои `conversation.*` entity_id;
   - `default_speaker:` и `speakers:` — `application_id` → колонка (id видны в логе HA
     по строкам `alisa: application_id=…` после первого обращения с каждой колонки).
2. Перезапустить HA.
3. Настройки → Интеграции → Добавить → **Yandex Dialogs**: аккаунт Яндекса, публичный URL
   HA, имя навыка из двух слов. Интеграция сама создаст приватный навык и впишет
   `user_id` в белый список.
4. Говорить: «Алиса, **попроси <Имя навыка>** включить свет в прихожей». Без имени навыка
   фразу обработает сама Алиса.

## Управление из UI

- `input_select.alisa_claude_agent` — какой агент отвечает.
- `input_text.alisa_claude_voice` — голос колонки (`<speaker voice="…">`, пусто = Алиса).
- Трассировки автоматизации «Алиса → Claude → колонка» — полный разбор каждого запроса.
- Настройки → Система → Журналы → полный журнал → `alisa:` — по две строки на запрос.
- Панель **AI Assist Memory** → Sessions, scope `all` — транскрипты (владелец `automation`,
  память у entry должна быть включена).
