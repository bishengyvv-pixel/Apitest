"""Tk 图形界面实现。"""

from ...adaptor.config.defaults import DEFAULT_WINDOW_GEOMETRY, DEFAULT_WINDOW_TITLE
from ...shell.requirements import FILEDIALOG, JSON, MESSAGEBOX, PATH, SCROLLEDTEXT, THREADING, TK, TTK


class DesktopGui:
    """桌面 GUI 主界面。"""

    def __init__(self):
        self._actions = {}
        self._root = TK.Tk()
        self._root.title(DEFAULT_WINDOW_TITLE)
        self._root.geometry(DEFAULT_WINDOW_GEOMETRY)
        self._root.minsize(1200, 760)

        self._busy = False
        self._status_var = TK.StringVar(value="欢迎使用 AI API 接口测试工具。")
        self._base_url_var = TK.StringVar()
        self._api_key_var = TK.StringVar()
        self._history_path_var = TK.StringVar()
        self._timeout_var = TK.StringVar()
        self._max_tokens_var = TK.StringVar()
        self._default_model_var = TK.StringVar()
        self._chat_model_var = TK.StringVar()
        self._vision_model_var = TK.StringVar()
        self._image_path_var = TK.StringVar()
        self._image_detail_var = TK.StringVar(value="auto")
        self._text_result_meta_var = TK.StringVar(value="等待发起文本对话。")
        self._vision_result_meta_var = TK.StringVar(value="等待发起图片对话。")
        self._models_summary_var = TK.StringVar(value="尚未加载模型列表。")
        self._stats_history_path_var = TK.StringVar(value="-")
        self._summary_vars = {
            "session_count": TK.StringVar(value="0"),
            "average_duration_seconds": TK.StringVar(value="0"),
            "total_tokens": TK.StringVar(value="0"),
            "latest_session_at": TK.StringVar(value="-"),
            "prompt_tokens": TK.StringVar(value="0"),
            "completion_tokens": TK.StringVar(value="0"),
            "chat_count": TK.StringVar(value="0"),
            "vision_count": TK.StringVar(value="0"),
        }
        self._image_preview = None

        self._build_style()
        self._build_layout()

    def bind_actions(self, **actions):
        """绑定界面事件。"""
        self._actions = actions

    def set_settings(self, settings):
        """将初始配置填充到界面。"""
        self._base_url_var.set(settings.get("base_url", ""))
        self._api_key_var.set(settings.get("api_key", ""))
        self._history_path_var.set(settings.get("history_path", ""))
        self._timeout_var.set(settings.get("timeout_seconds", ""))
        self._max_tokens_var.set(settings.get("max_tokens", ""))
        self._default_model_var.set(settings.get("default_model", ""))
        self._chat_model_var.set(settings.get("default_model", ""))
        self._vision_model_var.set(settings.get("default_model", ""))
        self._system_prompt_text.delete("1.0", TK.END)
        self._system_prompt_text.insert("1.0", settings.get("system_prompt", ""))

    def run(self):
        """进入 GUI 主循环。"""
        self._root.mainloop()

    def run_background(self, task, on_success=None, success_message=""):
        """在后台线程执行耗时任务，避免界面卡死。"""
        if self._busy:
            self.set_status("当前已有任务执行中，请稍候。", is_error=True)
            return

        self._set_busy(True)

        def worker():
            try:
                payload = task()
            except Exception as error:
                self._root.after(0, lambda: self._handle_background_error(error))
                return

            self._root.after(
                0,
                lambda: self._handle_background_success(payload, on_success, success_message),
            )

        THREADING.Thread(target=worker, daemon=True).start()

    def render_models(self, payload):
        """渲染模型列表。"""
        self._clear_tree(self._models_tree)
        for item in payload.get("rows") or []:
            self._models_tree.insert(
                "",
                TK.END,
                values=(item.get("id", ""), item.get("owned_by", ""), item.get("object", "")),
            )

        choices = payload.get("choices") or []
        self.apply_model_choices(choices)
        self._models_summary_var.set(
            f"接口: {payload.get('base_url', '-') or '-'} | 模型数: {payload.get('count', 0)}"
        )

    def render_text_result(self, payload):
        """更新文本结果区域。"""
        self._text_result_meta_var.set(self._build_result_meta(payload))
        self._set_text_widget(self._text_response_text, payload.get("response_text", ""))
        self._set_text_widget(self._text_raw_json_text, JSON.dumps(payload, ensure_ascii=False, indent=2))
        self.apply_model_choices([payload.get("model", "")])

    def render_vision_result(self, payload):
        """更新图片结果区域。"""
        self._vision_result_meta_var.set(self._build_result_meta(payload))
        self._set_text_widget(self._vision_response_text, payload.get("response_text", ""))
        self._set_text_widget(self._vision_raw_json_text, JSON.dumps(payload, ensure_ascii=False, indent=2))
        self.apply_model_choices([payload.get("model", "")])
        if payload.get("image_path"):
            self._image_path_var.set(payload.get("image_path", ""))
            self._refresh_image_preview(payload.get("image_path", ""))

    def render_stats(self, payload):
        """渲染统计页。"""
        summary = payload.get("summary") or {}
        self._stats_history_path_var.set(payload.get("history_path", "-") or "-")
        for key, variable in self._summary_vars.items():
            variable.set(summary.get(key, "0") or "0")

        self._clear_tree(self._stats_history_tree)
        for item in payload.get("history_rows") or []:
            self._stats_history_tree.insert(
                "",
                TK.END,
                values=(
                    item.get("created_at", ""),
                    item.get("kind", ""),
                    item.get("model", ""),
                    item.get("elapsed_seconds", ""),
                    item.get("total_tokens", ""),
                ),
            )

        self._clear_tree(self._stats_per_model_tree)
        for item in payload.get("per_model_rows") or []:
            self._stats_per_model_tree.insert(
                "",
                TK.END,
                values=(
                    item.get("model", ""),
                    item.get("session_count", "0"),
                    item.get("average_duration_seconds", "0"),
                    item.get("total_tokens", "0"),
                ),
            )

    def apply_model_choices(self, choices):
        """刷新多个模型选择框。"""
        normalized = []
        seen = {}
        for item in choices:
            text = str(item).strip()
            if not text or text in seen:
                continue
            seen[text] = True
            normalized.append(text)

        current_values = list(self._default_model_combo.cget("values"))
        for item in current_values:
            text = str(item).strip()
            if text and text not in seen:
                normalized.append(text)
                seen[text] = True

        self._default_model_combo.configure(values=normalized)
        self._chat_model_combo.configure(values=normalized)
        self._vision_model_combo.configure(values=normalized)

    def set_status(self, message, is_error=False):
        """更新底部状态栏。"""
        prefix = "错误" if is_error else "状态"
        self._status_var.set(f"{prefix}: {message}")

    def _build_style(self):
        """构建整体风格。"""
        style = TTK.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 11, "bold"))
        style.configure("CardTitle.TLabel", font=("Microsoft YaHei UI", 10, "bold"))

    def _build_layout(self):
        """搭建主界面布局。"""
        root_frame = TTK.Frame(self._root, padding=12)
        root_frame.pack(fill=TK.BOTH, expand=True)

        root_frame.columnconfigure(0, weight=0)
        root_frame.columnconfigure(1, weight=1)
        root_frame.rowconfigure(0, weight=1)

        config_frame = TTK.LabelFrame(root_frame, text="连接配置", padding=12)
        config_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        content_frame = TTK.Frame(root_frame)
        content_frame.grid(row=0, column=1, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self._build_config_panel(config_frame)
        self._build_tabs(content_frame)

        status_bar = TTK.Label(self._root, textvariable=self._status_var, anchor="w", padding=(12, 8))
        status_bar.pack(fill=TK.X, side=TK.BOTTOM)

    def _build_config_panel(self, frame):
        """构建左侧配置面板。"""
        self._add_labeled_entry(frame, "Base URL", self._base_url_var, 0, width=34)
        self._add_labeled_entry(frame, "API Key", self._api_key_var, 1, width=34, show="*")
        self._add_labeled_entry(frame, "历史文件", self._history_path_var, 2, width=34)
        self._default_model_combo = self._add_labeled_combo(frame, "默认模型", self._default_model_var, 3)
        self._add_labeled_entry(frame, "超时(秒)", self._timeout_var, 4, width=16)
        self._add_labeled_entry(frame, "Max Tokens", self._max_tokens_var, 5, width=16)

        TTK.Label(frame, text="系统提示词", style="Title.TLabel").grid(row=12, column=0, sticky="w", pady=(10, 4))
        self._system_prompt_text = SCROLLEDTEXT(frame, width=34, height=8, wrap=TK.WORD)
        self._system_prompt_text.grid(row=13, column=0, sticky="ew")

        button_frame = TTK.Frame(frame)
        button_frame.grid(row=14, column=0, sticky="ew", pady=(12, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        TTK.Button(button_frame, text="保存配置", command=self._trigger_save_settings).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        TTK.Button(button_frame, text="刷新模型", command=self._trigger_load_models).grid(row=0, column=1, sticky="ew", padx=(4, 0))
        TTK.Button(frame, text="刷新统计", command=self._trigger_refresh_stats).grid(row=15, column=0, sticky="ew", pady=(8, 0))

    def _build_tabs(self, frame):
        """构建主工作区标签页。"""
        notebook = TTK.Notebook(frame)
        notebook.grid(row=0, column=0, sticky="nsew")

        text_tab = TTK.Frame(notebook, padding=12)
        vision_tab = TTK.Frame(notebook, padding=12)
        models_tab = TTK.Frame(notebook, padding=12)
        stats_tab = TTK.Frame(notebook, padding=12)

        notebook.add(text_tab, text="文本对话")
        notebook.add(vision_tab, text="图片对话")
        notebook.add(models_tab, text="模型列表")
        notebook.add(stats_tab, text="历史统计")

        self._build_text_tab(text_tab)
        self._build_vision_tab(vision_tab)
        self._build_models_tab(models_tab)
        self._build_stats_tab(stats_tab)

    def _build_text_tab(self, frame):
        """构建文本对话页。"""
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        top_bar = TTK.Frame(frame)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(1, weight=1)

        TTK.Label(top_bar, text="模型", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self._chat_model_combo = TTK.Combobox(top_bar, textvariable=self._chat_model_var)
        self._chat_model_combo.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        TTK.Button(top_bar, text="发送文本请求", command=self._trigger_send_text).grid(row=0, column=2, sticky="e")

        TTK.Label(frame, text="Prompt", style="Title.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 4))
        self._text_prompt_text = SCROLLEDTEXT(frame, height=8, wrap=TK.WORD)
        self._text_prompt_text.grid(row=2, column=0, sticky="nsew")

        result_frame = TTK.LabelFrame(frame, text="响应结果", padding=12)
        result_frame.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        result_frame.rowconfigure(3, weight=1)

        TTK.Label(result_frame, textvariable=self._text_result_meta_var, foreground="#2f4f4f").grid(row=0, column=0, sticky="w")
        self._text_response_text = SCROLLEDTEXT(result_frame, height=10, wrap=TK.WORD)
        self._text_response_text.grid(row=1, column=0, sticky="nsew", pady=(8, 8))
        TTK.Label(result_frame, text="原始响应 JSON", style="CardTitle.TLabel").grid(row=2, column=0, sticky="w")
        self._text_raw_json_text = SCROLLEDTEXT(result_frame, height=8, wrap=TK.WORD)
        self._text_raw_json_text.grid(row=3, column=0, sticky="nsew", pady=(8, 0))

    def _build_vision_tab(self, frame):
        """构建图片对话页。"""
        frame.columnconfigure(0, weight=1)

        top_bar = TTK.Frame(frame)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(1, weight=1)
        top_bar.columnconfigure(3, weight=1)

        TTK.Label(top_bar, text="模型", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self._vision_model_combo = TTK.Combobox(top_bar, textvariable=self._vision_model_var)
        self._vision_model_combo.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        TTK.Label(top_bar, text="细节等级", style="Title.TLabel").grid(row=0, column=2, sticky="w")
        TTK.Combobox(top_bar, textvariable=self._image_detail_var, values=["auto", "low", "high"], state="readonly").grid(row=0, column=3, sticky="ew", padx=(8, 8))
        TTK.Button(top_bar, text="发送图片请求", command=self._trigger_send_vision).grid(row=0, column=4, sticky="e")

        image_bar = TTK.Frame(frame)
        image_bar.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        image_bar.columnconfigure(1, weight=1)
        TTK.Label(image_bar, text="图片路径", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        TTK.Entry(image_bar, textvariable=self._image_path_var).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        TTK.Button(image_bar, text="选择图片", command=self._choose_image_file).grid(row=0, column=2, sticky="e")

        preview_frame = TTK.Frame(frame)
        preview_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        preview_frame.columnconfigure(1, weight=1)
        self._image_preview_label = TTK.Label(preview_frame, text="尚未选择图片。", anchor="center", relief="groove", width=28)
        self._image_preview_label.grid(row=0, column=0, sticky="nw")
        self._image_info_label = TTK.Label(preview_frame, text="支持 png/jpg/jpeg/webp；PNG 会优先尝试预览。", justify="left")
        self._image_info_label.grid(row=0, column=1, sticky="nw", padx=(12, 0))

        TTK.Label(frame, text="Prompt", style="Title.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 4))
        self._vision_prompt_text = SCROLLEDTEXT(frame, height=7, wrap=TK.WORD)
        self._vision_prompt_text.grid(row=4, column=0, sticky="ew")

        result_frame = TTK.LabelFrame(frame, text="响应结果", padding=12)
        result_frame.grid(row=5, column=0, sticky="nsew", pady=(12, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        result_frame.rowconfigure(3, weight=1)

        TTK.Label(result_frame, textvariable=self._vision_result_meta_var, foreground="#2f4f4f").grid(row=0, column=0, sticky="w")
        self._vision_response_text = SCROLLEDTEXT(result_frame, height=9, wrap=TK.WORD)
        self._vision_response_text.grid(row=1, column=0, sticky="nsew", pady=(8, 8))
        TTK.Label(result_frame, text="原始响应 JSON", style="CardTitle.TLabel").grid(row=2, column=0, sticky="w")
        self._vision_raw_json_text = SCROLLEDTEXT(result_frame, height=7, wrap=TK.WORD)
        self._vision_raw_json_text.grid(row=3, column=0, sticky="nsew", pady=(8, 0))

    def _build_models_tab(self, frame):
        """构建模型列表页。"""
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        top_bar = TTK.Frame(frame)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(0, weight=1)
        TTK.Label(top_bar, textvariable=self._models_summary_var).grid(row=0, column=0, sticky="w")
        TTK.Button(top_bar, text="重新加载", command=self._trigger_load_models).grid(row=0, column=1, sticky="e")

        columns = ("id", "owned_by", "object")
        self._models_tree = TTK.Treeview(frame, columns=columns, show="headings", height=16)
        for name, title, width in (
            ("id", "模型", 320),
            ("owned_by", "归属", 180),
            ("object", "类型", 120),
        ):
            self._models_tree.heading(name, text=title)
            self._models_tree.column(name, width=width, anchor="w")
        self._models_tree.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self._models_tree.bind("<Double-1>", self._handle_model_double_click)

    def _build_stats_tab(self, frame):
        """构建历史统计页。"""
        frame.columnconfigure(0, weight=1)

        top_bar = TTK.Frame(frame)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(1, weight=1)
        TTK.Label(top_bar, text="历史文件", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        TTK.Label(top_bar, textvariable=self._stats_history_path_var).grid(row=0, column=1, sticky="w", padx=(8, 0))
        TTK.Button(top_bar, text="刷新统计", command=self._trigger_refresh_stats).grid(row=0, column=2, sticky="e")

        summary_frame = TTK.LabelFrame(frame, text="统计概览", padding=12)
        summary_frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        for index in range(4):
            summary_frame.columnconfigure(index, weight=1)

        cards = [
            ("会话总数", "session_count"),
            ("平均时长(秒)", "average_duration_seconds"),
            ("累计 Token", "total_tokens"),
            ("最近会话", "latest_session_at"),
            ("Prompt Token", "prompt_tokens"),
            ("Completion Token", "completion_tokens"),
            ("文本会话", "chat_count"),
            ("图片会话", "vision_count"),
        ]
        for index, (title, key) in enumerate(cards):
            row = index // 4
            column = index % 4
            card = TTK.Frame(summary_frame, padding=10)
            card.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
            TTK.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            TTK.Label(card, textvariable=self._summary_vars[key], font=("Microsoft YaHei UI", 11)).pack(anchor="w", pady=(6, 0))

        TTK.Label(frame, text="按模型统计", style="Title.TLabel").grid(row=2, column=0, sticky="w", pady=(12, 4))
        self._stats_per_model_tree = TTK.Treeview(frame, columns=("model", "sessions", "avg_seconds", "tokens"), show="headings", height=8)
        for name, title, width in (
            ("model", "模型", 280),
            ("sessions", "会话数", 100),
            ("avg_seconds", "平均时长", 120),
            ("tokens", "累计 Token", 120),
        ):
            self._stats_per_model_tree.heading(name, text=title)
            self._stats_per_model_tree.column(name, width=width, anchor="w")
        self._stats_per_model_tree.grid(row=3, column=0, sticky="nsew")

        TTK.Label(frame, text="最近会话", style="Title.TLabel").grid(row=4, column=0, sticky="w", pady=(12, 4))
        self._stats_history_tree = TTK.Treeview(frame, columns=("created_at", "kind", "model", "elapsed", "tokens"), show="headings", height=6)
        for name, title, width in (
            ("created_at", "时间", 220),
            ("kind", "类型", 90),
            ("model", "模型", 220),
            ("elapsed", "耗时", 100),
            ("tokens", "Token", 100),
        ):
            self._stats_history_tree.heading(name, text=title)
            self._stats_history_tree.column(name, width=width, anchor="w")
        self._stats_history_tree.grid(row=5, column=0, sticky="nsew")

    def _trigger_save_settings(self):
        """触发保存配置动作。"""
        callback = self._actions.get("on_save_settings")
        if callback:
            callback(self._collect_settings())

    def _trigger_load_models(self):
        """触发模型加载动作。"""
        callback = self._actions.get("on_load_models")
        if callback:
            callback(self._collect_settings())

    def _trigger_send_text(self):
        """触发文本对话动作。"""
        callback = self._actions.get("on_send_text")
        if callback:
            callback(self._collect_settings(), self._collect_text_request())

    def _trigger_send_vision(self):
        """触发图片对话动作。"""
        callback = self._actions.get("on_send_vision")
        if callback:
            callback(self._collect_settings(), self._collect_vision_request())

    def _trigger_refresh_stats(self):
        """触发统计刷新动作。"""
        callback = self._actions.get("on_refresh_stats")
        if callback:
            callback(self._collect_settings())

    def _collect_settings(self):
        """收集左侧配置面板数据。"""
        return {
            "base_url": self._base_url_var.get().strip(),
            "api_key": self._api_key_var.get().strip(),
            "history_path": self._history_path_var.get().strip(),
            "timeout_seconds": self._timeout_var.get().strip(),
            "max_tokens": self._max_tokens_var.get().strip(),
            "default_model": self._default_model_var.get().strip(),
            "system_prompt": self._system_prompt_text.get("1.0", TK.END).strip(),
        }

    def _collect_text_request(self):
        """收集文本对话输入。"""
        return {
            "model": self._chat_model_var.get().strip(),
            "prompt": self._text_prompt_text.get("1.0", TK.END).strip(),
        }

    def _collect_vision_request(self):
        """收集图片对话输入。"""
        return {
            "model": self._vision_model_var.get().strip(),
            "prompt": self._vision_prompt_text.get("1.0", TK.END).strip(),
            "image_path": self._image_path_var.get().strip(),
            "detail": self._image_detail_var.get().strip(),
        }

    def _choose_image_file(self):
        """选择本地图片。"""
        path = FILEDIALOG.askopenfilename(
            title="选择图片",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp"), ("All Files", "*.*")],
        )
        if not path:
            return
        self._image_path_var.set(path)
        self._refresh_image_preview(path)

    def _refresh_image_preview(self, image_path):
        """刷新图片预览和元信息。"""
        path = PATH(image_path)
        if not path.exists():
            self._image_preview_label.configure(text="图片不存在", image="")
            self._image_preview = None
            self._image_info_label.configure(text="请重新选择有效图片。")
            return

        info = [
            f"文件名: {path.name}",
            f"大小: {round(path.stat().st_size / 1024, 2)} KB",
            f"格式: {path.suffix.lower() or 'unknown'}",
        ]
        self._image_info_label.configure(text="\n".join(info))

        try:
            preview = TK.PhotoImage(file=str(path))
            self._image_preview = preview
            self._image_preview_label.configure(image=preview, text="")
        except Exception:
            self._image_preview = None
            self._image_preview_label.configure(image="", text="当前格式无法预览，仍可发送请求。")

    def _handle_model_double_click(self, _event):
        """双击模型时将其同步到当前选择。"""
        selected_items = self._models_tree.selection()
        if not selected_items:
            return
        values = self._models_tree.item(selected_items[0], "values")
        if not values:
            return
        model_name = str(values[0]).strip()
        self._default_model_var.set(model_name)
        self._chat_model_var.set(model_name)
        self._vision_model_var.set(model_name)
        self.set_status(f"已选择模型 {model_name}。")

    def _handle_background_success(self, payload, on_success, success_message):
        """统一处理后台任务成功。"""
        self._set_busy(False)
        if on_success:
            on_success(payload)
        if success_message:
            self.set_status(success_message)

    def _handle_background_error(self, error):
        """统一处理后台任务失败。"""
        self._set_busy(False)
        self.set_status(str(error), is_error=True)
        MESSAGEBOX.showerror("执行失败", str(error))

    def _set_busy(self, busy):
        """切换忙碌态。"""
        self._busy = busy
        self._root.configure(cursor="watch" if busy else "")

    def _add_labeled_entry(self, frame, title, variable, row_index, width=24, show=""):
        """创建带标签输入框。"""
        TTK.Label(frame, text=title, style="Title.TLabel").grid(row=row_index * 2, column=0, sticky="w", pady=(0 if row_index == 0 else 10, 4))
        entry = TTK.Entry(frame, textvariable=variable, width=width, show=show)
        entry.grid(row=row_index * 2 + 1, column=0, sticky="ew")
        return entry

    def _add_labeled_combo(self, frame, title, variable, row_index):
        """创建带标签下拉框。"""
        TTK.Label(frame, text=title, style="Title.TLabel").grid(row=row_index * 2, column=0, sticky="w", pady=(10, 4))
        combo = TTK.Combobox(frame, textvariable=variable)
        combo.grid(row=row_index * 2 + 1, column=0, sticky="ew")
        return combo

    def _set_text_widget(self, widget, text):
        """刷新多行文本框内容。"""
        widget.delete("1.0", TK.END)
        widget.insert("1.0", text or "")

    def _clear_tree(self, tree):
        """清空表格。"""
        for item in tree.get_children():
            tree.delete(item)

    def _build_result_meta(self, payload):
        """生成结果摘要文本。"""
        usage = payload.get("usage") or {}
        return (
            f"模型: {payload.get('model', '-')} | "
            f"时间: {payload.get('created_at', '-')} | "
            f"耗时: {payload.get('elapsed_seconds', 0)} 秒 | "
            f"Prompt: {usage.get('prompt_tokens', 0)} | "
            f"Completion: {usage.get('completion_tokens', 0)} | "
            f"Total: {usage.get('total_tokens', 0)}"
        )


