import subprocess
import time
import random

venv1_path = r'D:\work\project1\finditsite\venv1\Scripts\activate'
venv2_path = r'D:\work\project1\finditsite\venv2\Scripts\activate'


nginx_conf1 = r'D:\work\project1\finditsite\venv1\nginx-1.25.3\conf\nginx-venv1.conf'
nginx_conf2 = r'D:\work\project1\finditsite\venv2\nginx-1.25.3\conf\nginx-venv2.conf'


nginx_error_log_1 = r'D:\work\project1\finditsite\venv1\nginx-1.25.3\logs\error.log'
nginx_access_log_1 = r'D:\work\project1\finditsite\venv1\nginx-1.25.3\logs\access.log'

nginx_error_log_2 = r'D:\work\project1\finditsite\venv2\nginx-1.25.3\logs\error.log'
nginx_access_log_2 = r'D:\work\project1\finditsite\venv2\nginx-1.25.3\logs\access.log'


nginx_executable_path_1 = r'D:\work\project1\finditsite\venv1\nginx-1.25.3\nginx.exe'
nginx_executable_path_2 = r'D:\work\project1\finditsite\venv2\nginx-1.25.3\nginx.exe'

with open('ports.txt', 'r') as ports_file:
    ports = [int(port) for port in ports_file.readlines()]


selected_port = random.choice(ports)


subprocess.Popen(f'cmd /K {venv1_path}', shell=True)
print(f'Started the first virtual environment')


time.sleep(5)
subprocess.Popen(f'python manage.py runserver {selected_port}', shell=True)
print(f'Started Django server on port {selected_port}')


subprocess.Popen(f'{nginx_executable_path_1} -c {nginx_conf1}', shell=True)
print(f'Started Nginx for the first virtual environment')


subprocess.Popen(f'cmd /K {venv2_path}', shell=True)
print(f'Started the second virtual environment')


time.sleep(5)
other_port = [port for port in ports if port != selected_port][0]


subprocess.Popen(f'python manage.py runserver {other_port}', shell=True)
print(f'Started Django server on port {other_port}')


subprocess.Popen(f'{nginx_executable_path_2} -c {nginx_conf2}', shell=True)
print(f'Started Nginx for the second virtual environment')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    subprocess.run('taskkill /f /im python.exe', shell=True)
    subprocess.run('taskkill /f /im nginx.exe', shell=True)
    print('Stopped Django servers, Nginx, and virtual environments')
