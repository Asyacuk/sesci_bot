import os
import random
import telebot
import whisper
import time

TOKEN = "5691595236:AAEGx_WkQJmA8kKjz4fnypqn-kZMZximHQ0"  # Telegram bot tokeninizi buraya girin
DOWNLOAD_PATH = "voice/"  # Ses dosyalarının indirileceği klasör yolunu buraya girin

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(chat_id=message.chat.id, text="Merhaba! Ben ses dosyalarını transkript edebilen bir botum. Bana bir ses dosyası veya şarkı gönderin, transkriptini size göndereyim! /info yazarak daha fazla bilgi edinebilirsiniz.\n\n Sürüm: Beta (testleri yapılıyor) --- Sahip: @Asyacuk --- Kanal: @Asyacukproject")

@bot.message_handler(commands=['info'])
def handle_info(message):
    bot.send_message(chat_id=message.chat.id, text="Botunuzu kullanmak için aşağıdaki komutları kullanabilirsiniz:\n\n"
                                                  "/start - Botu başlatır ve hoşgeldin mesajını görüntüler.\n"
                                                  "/info - Bot hakkında bilgi verir.\n"
                                                  "/transcribe - Ses dosyasını transkript eder.\n"
                                                  "/cancel - Aktif işlemi iptal eder.\n")

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    try:
        if message.voice:
            file = message.voice
        elif message.audio:
            file = message.audio
        else:
            bot.send_message(chat_id=message.chat.id, text="Sadece ses dosyaları ve şarkılar desteklenmektedir.")
            return

        file_id = file.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # Ses dosyasını indir
        downloaded_file = bot.download_file(file_path)
        random_number = random.randint(1, 10000)
        file_extension = file_path.split('.')[-1]
        file_name = f"{random_number}_{file_id}.{file_extension}"  # Rastgele sayı ile ses dosyasının adını oluştur
        # Transkripti kullanıcıya gönder ve tamamlanan yüzdeyi güncelle
        sent_message = bot.send_message(chat_id=message.chat.id, text=f"İndirme işlemi %{0} tamamlandı.")
        for i in range(1, 101):
            bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=f"İndirme işlemi %{i} tamamlandı.")



        # Ses dosyasını diske kaydet
        with open(os.path.join(DOWNLOAD_PATH, file_name), 'wb') as f:
            f.write(downloaded_file)

        # Ses dosyasını transkript et
        model = whisper.load_model("small")
        result = model.transcribe(os.path.join(DOWNLOAD_PATH, file_name))
        text = result["text"]

#https://github.com/openai/whisper Parametersss

#Size	Parameters	English-only model	   Multilingual model	Required VRAM	Relative speed
#tiny	39 M	     tiny.en	               tiny               ~1 GB	            ~32x
#base	74 M	     base.en	               base	              ~1 GB	            ~16x
#small	244 M	     small.en	               small	          ~2 GB	            ~6x
#medium	769 M	     medium.en                 medium	          ~5 GB	            ~2x
#large	1550 M	     N/A	                   large	          ~10 GB	        ~1x


        # Transkripti kullanıcıya gönder ve tamamlanan yüzdeyi güncelle
        sent_message = bot.send_message(chat_id=message.chat.id, text=f"Transkript işlemi %{0} tamamlandı.")
        for i in range(1, 101):
            bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=f"Transkript işlemi %{i} tamamlandı.")
            time.sleep(1)  # Her bir istek arasına 0 saniye bekleme süresi ekleyin

        # Sonuçları kullanıcıya gönder
        bot.send_message(chat_id=message.chat.id, text=f"Transkript: {text}")

    except Exception as e:
        bot.send_message(chat_id=message.chat.id, text=f"Bir hata oluştu: {e}")

if __name__ == '__main__':
    bot.polling()