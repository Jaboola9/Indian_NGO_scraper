import time
import pandas as pd
import stringcase as sc
from selenium import webdriver

main = {}
fcra = {}
members = {}
source_funds = {}


def col_name_create(df):
    """Forms blank dictionary based on complete NGO info (will not work if missing values are present)."""
    new_df = {}
    new_df['ngo'] = []
    new_df[0] = []
    for col in df.columns:
        new_df[col] = []
    return new_df


def col_name_append(df, dct, ngo_name):
    """appends dictionary based on missing or non missing values"""
    ngo_repeat = [ngo_name] * len(df)
    zero_fill = ['Not missing'] * len(df)
    if 0 in df.columns:
        dct[0] = dct[0] + ['Missing info']
        dct['ngo'] = dct['ngo'] + [ngo_name]
        all_keys = list(dct.keys())
        fill_keys = all_keys[2:]
        # print(fill_keys)
        for key in fill_keys:
            dct[key] = dct[key] + ['Missing info']
    else:
        dct['ngo'] = dct['ngo'] + ngo_repeat
        dct[0] = dct[0] + zero_fill
        for col in df.columns:
            value_list = []
            for value in df[col]:
                value_list.append(value)
            dct[col] = dct[col] + value_list
    return dct


#
# browser = webdriver.Chrome()

darpan_url = "https://ngodarpan.gov.in/index.php/home/statewise"


def get_ngo_name(ngo_info):
    """scrapes name of NGO using selenium <--"""
    ngo_title = ngo_info.find_element_by_id("ngo_name_title")
    ngo_name = ngo_title.text
    return ngo_name


