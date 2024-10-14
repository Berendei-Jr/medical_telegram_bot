SUBSCRIPTION_COMMAND = 'подписка'
PRICES_COMMAND = 'цены'

PERIODS = {1: ['1 месяц', 4000], 2: ['2 месяца', 7000], 3: ['3 месяца', 11000]}

GREETING_MESSAGE = f'Здравствуйте! \U0001F609\n\
Это бот *Карединой Екатерины Федоровны* \U0001F48A\n\
Если Вы хотите попасть в мой закрытый канал, напишите "*{SUBSCRIPTION_COMMAND}*".\n\
Чтобы узнать цены, напишите "*{PRICES_COMMAND}*".\n\
После подтверждения оплаты я вышлю Вам _ссылку_ на добавление в канал.'

HELP_MESSAGE = f'Чтобы узнать цены на подписку - напишите "{PRICES_COMMAND}", что купить подписку - напишите "{SUBSCRIPTION_COMMAND}"'
PAYMENT_CONFIRMATION_REQUEST = 'Спасибо! Оплата отправлена на подтверждение.'
PAYMENT_CONFIRMATION = 'Оплата подтверждена. Ваша ссылка для добавления в канал: '
RULES = 'Какие правила:\n\
➡Уважение, терпение, поддержка\n\
➡Нет неудобных вопросов, лучше спросить, чем не спросить и сделать неправильно\n\
➡Захожу минимум 2 раза в день, это значит, что на вопрос можно получить ответ в течение 12 часов. Не всегда СИЮМИНУТНО\n\
➡Нет грубости\n\
➡Всё, что в чате, остаётся в чате\n\
➡Если вопрос нуждается в консультации и очном осмотре- НЕТ ПРЕТЕНЗИЙ\n\
➡НЕ ЗАМЕНЯЕТ ОСМОТР\n\
➡Второе мнение, обсуждение вопроса\n\
➡Тот, кто в чате, может высказаться и ответить тоже.'
PAYMENT_REJECT = 'Оплата не была подтверждена. Свяжитесь с Екатериной Федоровной для получения дополнительной информации'
REMOVAL_MESSAGE = f'Ваша подписка истекла. Если Вы хотите подписаться еще раз, напишите "{SUBSCRIPTION_COMMAND}"'

#ADMIN_ID = 999166963
ADMIN_ID = 476882341
CLEANER_INTERVAL_S = 3600
