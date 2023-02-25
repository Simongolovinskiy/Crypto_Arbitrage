import aiogram
import main
import threading
import asyncio

crypt = main.Socket()
bot = aiogram.Bot('6002043488:AAEPXzY7pgxT1TLVvR_uLrOsA1wgHwuLXI4')
dispatcher = aiogram.Dispatcher(bot)

@dispatcher.message_handler(commands = ['start'])
async def StartCommand(Message: aiogram.types.Message):
    await bot.delete_message(Message.chat.id, Message.message_id)
    await bot.send_message(Message.chat.id, 'Все заебись')
    print(f'Message: {Message}')


async def SendMessageToUsers():
    while True:
        try:
            while not crypt.final_message.empty():
                TGMessage = crypt.final_message.get()

                for IDStr in UsersID:
                    try:
                        await bot.send_message(IDStr, TGMessage)
                    except aiogram.utils.exceptions.BotBlocked:
                        pass
                print(f'Сигнал отправлен для {UsersID}\nСигнал: {TGMessage}')
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(15)


async def OnStartUp(x):
    asyncio.create_task(SendMessageToUsers())


if __name__ == '__main__':
    UsersID = [543547281, 944598197]
    threading.Thread(target=crypt.main).start()
    aiogram.executor.start_polling(dispatcher, on_startup=OnStartUp)
