import ConfigParser


def proxy_parser(proxy_file, proxy_nature):
    config = ConfigParser.ConfigParser()
    config.read(proxy_file)
    dict1 = {}
    options = config.options(proxy_nature)
    for option in options:
        try:
            dict1[option] = config.get(proxy_nature, option)
        except:
            dict1[option] = None
    return dict1


def set_proxy(args):
    _proxy = {}
    mitm_server_port = proxy_parser(args.proxy_file, "mitm_server_port")['port']
    _proxy_nature = {"native_proxy": set_native_proxy,
                     "firefox_proxy": set_firefox_proxy,
                     "chrome_proxy": set_chrome_proxy,
                     "mitm_server_proxy": set_mitm_proxy}

    if args.proxy_file is not None:
        for key in _proxy_nature:
            _proxy[key] = _proxy_nature[key](mitm_server_port)

        _proxy["couchdb_server_proxy"] = set_couchdb_server_proxy(args)

    return _proxy


def set_firefox_proxy(mitm_server_port):
    firefox_proxy = '127.0.0.1:'+mitm_server_port
    return firefox_proxy


def set_chrome_proxy(mitm_server_port):
    chrome_proxy = '--proxy-server=127.0.0.1:'+mitm_server_port
    return chrome_proxy


def set_mitm_proxy(mitm_server_port):
    return mitm_server_port


def set_native_proxy(mitm_server_port):
    protos = ['http', 'https', 'ssl', 'ftp']
    ret_dict = {}
    for proto in protos:
        ret_dict[proto] = proto+'://'+'127.0.0.1:'+mitm_server_port

    return ret_dict


def set_couchdb_server_proxy(args):
    return proxy_parser(args.proxy_file, "couchdb_server_proxy")['proxy']


def set_db(args):
    return proxy_parser(args.proxy_file, "couchdb_server_name")['server_name']


def set_data_requirement(args):
    data_required = proxy_parser(args.proxy_file, "capture_data")['data_required']
    return data_required.split(',')
