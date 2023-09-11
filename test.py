kb_dict = dict(
            suscribe_channel="Подпишитесь на канал",
            greeting="Приветствие",
            nothing_found="Ничего не найдено",
            found_materials="Найдены брошюры",
            write_request="Напишите свой вопрос",
            message_sent="Сообщение отправлено",
            message_from_support="Сообщение от поддержки",
        )

for button in kb_dict:
    print(button, kb_dict[button])