import os
import shutil
import re
from html.parser import HTMLParser

# 創建名為 Cloud_report 的資料夾
new_folder_path = 'Cloud_report'
os.makedirs(new_folder_path, exist_ok=True)

# 源資料夾路徑
source_folder_path = '/usr/local/bin/WFA-QuickTrack-Tool/Cloud-Reports'

# 獲取源資料夾下所有資料夾的列表
subfolders = [f.path for f in os.scandir(source_folder_path) if f.is_dir()]

# 找到最新的資料夾
latest_folder = max(subfolders, key=os.path.getmtime)

# 自訂複製函數來保留文件權限
def copy_with_permissions(src, dst):
    shutil.copy2(src, dst)

# 將最新資料夾複製到 Cloud_report 資料夾下並保留文件權限
shutil.copytree(latest_folder, os.path.join(new_folder_path, os.path.basename(latest_folder)), copy_function=copy_with_permissions)

# 創建 pass、fail、not_run 資料夾
for folder_name in ['pass', 'fail', 'not_run']:
    folder_path = os.path.join(new_folder_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

print("資料夾複製完成，並創建 pass、fail、not_run 資料夾")

# 定義匹配 TestResult:PASS 的正則表達式
pass_pattern = re.compile(r'TestResult:PASS')

# 定義匹配 TestResult:FAIL 的正則表達式
fail_pattern = re.compile(r'TestResult:FAIL')

# 定義匹配 TestResult:NOT_TESTED 的正則表達式
not_tested_pattern = re.compile(r'TestResult:NOT_TESTED')

# 解析 HTML 文件並查找 TestResult:PASS、TestResult:FAIL 和 TestResult:NOT_TESTED 的數量
class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pass_count = 0
        self.fail_count = 0
        self.not_tested_count = 0

    def handle_data(self, data):
        if "TestResult:PASS" in data:
            self.pass_count += 1
        elif "TestResult:FAIL" in data:
            self.fail_count += 1
        elif "TestResult:NOT_TESTED" in data:
            self.not_tested_count += 1

# 從2.開頭的文件夾中查找 HTML 文件並解析
html_files = []
for folder in os.listdir(new_folder_path):
    if folder.startswith('2.') and os.path.isdir(os.path.join(new_folder_path, folder)):
        folder_path = os.path.join(new_folder_path, folder)
        for file in os.listdir(folder_path):
            if file.startswith('Tool-report') and file.endswith('.html'):
                html_files.append(os.path.join(folder_path, file))

if html_files:
    parser = MyHTMLParser()
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            parser.feed(f.read())

    pass_count = parser.pass_count
    fail_count = parser.fail_count
    not_tested_count = parser.not_tested_count

    # 根據 PASS 的數量複製相應數量的最新文件夾到 pass 目錄中
    pass_folder_path = os.path.join(new_folder_path, 'pass')
    pass_source_folder_path = '/usr/local/bin/WFA-QuickTrack-Tool/Test-Logs/PASS'
    pass_subfolders = sorted([f.path for f in os.scandir(pass_source_folder_path) if f.is_dir()], key=os.path.getmtime, reverse=True)
    for i in range(pass_count):
        if i < len(pass_subfolders):
            shutil.copytree(pass_subfolders[i], os.path.join(pass_folder_path, os.path.basename(pass_subfolders[i])))

    # 根據 FAIL 的數量複製相應數量的最新文件夾到 fail 目錄中
    fail_folder_path = os.path.join(new_folder_path, 'fail')
    fail_source_folder_path = '/usr/local/bin/WFA-QuickTrack-Tool/Test-Logs/FAIL'
    fail_subfolders = sorted([f.path for f in os.scandir(fail_source_folder_path) if f.is_dir()], key=os.path.getmtime, reverse=True)
    for i in range(fail_count):
        if i < len(fail_subfolders):
            shutil.copytree(fail_subfolders[i], os.path.join(fail_folder_path, os.path.basename(fail_subfolders[i])))

    # 根據 NOT_TESTED 的數量複製相應數量的最新文件夾到 not_run 目錄中
    not_run_folder_path = os.path.join(new_folder_path, 'not_run')
    not_run_source_folder_path = '/usr/local/bin/WFA-QuickTrack-Tool/Test-Logs/NOT_TESTED'
    not_run_subfolders = sorted([f.path for f in os.scandir(not_run_source_folder_path) if f.is_dir()], key=os.path.getmtime, reverse=True)
    for i in range(not_tested_count):
        if i < len(not_run_subfolders):
            shutil.copytree(not_run_subfolders[i], os.path.join(not_run_folder_path, os.path.basename(not_run_subfolders[i])))

else:
    print("找不到 Tool-report 開頭的 HTML 文件")

print("PASS、FAIL 和 NOT_TESTED 目錄複製完成")