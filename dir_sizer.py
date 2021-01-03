import math
import os

IGNORED_ERRORS = (PermissionError, FileNotFoundError, OSError)


def main():
    start_path = '/Users/doruk'

    stats = do_dir(start_path)
    print_stats(start_path, stats, tree_depth=3)


def do_dir(dir_path):
    result = {
        "item_path": dir_path,
        "item_size": 0,
        "items": []
    }

    try:
        item_list = os.listdir(dir_path)
    except IGNORED_ERRORS:
        return result

    for item_name in item_list:
        item_path = os.path.join(dir_path, item_name)

        if os.path.isdir(item_path):
            sub_result = do_dir(item_path)

            result["items"].append(sub_result)
            result["item_size"] += sub_result['item_size']
        else:
            try:
                item_size = os.path.getsize(item_path)
            except IGNORED_ERRORS:
                continue

            result["item_size"] += item_size
            result['items'].append({
                "item_path": item_path,
                "item_size": item_size,
                "items": []
            })

    return result


def print_stats(dir_path, stats, tree_depth=3):
    if tree_depth == -1:
        return

    indent = "# " * (3 - tree_depth)
    print(indent, stats['item_path'].replace(dir_path, ''))
    print(indent, convert_size(stats['item_size']))
    print('---------------------')

    sub_folders = sorted(stats['items'], key=lambda x: x['item_size'], reverse=True)[0:10]

    for sub_folder in sub_folders:
        print_stats(dir_path, sub_folder, tree_depth - 1)


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


if __name__ == '__main__':
    main()
