import os
import json
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import hashlib
import datetime

import config
import utils
import logic

# 统一勾选框样式 (Unicode)
ICON_UNCHECKED = "☐"
ICON_CHECKED = "☑"
ICON_PARTIAL = "⊟"  # 保持部分选中状态图标，用于文件夹
ICON_BIN = ""


class SettingsDialog(tk.Toplevel):
    """设置弹窗页面"""

    def __init__(self, parent, config_data, callback):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.config_data = config_data
        self.callback = callback

        # 默认值
        self.use_timestamp = tk.BooleanVar(value=config_data.get("use_timestamp", False))
        self.keep_latest = tk.BooleanVar(value=config_data.get("keep_latest", False))
        self.custom_name = tk.StringVar(value=config_data.get("custom_name", "code_context"))

        self._build_ui()
        utils.apply_windows_dark_mode(self, False)  # 简单处理，跟随主窗口稍显复杂

    def _build_ui(self):
        p = ttk.Frame(self, padding=20)
        p.pack(fill="both", expand=True)

        # 1. 文件命名设置
        grp1 = ttk.LabelFrame(p, text="Output Filename Settings", padding=10)
        grp1.pack(fill="x", pady=5)

        ttk.Label(grp1, text="Base Filename (.txt):").pack(anchor="w")
        ttk.Entry(grp1, textvariable=self.custom_name).pack(fill="x", pady=5)

        ttk.Checkbutton(grp1, text="Append Timestamp (YYYY-MM-DD_...)",
                        variable=self.use_timestamp).pack(anchor="w", pady=5)

        # 2. 文件管理
        grp2 = ttk.LabelFrame(p, text="File Management", padding=10)
        grp2.pack(fill="x", pady=15)

        ttk.Checkbutton(grp2, text="Keep Latest Only (Auto-delete old exports)",
                        variable=self.keep_latest).pack(anchor="w")
        ttk.Label(grp2, text="* Checks file header for safety.",
                  font=("Arial", 8), foreground="gray").pack(anchor="w", padx=20)

        # 按钮
        btn_frame = ttk.Frame(p)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side="right")
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)

    def save(self):
        new_conf = {
            "use_timestamp": self.use_timestamp.get(),
            "keep_latest": self.keep_latest.get(),
            "custom_name": self.custom_name.get().strip() or "code_context"
        }
        self.callback(new_conf)
        self.destroy()


class CodeSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("950x850")

        self.node_data = {}
        self.all_configs = {}
        self.project_list = {}
        self.gitignore_patterns = []
        self.translations = {}

        # 导出设置 (默认)
        self.export_settings = {
            "use_timestamp": False,
            "keep_latest": False,
            "custom_name": "code_context"
        }

        # 加载语言包
        self._load_translations()

        # UI 变量
        self.name_var = tk.StringVar()
        self.url_var = tk.StringVar(value="https://code.ryan416.com")
        self.path_var = tk.StringVar()
        self.sort_mode = tk.StringVar(value="name")
        self.sort_desc = tk.BooleanVar(value=False)
        self.lang_var = tk.StringVar(value="en")
        self.theme_var = tk.StringVar(value="system")
        self.auto_export_var = tk.BooleanVar(value=False)

        # 配置加载
        self._load_local_config()
        self._detect_initial_settings()

        self.root.title(self.tr("app_title"))
        self._build_ui()
        self.root.update()
        self._apply_theme()

        self._refresh_project_combo()
        last = self.all_configs.get("last_active", "")
        if last and last in self.project_list:
            self.project_combo.set(last)
            self.root.after(100, lambda: self.switch_project(None))

    def _load_translations(self):
        lang_path = config.get_resource_path(config.LANG_FILE_REL)
        try:
            with open(lang_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            self.translations = {"en": {}, "zh": {}}

    def tr(self, key):
        lang = self.lang_var.get()
        dct = self.translations.get(lang, self.translations.get("en", {}))
        return dct.get(key, key)

    def _detect_initial_settings(self):
        # 语言
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

        # 主题
        self.theme_var.set(self.all_configs.get("theme", "system"))
        self.auto_export_var.set(self.all_configs.get("auto_export", False))

        # 导出设置
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
        try:
            with open(config.CONFIG_FILE, 'w') as f:
                json.dump(self.all_configs, f)
        except:
            pass

    def open_settings_dialog(self):
        SettingsDialog(self.root, self.export_settings, self.update_export_settings)

    def update_export_settings(self, new_settings):
        self.export_settings = new_settings
        self._save_local_config()
        messagebox.showinfo(self.tr("status_done"), "Settings Saved!")

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
            # 使用新的跨平台检测
            is_dark = utils.is_system_dark_mode()

        utils.apply_windows_dark_mode(self.root, is_dark)

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

    def _build_ui(self):
        # 清理旧组件 (如果重建 UI)
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
        edit_menu.add_command(label="Settings...", command=self.open_settings_dialog)  # 新增设置入口

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

        # 信息栏
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

        # 工具栏
        tool_frame = ttk.Frame(self.root)
        tool_frame.pack(fill="x", padx=10, pady=2)
        ttk.Button(tool_frame, text=self.tr("btn_pull"), command=self.pull_cloud_config).pack(side="left")

        # 右侧工具
        ttk.Label(tool_frame, text=self.tr("lbl_sort")).pack(side="right", padx=5)
        self.sort_btn = ttk.Button(tool_frame, text="⬇", width=3, command=self.toggle_sort_dir)
        self.sort_btn.pack(side="right")
        sort_cb = ttk.Combobox(tool_frame, textvariable=self.sort_mode, state="readonly", width=8)
        sort_cb['values'] = ("name", "time", "type")
        sort_cb.pack(side="right", padx=2)
        sort_cb.bind("<<ComboboxSelected>>", self.on_sort_change)

        # === 新增：刷新按钮 ===
        ttk.Button(tool_frame, text="🔄", width=3, command=lambda: self.refresh_tree_structure(keep_state=True)).pack(
            side="right", padx=10)

        # 树状图
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

        # 底部按钮
        b_frame = ttk.Frame(self.root)
        b_frame.pack(fill="x", padx=10, pady=10)
        self.status_lbl = ttk.Label(b_frame, text=self.tr("status_ready"))
        self.status_lbl.pack(side="left")

        ttk.Button(b_frame, text=self.tr("btn_sync"), command=self.sync_logic).pack(side="right", padx=2)
        ttk.Checkbutton(b_frame, text=self.tr("chk_also_local"), variable=self.auto_export_var).pack(side="right",
                                                                                                     padx=5)
        ttk.Button(b_frame, text=self.tr("btn_export_txt"), command=self.export_local_only).pack(side="right", padx=5)

    def refresh_tree_structure(self, keep_state=False):
        """
        刷新树状结构
        keep_state=True:
        - 记录当前选中的文件 (relpath)
        - 重新扫描目录
        - 恢复选中状态
        - 逻辑结果：
          1. 文件如果消失了 -> 自动不显示 (因为新扫描没有)
          2. 新文件 -> 默认 state=0 (因为不在记录的 relpath 中)
          3. 文件内容改变 -> 保持原状态 (因为 relpath 没变)
        """
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
            # 恢复之前的状态
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
        while p:
            self._update_parent(p)
            p = self.tree.parent(p)

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
        self.root.clipboard_clear();
        self.root.clipboard_append(f"{self.url_var.get()}/{self.name_var.get()}")

    def clear_cloud_data(self):
        u, n = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        if not u or not n: return
        if messagebox.askyesno(self.tr("status_error"), self.tr("msg_confirm_clear").format(n)):
            try:
                requests.delete(f"{u}/project/{n}")
            except:
                pass
            messagebox.showinfo(self.tr("status_done"), self.tr("msg_done"))

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

    def _generate_payload(self):
        url, name, root = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip(), self.path_var.get()
        if not name or not root: return None, None

        # === 修改：注入元数据头 ===
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
                        out.append("[Err]")
                    out.append(f"\n--- END: {rel} ---\n")
                if d['type'] == 'dir': walk_c(self.tree.get_children(uid))

        walk_c(self.tree.get_children(""))

        return "\n".join(out), sel_list

    def _get_export_filename(self):
        """根据设置生成输出文件名"""
        base = self.export_settings.get("custom_name", "code_context")
        if not base.endswith(".txt"): base += ".txt"

        if self.export_settings.get("use_timestamp", False):
            ts = datetime.datetime.now().strftime(config.DATE_FMT_FILE)
            name_part, ext_part = os.path.splitext(base)
            return f"{name_part}_{ts}{ext_part}"
        return base

    def export_local_only(self):
        payload, _ = self._generate_payload()
        if not payload:
            messagebox.showwarning("Warning", "Please select a project first.")
            return

        root = self.path_var.get()
        filename = self._get_export_filename()
        target_path = os.path.join(root, filename)

        # 如果没有开启时间戳，或者是自定义名称，询问保存路径（提供默认值）
        if not self.export_settings.get("use_timestamp", False):
            target_path = filedialog.asksaveasfilename(
                initialdir=root,
                initialfile=filename,
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )

        if target_path:
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(payload)

                # === 新增：清理旧文件逻辑 ===
                if self.export_settings.get("keep_latest", False):
                    logic.clean_old_exports(root, target_path)

                messagebox.showinfo("Success", self.tr("msg_export_ok").format(target_path))
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def sync_logic(self):
        self.save_local_project_info()
        payload, sel_list = self._generate_payload()
        if not payload: return

        # 本地自动备份逻辑
        if self.auto_export_var.get():
            root = self.path_var.get()
            filename = self._get_export_filename()
            target_path = os.path.join(root, filename)
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(payload)
                # 清理旧文件
                if self.export_settings.get("keep_latest", False):
                    logic.clean_old_exports(root, target_path)
            except:
                pass

        url, name = self.url_var.get().strip().rstrip("/"), self.name_var.get().strip()
        self.status_lbl.config(text=self.tr("status_packing"), foreground="blue");
        self.root.update()

        try:
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