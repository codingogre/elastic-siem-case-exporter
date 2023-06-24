import simplejson as json
import requests
import getopt
import sys
import math

url = ''
username = ''
password = ''
output_file = ''
cases_per_page = 100


def usage():
    usage = """
    Kibana should be host and port
    Example: mykibana.sample.com:5601
    
    Short options
    usage: elastic-siem-case-exporter.py -u <username> -p <password> -n <kibana_host:port> -o <output_file>
    
    GNU long options
    usage: elastic-siem-case-exporter.py --username=<username> --password=<password> --host=<kibana_host:port> --output_file=<output_file>
    """
    print(usage)


def parse_cli(argv):
    global username
    global password
    global url
    global output_file
    try:
        opts, args = getopt.getopt(argv, shortopts="hu:p:n:o:", longopts=["username=", "password=", "host=", "output_file="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-n", "--host"):
            url = "https://%s/api" % arg
        elif opt in ("-o", "--output_file"):
            output_file = arg


def get_case_ids(kibana_url, current_page):
    cases_url = "%s/cases/_find" % kibana_url
    params = {'perPage': cases_per_page, 'page': current_page, 'sortField': 'createdAt'}
    try:
        r = requests.request("GET", cases_url, params=params, auth=(username, password), verify=False)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    return json.loads(r.text)


def export_cases(kibana_url, cases):
    object_url = "%s/saved_objects/_export" % kibana_url
    params = {}
    try:
        r = requests.request("POST", object_url, params=params, auth=(username, password), verify=False)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    return json.loads(r.text)

def main(argv):
    parse_cli(argv)
    current_page = 1
    print("Retrieving Cases from %s/cases/_find" % url)
    response = get_case_ids(url, current_page)
    print('Total cases to process: ', response['total'])
    total_pages = math.ceil(response['total'] / cases_per_page)
    print('Total "pages" to process: ', total_pages)
    case_ids = []
    for current_page in range(current_page, total_pages + 1):
        if current_page != 1:
            response = get_case_ids(url, current_page)
        for case in response['cases']:
            case_ids.append(case['id'])
    print(len(case_ids))
    print(case_ids)
    print('Exporting cases to', output_file)
    export_cases(url, case_ids)
    print('Exporting cases completed!')

if __name__ == '__main__':
    main(sys.argv[1:])
