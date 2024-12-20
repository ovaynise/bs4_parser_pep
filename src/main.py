import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections import defaultdict

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = soup.find_all('div',
                            attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar[0].find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise ValueError('Не найден раздел "All versions" на странице')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    table_tag = soup.find_all('table', attrs={'class': 'docutils'})[0]
    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar_tr = soup.find_all('tr', attrs={'class': 'row-even'})
    all_statuses_detail = defaultdict(int)
    status_mismatch_list = []
    results = [('Статус', 'Количество')]
    for pep_element in tqdm(sidebar_tr):
        pep_a_tag = pep_element.find('a')
        if not pep_a_tag:
            continue
        abbr_tag = pep_element.find('abbr')
        status_on_list_page = abbr_tag.get('title') if abbr_tag else None
        if status_on_list_page:
            parts = status_on_list_page.split(', ')
            status_on_list_page = parts[1] if len(parts) > 1 else None
        pep_status = None
        if abbr_tag and abbr_tag.text:
            pep_status = abbr_tag.text[1:]
        href = pep_a_tag['href']
        pep_link = urljoin(PEP_URL, href)
        response = get_response(session, pep_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        status_on_detail_page = soup.find('abbr').text
        all_statuses_detail[status_on_detail_page] += 1
        expected_statuses = EXPECTED_STATUS.get(pep_status, [])
        if status_on_detail_page not in expected_statuses:
            mismatch = (pep_link, status_on_list_page, status_on_detail_page)
            status_mismatch_list.append(mismatch)
    if status_mismatch_list:
        logging.info('Несовпадающие статусы:')
        for (pep_link,
             status_on_list_page,
             status_on_detail_page) in status_mismatch_list:
            logging.info(f'{pep_link}\nСтатус в карточке:'
                         f' {status_on_list_page}')
            logging.info(f'Ожидаемые статусы: {status_on_detail_page}')
    results.extend(all_statuses_detail.items())
    total_count = sum(all_statuses_detail.values())
    results.append(('Total', total_count))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
