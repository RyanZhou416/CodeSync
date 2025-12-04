import os
import fnmatch


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
    # 1. 精确匹配文件名
    if filename in patterns: return True
    # 2. 通配符匹配
    for p in patterns:
        if fnmatch.fnmatch(filename, p): return True
        # 3. 路径片段匹配 (例如 node_modules)
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
        # 文件夹在前
        f_objs.sort(key=lambda x: (not x['d'], x['name'].lower()), reverse=reverse)
    elif sort_mode == 'time':
        f_objs.sort(key=lambda x: x['t'], reverse=reverse)
    elif sort_mode == 'type':
        f_objs.sort(key=lambda x: (x['e'], x['name'].lower()), reverse=reverse)

    return [x['name'] for x in f_objs]