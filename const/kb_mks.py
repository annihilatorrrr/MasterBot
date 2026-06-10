from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class KeyboardMK:
    @staticmethod
    def refresh_stats() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Refresh", callback_data="refresh")]]
        )

    @staticmethod
    def get_logs_btn(alias: str, button_name: str = None) -> InlineKeyboardButton:
        return InlineKeyboardButton(f"{button_name or alias}", callback_data=f"logs_{alias}")

    @staticmethod
    def repo() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "See me in Action",
                        url = "https://t.me/ys0seri0us_bots/19"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🍴 Fork me",
                        url="https://github.com/GauthamramRavichandran/MasterBot/",
                    )
                ]
            ]
        )
