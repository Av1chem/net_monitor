import json
import logging
import argparse
from time import sleep
from random import randint
from selenium import webdriver
from browsermobproxy import Server

def parse_proxy_log(url):
    global proxy, logs
    target_request_found = False
    current_log = []
    for entry in proxy.har['log']['entries']:
        if 'b/ss' in entry['request']['url']:
            entry['pageref'] = entry['pageref'].replace(prefix, '')
            current_log.append(entry)
            target_request_found = True
    if target_request_found:
        logs.append({
            'url': url,
            'status': 'success',
            'requests': current_log
        })
        logging.info('target request found')
    else:
        logs.append({
            'url': url,
            'status': 'failed'
        })
        logging.warning('target request not found')


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    # parse arguments
    parser = argparse.ArgumentParser(add_help=True, description='Net monitor tool')
    parser.add_argument('-i', '--input', action='store', dest='inp', help='input filename')
    parser.add_argument('-o', '--output', action='store', dest='out', help='output filename')
    parser.add_argument('-v', '--visible', action='store_const', dest='vis', help='make browser visible', const=True)
    parser.add_argument('-p', '--page', action='store_const', dest='page', help='check page', const=True)
    parser.add_argument('-l', '--links', action='store_const', dest='links', help='check links on page', const=True)
    parser.add_argument('-w', '--wait', action='store', dest='wait', help='wait for page loading, seconds',
                        type=int, default=10)
    args = parser.parse_args()
    if args.inp is None or args.out is None:
        logging.info('''Input or output filename doesn't provided.''')
        exit(-1)

    # starting proxy server
    logging.info('starting proxy')
    with open('config.txt') as f:
        path = f.readline()
    server = Server(path=path, options={'port': 8090})
    server.start()
    proxy = server.create_proxy()
    logging.info('proxy started')

    # starting selenium
    logging.info('starting selenium')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if not bool(args.vis):
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--proxy-server=%s' % proxy.proxy)
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)
    logging.info('selenium started')
    prefix = 't{}_'.format(randint(0, 10000000))
    logs = []

    # check each page from the input file
    with open(args.inp) as f:
        for page in f:
            page_stripped = page.strip()

            # parsing requests info for page
            proxy.new_har('{0}{1}'.format(prefix, page_stripped))
            logging.info('getting page: {}'.format(page_stripped))
            try:
                driver.get(page_stripped)
                if bool(args.page):
                    sleep(args.wait)
                    parse_proxy_log(page_stripped)

                # check each link on page
                if bool(args.links):
                    links = [a.get_attribute('href') for a in driver.find_elements_by_css_selector('a[href]')]
                    links_total = len(links)
                    logging.info('found {0} links on page {1}'.format(links_total, page_stripped))
                    for i, link in zip(range(links_total), links):
                        proxy.new_har('{0}{1}'.format(prefix, link))
                        logging.info('checking link ({0} of {1}): {2}'.format(i + 1, links_total, link))
                        try:
                            driver.get(link)
                            sleep(args.wait)
                            parse_proxy_log(link)
                        except Exception as e:
                            logging.error(str(e))
                        a = 1
            except Exception as e:
                logging.error(str(e))

    # write data
    logging.info('write data to file: {}'.format(args.out))
    with open(args.out, "w+") as f:
        f.write(json.dumps(logs, indent=4))

    # shutdown webdriver & proxy server
    logging.info('shutting down')
    server.stop()
    driver.quit()
