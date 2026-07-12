import flet as ft
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- GOOGLE SHEETS BAĞLANTISI ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gizli_anahtar.json", scope)
client = gspread.authorize(creds)

# İki ayrı sayfayı da tanımlıyoruz
db_sheet = client.open("depo_takip")
data_sheet = db_sheet.sheet1                  # Verilerin kaydedileceği yer (1. Sekme)
user_sheet = db_sheet.worksheet("Kullanıcılar") # Şifrelerin okunacağı yer (2. Sekme)

def main(page: ft.Page):
    page.title = "Depo Takip Otomasyonu"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    username_input = ft.TextField(label="Kullanıcı Adı", width=280)
    password_input = ft.TextField(label="Şifre", password=True, can_reveal_password=True, width=280)
    info_text = ft.Text(value="", color=ft.Colors.RED)
    barcode_result = ft.TextField(label="Barkod Kodu", width=280)
    
    # Giriş yapan kullanıcının adını tutmak için
    current_user = ft.Ref[str]()

    def save_to_sheets(e):
        if not barcode_result.value:
            info_text.value = "Lütfen bir barkod girin!"
            info_text.color = ft.Colors.RED
            page.update()
            return
        
        try:
            # Hangi kullanıcının tarama yaptığını da Sheets'e yazıyoruz
            data_sheet.append_row([barcode_result.value, username_input.value, "Giriş Yapıldı"])
            info_text.value = f"Barkod ({barcode_result.value}) başarıyla kaydedildi! ✅"
            info_text.color = ft.Colors.GREEN
            barcode_result.value = ""
        except Exception as err:
            info_text.value = f"Sheets Hatası: {str(err)}"
            info_text.color = ft.Colors.RED
        page.update()

    def login_click(e):
        info_text.value = "Kontrol ediliyor..."
        info_text.color = ft.Colors.BLUE
        page.update()
        
        try:
            # Google Sheets'teki tüm kullanıcı listesini çeker
            all_users = user_sheet.get_all_records()
            
            # Girilen bilgiler listede var mı kontrol et
            authenticated = False
            for user in all_users:
                if str(user['Kullanıcı Adı']) == username_input.value and str(user['Şifre']) == password_input.value:
                    authenticated = True
                    break
            
            if authenticated:
                login_box.visible = False
                app_box.visible = True
                info_text.value = f"Hoş geldiniz, {username_input.value}! 👋"
                info_text.color = ft.Colors.GREEN
            else:
                info_text.value = "Hatalı kullanıcı adı veya şifre!"
                info_text.color = ft.Colors.RED
        except Exception as err:
            info_text.value = f"Bağlantı Hatası: {str(err)}"
            info_text.color = ft.Colors.RED
        page.update()

    login_box = ft.Column(
        controls=[
            ft.Text("Depo Girişi", size=24, weight=ft.FontWeight.BOLD),
            username_input,
            password_input,
            ft.ElevatedButton("Giriş Yap", on_click=login_click, width=280)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    app_box = ft.Column(
        controls=[
            ft.Text("📦 Ürün Tarama Sistemi", size=22, weight=ft.FontWeight.BOLD),
            barcode_result,
            ft.ElevatedButton("Kaydet / Gönder", on_click=save_to_sheets, width=280, icon=ft.Icons.SAVE),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False
    )

    page.add(login_box, app_box, info_text)

ft.app(target=main)