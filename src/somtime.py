# from utils import  get_response
# from constants import PEP_URL
# from bs4 import BeautifulSoup
# import requests_cache
# from pprint import pprint
# from urllib.parse import urljoin
# from configs import EXPECTED_STATUS
# from tqdm import tqdm
# import logging
# import re
#
#
# EXPECTED_STATUS = {
#     'A': ('Active', 'Accepted'),
#     'D': ('Deferred',),
#     'F': ('Final',),
#     'P': ('Provisional',),
#     'R': ('Rejected',),
#     'S': ('Superseded',),
#     'W': ('Withdrawn',),
#     '': ('Draft', 'Active'),
# }
#
#
#
# def pep_versions(session):
#     response = get_response(session, PEP_URL)
#     if response is None:
#         return
#
#     soup = BeautifulSoup(response.text, features='lxml')
#     sidebar_tr = soup.find_all('tr', attrs={'class': 'row-even'})
#     pep_list = []
#     all_statuses_detail = {}
#     all_statuses_list = {}
#     status_mismatch_list = []
#     results = [('Статус', 'Количество')]
#     for pep_element in tqdm(sidebar_tr):
#         pep_a_tag = pep_element.find('a')
#         if not pep_a_tag:
#             continue
#         pep_types_key = None
#         abbr_tag = pep_element.find('abbr')
#         status_on_list_page = abbr_tag.get('title') if abbr_tag else None
#         if status_on_list_page:
#             parts = status_on_list_page.split(', ')
#             pep_types_key = parts[0]
#             status_on_list_page = parts[1] if len(parts) > 1 else None
#         pep_status = None
#         if abbr_tag and abbr_tag.text:
#             pep_status = abbr_tag.text[1:]
#         pep_number = pep_a_tag.text
#         pep_title = pep_element.find_all('a')[1].text if len(
#             pep_element.find_all('a')) > 1 else None
#         pep_authors = pep_element.find_all('td')[3].text.strip() if len(
#             pep_element.find_all('td')) > 3 else 'N/A'
#         href = pep_a_tag['href']
#         pep_link = urljoin(PEP_URL, href)
#         response = get_response(session, pep_link)
#         if response is None:
#             continue
#         soup = BeautifulSoup(response.text, features='lxml')
#         status_on_detail_page = soup.find('abbr').text
#         data_dict = {'pep_number': pep_number, 'link': pep_link,
#                      'status': pep_status,
#                      'status_on_list_page': status_on_list_page,
#                      'title': pep_title, 'authors': pep_authors,
#                      'status_on_detail_page': status_on_detail_page,
#                      'pep_type_key': pep_types_key}
#         pep_list.append(data_dict)
#         all_statuses_detail[status_on_detail_page] = all_statuses_detail.get(
#             status_on_detail_page, 0) + 1
#
#         all_statuses_list[pep_status] = all_statuses_list.get(pep_status, 0) + 1
#         expected_statuses = EXPECTED_STATUS.get(pep_status, [])
#
#         if status_on_detail_page not in expected_statuses:
#             mismatch = (
#             pep_link, status_on_list_page, pep_number, status_on_detail_page)
#             status_mismatch_list.append(mismatch)
#     if status_mismatch_list:
#         print("Несовпадающие статусы:")
#         for pep_link, status_on_list_page, pep_number, status_on_detail_page in status_mismatch_list:
#             print(f"{pep_link}\nСтатус в карточке: {status_on_list_page}")
#             print(f"Ожидаемые статусы: {status_on_detail_page}")
#     # for key, value in all_statuses_detail:
#     #     results.append((key, value))
#     results.extend((key, value) for key, value in all_statuses_detail.items())
#     print(results)
#     # pprint(pep_list[-1])
#     # print(f'Всего найдено PEP: {len(pep_list)}')
#     pprint(all_statuses_detail)
#     # pprint(all_statuses_list)
#     return results
#
#
#
# if __name__ == '__main__':
#     session = requests_cache.CachedSession()
#     pep_versions(session)