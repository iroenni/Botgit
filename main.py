import asyncio
import os
from github import Github  # PyGithub library
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Configuración (¡Mueve esto a variables de entorno en producción!) ---
TELEGRAM_BOT_TOKEN = "8534765454:AAFjZZbb35rjS594M2kF0NdFQpR5PbQX8qI"
GITHUB_ACCESS_TOKEN = "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"
# ----------------------------------------------------------------

# Inicializar cliente de GitHub
github_client = Github(GITHUB_ACCESS_TOKEN)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Hola! Soy tu gestor de repositorios de GitHub. Usa /list para ver tus repos.'
    )

# Comando /list - Lista repositorios con botones
async def list_repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = github_client.get_user()
    repos = user.get_repos()

    keyboard = []
    for repo in repos:  # Solo iteramos sobre los primeros X repos para no saturar
        # Cada repo tiene un botón que al pulsarlo envía un callback con su nombre
        keyboard.append([InlineKeyboardButton(repo.name, callback_data=f"repo_{repo.name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Tus repositorios:', reply_markup=reply_markup)

# Manejar la pulsación de botones (CallbackQueries)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Responde a la callback para quitar el "reloj de carga"

    data = query.data

    if data.startswith("repo_"):
        repo_name = data.split("_", 1)[1]
        # Mostrar un nuevo menú con acciones para este repo
        keyboard = [
            [InlineKeyboardButton("⬇️ Descargar ZIP", callback_data=f"dl_{repo_name}")],
            [InlineKeyboardButton("🗑️ Eliminar Repositorio", callback_data=f"del_ask_{repo_name}")],
            [InlineKeyboardButton("↩️ Volver a la lista", callback_data="back_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Repositorio seleccionado: `{repo_name}`\nElige una acción:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    elif data.startswith("dl_"):
        repo_name = data.split("_", 1)[1]
        # Lógica para descargar (similar a GitGat [citation:5] o usando la API de GitHub)
        await query.edit_message_text(text=f"⏳ Preparando descarga de `{repo_name}`...")
        # ... (código para descargar y enviar el archivo)
        # await context.bot.send_document(chat_id=query.message.chat_id, document=open('repo.zip', 'rb'))

    elif data.startswith("del_ask_"):
        repo_name = data.split("_", 2)[2]
        # Pide confirmación antes de eliminar
        keyboard = [
            [InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"del_confirm_{repo_name}")],
            [InlineKeyboardButton("❌ Cancelar", callback_data=f"repo_{repo_name}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"⚠️ ¿Estás **SEGURO** de que quieres eliminar `{repo_name}`? Esta acción es irreversible.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    elif data.startswith("del_confirm_"):
        repo_name = data.split("_", 2)[2]
        user = github_client.get_user()
        repo = user.get_repo(repo_name)
        repo.delete()
        await query.edit_message_text(text=f"✅ Repositorio `{repo_name}` eliminado correctamente de GitHub.")

    elif data == "back_list":
        # Volver a listar repositorios (podría requerir recargar la lista)
        await list_repos(update, context)

# Función principal
def main():
    # Crear la aplicación y pasar el token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_repos))

    # Manejador de pulsaciones de botones en el chat
    application.add_handler(CallbackQueryHandler(button_callback))

    # Iniciar el bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
