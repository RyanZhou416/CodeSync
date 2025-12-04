import os
import json
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import hashlib
import locale

# 导入同目录下的模块
from . import config
from . import utils
from . import logic

# 状态图标
ICON_UNCHECKED = "☐"
ICON_CHECKED = "☑"
ICON_PARTIAL = "⊟"
ICON_BIN = ""


class CodeSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("950x850")

        self.node_data = {}
        self.all_configs = {}
        self.project_list = {}
        self.gitignore_patterns = []
        self.translations = {}

        # 加载语言包
        self._load_translations()

        # 变量初始化
        self.name_var = tk.StringVar()
        self.url_var = tk.StringVar(value="https://code.ryan416.com")
        self.path_var = tk.StringVar()
        self.sort_mode = tk.StringVar(value="name")
        self.sort_desc = tk.BooleanVar(value=False)
        self.lang_var = tk.StringVar(value="en")
        self.theme_var = tk.StringVar(value="system")

        # 配置加载顺序：本地配置 -> 初始设置 -> 构建UI -> 应用主题 -> 恢复项目
        self._load_local_config()
        self._detect_initial_settings()

        self._build_ui()
        # 强制刷新确保 Windows 句柄存在，以便应用深色标题栏
        self.root.update()
        self._apply_theme()

        self._refresh_project_combo()
        last = self.all_configs.get("last_active", "")
        if last and last in self.project_list:
            self.project_combo.set(last)
            self.root.after(100, lambda: self.switch_project(None))

    def _load_translations(self):
        # 使用 config 模块获取资源路径
        lang_path = config.get_resource_path(config.LANG_FILE_REL)
        try:
            with open(lang_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            # 如果加载失败，提供最基础的英文回退，防止崩溃
            messagebox.showerror("Error", f"Cannot load languages from:\n{lang_path}\nError: {e}")
            self.translations = {"en": {}, "zh": {}}

    def tr(self, key):
        """翻译帮助函数"""
        lang = self.lang_var.get()
        dct = self.translations.get(lang, self.translations.get("en", {}))
        return dct.get(key, key)

    def _detect_initial_settings(self):
        # 语言检测
        if "language" in self.all_configs:
            self.lang_var.set(self.all_configs["language"])
        else:
            try:
                sys_lang = locale.getdefaultlocale()[0]
                if sys_lang and "zh" in sys_lang.lower():
                    self.lang_var.set("zh")
                else:
                    self.lang_var.set("en")
            except:
                self.lang_var.set("en")

        # 主题检测
        if "theme" in self.all_configs:
            self.theme_var.set(self.all_configs["theme"])
        else:
            self.theme_var.set("system")

        self._save_local_config()

    # === 配置与重置 ===
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
        try:
            with open(config.CONFIG_FILE, 'w') as f:
                json.dump(self.all_configs, f)
        except:
            pass

    def reset_app_config(self):
        """重置所有设置"""
        if messagebox.askyesno(self.tr("status_error"), self.tr("msg_confirm_reset")):
            try:
                if os.path.exists(config.CONFIG_FILE):
                    os.remove(config.CONFIG_FILE)
                self.root.quit()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # === 外观逻辑 ===
    def change_language(self):
        self.all_configs["language"] = self.lang_var.get()
        self._save_local_config()
        self._rebuild_ui()

    def change_theme(self):
        self.all_configs["theme"] = self.theme_var.get()
        self._save_local_config()
        self._apply_theme()

    def _apply_theme(self):
        style = ttk.Style()
        style.theme_use('clam')

        mode = self.theme_var.get()
        is_dark = False

        if mode == "dark":
            is_dark = True
        elif mode == "system":
            # 简易系统主题检测 (仅 Windows)
            if os.name == 'nt':
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                    val, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                    is_dark = (val == 0)
                except:
                    pass

        # 调用 utils 里的跨平台安全函数
        utils.apply_windows_dark_mode(self.root, is_dark)

        # 设置颜色
        if is_dark:
            bg, fg, field, sel = "#2d2d2d", "#ffffff", "#3d3d3d", "#0078d7"
            self.root.configure(bg=bg)
            style.configure(".", background=bg, foreground=fg, fieldbackground=field)
            style.configure("Treeview", background=field, foreground=fg, fieldbackground=field)
            style.map("Treeview", background=[('selected', sel)], foreground=[('selected', 'white')])
            style.configure("TCombobox", fieldbackground=field, background=bg, foreground=fg, arrowcolor="white")
            style.map("TCombobox", fieldbackground=[('readonly', field)], selectbackground=[('readonly', sel)],
                      selectforeground=[('readonly', 'white')])
        else:
            bg, fg, field = "#f0f0f0", "#000000", "#ffffff"
            self.root.configure(bg=bg)
            style.configure(".", background=bg, foreground=fg, fieldbackground=field)
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
            style.map("Treeview", background=[('selected', '#0078d7')], foreground=[('selected', 'white')])
            style.configure("TCombobox", fieldbackground="white", background="white", foreground="black",
                            arrowcolor="black")
            style.map("TCombobox", fieldbackground=[('readonly', 'white')], selectbackground=[('readonly', '#0078d7')],
                      selectforeground=[('readonly', 'white')])

    # === UI 构建 ===
    def _rebuild_ui(self):
        curr_proj = self.name_var.get()
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu): widget.destroy()

        self.root.title(self.tr("app_title"))
        self._build_ui()
        self._apply_theme()

        self._refresh_project_combo()
        if curr_proj in self.project_list:
            self.project_combo.set(curr_proj)

        if self.path_var.get():
            self.refresh_tree_structure(keep_state=True)

    def _build_ui(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Project Menu
        proj_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr("menu_project"), menu=proj_menu)
        proj_menu.add_command(label=self.tr("cmd_add_save"), command=self.save_local_project_info)
        proj_menu.add_command(label=self.tr("cmd_delete_local"), command=self.delete_local_project)
        proj_menu.add_separator()
        proj_menu.add_command(label=self.tr("cmd_clear_cloud"), command=self.clear_cloud_data)
        proj_menu.add_separator()
        proj_menu.add_command(label=self.tr("cmd_reset_config"), command=self.reset_app_config)
        proj_menu.add_command(label=self.tr("cmd_exit"), command=self.root.quit)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr("menu_edit"), menu=edit_menu)
        edit_menu.add_command(label=self.tr("cmd_sel_all"), command=lambda: self.set_all_state(1))
        edit_menu.add_command(label=self.tr("cmd_desel_all"), command=lambda: self.set_all_state(0))
        edit_menu.add_separator()
        edit_menu.add_command(label=self.tr("cmd_check_high"), command=lambda: self.batch_set_state(1))
        edit_menu.add_command(label=self.tr("cmd_uncheck_high"), command=lambda: self.batch_set_state(0))

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr("menu_view"), menu=view_menu)

        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label=self.tr("submenu_theme"), menu=theme_menu)
        theme_menu.add_radiobutton(label=self.tr("theme_system"), variable=self.theme_var, value="system",
                                   command=self.change_theme)
        theme_menu.add_radiobutton(label=self.tr("theme_light"), variable=self.theme_var, value="light",
                                   command=self.change_theme)
        theme_menu.add_radiobutton(label=self.tr("theme_dark"), variable=self.theme_var, value="dark",
                                   command=self.change_theme)

        lang_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label=self.tr("submenu_lang"), menu=lang_menu)
        lang_menu.add_radiobutton(label="English", variable=self.lang_var, value="en", command=self.change_language)
        lang_menu.add_radiobutton(label="中文", variable=self.lang_var, value="zh", command=self.change_language)

        # Info Frame
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
        ttk.Button(r1, text="🔗", command=self.copy_url, width=3).pack(side="left", padx=2)
        ttk.Button(r1, text="🌏", command=self.open_url, width=3).pack(side="left", padx=2)

        r2 = ttk.Frame(info_frame)
        r2.pack(fill="x", pady=5, padx=5)
        ttk.Label(r2, text=self.tr("lbl_path")).pack(side="left")
        ttk.Entry(r2, textvariable=self.path_var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(r2, text=self.tr("btn_browse"), command=self.select_folder).pack(side="left")

        # Toolbar
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

        # Treeview
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("status"), selectmode="extended")

        self.tree.column("#0", width=600, minwidth=150, anchor="w", stretch=True)
        self.tree.heading("#0", text=self.tr("col_file"))

        self.tree.column("status", width=80, minwidth=60, anchor="center", stretch=False)
        self.tree.heading("status", text=self.tr("col_check"))

        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Button-1>", self.on_click)

        # Bottom
        b_frame = ttk.Frame(self.root)
        b_frame.pack(fill="x", padx=10, pady=10)
        self.status_lbl = ttk.Label(b_frame, text=self.tr("status_ready"))
        self.status_lbl.pack(side="left")
        ttk.Button(b_frame, text=self.tr("btn_sync"), command=self.sync_logic).pack(side="right")

    # === Tree & Logic ===
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

        # 使用 logic 模块加载 ignore
        self.gitignore_patterns = logic.load_gitignore(root, config.DEFAULT_IGNORE)
        self._populate(root, "", current_selections)
        self._recalc_folder_states()

    def _populate(self, current_path, parent_uid, selections):
        # 使用 logic 模块排序
        items = logic.get_sorted_items(current_path, self.sort_mode.get(), self.sort_desc.get())
        root_abs = self.path_var.get()

        for item in items:
            full = os.path.join(current_path, item)
            rel = os.path.relpath(full, root_abs)

            # 使用 logic 模块检查 ignore
            if logic.is_ignored(item, rel, self.gitignore_patterns):
                continue

            is_dir = os.path.isdir(full)
            ext = os.path.splitext(item)[1].lower()
            is_bin = ext in config.BINARY_EXTS

            node_type = "dir" if is_dir else ("binary" if is_bin else "file")
            state = 0
            if node_type == 'file' and rel in selections: state = 1

            status_text = self._get_status_icon(state, node_type)
            uid = self.tree.insert(parent_uid, "end", text=f" {item}", values=(status_text,), open=False)
            self.node_data[uid] = {"path": full, "type": node_type, "state": state, "name": item}

            if node_type == 'dir': self._populate(full, uid, selections)

    def _get_status_icon(self, state, ntype):
        if ntype == 'binary': return ICON_BIN
        if state == 1: return ICON_CHECKED
        if state == 2: return ICON_PARTIAL
        return ICON_UNCHECKED

    def on_click(self, event):
        col_id = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        data = self.node_data.get(item_id)
        if not data or data["type"] == "binary": return
        if col_id == "#1":
            new_state = 0 if data["state"] == 1 else 1
            self.set_item_state(item_id, new_state)
            return "break"

    def set_item_state(self, uid, state):
        d = self.node_data[uid]
        d['state'] = state
        self.tree.item(uid, values=(self._get_status_icon(state, d['type']),))
        if d['type'] == 'dir':
            for c in self.tree.get_children(uid): self._set_down(c, state)
        p = self.tree.parent(uid)
        while p: self._update_parent(p); p = self.tree.parent(p)

    def _set_down(self, uid, state):
        d = self.node_data[uid]
        if d['type'] == 'binary': return
        d['state'] = state
        self.tree.item(uid, values=(self._get_status_icon(state, d['type']),))
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
            self.tree.item(uid, values=(self._get_status_icon(ns, d['type']),))

    def _recalc_folder_states(self):
        for uid, d in self.node_data.items():
            if d['type'] == 'file' and d['state'] == 1:
                p = self.tree.parent(uid)
                while p: self._update_parent(p); p = self.tree.parent(p)

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
        if p: self.path_var.set(p); self.refresh_tree_structure()

    def _refresh_project_combo(self):
        self.project_combo['values'] = list(self.project_list.keys())

    def save_local_project_info(self):
        n, p = self.name_var.get().strip(), self.path_var.get()
        if n and p:
            self.project_list[n] = {"url": self.url_var.get(), "path": p}
            self.all_configs["last_active"] = n
            self._save_local_config();
            self._refresh_project_combo();
            self.project_combo.set(n)
            self.status_lbl.config(text=self.tr("msg_saved"))

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
            self.refresh_tree_structure();
            self.pull_cloud_config()
            self.all_configs["last_active"] = n;
            self._save_local_config()

    def copy_url(self):
        self.root.clipboard_clear(); self.root.clipboard_append(f"{self.url_var.get()}/{self.name_var.get()}")

    def open_url(self):
        webbrowser.open(f"{self.url_var.get()}/{self.name_var.get()}")

    def pull_cloud_config(self):
        u, n = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        if not u or not n: return
        self.status_lbl.config(text=self.tr("status_pulling"), foreground="blue");
        self.root.update()
        try:
            r = requests.get(f"{u}/config/{n}", timeout=3)
            if r.status_code == 200:
                s = set(r.json())
                root = self.path_var.get()
                for uid, d in self.node_data.items():
                    if d['type'] == 'file':
                        rel = os.path.relpath(d['path'], root).replace("\\", "/")
                        d['state'] = 1 if (rel in s or rel.replace("/", "\\") in s) else 0
                        self.tree.item(uid, values=(self._get_status_icon(d['state'], 'file'),))
                self._recalc_folder_states()
                self.status_lbl.config(text=self.tr("status_restored"), foreground="green")
            else:
                self.status_lbl.config(text="No Cloud Config", foreground="orange")
        except:
            pass

    def sync_logic(self):
        self.save_local_project_info()
        url, name, root = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip(), self.path_var.get()
        if not url or not name: return
        self.status_lbl.config(text=self.tr("status_packing"), foreground="blue");
        self.root.update()
        try:
            out = [f"# Project: {name}\n## Structure\n"]
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
                            out.append("[Err]")
                        out.append(f"\n--- END: {rel} ---\n")
                    if d['type'] == 'dir': walk_c(self.tree.get_children(uid))

            walk_c(self.tree.get_children(""))
            payload = "\n".join(out)
            requests.post(f"{url}/config/{name}", json=sel_list)
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
                              headers={'Content-Type': 'text/plain; charset=utf-8'})
                self.status_lbl.config(text=self.tr("status_done"), foreground="green")
            else:
                self.status_lbl.config(text=self.tr("status_done"), foreground="green")
        except Exception as e:
            self.status_lbl.config(text=self.tr("status_error"), foreground="red")
            messagebox.showerror(self.tr("status_error"), str(e))

    def clear_cloud_data(self):
        u, n = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        if not u or not n: return
        if messagebox.askyesno(self.tr("status_error"), self.tr("msg_confirm_clear").format(n)):
            try:
                requests.delete(f"{u}/project/{n}")
            except:
                pass
            messagebox.showinfo(self.tr("status_done"), self.tr("msg_done"))