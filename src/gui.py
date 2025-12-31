import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import hashlib
import datetime
import sys
import platform
import webbrowser
import subprocess
import config
import utils
import logic

class MDICheckbutton(ttk.Frame):
    """
    基于图片的自定义勾选框 (仅支持 PNG)
    """

    def __init__(self, parent, images, text="", variable=None, command=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.variable = variable
        self.command = command
        self.images = images  # {'on': image, 'off': image}

        # 图标标签
        self.lbl_icon = ttk.Label(self)
        self.lbl_icon.pack(side="left")

        # 文字标签
        if text:
            self.lbl_text = ttk.Label(self, text=text)
            self.lbl_text.pack(side="left", padx=(5, 0))
            self.lbl_text.bind("<Button-1>", self._toggle)

        self.lbl_icon.bind("<Button-1>", self._toggle)

        if self.variable:
            self.variable.trace_add("write", self._update_icon)
            self._update_icon()

    def _toggle(self, event=None):
        if self.variable:
            self.variable.set(not self.variable.get())
            if self.command:
                self.command()

    def _update_icon(self, *args):
        if self.variable:
            state = self.variable.get()
            img = self.images.get('on' if state else 'off')
            if img:
                self.lbl_icon.config(image=img)


class CodeSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("980x850")

        self.node_data = {}
        self.all_configs = {}
        self.project_list = {}
        self.gitignore_patterns = []
        self.translations = {}

        # 导出设置
        self.export_settings = {
            "use_timestamp": False,
            "keep_latest": False,
            "custom_name": "code_context"
        }

        # UI 变量
        self.name_var = tk.StringVar()
        self.url_var = tk.StringVar(value="https://code.ryan416.com")
        self.path_var = tk.StringVar()
        self.sort_mode = tk.StringVar(value="name")
        self.sort_desc = tk.BooleanVar(value=False)
        self.lang_var = tk.StringVar(value="en")
        self.theme_var = tk.StringVar(value="system")
        self.auto_export_var = tk.BooleanVar(value=False)

        # 1. 加载配置
        self._load_local_config()
        self._detect_initial_settings()

        # 2. 加载资源 (必须在创建 root 之后)
        self._load_resources()
        self._load_translations()

        self.root.title(self.tr("app_title"))
        self._build_ui()
        self.root.update()
        self._apply_theme()

        self._refresh_project_combo()
        last = self.all_configs.get("last_active", "")
        if last and last in self.project_list:
            self.project_combo.set(last)
            self.root.after(200, lambda: self.switch_project(None))

    def reload_ui_with_state(self):
        """重建 UI，同时保留当前选中的项目状态"""
        # 1. 保存当前状态
        current_proj = self.project_combo.get()

        # 2. 应用当前的主题设置，切换对应的图标集
        # 这一步决定了 self.icons 是 light 还是 dark
        is_dark = False
        mode = self.theme_var.get()
        if mode == "dark":
            is_dark = True
        elif mode == "system":
            is_dark = utils.is_system_dark_mode()

        # 切换图标集
        self.icons = self.icons_map["dark"] if is_dark else self.icons_map["light"]
        self._update_check_imgs()

        # 3. 重建 UI (此时会使用新的 self.icons)
        self._build_ui()

        # 4. 应用颜色主题 (背景色、字体颜色等)
        self._apply_theme()  # 这里面其实也有判断 is_dark 的逻辑，可以保留

        # 5. === 核心修复：恢复状态 ===
        # 重新填充下拉列表
        self._refresh_project_combo()

        # 如果之前选中的项目还在列表中，恢复它
        if current_proj and current_proj in self.project_list:
            self.project_combo.set(current_proj)
            # 恢复输入框的内容
            data = self.project_list[current_proj]
            self.name_var.set(current_proj)
            self.url_var.set(data.get("url", ""))
            self.path_var.set(data.get("path", ""))
            # 刷新树形图 (但不强制从云端拉取，避免卡顿)
            self.refresh_tree_structure()

    def _load_resources(self):
        """
        加载 PNG 图标资源 (保持原始大小，不缩放以保证清晰度)
        """
        self.icons_map = {"light": {}, "dark": {}}

        # 需要的图标文件名
        files = {
            "checkbox_on": "checkbox_on",
            "checkbox_off": "checkbox_off",
            "checkbox_partial": "checkbox_partial",
            "refresh": "refresh",
            "settings": "settings",
            "web": "web",
            "folder": "folder"
        }

        search_paths = [
            config.get_resource_path(os.path.join("assets", "icons")),
            config.get_resource_path("assets")
        ]

        self.img_bin = tk.PhotoImage(width=1, height=1)

        for key, basename in files.items():
            # 加载亮色图标
            self.icons_map["light"][key] = self._try_load_icon(search_paths, basename, "light")
            # 加载暗色图标
            self.icons_map["dark"][key] = self._try_load_icon(search_paths, basename, "dark")
        mode = self.theme_var.get()

        # 如果是跟随系统，先判断系统当前是深色还是浅色
        if mode == "system":
            is_dark = utils.is_system_dark_mode()
            actual_mode = "dark" if is_dark else "light"
        else:
            # 否则直接使用 "light" 或 "dark"
            actual_mode = mode

        # 使用解析后的 actual_mode 去取图标
        self.icons = self.icons_map[actual_mode]
        self._update_check_imgs()

    def _try_load_icon(self, paths, basename, theme):
        """
        尝试加载图标。
        优先找: basename_theme.png (例如 refresh_dark.png)
        找不到则回退找: basename.png (例如 refresh.png)
        """
        candidates = [f"{basename}_{theme}.png", f"{basename}.png"]

        for filename in candidates:
            for folder in paths:
                p = os.path.join(folder, filename)
                if os.path.exists(p):
                    try:
                        return tk.PhotoImage(file=p)
                    except Exception:
                        pass
        return self.img_bin

    def _update_check_imgs(self):
        self.check_imgs = {
            'on': self.icons.get('checkbox_on', self.img_bin),
            'off': self.icons.get('checkbox_off', self.img_bin)
        }

    def _get_status_image(self, state, ntype):
        if ntype == 'binary': return self.img_bin
        if state == 1: return self.icons.get('checkbox_on', self.img_bin)
        if state == 2: return self.icons.get('checkbox_partial', self.img_bin)
        return self.icons.get('checkbox_off', self.img_bin)

    def _load_translations(self):
        lang_path = config.get_resource_path(config.LANG_FILE_REL)
        try:
            with open(lang_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception:
            self.translations = {"en": {}, "zh": {}}

    def tr(self, key):
        lang = self.lang_var.get()
        dct = self.translations.get(lang, self.translations.get("en", {}))
        return dct.get(key, key)

    def _detect_initial_settings(self):
        if "language" in self.all_configs:
            self.lang_var.set(self.all_configs["language"])
        else:
            try:
                sys_lang = str(getattr(os, 'environ', {}).get('LANG', ''))
                if "zh" in sys_lang.lower():
                    self.lang_var.set("zh")
                else:
                    self.lang_var.set("en")
            except:
                self.lang_var.set("en")

        self.theme_var.set(self.all_configs.get("theme", "system"))
        self.auto_export_var.set(self.all_configs.get("auto_export", False))

        if "export_settings" in self.all_configs:
            self.export_settings.update(self.all_configs["export_settings"])

    def _load_local_config(self):
        if os.path.exists(config.CONFIG_FILE):
            try:
                with open(config.CONFIG_FILE, 'r') as f:
                    self.all_configs = json.load(f)
            except:
                self.all_configs = {}
        self.project_list = self.all_configs.get("projects", {})

    def _save_local_config(self):
        self.all_configs["projects"] = self.project_list
        self.all_configs["auto_export"] = self.auto_export_var.get()
        self.all_configs["export_settings"] = self.export_settings
        self.all_configs["language"] = self.lang_var.get()
        try:
            with open(config.CONFIG_FILE, 'w') as f:
                json.dump(self.all_configs, f)
        except:
            pass

    def open_settings_dialog(self):
        SettingsDialog(self.root, self.export_settings, self.update_export_settings, self.check_imgs, self.tr)

    def update_export_settings(self, new_settings):
        self.export_settings = new_settings
        self._save_local_config()
        messagebox.showinfo(self.tr("status_done"), "Settings Saved!")

    def change_theme(self):
        self.all_configs["theme"] = self.theme_var.get()
        self._save_local_config()
        self.reload_ui_with_state()

    def change_lang(self):
        self._save_local_config()
        self.root.title(self.tr("app_title"))
        self.reload_ui_with_state()

    def _apply_theme(self, is_dark=None):
        style = ttk.Style()
        style.theme_use('clam')

        if is_dark is None:
            mode = self.theme_var.get()
            if mode == "dark":
                is_dark = True
            elif mode == "system":
                is_dark = utils.is_system_dark_mode()
            else:
                is_dark = False

        utils.apply_windows_dark_mode(self.root, is_dark)

        # === 核心修改：设置行高适应图标 ===
        # 假设图标是 24px，我们给一点余量设为 28px
        ROW_HEIGHT = 24

        if is_dark:
            bg, fg, field, sel = "#2d2d2d", "#ffffff", "#3d3d3d", "#0078d7"
            self.root.configure(bg=bg)
            style.configure(".", background=bg, foreground=fg, fieldbackground=field)
            # 设置 Treeview 行高
            style.configure("Treeview", background=field, foreground=fg, fieldbackground=field, borderwidth=0,
                            rowheight=ROW_HEIGHT)
            style.map("Treeview", background=[('selected', sel)], foreground=[('selected', 'white')])
            style.configure("TCombobox", fieldbackground=field, background=bg, foreground=fg, arrowcolor="white")
            style.map("TCombobox", fieldbackground=[('readonly', field)], selectbackground=[('readonly', sel)],
                      selectforeground=[('readonly', 'white')])
        else:
            bg, fg, field = "#f0f0f0", "#000000", "#ffffff"
            self.root.configure(bg=bg)
            style.configure(".", background=bg, foreground=fg, fieldbackground=field)
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white", borderwidth=0,
                            rowheight=ROW_HEIGHT)
            style.map("Treeview", background=[('selected', '#0078d7')], foreground=[('selected', 'white')])
            style.configure("TCombobox", fieldbackground="white", background="white", foreground="black",
                            arrowcolor="black")
            style.map("TCombobox", fieldbackground=[('readonly', 'white')], selectbackground=[('readonly', '#0078d7')],
                      selectforeground=[('readonly', 'white')])

    def _build_ui(self):
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu): widget.destroy()

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        proj_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr("menu_project"), menu=proj_menu)
        proj_menu.add_command(label=self.tr("cmd_add_save"), command=self.save_local_project_info)
        proj_menu.add_command(label=self.tr("cmd_delete_local"), command=self.delete_local_project)
        proj_menu.add_separator()
        proj_menu.add_command(label=self.tr("cmd_exit"), command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr("menu_edit"), menu=edit_menu)
        edit_menu.add_command(label=self.tr("cmd_sel_all"), command=lambda: self.set_all_state(1))
        edit_menu.add_command(label=self.tr("cmd_desel_all"), command=lambda: self.set_all_state(0))
        edit_menu.add_separator()
        edit_menu.add_command(label=self.tr("menu_settings"), command=self.open_settings_dialog)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr("menu_view"), menu=view_menu)

        lang_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label=self.tr("submenu_lang"), menu=lang_menu)
        lang_menu.add_radiobutton(label="English", variable=self.lang_var, value="en", command=self.change_lang)
        lang_menu.add_radiobutton(label="中文", variable=self.lang_var, value="zh", command=self.change_lang)

        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label=self.tr("submenu_theme"), menu=theme_menu)
        theme_menu.add_radiobutton(label=self.tr("theme_system"), variable=self.theme_var, value="system",
                                   command=self.change_theme)
        theme_menu.add_radiobutton(label=self.tr("theme_light"), variable=self.theme_var, value="light",
                                   command=self.change_theme)
        theme_menu.add_radiobutton(label=self.tr("theme_dark"), variable=self.theme_var, value="dark",
                                   command=self.change_theme)

        info_frame = ttk.LabelFrame(self.root, text=self.tr("lbl_curr_proj"))
        info_frame.pack(fill="x", padx=10, pady=5)

        r1 = ttk.Frame(info_frame)
        r1.pack(fill="x", pady=5, padx=5)
        self.project_combo = ttk.Combobox(r1, state="readonly", width=20)
        self.project_combo.pack(side="left")
        self.project_combo.bind("<<ComboboxSelected>>", self.switch_project)

        ttk.Label(r1, text=" | ").pack(side="left")
        ttk.Label(r1, text=self.tr("lbl_proj_name")).pack(side="left")
        ttk.Entry(r1, textvariable=self.name_var, width=15).pack(side="left", padx=5)
        ttk.Label(r1, text=self.tr("lbl_url")).pack(side="left")
        ttk.Entry(r1, textvariable=self.url_var, width=25).pack(side="left", padx=5)

        r2 = ttk.Frame(info_frame)
        r2.pack(fill="x", pady=5, padx=5)
        ttk.Label(r2, text=self.tr("lbl_path")).pack(side="left")
        ttk.Entry(r2, textvariable=self.path_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(r2, text=self.tr("btn_browse"), command=self.select_folder).pack(side="left")

        tool_frame = ttk.Frame(self.root)
        tool_frame.pack(fill="x", padx=10, pady=2)
        ttk.Button(tool_frame, text=self.tr("btn_pull"), command=self.pull_cloud_config).pack(side="left")

        ttk.Label(tool_frame, text=self.tr("lbl_sort")).pack(side="right", padx=5)
        self.sort_btn = ttk.Button(tool_frame, text="⬇", width=3, command=self.toggle_sort_dir)
        self.sort_btn.pack(side="right")
        sort_cb = ttk.Combobox(tool_frame, textvariable=self.sort_mode, state="readonly", width=8)
        sort_cb['values'] = ("name", "time", "type")
        sort_cb.pack(side="right", padx=2)
        sort_cb.bind("<<ComboboxSelected>>", self.on_sort_change)

        btn_folder = ttk.Button(tool_frame, image=self.icons.get('folder', self.img_bin), width=3,
                                command=self.open_local_folder)
        btn_folder.pack(side="right", padx=2)

        # 2. 打开网页
        btn_web = ttk.Button(tool_frame, image=self.icons.get('web', self.img_bin), width=3,
                             command=self.open_project_url)
        btn_web.pack(side="right", padx=2)


        # 刷新按钮
        ref_btn = ttk.Button(tool_frame, image=self.icons.get('refresh', self.img_bin), width=3,
                             command=lambda: self.refresh_tree_structure(keep_state=True))
        ref_btn.image = self.icons.get('refresh')
        ref_btn.pack(side="right", padx=(10, 2))

        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=(), selectmode="extended")
        self.tree.column("#0", width=800, minwidth=200, anchor="w", stretch=True)
        self.tree.heading("#0", text=self.tr("col_file"))

        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Button-1>", self.on_click)

        b_frame = ttk.Frame(self.root)
        b_frame.pack(fill="x", padx=10, pady=10)
        self.status_lbl = ttk.Label(b_frame, text=self.tr("status_ready"))
        self.status_lbl.pack(side="left")

        ttk.Button(b_frame, text=self.tr("btn_sync"), command=self.sync_logic).pack(side="right", padx=2)

        MDICheckbutton(b_frame, images=self.check_imgs, text=self.tr("chk_also_local"),
                       variable=self.auto_export_var).pack(side="right", padx=5)

        ttk.Button(b_frame, text=self.tr("btn_export_txt"), command=self.export_local_only).pack(side="right", padx=5)

    def refresh_tree_structure(self, keep_state=False):
        current_selections = set()
        if keep_state:
            root_abs = self.path_var.get()
            for uid, d in self.node_data.items():
                if d['type'] == 'file' and d['state'] == 1:
                    try:
                        current_selections.add(os.path.relpath(d['path'], root_abs))
                    except:
                        pass

        self.tree.delete(*self.tree.get_children())
        self.node_data = {}
        root = self.path_var.get()
        if not root or not os.path.exists(root): return

        self.gitignore_patterns = logic.load_gitignore(root, config.DEFAULT_IGNORE)
        self._populate(root, "", current_selections)
        self._recalc_folder_states()

    def _populate(self, current_path, parent_uid, selections):
        items = logic.get_sorted_items(current_path, self.sort_mode.get(), self.sort_desc.get())
        root_abs = self.path_var.get()

        for item in items:
            full = os.path.join(current_path, item)
            rel = os.path.relpath(full, root_abs)

            if logic.is_ignored(item, rel, self.gitignore_patterns):
                continue

            is_dir = os.path.isdir(full)
            ext = os.path.splitext(item)[1].lower()
            is_bin = ext in config.BINARY_EXTS

            node_type = "dir" if is_dir else ("binary" if is_bin else "file")
            state = 0
            if node_type == 'file' and rel in selections: state = 1

            img = self._get_status_image(state, node_type)
            uid = self.tree.insert(parent_uid, "end", text=f" {item}", image=img, open=False)
            self.node_data[uid] = {"path": full, "type": node_type, "state": state, "name": item}

            if node_type == 'dir': self._populate(full, uid, selections)

    def on_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        data = self.node_data.get(item_id)
        if not data or data["type"] == "binary": return
        element = self.tree.identify_element(event.x, event.y)
        if "image" in element:
            new_state = 0 if data["state"] == 1 else 1
            self.set_item_state(item_id, new_state)
            return "break"

    def set_item_state(self, uid, state):
        d = self.node_data[uid]
        d['state'] = state
        self.tree.item(uid, image=self._get_status_image(state, d['type']))
        if d['type'] == 'dir':
            for c in self.tree.get_children(uid): self._set_down(c, state)
        p = self.tree.parent(uid)
        while p:
            self._update_parent(p)
            p = self.tree.parent(p)

    def _set_down(self, uid, state):
        d = self.node_data[uid]
        if d['type'] == 'binary': return
        d['state'] = state
        self.tree.item(uid, image=self._get_status_image(state, d['type']))
        if d['type'] == 'dir':
            for c in self.tree.get_children(uid): self._set_down(c, state)

    def _update_parent(self, uid):
        chs = self.tree.get_children(uid)
        has_1, has_0, has_2 = False, False, False
        for c in chs:
            cd = self.node_data[c]
            if cd['type'] == 'binary': continue
            if cd['state'] == 1:
                has_1 = True
            elif cd['state'] == 0:
                has_0 = True
            elif cd['state'] == 2:
                has_2 = True
        ns = 2 if has_2 or (has_1 and has_0) else (1 if has_1 else 0)
        d = self.node_data[uid]
        if d['state'] != ns:
            d['state'] = ns
            self.tree.item(uid, image=self._get_status_image(ns, d['type']))

    def _recalc_folder_states(self):
        for uid, d in self.node_data.items():
            if d['type'] == 'file' and d['state'] == 1:
                p = self.tree.parent(uid)
                while p:
                    self._update_parent(p)
                    p = self.tree.parent(p)

    def batch_set_state(self, state):
        for uid in self.tree.selection():
            if uid in self.node_data: self.set_item_state(uid, state)

    def set_all_state(self, s):
        for item in self.tree.get_children(""): self._set_down(item, s)

    def toggle_sort_dir(self):
        self.sort_desc.set(not self.sort_desc.get())
        self.sort_btn.config(text="⬆" if self.sort_desc.get() else "⬇")
        self.refresh_tree_structure(keep_state=True)

    def on_sort_change(self, e):
        self.refresh_tree_structure(keep_state=True)

    def select_folder(self):
        p = filedialog.askdirectory()
        if p:
            p = os.path.normpath(p)
            self.path_var.set(p);
            self.refresh_tree_structure()

    def _refresh_project_combo(self):
        self.project_combo['values'] = list(self.project_list.keys())

    def save_local_project_info(self):
        n, p = self.name_var.get().strip(), self.path_var.get().strip()
        if n and p:
            self.project_list[n] = {"url": self.url_var.get().strip(), "path": p}
            self.all_configs["last_active"] = n
            self._save_local_config();
            self._refresh_project_combo();
            self.project_combo.set(n)
            self.status_lbl.config(text=self.tr("msg_saved"), foreground="green")

    def delete_local_project(self):
        n = self.project_combo.get()
        if n in self.project_list:
            if messagebox.askyesno(self.tr("status_error"), self.tr("msg_confirm_del").format(n)):
                del self.project_list[n]
                self.name_var.set("");
                self.path_var.set("");
                self.tree.delete(*self.tree.get_children())
                self._save_local_config();
                self._refresh_project_combo();
                self.project_combo.set("")

    def switch_project(self, e):
        n = self.project_combo.get()
        if n in self.project_list:
            c = self.project_list[n]
            self.name_var.set(n);
            self.url_var.set(c.get("url", ""));
            self.path_var.set(c.get("path", ""))
            self.refresh_tree_structure()
            self._pull_cloud_config_silent()
            self.all_configs["last_active"] = n;
            self._save_local_config()

    def clear_cloud_data(self):
        u, n = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        if not u or not n: return
        if messagebox.askyesno(self.tr("status_error"), self.tr("msg_confirm_clear").format(n)):
            try:
                requests.delete(f"{u}/project/{n}", timeout=5)
            except:
                pass
            messagebox.showinfo(self.tr("status_done"), self.tr("msg_done"))

    def pull_cloud_config(self):
        u, n = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        if not u or not n: return
        self.status_lbl.config(text=self.tr("status_pulling"), foreground="blue");
        self.root.update()
        if self._do_pull_logic(u, n):
            self.status_lbl.config(text=self.tr("status_restored"), foreground="green")
        else:
            self.status_lbl.config(text="Pull failed or no config.", foreground="red")

    def _pull_cloud_config_silent(self):
        u, n = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        if not u or not n: return
        self.root.after(50, lambda: self._do_pull_logic(u, n, timeout=2))

    def _do_pull_logic(self, u, n, timeout=4):
        try:
            r = requests.get(f"{u}/config/{n}", timeout=timeout)
            if r.status_code == 200:
                s = set(r.json())
                root = self.path_var.get()
                for uid, d in self.node_data.items():
                    if d['type'] == 'file':
                        rel = os.path.relpath(d['path'], root).replace("\\", "/")
                        new_st = 1 if (rel in s or rel.replace("/", "\\") in s) else 0
                        if d['state'] != new_st:
                            d['state'] = new_st
                            self.tree.item(uid, image=self._get_status_image(new_st, 'file'))
                self._recalc_folder_states()
                return True
        except:
            pass
        return False

    def _generate_payload(self):
        name, root = self.name_var.get().strip(), self.path_var.get().strip()
        if not name or not root: return None, None
        header = logic.generate_metadata_header(name, root)
        out = [header]
        out.append(f"# Project Structure\n## Structure\n")
        sel_list = []

        def walk(parent_uid, pre=""):
            children = self.tree.get_children(parent_uid)
            vis_children = [c for c in children if self.node_data[c]['type'] != 'binary']
            cnt = len(vis_children)
            for i, uid in enumerate(vis_children):
                d = self.node_data[uid]
                is_last = (i == cnt - 1)
                marker = "└─" if is_last else "├─"
                mark = "[x]" if d['state'] == 1 else "[ ]"
                if d['state'] == 2: mark = "[-]"
                out.append(f"{pre}{marker} {mark} {d['name']}")
                walk(uid, pre + ("   " if is_last else "│  "))

        walk("")
        out.append("\n" + "=" * 40 + "\n## Contents\n")

        def walk_c(items):
            for uid in items:
                d = self.node_data[uid]
                if d['type'] == 'file' and d['state'] == 1:
                    rel = os.path.relpath(d['path'], root).replace("\\", "/")
                    sel_list.append(rel)
                    out.append(f"\n--- START: {rel} ---\n")
                    try:
                        with open(d['path'], 'r', encoding='utf-8', errors='ignore') as f:
                            out.append(f.read())
                    except:
                        out.append("[Error reading file]")
                    out.append(f"\n--- END: {rel} ---\n")
                if d['type'] == 'dir': walk_c(self.tree.get_children(uid))

        walk_c(self.tree.get_children(""))
        return "\n".join(out), sel_list

    def _get_export_filename(self):
        base = self.export_settings.get("custom_name", "code_context")
        if not base.lower().endswith(".txt"): base += ".txt"
        if self.export_settings.get("use_timestamp", False):
            ts = datetime.datetime.now().strftime(config.DATE_FMT_FILE)
            name_part, ext_part = os.path.splitext(base)
            return f"{name_part}_{ts}{ext_part}"
        return base

    def export_local_only(self):
        payload, _ = self._generate_payload()
        if not payload:
            messagebox.showwarning("Warning", "Project or path not set.")
            return
        root = self.path_var.get()
        filename = self._get_export_filename()
        target_path = os.path.join(root, filename)
        if not self.export_settings.get("use_timestamp", False):
            target_path = filedialog.asksaveasfilename(
                initialdir=root, initialfile=filename, defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
        if target_path:
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(payload)
                if self.export_settings.get("keep_latest", False):
                    logic.clean_old_exports(root, target_path)
                self.status_lbl.config(text="Export OK.", foreground="green")
                messagebox.showinfo("Success", self.tr("msg_export_ok").format(target_path))
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def sync_logic(self):
        self.save_local_project_info()
        payload, sel_list = self._generate_payload()
        if not payload: return
        if self.auto_export_var.get():
            root = self.path_var.get()
            filename = self._get_export_filename()
            target_path = os.path.join(root, filename)
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(payload)
                if self.export_settings.get("keep_latest", False):
                    logic.clean_old_exports(root, target_path)
            except:
                pass
        url, name = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        if not url or not name: return
        self.status_lbl.config(text=self.tr("status_packing"), foreground="blue");
        self.root.update()
        try:
            requests.post(f"{url}/config/{name}", json=sel_list, timeout=5)
            lh = hashlib.md5(payload.encode('utf-8')).hexdigest()
            need = True
            try:
                r = requests.get(f"{url}/hash/{name}", timeout=3)
                if r.status_code == 200 and r.json().get("hash") == lh: need = False
            except:
                pass
            if need:
                self.status_lbl.config(text=self.tr("status_uploading"), foreground="orange");
                self.root.update()
                requests.post(f"{url}/upload/{name}", data=payload.encode('utf-8'),
                              headers={'Content-Type': 'text/plain; charset=utf-8'}, timeout=30)
            self.status_lbl.config(text=self.tr("status_done"), foreground="green")
        except Exception as e:
            self.status_lbl.config(text=self.tr("status_error"), foreground="red")
            messagebox.showerror(self.tr("status_error"), str(e))

    def open_project_url(self):
        # 1. 去除 Base URL 末尾可能存在的多余斜杠
        base_url = self.url_var.get().strip().rstrip("/")
        # 2. 获取项目名
        project_name = self.name_var.get().strip()

        # 3. 只有当 Base URL 和 项目名 都有值时才拼接
        if base_url and project_name:
            full_url = f"{base_url}/{project_name}"
            webbrowser.open(full_url)
        elif base_url:
            # 如果只有 URL 没有项目名，也可以选择只打开主页，或者报错
            webbrowser.open(base_url)
        else:
            # 如果什么都没填，可以选择不做任何事或弹窗提示
            pass

    def open_local_folder(self):
        path = self.path_var.get().strip()
        if not path or not os.path.exists(path):
            return

        # 跨平台打开文件夹
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
        except Exception as e:
            print(f"Error opening folder: {e}")


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config_data, callback, check_imgs, tr_func):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("430x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.tr = tr_func
        self.title(self.tr("settings_title"))
        self.config_data = config_data
        self.callback = callback
        self.check_imgs = check_imgs

        self.use_timestamp = tk.BooleanVar(value=config_data.get("use_timestamp", False))
        self.keep_latest = tk.BooleanVar(value=config_data.get("keep_latest", False))
        self.custom_name = tk.StringVar(value=config_data.get("custom_name", "code_context"))
        self._build_ui()
        style = ttk.Style()
        if style.theme_use() == 'clam':
            utils.apply_windows_dark_mode(self, utils.is_system_dark_mode())

    def _build_ui(self):
        p = ttk.Frame(self, padding=20)
        p.pack(fill="both", expand=True)

        # 分组 1
        grp1 = ttk.LabelFrame(p, text=self.tr("settings_grp_filename"), padding=10)
        grp1.pack(fill="x", pady=5)

        ttk.Label(grp1, text=self.tr("settings_lbl_base_name")).pack(anchor="w")
        ttk.Entry(grp1, textvariable=self.custom_name).pack(fill="x", pady=5)

        MDICheckbutton(grp1, images=self.check_imgs, text=self.tr("settings_chk_timestamp"),
                       variable=self.use_timestamp).pack(anchor="w", pady=5)

        # 分组 2
        grp2 = ttk.LabelFrame(p, text=self.tr("settings_grp_manage"), padding=10)
        grp2.pack(fill="x", pady=15)

        MDICheckbutton(grp2, images=self.check_imgs, text=self.tr("settings_chk_keep_latest"),
                       variable=self.keep_latest).pack(anchor="w")

        ttk.Label(grp2, text=self.tr("settings_note_safety"),
                  font=("Arial", 8), foreground="gray", wraplength=350).pack(anchor="w", padx=25)

        # 按钮
        btn_frame = ttk.Frame(p)
        btn_frame.pack(fill="x", pady=10, side="bottom")
        ttk.Button(btn_frame, text=self.tr("btn_save"), command=self.save).pack(side="right")
        ttk.Button(btn_frame, text=self.tr("btn_cancel"), command=self.destroy).pack(side="right", padx=10)

    def save(self):
        safe_name = self.custom_name.get().strip()
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            safe_name = safe_name.replace(char, '')
        new_conf = {
            "use_timestamp": self.use_timestamp.get(),
            "keep_latest": self.keep_latest.get(),
            "custom_name": safe_name or "code_context"
        }
        self.callback(new_conf)
        self.destroy()