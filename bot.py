import aiogram
import main
import threading
import asyncio


app = main.Build_app()
bot = aiogram.Bot('Your API TOKEN Here')
dispatcher = aiogram.Dispatcher(bot)
UsersID = ["Your id", "Your friend's id"]


@dispatcher.message_handler(commands=['start'])
async def StartCommand(Message: aiogram.types.Message):
    await bot.delete_message(Message.chat.id, Message.message_id)
    await bot.send_message(Message.chat.id, "It's time to start!")
    print(f'Message: {Message}')


async def SendMessageToUsers():
    while True:
        try:
            if not app.final_message.empty():
                for IDStr in UsersID:
                    try:
                        await bot.send_message(IDStr, app.final_message.get())
                    except aiogram.utils.exceptions.BotBlocked:
                        pass
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(15)


async def OnStartUp(x):
    await asyncio.create_task(SendMessageToUsers())


if __name__ == '__main__':
    threading.Thread(target=app.main).start()
    aiogram.executor.start_polling(dispatcher, on_startup=OnStartUp)
