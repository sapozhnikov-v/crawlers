import ujson


def read_json_from_file(path):
    with open(path, encoding='utf-8') as r:
        return ujson.loads(r.read())


def write_json_to_file(path, dumped_json):
    with open(path, 'w', encoding='utf-8') as w:
        w.write(dumped_json)


def dump(item):
    return ujson.dumps(item, indent=4, ensure_ascii=False)