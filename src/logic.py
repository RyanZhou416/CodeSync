import os
import fnmatch
import config
import datetime
import glob


def load_gitignore(root_path, default_ignore):
    """读取 .gitignore 并合并默认忽略列表"""
    patterns = set(default_ignore)
    git_file = os.path.join(root_path, ".gitignore")
    if os.path.exists(git_file):
        try:
            with open(git_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line.rstrip('/'))
        except:
            pass
    return list(patterns)


def is_ignored(filename, rel_path, patterns):
    """判断文件是否被忽略"""
    if filename in patterns: return True
    for p in patterns:
        if fnmatch.fnmatch(filename, p): return True
        if p in rel_path.split(os.sep): return True
    return False


def get_sorted_items(path, sort_mode, reverse):
    """获取排序后的文件列表"""
    try:
        items = os.listdir(path)
    except:
        return []

    f_objs = []
    for item in items:
        full = os.path.join(path, item)
        is_dir = os.path.isdir(full)
        mtime = 0
        ext = os.path.splitext(item)[1].lower()

        if sort_mode == 'time':
            try:
                mtime = os.stat(full).st_mtime
            except:
                pass

        f_objs.append({
            'name': item,
            'd': is_dir,
            't': mtime,
            'e': ext
        })

    if sort_mode == 'name':
        f_objs.sort(key=lambda x: (not x['d'], x['name'].lower()), reverse=reverse)
    elif sort_mode == 'time':
        f_objs.sort(key=lambda x: x['t'], reverse=reverse)
    elif sort_mode == 'type':
        f_objs.sort(key=lambda x: (x['e'], x['name'].lower()), reverse=reverse)

    return [x['name'] for x in f_objs]


def generate_metadata_header(project_name, root_path):
    """生成文件头的元数据"""
    now = datetime.datetime.now().strftime(config.DATE_FMT_LOG)
    return (
        f"{config.MAGIC_HEADER}\n"
        f"# Project: {project_name}\n"
        f"# Generated: {now}\n"
        f"# Root: {root_path}\n"
        f"{'=' * 40}\n\n"
    )


def clean_old_exports(root_path, current_new_file):
    """
    只保留最新的输出文件。
    安全策略：
    1. 扫描根目录所有文件
    2. 只检查包含 MAGIC_HEADER 的文件
    3. 解析生成时间，删除比 current_new_file 旧的文件
    """
    try:
        # === 修复 1: 规范化 root_path，防止 glob 在 Windows 上因为混合斜杠而出错 ===
        root_path = os.path.normpath(root_path)

        # 获取所有文件
        files = glob.glob(os.path.join(root_path, "*"))

        # === 修复 2: 统一路径格式以便比较 ===
        # Windows 不区分大小写，必须用 normcase 统一转小写比较
        abs_current = os.path.normcase(os.path.abspath(current_new_file))

        for f_path in files:
            if os.path.isdir(f_path): continue

            # === 修复 2 的应用 ===
            abs_f = os.path.normcase(os.path.abspath(f_path))
            if abs_f == abs_current:
                continue

            try:
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline().strip()
                    if first_line == config.MAGIC_HEADER:
                        print(f"Removing old export: {f_path}")
                        os.remove(f_path)
            except Exception:
                continue
    except Exception as e:
        print(f"Error cleaning old files: {e}")