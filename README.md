# Telegram Bot

This is a Telegram bot that can provide information about phone numbers and vehicles.

## Deployment on Render

1.  Create a new "Web Service" on Render.
2.  Connect your Git repository.
3.  Render will automatically detect the `render.yaml` file and configure the build and start commands.
4.  Go to the "Environment" tab for your service on Render and add a new environment variable:
    -   **Key**: `BOT_TOKEN`
    -   **Value**: Your actual Telegram bot token.

## Usage

-   Start a chat with the bot on Telegram.
-   Use the `/start` command to see the main menu.
-   You can get information about phone numbers and vehicles, redeem codes, check your balance, and refer friends.