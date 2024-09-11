import requests
import re
import warnings
import os
import shutil



warnings.filterwarnings("ignore")  # ignore SSL cert errors
MAIN_URL = "https://exampapers.must.ac.ke/"


def getLogger():
    import logging
    logger = logging.getLogger()
    handler2 = logging.StreamHandler()
    handler2.setLevel(logging.CRITICAL)
    FORMAT = logging.Formatter(style='{', fmt="{message}", )
    handler2.setFormatter(FORMAT)
    logger.addHandler(handler2)
    logger.critical('--START--\n2 many requests @ the same time may be perceived as ddos.')
    return logger


def get_all_urls():
    return requests.get(MAIN_URL, verify=False).text.split("et-top-navigation")[1].replace("\n", '')


def get_school():
    len_ = len(schs)
    [print(s, '.' * 3, id.upper(), sep='') for (s, id) in enumerate(schs)]
    schs_selected = []
    print("Select your  school(1 or more school can be selected,,,and should be SPACE  separated VALUES,,++++,,:")
  
    try:
        sch = input("school index: ").split(' ')
        # index_sch=sch.split(' ')
        index_int= [int(index) for index in sch]
        # print(f'{schs[index_int[0]]}  and {schs[index_int[1]]} selected')
    
        print(index_int)
        for sch_index in index_int:
            print(f'{schs[sch_index].upper()} selected')
                
            if sch in index_int:  
                break 

            try:
                school_idx = sch_index
                if 0 <= school_idx < len_:
                    schs_selected.append(schs[school_idx])                
            except ValueError:
                        print("OYAH OYAH,,,,,ERROR WRITING FILES")
    except ValueError:
            print("OYAH OYAH,,,,, an Invalid input. Please enter a valid school index. OR an Integer.")
    return schs_selected


def get_year_urls(sch: str):
    pattern = re.escape(f'<a href="#">{sch.upper()}</a>') + "(.+?)</ul>"
    if sch == schs[-1]:
        pattern = pattern.replace("\#", MAIN_URL + sch + "/")
    if sch == schs[6]:
        pattern = pattern.replace("SON", "SoN")
        pattern = pattern.replace("\#", MAIN_URL + sch + "/")
    content = get_all_urls()
    content = re.search(pattern, content).group(1)
    content = [d.split('">') for d in re.findall('(?:href="(.+?)</a>)', content)]
    return content


def make_dirs(sch, urls: list):
    exams = os.path.join(os.getcwd(), "exams")
    schd = os.path.join(exams, sch)
    for dir_ in (exams, schd):
        try:
            os.mkdir(dir_)
        except OSError:
            if input(f"path {dir_} exists. reuse it? ('y','n') ") == 'n':
                shutil.rmtree(dir_)
                os.mkdir(dir_)
                logger.critical(f"CLEARED {dir_}")
    for url in urls:
        url[1] = re.sub("\ ", "_", url[1])
        try:
            os.mkdir(os.path.join(schd, url[1]))
        except OSError:
            pass
    return schd

def keep_existing(fnames:list,path_:str)->None:
    names=os.listdir(path_)
    for x in range(len(fnames)-1,-1,-1):
        name=fnames[x]
        if name[1] in names: 
            fnames.remove(name)
            logger.critical(f"\tfile {name[1]} exists, not downloaded")  
            

def write_file(x):
    path_, url = x
    try:
        with open(os.path.join(path_, url[1]), "wb") as wrt:
            wrt.write(requests.get(url[0], verify=False).content)
            logger.critical(f"\twrote '{url[1]}'")
    except Exception as e:
        print("\n" * 10, "ERROR", e)


def get_file_names(url: str, target_patterns: list) -> list:
    if url := re.search(r'<div\ class="entry\-content">(.+?)</div', requests.get(url, verify=False).text.replace("\n", '')):        
            url = url.group(1)
            url = [[d, d.split('/')[-1].replace(" ", "_")] for d in re.findall(r'(?:<p><a\ href=")(.+?)(?:")', url)]
            filtered_urls = []
            for l in url:
                if any(pattern in l[0] for pattern in target_patterns):
                    filtered_urls.append(l)
            if not filtered_urls:
                filtered_urls = None       
    else:
        url = None
    return filtered_urls


def download(path_, urls,target_patterns, tpool):
    files = 0
    for url in urls:
        path = os.path.join(path_, url[1])
    
        todo = get_file_names(url[0],target_patterns)
        if todo:
                keep_existing(todo, path)
                logger.critical(f"downloading {url[0]}...")
                tpool.map(write_file, zip(itertools.cycle((path,)), todo))
                files += len(todo)
        else:
                logger.critical(f"No files on {url[0]}")
    return files


if __name__ == "__main__":
    import time,itertools
    from concurrent.futures import ThreadPoolExecutor
    THREAD_C = 32
    executor = ThreadPoolExecutor(max_workers=THREAD_C)
    schs = ['safs', 'sbe', 'sci', 'sea', 'sed', 'shs', 'son', 'spas', 'tvet']
    logger = getLogger()
    logger.critical(f"USING {THREAD_C} threads\n")

    selected_schools = get_school() 
    if selected_schools:   
        files_names=input("Enter the unit code(s) (e.g SMA-3300): ").split()
        target_patterns=[file.upper() for file in files_names]
        for file in target_patterns:
         print(f'{file} selected')         
        for school in selected_schools:
            timer = time.perf_counter()
            # target_patterns=['SMA-3300']
            # target_patterns = ['SMA-3355','CCS-3275','SMA-3303', 'SMA-3404', 'SMA-3300', 'SMA-3302', 'CIT-3229', 'SMA 3301','BFC-3125']  
            logger.critical(f"\nDownloading exams for {school.upper()} .......")
            urls = get_year_urls(school)
            pdir = make_dirs(school, urls)            
            files = download(pdir, urls, target_patterns, executor)        
        executor.shutdown(wait=True)
        logger.critical(f"\n{'+' * 3} DONE {'+' * 3} took: {(time.perf_counter() - timer):.2f}s wrote {files} files")

# CCA 3250
# CCA 3202
# CCA 3351
# SMA 3354
# SMA 3355
# SMS 3350
# SMA 3352