
def cleanup_domain(domain):
    nr_dots = domain.count(".")
    parts = domain.split(".")

    if nr_dots == 1:
        return [parts[0],".%s" % parts[1]]

    # Domains like: .co.uk, .co.in, and so on
    if parts[-2] in ["co","com","url","net","org","gov","ac","edu","me","gob","gen"]:
        return [parts[-3],".%s" % '.'.join(parts[-2:])]

    # Check pairs
    pairs =  [
            '.go.jp',
            '.ne.jp',
            '.gr.jp',
            '.or.jp',
            '.co.uk',
            '.sh.cn',
            '.cq.cn',
            '.nic.in',
            '.co.kr',
            '.or.kr',
            '.ne.kr',
            '.tx.us',
            '.nj.us',
            '.fl.us',
            '.ny.us',
            '.ca.us',
            '.pa.us',
            '.ga.us',
            '.qa.ca',
            '.qc.ca',
            '.on.ca',
            '.mus.br',
            '.jus.br',
            '.msk.ru'
    ]
    for p in pairs:
        if domain.endswith(p):
            return [domain.replace(p,""),p]

    if parts[-1] in ['fr', 'com', 'net', 'gr', 'be', 'uk']:
        return [parts[-2], ".%s" % parts[-1]]

    else:
        print "Didn't parse: %s " % domain

    return [''.join(parts[:-1]), ".%s" % parts[-1]]


def print_all_ts(ts_domains):

    init_crawling_list = []
    for d in ts_domains:
        for model in ts_domains[d]:
            for td in ts_domains[d][model]:
                if td == d:
                    continue
                init_crawling_list.append("http://www."+td)

    return init_crawling_list


def generate_ts_domains(domain, f_fingers):
    # global f_fingers
    ts_domains = {}

    # google.com -> ['google', '.com']
    cl_domain = cleanup_domain(domain)
    f_clean_domain = ''.join(cl_domain)

    ts_domains[f_clean_domain] = {}

    cld_len = len(cl_domain[0])

    # Model 1: Character substitution, fat finger one
    ts_domains[f_clean_domain]["c_subs"] = []
    for i in range(0,cld_len):
        ts_characters = f_fingers[cl_domain[0][i]]
        for c in ts_characters:
            ts_domains[f_clean_domain]["c_subs"].append("%s%c%s%s" % (cl_domain[0][0:i],c,cl_domain[0][i+1:],cl_domain[1]))

    # Model 2: Missing dot typos:
    ts_domains[f_clean_domain]["c_mdot"] = []
    nr_dots = f_clean_domain.count(".")

    ts_domains[f_clean_domain]["c_mdot"].append('www' + f_clean_domain)
    if nr_dots == 2:
        dot_index = f_clean_domain.find(".")
        ts_domains[f_clean_domain]["c_mdot"].append(f_clean_domain[:dot_index]+ f_clean_domain[dot_index + 1:])

    # Model 3: Character omission
    ts_domains[f_clean_domain]["c_omm"] = []
    for i in range(0, cld_len):
        ts_domains[f_clean_domain]["c_omm"].append(f_clean_domain[:i]+ f_clean_domain[i + 1:])

    # Model 4: Character permutation
    ts_domains[f_clean_domain]["c_perm"] = []
    for i in range(0, cld_len - 1):
        ts_domains[f_clean_domain]["c_perm"].append(f_clean_domain[:i] + f_clean_domain[i+1] + f_clean_domain[i] + f_clean_domain[i+2:])

    # Model 5: Character duplication
    ts_domains[f_clean_domain]["c_dupl"] = []
    for i in range(0, cld_len):
        ts_domains[f_clean_domain]["c_dupl"].append(f_clean_domain[:i] + f_clean_domain[i] + f_clean_domain[i] + f_clean_domain[i+1:])

    return ts_domains[f_clean_domain]


def get_url_list(num_of_url):
    f_fingers = {}
    ts_domains = {}

    # Read in the qwerty maps
    f = open("/home/siddharth/Documents/WebCrawlerV1/producer/typo_squat_utils/qwerty.map")
    for line in f:
        line = line.strip()
        parts = line.split(" ")
        f_fingers[parts[0]] = parts[1]
    f.close()

    # Read in list of domains list
    f = open("/home/siddharth/Documents/WebCrawlerV1/producer/typo_squat_utils/domains.txt", "r")
    all_domains = list()
    counter = 0
    for d in f:
        if counter < num_of_url:
            all_domains.append(d.strip())
        else:
            break
        counter += 1
    f.close()

    for domain in all_domains:
        ts_domains[domain] = generate_ts_domains(domain, f_fingers)

    return print_all_ts(ts_domains)


if __name__ == "__main__":
    print get_url_list(2)
