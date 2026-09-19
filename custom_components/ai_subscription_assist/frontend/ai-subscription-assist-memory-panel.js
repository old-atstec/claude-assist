const WS = {
  ENTRY_LIST: "ai_subscription_assist/entry_list",
  MEMORY_STATUS: "ai_subscription_assist/memory_status",
  MEMORY_LIST: "ai_subscription_assist/memory_list",
  MEMORY_DELETE: "ai_subscription_assist/memory_delete",
  MEMORY_CLEAR: "ai_subscription_assist/memory_clear",
  SESSION_LIST: "ai_subscription_assist/session_list",
  SESSION_GET: "ai_subscription_assist/session_get",
  SESSION_CLEAR: "ai_subscription_assist/session_clear",
};

// Panel UI strings. The panel picks the language from the HA user profile
// (hass.language) and falls back to English for any missing key.
const STRINGS = {
  en: {
    title: "AI Assist Memory",
    subtitle: "Long-term memories and resumable Assist sessions",
    entry: "Provider entry",
    refresh: "Refresh",
    loading: "Loading…",
    no_entries: "No AI Subscription Assist entries found. Add the integration first.",
    error_ws: "Home Assistant WebSocket connection is unavailable.",
    error_generic: "Unexpected error while loading the memory panel.",
    settings: "Settings",
    memory_on: "Memory enabled",
    memory_off: "Memory disabled",
    stat_shared: "Shared memories",
    stat_own: "Your memories",
    stat_sessions: "Your sessions",
    stat_sessions_total: "All sessions",
    stat_users: "Users with memories",
    setting_auto_write: "Auto-capture",
    setting_auto_recall: "Auto-recall",
    setting_resume: "Resume context",
    setting_ttl: "Retention {days} d",
    setting_max: "Max {n} per scope",
    setting_top_k: "Recall top {n}",
    setting_resume_max: "Resume {n} msgs",
    on: "on",
    off: "off",
    tab_memories: "Memories",
    tab_sessions: "Sessions",
    scope: "Scope",
    scope_mine: "Mine",
    scope_shared: "Shared",
    scope_all: "All",
    limit: "Limit",
    target_user: "User",
    target_user_me: "Me",
    target_user_placeholder: "user_id (optional)",
    search: "Search",
    search_placeholder: "Filter by text, ID or scope",
    agent: "Agent",
    agent_all: "All agents",
    clear_scope: "Clear scope",
    delete: "Delete",
    view: "Open",
    clear: "Clear",
    back: "Back to sessions",
    clear_this_session: "Clear this session",
    memories_empty: "No memories match the current filter.",
    memories_count: "Showing {shown} of {total}",
    sessions_empty: "No sessions match the current filter.",
    session_detail: "Session",
    scope_user: "Personal",
    scope_shared_badge: "Shared",
    source_slash: "command",
    source_heuristic: "auto",
    updated: "Updated",
    created: "Created",
    copy_id: "Copy ID",
    copied: "ID copied to clipboard.",
    copy_failed: "Could not copy — select the ID manually.",
    messages_count: { one: "{n} message", other: "{n} messages" },
    role_user: "User",
    role_assistant: "Assistant",
    role_system: "System",
    unknown_agent: "Unknown agent",
    user_label: "User {id}",
    confirm_delete_memory: "Delete this memory?\n\n{text}",
    confirm_clear_memories:
      "Delete all memories in scope “{scope}”? This cannot be undone.",
    confirm_clear_session: "Clear session “{name}”? This cannot be undone.",
    confirm_clear_sessions:
      "Clear all sessions in scope “{scope}”? This cannot be undone.",
    toast_memory_deleted: "Memory deleted.",
    toast_memory_not_deleted: "Memory was not deleted (not found or not permitted).",
    toast_memories_cleared: { one: "{n} memory removed.", other: "{n} memories removed." },
    toast_sessions_cleared: "Removed {s} session(s) and {m} message(s).",
  },
  ru: {
    title: "Память AI Assist",
    subtitle: "Долговременная память и возобновляемые сессии Assist",
    entry: "Запись провайдера",
    refresh: "Обновить",
    loading: "Загрузка…",
    no_entries: "Записи AI Subscription Assist не найдены. Сначала добавьте интеграцию.",
    error_ws: "WebSocket-соединение с Home Assistant недоступно.",
    error_generic: "Непредвиденная ошибка при загрузке панели памяти.",
    settings: "Настройки",
    memory_on: "Память включена",
    memory_off: "Память выключена",
    stat_shared: "Общие записи",
    stat_own: "Ваши записи",
    stat_sessions: "Ваши сессии",
    stat_sessions_total: "Все сессии",
    stat_users: "Пользователей с памятью",
    setting_auto_write: "Автозапись",
    setting_auto_recall: "Автоподстановка",
    setting_resume: "Продолжение диалога",
    setting_ttl: "Хранение {days} дн.",
    setting_max: "Не более {n} на область",
    setting_top_k: "Подстановка до {n}",
    setting_resume_max: "Продолжение {n} сообщ.",
    on: "вкл",
    off: "выкл",
    tab_memories: "Память",
    tab_sessions: "Сессии",
    scope: "Область",
    scope_mine: "Мои",
    scope_shared: "Общие",
    scope_all: "Все",
    limit: "Лимит",
    target_user: "Пользователь",
    target_user_me: "Я",
    target_user_placeholder: "user_id (необязательно)",
    search: "Поиск",
    search_placeholder: "По тексту, ID или области",
    agent: "Агент",
    agent_all: "Все агенты",
    clear_scope: "Очистить область",
    delete: "Удалить",
    view: "Открыть",
    clear: "Очистить",
    back: "К списку сессий",
    clear_this_session: "Очистить эту сессию",
    memories_empty: "Нет записей по текущему фильтру.",
    memories_count: "Показано {shown} из {total}",
    sessions_empty: "Нет сессий по текущему фильтру.",
    session_detail: "Сессия",
    scope_user: "Личная",
    scope_shared_badge: "Общая",
    source_slash: "команда",
    source_heuristic: "авто",
    updated: "Обновлено",
    created: "Создано",
    copy_id: "Скопировать ID",
    copied: "ID скопирован в буфер обмена.",
    copy_failed: "Не удалось скопировать — выделите ID вручную.",
    messages_count: {
      one: "{n} сообщение",
      few: "{n} сообщения",
      many: "{n} сообщений",
      other: "{n} сообщений",
    },
    role_user: "Пользователь",
    role_assistant: "Ассистент",
    role_system: "Система",
    unknown_agent: "Неизвестный агент",
    user_label: "Пользователь {id}",
    confirm_delete_memory: "Удалить эту запись?\n\n{text}",
    confirm_clear_memories:
      "Удалить все записи в области «{scope}»? Это действие нельзя отменить.",
    confirm_clear_session: "Очистить сессию «{name}»? Это действие нельзя отменить.",
    confirm_clear_sessions:
      "Очистить все сессии в области «{scope}»? Это действие нельзя отменить.",
    toast_memory_deleted: "Запись удалена.",
    toast_memory_not_deleted: "Запись не удалена (не найдена или нет прав).",
    toast_memories_cleared: {
      one: "Удалена {n} запись.",
      few: "Удалено {n} записи.",
      many: "Удалено {n} записей.",
      other: "Удалено {n} записей.",
    },
    toast_sessions_cleared: "Удалено сессий: {s}, сообщений: {m}.",
  },
};

