import requests,time
import re,random,string
class tempmail:
    def extract_code(self,data):
        try:
            subject = data['mail_list'][0]['subject']
            return re.search(r'\b\d{4,8}\b', subject).group(0)
        except:
            return None
    def extract_code1(self,data,email):
        try:
            mail_id = data['mail_list'][0]['mail_id']
            print(mail_id)
            cc = requests.get(f'https://tempmail.plus/api/mails/{mail_id}?email={email}&epin=').json()

            subject = cc['text']

            # return re.search(r'\b\d{4,6}\b', subject).group(0)
            match = re.search(r'\*(\d+)\*', subject)
            if match:
                # Return the captured group, which is the number
                return match.group(1)
        except:
            return None
    
        
    def get_code(self,email):
        for i in range(20):
            time.sleep(2)
            print(email)
            cookies = {
                'email': email,
            }

            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=1, i',
                'referer': 'https://tempmail.plus/en/',
                'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                # 'cookie': 'email=hccem%40fexpost.com',
            }

            params = {
                'email': email,
                'limit': '20',
                'epin': '',
            }

            response = requests.get('https://tempmail.plus/api/mails', params=params, cookies=cookies, headers=headers).json()
            # print(response)
            if response['count'] == 1:
                # print(self.extract_code1(response))
                return self.extract_code1(response,email)
            else:
                continue
    def random_email(self,length=10):
        # Tạo phần đầu email: bao gồm chữ cái và số, không ký tự đặc biệt
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return f"{prefix}@fextemp.com"