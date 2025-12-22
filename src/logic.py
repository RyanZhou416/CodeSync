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
        # 获取所有文件
        files = glob.glob(os.path.join(root_path, "*"))

        for f_path in files:
            # 跳过目录和刚刚生成的文件
            if os.path.isdir(f_path): continue
            if os.path.abspath(f_path) == os.path.abspath(current_new_file): continue

            # 安全检查：是否是 CodeSync 生成的文件
            try:
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline().strip()
                    # 只有第一行严格匹配 MAGIC_HEADER 才删除
                    if first_line == config.MAGIC_HEADER:
                        # 这是一个旧的导出文件，安全删除
                        print(f"Removing old export: {f_path}")
                        os.remove(f_path)
            except Exception:
                continue
    except Exception as e:
        print(f"Error cleaning old files: {e}")