const ICONS = {
  refresh:
    "M17.65 6.35A7.96 7.96 0 0 0 12 4a8 8 0 1 0 7.73 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35Z",
  delete:
    "M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6v12ZM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4Z",
  copy: "M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1Zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Zm0 16H8V7h11v14Z",
  back: "M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2Z",
  open: "M9 5v2h6.59L4 18.59 5.41 20 17 8.41V15h2V5H9Z",
  brain:
    "M12 3a4 4 0 0 0-3.9 3.1A3.5 3.5 0 0 0 5 9.5c0 .6.15 1.16.42 1.66A3.5 3.5 0 0 0 4 14a3.5 3.5 0 0 0 3.1 3.48A3.5 3.5 0 0 0 10.5 21c.57 0 1.1-.14 1.5-.38.4.24.93.38 1.5.38a3.5 3.5 0 0 0 3.4-3.52A3.5 3.5 0 0 0 20 14a3.5 3.5 0 0 0-1.42-2.84c.27-.5.42-1.06.42-1.66a3.5 3.5 0 0 0-3.1-3.4A4 4 0 0 0 12 3Z",
};

function icon(name) {
  return `<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS[name]}"/></svg>`;
}

class AiSubscriptionAssistMemoryPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._initialized = false;
    this._lang = "en";
    this._isAdmin = false;
    this._userId = null;
    this._state = {
      loading: false,
      error: "",
      entries: [],
      selectedEntryId: "",
      status: null,
      users: [],
      tab: "memories",
      memoryScope: "mine",
      memoryLimit: 50,
      memorySearch: "",
      memoryTargetUserId: "",
      memories: [],
      sessionScope: "mine",
      sessionLimit: 50,
      sessionSubentryId: "",
      sessionTargetUserId: "",
      sessions: [],
      selectedSession: null,
    };

    // One delegated listener per event type: the DOM is re-rendered from
    // state, so nothing needs to be re-bound after each render.
    this.shadowRoot.addEventListener("click", (event) => this._onClick(event));
    this.shadowRoot.addEventListener("change", (event) => this._onChange(event));
    this.shadowRoot.addEventListener("input", (event) => this._onInput(event));
  }

  set hass(hass) {
    const prev = this._hass;
    this._hass = hass;
    const lang = this._resolveLang(hass);
    const isAdmin = Boolean(hass?.user?.is_admin);
    const userId = hass?.user?.id || null;
    const changed =
      lang !== this._lang || isAdmin !== this._isAdmin || userId !== this._userId;
    this._lang = lang;
    this._isAdmin = isAdmin;
    this._userId = userId;

    if (!this._initialized) {
      this._initialized = true;
      this._bootstrap();
      return;
    }
    // hass is re-assigned on every state change in HA; only re-render when
    // something the panel actually displays has changed.
    if (changed || !prev) {
      this._render();
    }
  }

  set panel(_panel) {
    // Home Assistant sets this when rendering a panel.
  }

  set narrow(_narrow) {
    // Layout is driven by container queries; nothing to do.
  }

  connectedCallback() {
    this._render();
  }

  // ---------------------------------------------------------------------
  // i18n helpers
  // ---------------------------------------------------------------------

  _resolveLang(hass) {
    const raw = String(hass?.language || hass?.locale?.language || "en").toLowerCase();
    const short = raw.split(/[-_]/)[0];
    return STRINGS[short] ? short : "en";
  }

  _t(key, params = {}) {
    let template = STRINGS[this._lang]?.[key] ?? STRINGS.en[key] ?? key;
    if (typeof template === "object") {
      const n = Number(params.n ?? 0);
      let category = "other";
      try {
        category = new Intl.PluralRules(this._lang).select(n);
      } catch (_err) {
        category = n === 1 ? "one" : "other";
      }
      template = template[category] ?? template.other ?? "";
    }
    return String(template).replace(/\{(\w+)\}/g, (_m, name) =>
      params[name] === undefined ? `{${name}}` : String(params[name])
    );
  }

  _formatDate(iso) {
    if (!iso) {
      return "";
    }
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) {
      return String(iso);
    }
    try {
      return new Intl.DateTimeFormat(this._lang, {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(date);
    } catch (_err) {
      return date.toLocaleString();
    }
  }

  _formatRelative(iso) {
    if (!iso) {
      return "";
    }
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) {
      return String(iso);
    }
    const diffSec = Math.round((date.getTime() - Date.now()) / 1000);
    const abs = Math.abs(diffSec);
    if (abs > 7 * 86400) {
      return this._formatDate(iso);
    }
    const units = [
      ["day", 86400],
      ["hour", 3600],
      ["minute", 60],
    ];
    try {
      const rtf = new Intl.RelativeTimeFormat(this._lang, { numeric: "auto" });
      for (const [unit, seconds] of units) {
        if (abs >= seconds) {
          return rtf.format(Math.round(diffSec / seconds), unit);
        }
      }
      return rtf.format(diffSec, "second");
    } catch (_err) {
      return this._formatDate(iso);
    }
  }

  // ---------------------------------------------------------------------
  // Data access
  // ---------------------------------------------------------------------

  async _bootstrap() {
    try {
      await this._loadEntries();
      await this._loadUsers();
      await this._refreshAll();
    } catch (err) {
      this._setError(err);
    }
  }

  _setState(patch, { render = true } = {}) {
    this._state = { ...this._state, ...patch };
    if (render) {
      this._render();
    }
  }

  _setError(err) {
    const message =
      typeof err === "string" ? err : err?.message || this._t("error_generic");
    this._setState({ error: message, loading: false });
  }

  _toast(message) {
    this.dispatchEvent(
      new CustomEvent("hass-notification", {
        detail: { message },
        bubbles: true,
        composed: true,
      })
    );
  }

  async _ws(type, payload = {}) {
    if (!this._hass?.connection) {
      throw new Error(this._t("error_ws"));
    }
    return this._hass.connection.sendMessagePromise({ type, ...payload });
  }

  async _loadEntries() {
    const response = await this._ws(WS.ENTRY_LIST);
    const entries = Array.isArray(response?.entries) ? response.entries : [];
    let selectedEntryId = this._state.selectedEntryId;
    if (!selectedEntryId && entries.length > 0) {
      selectedEntryId = entries[0].entry_id;
    } else if (
      selectedEntryId &&
      !entries.some((entry) => entry.entry_id === selectedEntryId)
    ) {
      selectedEntryId = entries.length > 0 ? entries[0].entry_id : "";
    }
    this._setState({ entries, selectedEntryId });
  }

  async _loadUsers() {
    // Admin-only: lets the panel show user names instead of raw ids.
    if (!this._isAdmin) {
      return;
    }
    try {
      const users = await this._ws("config/auth/list");
      if (Array.isArray(users)) {
        this._setState(
          {
            users: users
              .filter((user) => user?.id)
              .map((user) => ({ id: user.id, name: user.name || user.username || user.id })),
          },
          { render: false }
        );
      }
    } catch (_err) {
      // Not fatal: ids are shown instead.
    }
  }

  _selectedEntry() {
    return this._state.entries.find(
      (entry) => entry.entry_id === this._state.selectedEntryId
    );
  }

  _basePayload() {
    return this._state.selectedEntryId
      ? { config_entry_id: this._state.selectedEntryId }
      : {};
  }

  async _refreshStatus() {
    const status = await this._ws(WS.MEMORY_STATUS, this._basePayload());
    this._setState({ status }, { render: false });
  }

  async _refreshMemories() {
    const payload = {
      ...this._basePayload(),
      scope: this._state.memoryScope,
      limit: Number(this._state.memoryLimit) || 50,
    };
    if (this._isAdmin && this._state.memoryTargetUserId.trim()) {
      payload.target_user_id = this._state.memoryTargetUserId.trim();
    }
    const response = await this._ws(WS.MEMORY_LIST, payload);
    const memories = Array.isArray(response?.items) ? response.items : [];
    this._setState({ memories }, { render: false });
  }

  async _refreshSessions() {
    const payload = {
      ...this._basePayload(),
      scope: this._state.sessionScope,
      limit: Number(this._state.sessionLimit) || 50,
    };
    if (this._state.sessionSubentryId.trim()) {
      payload.subentry_id = this._state.sessionSubentryId.trim();
    }
    if (this._isAdmin && this._state.sessionTargetUserId.trim()) {
      payload.target_user_id = this._state.sessionTargetUserId.trim();
    }
    const response = await this._ws(WS.SESSION_LIST, payload);
    const sessions = Array.isArray(response?.sessions) ? response.sessions : [];
    this._setState({ sessions }, { render: false });
  }

  async _refreshAll() {
    this._setState({ loading: true, error: "" });
    try {
      await Promise.all([
        this._refreshStatus(),
        this._refreshMemories(),
        this._refreshSessions(),
      ]);
      this._setState({ loading: false });
    } catch (err) {
      this._setError(err);
    }
  }

  async _run(action) {
    this._setState({ loading: true, error: "" });
    try {
      await action();
      this._setState({ loading: false });
    } catch (err) {
      this._setError(err);
    }
  }

  async _withWrite(action) {
    await this._run(async () => {
      await action();
      await Promise.all([
        this._refreshStatus(),
        this._refreshMemories(),
        this._refreshSessions(),
      ]);
    });
  }

  async _deleteMemory(memoryId) {
    const item = this._state.memories.find((memory) => memory.id === memoryId);
    const preview = this._truncate(item?.text || memoryId, 160);
    if (!window.confirm(this._t("confirm_delete_memory", { text: preview }))) {
      return;
    }
    await this._withWrite(async () => {
      const response = await this._ws(WS.MEMORY_DELETE, {
        ...this._basePayload(),
        memory_id: memoryId,
      });
      if (!response?.deleted) {
        throw new Error(this._t("toast_memory_not_deleted"));
      }
      this._toast(this._t("toast_memory_deleted"));
    });
  }

  async _clearMemories() {
    const scope = this._t(`scope_${this._state.memoryScope}`);
    if (!window.confirm(this._t("confirm_clear_memories", { scope }))) {
      return;
    }
    await this._withWrite(async () => {
      const payload = {
        ...this._basePayload(),
        scope: this._state.memoryScope,
        confirm: true,
      };
      if (this._isAdmin && this._state.memoryTargetUserId.trim()) {
        payload.target_user_id = this._state.memoryTargetUserId.trim();
      }
      const response = await this._ws(WS.MEMORY_CLEAR, payload);
      this._toast(this._t("toast_memories_cleared", { n: response?.removed || 0 }));
    });
  }

  async _selectSession(sessionId) {
    await this._run(async () => {
      const response = await this._ws(WS.SESSION_GET, {
        ...this._basePayload(),
        session_id: sessionId,
        limit: 500,
      });
      this._setState({ selectedSession: response?.session || null }, { render: false });
    });
    this._scrollTop();
  }

  async _clearSession(sessionId = null) {
    const message = sessionId
      ? this._t("confirm_clear_session", {
          name: this._sessionName(this._sessionById(sessionId) || { session_id: sessionId }),
        })
      : this._t("confirm_clear_sessions", {
          scope: this._t(`scope_${this._state.sessionScope}`),
        });
    if (!window.confirm(message)) {
      return;
    }
    await this._withWrite(async () => {
      const payload = {
        ...this._basePayload(),
        scope: this._state.sessionScope,
        confirm: true,
      };
      if (sessionId) {
        payload.session_id = sessionId;
      } else {
        if (this._state.sessionSubentryId.trim()) {
          payload.subentry_id = this._state.sessionSubentryId.trim();
        }
        if (this._isAdmin && this._state.sessionTargetUserId.trim()) {
          payload.target_user_id = this._state.sessionTargetUserId.trim();
        }
      }
      const response = await this._ws(WS.SESSION_CLEAR, payload);
      if (!sessionId || this._state.selectedSession?.session_id === sessionId) {
        this._setState({ selectedSession: null }, { render: false });
      }
      this._toast(
        this._t("toast_sessions_cleared", {
          s: response?.removed_sessions || 0,
          m: response?.removed_messages || 0,
        })
      );
    });
  }

  async _copyText(text) {
    try {
      if (navigator.clipboard?.writeText && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // HTTP-only installs have no async clipboard; fall back to execCommand.
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.select();
        const ok = document.execCommand("copy");
        area.remove();
        if (!ok) {
          throw new Error("execCommand failed");
        }
      }
      this._toast(this._t("copied"));
    } catch (_err) {
      this._toast(this._t("copy_failed"));
    }
  }

  // ---------------------------------------------------------------------
  // Derived data
  // ---------------------------------------------------------------------

  _filteredMemories() {
    const query = String(this._state.memorySearch || "").trim().toLowerCase();
    if (!query) {
      return this._state.memories;
    }
    return this._state.memories.filter((item) => {
      const haystack = [item?.text, item?.id, item?.scope, this._userName(item?.user_id)]
        .map((value) => String(value || "").toLowerCase())
        .join("\n");
      return haystack.includes(query);
    });
  }

  _sessionById(sessionId) {
    return this._state.sessions.find((session) => session.session_id === sessionId);
  }

  _agentTitle(subentryId) {
    const entry = this._selectedEntry();
    const subentry = (entry?.subentries || []).find(
      (item) => item.subentry_id === subentryId
    );
    if (subentry?.title) {
      return subentry.title;
    }
    return subentryId ? this._shortId(subentryId) : this._t("unknown_agent");
  }

  _userName(userId) {
    if (!userId) {
      return "";
    }
    const user = this._state.users.find((item) => item.id === userId);
    if (user) {
      return user.name;
    }
    if (userId === this._userId) {
      return this._t("target_user_me");
    }
    return this._t("user_label", { id: this._shortId(userId) });
  }

  _sessionName(session) {
    const agent = this._agentTitle(session?.subentry_id);
    const owner = session?.user_id ? this._userName(session.user_id) : "";
    return owner ? `${agent} · ${owner}` : agent;
  }

  _shortId(id) {
    const value = String(id || "");
    return value.length > 12 ? `${value.slice(0, 8)}…` : value;
  }

  _truncate(text, max) {
    const value = String(text || "");
    return value.length > max ? `${value.slice(0, max - 1)}…` : value;
  }

  _escape(text) {
    return String(text ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  _scrollTop() {
    try {
      this.shadowRoot.querySelector(".tabs")?.scrollIntoView({ block: "start" });
    } catch (_err) {
      // ignore
    }
  }

  // ---------------------------------------------------------------------
  // Rendering
  // ---------------------------------------------------------------------

  _styles() {
    return `
      :host {
        display: block;
        box-sizing: border-box;
        padding: 12px;
        color: var(--primary-text-color);
        font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif);
        -webkit-font-smoothing: antialiased;
      }
      *, *::before, *::after { box-sizing: border-box; }
      .wrap {
        container-type: inline-size;
        max-width: 1100px;
        margin: 0 auto;
        display: grid;
        gap: 12px;
      }
      @media (min-width: 900px) {
        :host { padding: 24px; }
        .wrap { gap: 16px; }
      }

      /* ---- typography ---- */
      h1, h2, h3 { margin: 0; font-weight: 500; line-height: 1.25; }
      h1 { font-size: 22px; display: flex; align-items: center; gap: 8px; }
      h2 { font-size: 17px; }
      h3 { font-size: 15px; }
      p { margin: 0; }
      .muted { color: var(--secondary-text-color); font-size: 13px; }
      .mono {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 12px;
      }
      .ico { width: 18px; height: 18px; fill: currentColor; flex: none; }

      /* ---- cards ---- */
      .card {
        background: var(--ha-card-background, var(--card-background-color, #fff));
        border-radius: var(--ha-card-border-radius, 12px);
        border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
        box-shadow: var(--ha-card-box-shadow, none);
        padding: 16px;
        display: grid;
        gap: 12px;
        min-width: 0;
      }
      /* Grid/flex children default to min-width:auto, which lets long ids
         and nowrap chips widen the page on phones. */
      .card > *, .card-head, .row, .item > * { min-width: 0; }
      .wrap > * { max-width: 100%; }
      .card-head {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 8px 12px;
      }

      /* ---- header ---- */
      .header {
        display: flex;
        flex-wrap: wrap;
        align-items: flex-end;
        justify-content: space-between;
        gap: 12px;
      }
      .header .titles { display: grid; gap: 4px; min-width: 0; }
      .header .actions {
        display: flex;
        flex-wrap: wrap;
        align-items: flex-end;
        gap: 8px;
        flex: 1 1 320px;
        justify-content: flex-end;
      }
      .header .actions .field { flex: 1 1 200px; max-width: 360px; }

      /* ---- form controls ---- */
      .field { display: grid; gap: 4px; min-width: 0; }
      .field > span {
        font-size: 12px;
        color: var(--secondary-text-color);
        white-space: nowrap;
      }
      .field input, .field select {
        width: 100%;
        height: 40px;
        padding: 0 10px;
        border: 1px solid var(--divider-color, #c9c9c9);
        border-radius: 8px;
        background: var(--card-background-color, #fff);
        color: var(--primary-text-color);
        font: inherit;
        font-size: 14px;
        outline: none;
        min-width: 0;
      }
      .field select { padding-right: 28px; appearance: auto; }
      .field input:focus, .field select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary-color) 25%, transparent);
      }
      .filters {
        display: grid;
        gap: 8px;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      }
      .filters .wide { grid-column: 1 / -1; }
      .row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
      }
      .row.end { justify-content: flex-end; }
      .spacer { flex: 1 1 auto; }

      /* ---- buttons ---- */
      .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        min-height: 36px;
        padding: 0 14px;
        border-radius: 18px;
        border: 1px solid transparent;
        background: transparent;
        color: var(--primary-color);
        font: inherit;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: .01em;
        cursor: pointer;
        user-select: none;
        white-space: nowrap;
        transition: background .12s ease, box-shadow .12s ease;
      }
      .btn:hover { background: color-mix(in srgb, currentColor 10%, transparent); }
      .btn:active { background: color-mix(in srgb, currentColor 18%, transparent); }
      .btn:focus-visible { outline: 2px solid var(--primary-color); outline-offset: 2px; }
      .btn[disabled] { opacity: .5; cursor: default; pointer-events: none; }
      .btn.primary {
        background: var(--primary-color);
        color: var(--text-primary-color, #fff);
      }
      .btn.primary:hover { background: color-mix(in srgb, var(--primary-color) 88%, #000); }
      .btn.outline { border-color: currentColor; }
      .btn.danger { color: var(--error-color, #db4437); }
      .btn.small { min-height: 32px; padding: 0 10px; font-size: 13px; }
      .btn.icon { padding: 0 8px; min-width: 36px; }
      .btn .ico { width: 18px; height: 18px; }

      /* ---- tabs ---- */
      .tabs {
        display: flex;
        border-bottom: 1px solid var(--divider-color);
        gap: 4px;
      }
      .tab {
        flex: 1 1 0;
        min-height: 44px;
        padding: 0 12px;
        border: 0;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
        background: transparent;
        color: var(--secondary-text-color);
        font: inherit;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
      }
      .tab:hover { color: var(--primary-text-color); }
      .tab[aria-selected="true"] {
        color: var(--primary-color);
        border-bottom-color: var(--primary-color);
      }
      .tab .count {
        font-size: 12px;
        padding: 1px 7px;
        border-radius: 999px;
        background: color-mix(in srgb, currentColor 12%, transparent);
      }

      /* ---- status ---- */
      .stats {
        display: grid;
        gap: 8px;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
      }
      .stat {
        border: 1px solid var(--divider-color);
        border-radius: 10px;
        padding: 8px 10px;
        display: grid;
        gap: 2px;
        min-width: 0;
        align-content: start;
      }
      .stat .label { font-size: 12px; line-height: 1.25; color: var(--secondary-text-color); }
      .stat .value { font-size: 22px; font-weight: 600; line-height: 1.2; }
      details.settings { min-width: 0; flex: 1 1 260px; }
      details.settings summary {
        cursor: pointer;
        font-size: 13px;
        color: var(--primary-color);
        list-style: none;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        min-height: 28px;
      }
      details.settings summary::-webkit-details-marker { display: none; }
      details.settings summary::before { content: "▸"; font-size: 11px; }
      details.settings[open] summary::before { content: "▾"; }
      details.settings .chips { margin-top: 6px; }
      .chips { display: flex; flex-wrap: wrap; gap: 6px; }
      .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 12px;
        border: 1px solid var(--divider-color);
        color: var(--secondary-text-color);
        max-width: 100%;
        min-width: 0;
      }
      .chip.ok { border-color: color-mix(in srgb, var(--success-color, #43a047) 60%, transparent); color: var(--success-color, #43a047); }
      .chip.off { opacity: .8; }
      .chip.accent { border-color: color-mix(in srgb, var(--primary-color) 55%, transparent); color: var(--primary-color); }
      .chip.warn { border-color: color-mix(in srgb, var(--warning-color, #ffa600) 60%, transparent); color: var(--warning-color, #b26a00); }

      /* ---- item lists ---- */
      .list { display: grid; gap: 8px; }
      .item {
        border: 1px solid var(--divider-color);
        border-radius: 10px;
        padding: 12px;
        display: grid;
        gap: 8px;
        min-width: 0;
      }
      .item-head {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px 8px;
      }
      .item-head .time { margin-left: auto; font-size: 12px; color: var(--secondary-text-color); white-space: nowrap; }
      .item-text {
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        word-break: break-word;
        font-size: 14px;
        line-height: 1.45;
      }
      .item-title {
        font-size: 15px;
        font-weight: 500;
        overflow-wrap: anywhere;
        min-width: 0;
      }
      .item-foot {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px 8px;
        min-width: 0;
      }
      .item-foot .actions { display: flex; gap: 4px; margin-left: auto; }
      .idchip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        max-width: 100%;
        min-width: 0;
        border: 1px dashed var(--divider-color);
        border-radius: 8px;
        padding: 3px 8px;
        background: transparent;
        color: var(--secondary-text-color);
        cursor: pointer;
        font: inherit;
      }
      .idchip:hover { color: var(--primary-text-color); border-style: solid; }
      .idchip .mono {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-width: 0;
        flex: 0 1 auto;
        max-width: 42ch;
      }
      .idchip .ico { width: 14px; height: 14px; }

      /* ---- transcript ---- */
      .transcript { display: grid; gap: 8px; }
      .msg {
        max-width: 92%;
        border-radius: 12px;
        padding: 8px 12px;
        display: grid;
        gap: 4px;
        min-width: 0;
      }
      .msg.user {
        justify-self: end;
        background: color-mix(in srgb, var(--primary-color) 14%, transparent);
        border-bottom-right-radius: 4px;
      }
      .msg.assistant {
        justify-self: start;
        background: color-mix(in srgb, var(--secondary-text-color) 12%, transparent);
        border-bottom-left-radius: 4px;
      }
      .msg.other { justify-self: stretch; border: 1px dashed var(--divider-color); }
      .msg .role { font-size: 12px; font-weight: 600; color: var(--secondary-text-color); }
      .msg .body { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 14px; line-height: 1.45; }
      .msg .time { font-size: 11px; color: var(--secondary-text-color); }

      .empty { padding: 24px 8px; text-align: center; color: var(--secondary-text-color); }
      .error {
        border-radius: 10px;
        padding: 10px 12px;
        background: color-mix(in srgb, var(--error-color, #db4437) 12%, transparent);
        color: var(--error-color, #db4437);
        overflow-wrap: anywhere;
      }
      .progress {
        height: 3px;
        border-radius: 2px;
        background: color-mix(in srgb, var(--primary-color) 25%, transparent);
        overflow: hidden;
        position: relative;
      }
      .progress::after {
        content: "";
        position: absolute;
        inset: 0;
        width: 40%;
        background: var(--primary-color);
        animation: slide 1.1s ease-in-out infinite;
      }
      @keyframes slide {
        from { transform: translateX(-100%); }
        to { transform: translateX(260%); }
      }
      .busy { opacity: .6; pointer-events: none; }

      /* ---- narrow layout ---- */
      @container (max-width: 560px) {
        .header .actions { flex-direction: column; align-items: stretch; }
        .header .actions .field { max-width: none; }
        .header .actions .btn { width: 100%; }
        .row.stack > .spacer { display: none; }
        .row.stack > .muted { flex: 1 1 100%; }
        .row.stack > .btn { flex: 1 1 45%; }
        .item-foot .actions { width: 100%; margin-left: 0; }
        .item-foot .actions .btn { flex: 1 1 0; }
        .idchip { width: 100%; }
        .idchip .mono { max-width: none; flex: 1 1 auto; }
        .msg { max-width: 100%; }
        .stat { padding: 8px; }
        .stat .value { font-size: 18px; }
        .stat .label { font-size: 11px; }
      }
    `;
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }
    const active = this.shadowRoot.activeElement;
    const focusId = active?.id;
    const selection =
      active && typeof active.selectionStart === "number"
        ? [active.selectionStart, active.selectionEnd]
        : null;

    const entry = this._selectedEntry();
    const s = this._state;

    this.shadowRoot.innerHTML = `
      <style>${this._styles()}</style>
      <div class="wrap">
        ${this._renderHeader(entry)}
        ${s.error ? `<div class="error" role="alert">${this._escape(s.error)}</div>` : ""}
        ${s.loading ? `<div class="progress" aria-label="${this._escape(this._t("loading"))}"></div>` : ""}
        ${
          !entry
            ? `<div class="card"><p class="empty">${this._escape(this._t("no_entries"))}</p></div>`
            : `
              ${this._renderStatus(entry)}
              <div class="card ${s.loading ? "busy" : ""}">
                ${this._renderTabs()}
                ${s.tab === "memories" ? this._renderMemories() : this._renderSessions()}
              </div>
            `
        }
      </div>
    `;

    if (focusId) {
      const el = this.shadowRoot.getElementById(focusId);
      if (el) {
        el.focus({ preventScroll: true });
        if (selection && typeof el.setSelectionRange === "function") {
          try {
            el.setSelectionRange(selection[0], selection[1]);
          } catch (_err) {
            // number inputs do not support selection ranges
          }
        }
      }
    }
  }

  _renderHeader(entry) {
    const s = this._state;
    const entrySelect =
      s.entries.length > 1
        ? `
          <label class="field">
            <span>${this._escape(this._t("entry"))}</span>
            <select id="entry-select">
              ${s.entries
                .map(
                  (item) =>
                    `<option value="${this._escape(item.entry_id)}" ${
                      item.entry_id === s.selectedEntryId ? "selected" : ""
                    }>${this._escape(item.title || item.entry_id)}</option>`
                )
                .join("")}
            </select>
          </label>
        `
        : "";
    return `
      <div class="header">
        <div class="titles">
          <h1>${icon("brain")}${this._escape(this._t("title"))}</h1>
          <p class="muted">${this._escape(this._t("subtitle"))}${
            entry && s.entries.length === 1 ? ` · ${this._escape(entry.title || entry.entry_id)}` : ""
          }</p>
        </div>
        <div class="actions">
          ${entrySelect}
          <button class="btn primary" data-action="refresh-all" ${s.loading ? "disabled" : ""}>
            ${icon("refresh")}<span>${this._escape(this._t("refresh"))}</span>
          </button>
        </div>
      </div>
    `;
  }

  _renderStatus(_entry) {
    const status = this._state.status;
    if (!status) {
      return "";
    }
    const counts = status.counts || {};
    const stat = (label, value) => `
      <div class="stat">
        <span class="label">${this._escape(label)}</span>
        <span class="value">${this._escape(value ?? 0)}</span>
      </div>
    `;
    const flag = (label, on) =>
      `<span class="chip ${on ? "ok" : "off"}">${this._escape(label)}: ${this._escape(
        this._t(on ? "on" : "off")
      )}</span>`;
    // Settings chips are collapsed on narrow screens to keep the lists reachable.
    const wide = (this.offsetWidth || 0) > 560;
    return `
      <div class="card">
        <div class="card-head">
          <span class="chip ${status.memory_enabled ? "ok" : "warn"}">
            ${this._escape(this._t(status.memory_enabled ? "memory_on" : "memory_off"))}
          </span>
          <details class="settings" ${wide ? "open" : ""}>
            <summary>${this._escape(this._t("settings"))}</summary>
            <div class="chips">
              ${flag(this._t("setting_auto_write"), status.auto_write)}
              ${flag(this._t("setting_auto_recall"), status.auto_recall)}
              ${flag(this._t("setting_resume"), status.resume_enabled)}
              <span class="chip">${this._escape(this._t("setting_ttl", { days: status.ttl_days }))}</span>
              <span class="chip">${this._escape(this._t("setting_max", { n: status.max_items_per_scope }))}</span>
              <span class="chip">${this._escape(this._t("setting_top_k", { n: status.recall_top_k }))}</span>
              <span class="chip">${this._escape(this._t("setting_resume_max", { n: status.resume_max_messages }))}</span>
            </div>
          </details>
        </div>
        <div class="stats">
          ${stat(this._t("stat_own"), counts.own_user_memories)}
          ${stat(this._t("stat_shared"), counts.shared_memories)}
          ${stat(this._t("stat_sessions"), counts.sessions_mine)}
          ${counts.sessions_total !== undefined ? stat(this._t("stat_sessions_total"), counts.sessions_total) : ""}
          ${counts.user_scopes !== undefined ? stat(this._t("stat_users"), counts.user_scopes) : ""}
        </div>
      </div>
    `;
  }

  _renderTabs() {
    const s = this._state;
    const tab = (id, label, count) => `
      <button class="tab" role="tab" data-action="tab" data-tab="${id}" aria-selected="${
        s.tab === id ? "true" : "false"
      }">
        <span>${this._escape(label)}</span>
        <span class="count">${this._escape(count)}</span>
      </button>
    `;
    return `
      <div class="tabs" role="tablist">
        ${tab("memories", this._t("tab_memories"), s.memories.length)}
        ${tab("sessions", this._t("tab_sessions"), s.sessions.length)}
      </div>
    `;
  }

  _renderUserField(id, value) {
    if (!this._isAdmin) {
      return "";
    }
    const users = this._state.users;
    const control =
      users.length > 0
        ? `
          <select id="${id}">
            <option value="" ${value ? "" : "selected"}>${this._escape(this._t("target_user_me"))}</option>
            ${users
              .map(
                (user) =>
                  `<option value="${this._escape(user.id)}" ${
                    user.id === value ? "selected" : ""
                  }>${this._escape(user.name)}</option>`
              )
              .join("")}
          </select>
        `
        : `<input id="${id}" type="text" value="${this._escape(value)}" placeholder="${this._escape(
            this._t("target_user_placeholder")
          )}">`;
    return `<label class="field"><span>${this._escape(this._t("target_user"))}</span>${control}</label>`;
  }

  _renderScopeField(id, value, scopes) {
    return `
      <label class="field">
        <span>${this._escape(this._t("scope"))}</span>
        <select id="${id}">
          ${scopes
            .map(
              (scope) =>
                `<option value="${scope}" ${scope === value ? "selected" : ""}>${this._escape(
                  this._t(`scope_${scope}`)
                )}</option>`
            )
            .join("")}
        </select>
      </label>
    `;
  }

  _renderLimitField(id, value) {
    return `
      <label class="field">
        <span>${this._escape(this._t("limit"))}</span>
        <input id="${id}" type="number" inputmode="numeric" min="1" max="500" value="${this._escape(value)}">
      </label>
    `;
  }

  _renderIdChip(id) {
    return `
      <button class="idchip" type="button" data-action="copy" data-value="${this._escape(id)}" title="${this._escape(
        this._t("copy_id")
      )}: ${this._escape(id)}">
        ${icon("copy")}<span class="mono">${this._escape(id)}</span>
      </button>
    `;
  }

  _renderMemories() {
    const s = this._state;
    const items = this._filteredMemories();
    const busy = s.loading ? "disabled" : "";
    return `
      <div class="filters">
        ${this._renderScopeField("memory-scope", s.memoryScope, ["mine", "shared", "all"])}
        ${this._renderUserField("memory-target-user", s.memoryTargetUserId)}
        ${this._renderLimitField("memory-limit", s.memoryLimit)}
        <label class="field wide">
          <span>${this._escape(this._t("search"))}</span>
          <input id="memory-search" type="search" value="${this._escape(s.memorySearch)}" placeholder="${this._escape(
            this._t("search_placeholder")
          )}" autocomplete="off">
        </label>
      </div>
      <div class="row stack">
        <span class="muted">${this._escape(
          this._t("memories_count", { shown: items.length, total: s.memories.length })
        )}</span>
        <span class="spacer"></span>
        <button class="btn outline" data-action="refresh-memory" ${busy}>${icon("refresh")}<span>${this._escape(
          this._t("refresh")
        )}</span></button>
        <button class="btn outline danger" data-action="clear-memory" ${busy || (s.memories.length ? "" : "disabled")}>${icon(
          "delete"
        )}<span>${this._escape(this._t("clear_scope"))}</span></button>
      </div>
      ${
        items.length < 1
          ? `<p class="empty">${this._escape(this._t("memories_empty"))}</p>`
          : `<div class="list">${items.map((item) => this._renderMemoryItem(item)).join("")}</div>`
      }
    `;
  }

  _renderMemoryItem(item) {
    const isShared = item.scope === "shared";
    const owner = !isShared && item.user_id ? this._userName(item.user_id) : "";
    const source = item.source ? this._t(`source_${item.source}`) : "";
    return `
      <article class="item">
        <div class="item-head">
          <span class="chip ${isShared ? "accent" : ""}">${this._escape(
            this._t(isShared ? "scope_shared_badge" : "scope_user")
          )}${owner ? ` · ${this._escape(owner)}` : ""}</span>
          ${source && source !== `source_${item.source}` ? `<span class="chip">${this._escape(source)}</span>` : ""}
          <span class="time" title="${this._escape(this._t("updated"))}: ${this._escape(
            this._formatDate(item.updated_at)
          )}">${this._escape(this._formatRelative(item.updated_at))}</span>
        </div>
        <div class="item-text">${this._escape(item.text)}</div>
        <div class="item-foot">
          ${this._renderIdChip(item.id)}
          <div class="actions">
            <button class="btn small danger" data-action="delete-memory" data-id="${this._escape(item.id)}">
              ${icon("delete")}<span>${this._escape(this._t("delete"))}</span>
            </button>
          </div>
        </div>
      </article>
    `;
  }

  _renderSessions() {
    const s = this._state;
    if (s.selectedSession) {
      return this._renderSessionDetail(s.selectedSession);
    }
    const entry = this._selectedEntry();
    const subentries = entry?.subentries || [];
    const busy = s.loading ? "disabled" : "";
    const agentField = `
      <label class="field">
        <span>${this._escape(this._t("agent"))}</span>
        <select id="session-subentry">
          <option value="" ${s.sessionSubentryId ? "" : "selected"}>${this._escape(this._t("agent_all"))}</option>
          ${subentries
            .map(
              (sub) =>
                `<option value="${this._escape(sub.subentry_id)}" ${
                  sub.subentry_id === s.sessionSubentryId ? "selected" : ""
                }>${this._escape(sub.title || sub.subentry_id)}</option>`
            )
            .join("")}
        </select>
      </label>
    `;
    return `
      <div class="filters">
        ${this._isAdmin ? this._renderScopeField("session-scope", s.sessionScope, ["mine", "all"]) : ""}
        ${this._renderUserField("session-target-user", s.sessionTargetUserId)}
        ${agentField}
        ${this._renderLimitField("session-limit", s.sessionLimit)}
      </div>
      <div class="row stack">
        <span class="spacer"></span>
        <button class="btn outline" data-action="refresh-sessions" ${busy}>${icon("refresh")}<span>${this._escape(
          this._t("refresh")
        )}</span></button>
        <button class="btn outline danger" data-action="clear-sessions" ${busy || (s.sessions.length ? "" : "disabled")}>${icon(
          "delete"
        )}<span>${this._escape(this._t("clear_scope"))}</span></button>
      </div>
      ${
        s.sessions.length < 1
          ? `<p class="empty">${this._escape(this._t("sessions_empty"))}</p>`
          : `<div class="list">${s.sessions.map((item) => this._renderSessionItem(item)).join("")}</div>`
      }
    `;
  }

  _renderSessionItem(session) {
    const id = this._escape(session.session_id);
    return `
      <article class="item">
        <div class="item-head">
          <span class="item-title">${this._escape(this._sessionName(session))}</span>
          <span class="chip">${this._escape(this._t("messages_count", { n: session.message_count || 0 }))}</span>
          <span class="time" title="${this._escape(this._t("updated"))}: ${this._escape(
            this._formatDate(session.updated_at)
          )}">${this._escape(this._formatRelative(session.updated_at))}</span>
        </div>
        <div class="item-foot">
          ${this._renderIdChip(session.session_id)}
          <div class="actions">
            <button class="btn small" data-action="view-session" data-id="${id}">
              ${icon("open")}<span>${this._escape(this._t("view"))}</span>
            </button>
            <button class="btn small danger" data-action="clear-session" data-id="${id}">
              ${icon("delete")}<span>${this._escape(this._t("clear"))}</span>
            </button>
          </div>
        </div>
      </article>
    `;
  }

  _renderSessionDetail(session) {
    const messages = Array.isArray(session.messages) ? session.messages : [];
    const roleClass = (role) =>
      role === "user" ? "user" : role === "assistant" ? "assistant" : "other";
    const roleLabel = (role) => {
      const key = `role_${role}`;
      const label = this._t(key);
      return label === key ? role : label;
    };
    return `
      <div class="row">
        <button class="btn" data-action="back">${icon("back")}<span>${this._escape(this._t("back"))}</span></button>
      </div>
      <div class="card-head">
        <div class="item-title">${this._escape(this._sessionName(session))}</div>
        <span class="chip">${this._escape(this._t("messages_count", { n: session.message_count || 0 }))}</span>
      </div>
      <div class="row">
        <span class="muted">${this._escape(this._t("created"))}: ${this._escape(
          this._formatDate(session.created_at)
        )} · ${this._escape(this._t("updated"))}: ${this._escape(this._formatDate(session.updated_at))}</span>
      </div>
      <div class="row">
        ${this._renderIdChip(session.session_id)}
        <span class="spacer"></span>
        <button class="btn outline danger" data-action="clear-session" data-id="${this._escape(session.session_id)}">
          ${icon("delete")}<span>${this._escape(this._t("clear_this_session"))}</span>
        </button>
      </div>
      <div class="transcript">
        ${messages
          .map(
            (message) => `
              <div class="msg ${roleClass(message.role)}">
                <span class="role">${this._escape(roleLabel(message.role))}</span>
                <div class="body">${this._escape(message.content)}</div>
                <span class="time">${this._escape(this._formatDate(message.created_at))}</span>
              </div>
            `
          )
          .join("")}
      </div>
    `;
  }

  // ---------------------------------------------------------------------
  // Events (delegated)
  // ---------------------------------------------------------------------

  async _onClick(event) {
    const target = event.target.closest("[data-action]");
    if (!target || !this.shadowRoot.contains(target)) {
      return;
    }
    const { action, id, tab, value } = target.dataset;
    switch (action) {
      case "refresh-all":
        await this._run(async () => {
          await this._loadEntries();
          await this._loadUsers();
        });
        await this._refreshAll();
        break;
      case "tab":
        this._setState({ tab });
        break;
      case "refresh-memory":
        await this._run(() => this._refreshMemories());
        break;
      case "clear-memory":
        await this._clearMemories();
        break;
      case "delete-memory":
        await this._deleteMemory(id);
        break;
      case "refresh-sessions":
        await this._run(() => this._refreshSessions());
        break;
      case "clear-sessions":
        await this._clearSession();
        break;
      case "view-session":
        await this._selectSession(id);
        break;
      case "clear-session":
        await this._clearSession(id);
        break;
      case "back":
        this._setState({ selectedSession: null });
        break;
      case "copy":
        await this._copyText(value);
        break;
      default:
        break;
    }
  }

  async _onChange(event) {
    const target = event.target;
    const value = target.value;
    switch (target.id) {
      case "entry-select":
        this._setState({ selectedEntryId: value, selectedSession: null });
        await this._refreshAll();
        break;
      case "memory-scope":
        this._setState({ memoryScope: value });
        await this._run(() => this._refreshMemories());
        break;
      case "memory-limit":
        this._setState({ memoryLimit: Math.min(500, Math.max(1, Number(value) || 50)) });
        await this._run(() => this._refreshMemories());
        break;
      case "memory-target-user":
        this._setState({ memoryTargetUserId: value });
        await this._run(() => this._refreshMemories());
        break;
      case "session-scope":
        this._setState({ sessionScope: value, selectedSession: null });
        await this._run(() => this._refreshSessions());
        break;
      case "session-subentry":
        this._setState({ sessionSubentryId: value, selectedSession: null });
        await this._run(() => this._refreshSessions());
        break;
      case "session-target-user":
        this._setState({ sessionTargetUserId: value, selectedSession: null });
        await this._run(() => this._refreshSessions());
        break;
      case "session-limit":
        this._setState({ sessionLimit: Math.min(500, Math.max(1, Number(value) || 50)) });
        await this._run(() => this._refreshSessions());
        break;
      default:
        break;
    }
  }

  _onInput(event) {
    if (event.target.id === "memory-search") {
      // Filtering is local; re-render keeps focus via _render().
      this._setState({ memorySearch: event.target.value });
    }
  }
}

customElements.define("ai-subscription-assist-memory-panel", AiSubscriptionAssistMemoryPanel);
