import asyncio

from tgbot.handlers.echo import router as echo_router
from tgbot.handlers.admin.main_block import router as admin_main_block
from tgbot.handlers.user.blocks.main_block import router as user_main_block
from tgbot.handlers.user.blocks.select_brochure_block import router as user_select_brochure_block
from tgbot.handlers.user.blocks.price_calculation_block import router as user_price_calculation_block
from tgbot.handlers.user.blocks.commercial_proposal_block import router as user_commercial_proposal_block

from create_bot import bot, dp, logger, register_global_middlewares, config


admin_router = [
    admin_main_block,
]


user_router = [
    user_main_block,
    user_select_brochure_block,
    user_price_calculation_block,
    user_commercial_proposal_block
]

# for router in user_router:
#     router.message.outer_middleware(NotInChannelMiddleware())
#     router.callback_query.outer_middleware(NotInChannelMiddleware())


async def main():
    logger.info("Starting bot")
    dp.include_routers(
        *admin_router,
        *user_router,
        echo_router
    )

    try:
        register_global_middlewares(dp, config)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
