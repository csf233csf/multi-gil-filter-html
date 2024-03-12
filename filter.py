from bs4 import BeautifulSoup
import os
from multiprocessing import Pool, Manager

# 这边是过滤函数
def filter_html(html_file_path):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_data = file.read()
        soup = BeautifulSoup(html_data, 'lxml')

        for table in soup.find_all('table'):
            if len(table.get_text(strip=True)) <= 500:
                table.decompose()

        if len(soup.get_text(separator='',strip=True)) <= 30:
            return True

        list_img = []
        for img in soup.find_all('img'):
            if 'height' in img.attrs and int(img.attrs['height']) >= 600:
                list_img.append(1)

        if len(list_img) >= 7:
            return True
        
    except Exception as e:
        print(f"Error processing file {html_file_path}: {e}") # 进程报错
    return False

def process_html_file(args):
    html_file_path, results = args
    if filter_html(html_file_path):
        results.append(html_file_path)

def prepare_file_paths(folder_path):
    pool_args = []
    file_names = []
    for root, _unused_, files in os.walk(folder_path):
        for file_name in files:
            file_names.append(file_name)
            if file_name.endswith('.html'):
                html_file_path = os.path.join(root, file_name)
                pool_args.append(html_file_path)
    with open('file.txt', 'w', encoding='utf-8') as file:
        for item in file_names:
            file.write(item + '\n')
    print(f'处理文件：{len(file_names)}')
    return pool_args

def main(folder_path, output_html_path):
    manager = Manager()
    results = manager.list() # 共享的进程列表

    pool_args = [(path, results) for path in prepare_file_paths(folder_path)] 

    with Pool() as pool:
        pool.map(process_html_file, pool_args)

    with open(output_html_path, 'w', encoding='utf-8') as file:
        file.write('<html><body>\n')
        file.write(f'<p>{' '*50}过滤出的html<p>\n')
        file.write('<ul>\n')
        for html_path in results:
            file.write(f'<li><a href="{html_path}">{os.path.basename(html_path)}</a></li>\n')
        file.write('</ul>\n')
        file.write('</body></html>')

if __name__ == "__main__":

    folder_path = r'D:\Work Files\headersclass\html2'
    output_html_path = 'filtered_html.html'
    main(folder_path, output_html_path)
    print('处理完成')