def load_all_pages(darpan_url):
    """initiates Selenium webdriver and gathers all page addresses to scrape"""
    browser = webdriver.Chrome()
    browser.get(darpan_url)
    all_states = [x.get_attribute('href') for x in browser.find_elements_by_class_name("bluelink11px")]
    print(len(all_states))
    all_pages = []
    for x in all_states:
        last = (int(x.rsplit('/')[-3]) // 100) + 1
        for n in range(0, last):
            all_pages.append(x[:-1] + f'{n + 1}' + '?per_page=100')
    print(len(all_pages))
    return all_pages, browser


def get_page_popups(single_page, browser):
    """finds all popup boxes on a single page"""
    all_page_popups = []
    browser.get(single_page)
    tds = browser.find_elements_by_tag_name("td")
    for td in tds:
        a_list = td.find_elements_by_tag_name("a")
        for name in a_list:
            if (name.get_attribute("href") is not None and "javascript:void" in name.get_attribute("href")):
                all_page_popups.append(name)
    print(len(all_page_popups))
    return all_page_popups


def initiate_ngo_data(pops, browser):
    """clicks on popup containing NGO table """
    pops[0].click()
    time.sleep(4)
    ngo_info = browser.find_element_by_id("ngo_info_modal")
    ngo_title = ngo_info.find_element_by_id("ngo_name_title")
    ngo_name = ngo_title.text
    tables = ngo_info.find_elements_by_tag_name("table")
    text_list = []
    rough_tables = []
    transpose = [1, 1, 0, 1, 0, 0, 0, 1]
    for table in tables:
        text_list.append(table.text)
        rough = pd.read_html(table.get_attribute('outerHTML'))
        rough_tables.append(rough[0])
    turntuples = list(zip(rough_tables, transpose))
    format_tables = []
    for df, y in turntuples:
        if y == 1:
            df = df.T
            format_tables.append(df)
        else:
            format_tables.append(df)
    headshot = [1, 1, 0, 1, 0, 2, 0, 1]
    tableshot = list(zip(format_tables, headshot))
    beautiful_tables = []
    for df, y in tableshot:
        if y == 1:
            new_header = df.iloc[0]  # grab the first row for the header
            df = df[1:]  # take the data less the header row
            df.columns = new_header
            beautiful_tables.append(df)
        elif y == 2:
            df.columns = ['info']
            beautiful_tables.append(df)
        else:
            beautiful_tables.append(df)
    sortframes = [0, 0, 1, 0, 2, 4, 3, 0]
    sortzip = list(zip(beautiful_tables, sortframes))
    for df, y in sortzip:
        if y == 0:
            main['ngo_id'] = []
            for col in list(df.columns):
                main[col] = []
        elif y == 1:
            members = col_name_create(df)
        elif y == 2: \
                fcra = col_name_create(df)
        elif y == 3:
            source_funds = col_name_create(df)
        else:
            info = dict(df)
            main['info'] = []
    browser.find_element_by_xpath("//div[@class='modal-header']/button[@class='close']/span").click()
    time.sleep(1)
    dict_list = [main, members, fcra, source_funds]
    return dict_list


def get_ngo_data(link, browser, dict_list):
    """scrapes all NGO data from table and closes popup"""
    main = dict_list[0]
    members = dict_list[1]
    fcra = dict_list[2]
    source_funds = dict_list[3]
    link.click()
    time.sleep(5)
    ngo_info = browser.find_element_by_id("ngo_info_modal")
    ngo_title = ngo_info.find_element_by_id("ngo_name_title")
    ngo_name = ngo_title.text
    tables = ngo_info.find_elements_by_tag_name("table")
    text_list = []
    rough_tables = []
    transpose = [1, 1, 0, 1, 0, 0, 0, 1]
    for table in tables:
        text_list.append(table.text)
        rough = pd.read_html(table.get_attribute('outerHTML'))
        rough_tables.append(rough[0])
    turntuples = list(zip(rough_tables, transpose))
    format_tables = []
    for df, y in turntuples:
        if y == 1:
            df = df.T
            format_tables.append(df)
        else:
            format_tables.append(df)
    headshot = [1, 1, 0, 1, 0, 2, 0, 1]
    tableshot = list(zip(format_tables, headshot))
    beautiful_tables = []
    for df, y in tableshot:
        if y == 1:
            new_header = df.iloc[0]
            df = df[1:]
            df.columns = new_header
            beautiful_tables.append(df)
        elif y == 2:
            df.columns = ['info']
            beautiful_tables.append(df)
        else:
            beautiful_tables.append(df)
    unique_id = sc.snakecase(beautiful_tables[0]['Unique Id of VO/NGO'])
    sortframes = [0, 0, 1, 0, 2, 4, 3, 0]
    sortzip = list(zip(beautiful_tables, sortframes))
    # print(ngo_name)
    ngo_id = unique_id + "__" + (ngo_name)
    for df, y in sortzip:
        if y == 0:
            if ngo_id in main['ngo_id']:
                pass
            else:
                main['ngo_id'] = main['ngo_id'] + [ngo_id]
            for col in list(df.columns):
                main[col] = main[col] + [df[col][1]]
        elif y == 1:
            try:
                col_name_append(df, members, ngo_name)
            except (KeyError):
                for key in members.keys():
                    members['ngo'] += [ngo_name]
                    members[key] += [f'data is missing for {ngo_name}']
        elif y == 2:
            try:
                col_name_append(df, fcra, ngo_name)
            except (KeyError):
                for key in fcra.keys():
                    fcra['ngo'] += [ngo_name]
                    fcra[key] += [f'data is missing for {ngo_name}']
        elif y == 3:
            try:
                col_name_append(df, source_funds, ngo_name)
            except (KeyError):
                print(source_funds.keys())
        else:
            info = dict(df)
            main['info'] = main['info'] + [str(list(info.values())[0])]
    browser.find_element_by_xpath("//div[@class='modal-header']/button[@class='close']/span").click()
    time.sleep(2)
    stats = {'main': [len(main['ngo_id'])],
             'members': [len(members['ngo'])],
             'fcra': [len(fcra['ngo'])],
             'source_funds': [len(source_funds['ngo'])]}
    # print(stats)
    dictionaries = [main, members, fcra, source_funds]
    return dictionaries


def scrape_pages(all_pages, browser, start=0, stop=1):
    """ensemble command to open NGO profile popup box, gather data (if it works), close popup, and move to the next"""
    pops = get_page_popups(all_pages[0], browser)
    dict_list = initiate_ngo_data(pops, browser)
    counter = start
    bad_links = []
    bad_page = []
    for page in all_pages[start:stop]:
        print(f"getting popups from {counter} {page}")
        time.sleep(5)
        pops_full = get_page_popups(page, browser)
        for link in pops_full:
            try:
                dict_list = get_ngo_data(link, browser, dict_list)
            except:
                bad_links.append(page)
                bad_page.append(counter)
        counter += 1
    bad_links = list(set(bad_links))
    bad_pages = list(set(bad_page))
    missed = pd.DataFrame(zip(bad_links, bad_pages))
    dict_list.append(missed)
    full = dict_list
    print(f"{len(bad_links)} (pages {bad_pages}) missed")
    return full


def check_dataframes(full):
    "returns basic shape of four dataframes generated <--"
    for dct in full:
        df = pd.DataFrame(dct)
        print(df.shape)
        display(df.head())


def encode_to_csv(full_list, start, stop):
    """saves 4 dataframes to csv as well as list of pages that failed to load (to be retried later"""
    main_file_name = 'main'+str(start)+'_'+str(stop-1)+'.csv'
    members_file_name = 'members'+str(start)+'_'+str(stop-1)+'.csv'
    fcra_file_name = 'fcra'+str(start)+'_'+str(stop-1)+'.csv'
    source_funds_file_name = 'source_funds'+str(start)+'_'+str(stop-1)+'.csv'
    missing_file_name = 'missing'+str(start)+'_'+str(stop-1)+'.csv'
    pd.DataFrame(full_list[0]).to_csv(main_file_name)
    pd.DataFrame(full_list[1]).to_csv(members_file_name)
    pd.DataFrame(full_list[2]).to_csv(fcra_file_name)
    pd.DataFrame(full_list[3]).to_csv(source_funds_file_name)
    pd.DataFrame(full_list[4]).to_csv(missing_file_name)
    display(full_list[4])
    return "encoded"


def scrape_encode(all_pages, browser, start=0, stop=1):
    "runs through all commands save summary stats"
    full = scrape_pages(all_pages, browser, start, stop)
    for dct in full:
        df = pd.DataFrame(dct)
        print(df.shape)
    encode_to_csv(full, start, stop)
    return full


def start_scrape(all_pages, browser):
    """gathers popup links and opens them <--"""
    pops = get_page_popups(all_pages[0], browser)
    dict_list = initiate_ngo_data(pops, browser)
    return dict_list


def stepwise_scrape(all_pages, browser, dict_list, step=1):
    """calculates how many pages remain in full list and scrapes them <--"""
    done_pages = all_pages[0:step]
    for page in done_pages:
        print(f"getting popups from {page}")
        pops_full = get_page_popups(page, browser)
        for link in pops_full:
            dict_list = get_ngo_data(link, browser, dict_list)
    remaining_pages = all_pages - done_pages
    full = dict_list
    return remaining_pages, full


def mass_encode(url, step):
    """runs through all of the commands INCLUDING AUTOMATIC ENCODING (use with caution - see sample notebook) <--"""
    all_pages, browser = load_all_pages(url)
    dict_list = start_scrape(all_pages, browser)
    remaining_pages, full = stepwise_scrape(all_pages, browser, dict_list, step)
    encode_to_csv(full)
    return remaining_pages
