import os
import asyncio
import logging
from github import Github
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURACIÓN (Se cargará desde variables de entorno en Render) ---
TELEGRAM_BOT_TOKEN = os.environ.get('8534765454:AAFjZZbb35rjS594M2kF0NdFQpR5PbQX8qI')
GITHUB_ACCESS_TOKEN = os.environ.get('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')

# Configurar logging para ver errores
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializar cliente de GitHub
if GITHUB_ACCESS_TOKEN:
    github_client = Github(GITHUB_ACCESS_TOKEN)
else:
    github_client = None
    logger.error("❌ GITHUB_ACCESS_TOKEN no configurado")

# ----- MANEJADORES DE COMANDOS (ASÍNCRONOS) -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Hola! Soy tu gestor de repositorios de GitHub. Usa /list para ver tus repos.'
    )

async def list_repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not github_client:
        await update.message.reply_text("Error: Configuración de GitHub incompleta.")
        return

    try:
        user = github_client.get_user()
        repos = user.get_repos()

        keyboard = []
        # Mostrar solo los primeros 30 repos para no saturar
        for repo in list(repos)[:30]:
            keyboard.append([InlineKeyboardButton(repo.name, callback_data=f"repo_{repo.name}")])

        if not keyboard:
            await update.message.reply_text("No tienes repositorios.")
            return

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Selecciona un repositorio:', reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error al listar repos: {e}")
        await update.message.reply_text(f"Error al conectar con GitHub: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("repo_"):
        repo_name = data.split("_", 1)[1]
        keyboard = [
            [InlineKeyboardButton("⬇️ Descargar ZIP", callback_data=f"dl_{repo_name}")],
            [InlineKeyboardButton("🗑️ Eliminar", callback_data=f"del_ask_{repo_name}")],
            [InlineKeyboardButton("↩️ Volver", callback_data="back_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"Repositorio: `{repo_name}`\nElige:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif data == "back_list":
        # Reenviar al usuario al comando /list
        await list_repos(update, context)
    elif data.startswith("dl_"):
        repo_name = data.split("_", 1)[1]
        await query.edit_message_text(f"⏳ Preparando descarga de `{repo_name}`... (Función en desarrollo)")
        # Aquí iría el código para descargar y enviar el ZIP
    elif data.startswith("del_ask_"):
        repo_name = data.split("_", 2)[2]
        keyboard = [
            [InlineKeyboardButton("✅ Sí, eliminar", callback_data=f"del_confirm_{repo_name}")],
            [InlineKeyboardButton("❌ Cancelar", callback_data=f"repo_{repo_name}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"⚠️ ¿Eliminar `{repo_name}`? *IRREVERSIBLE*.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif data.startswith("del_confirm_"):
        repo_name = data.split("_", 2)[2]
        try:
            user = github_client.get_user()
            repo = user.get_repo(repo_name)
            repo.delete()
            await query.edit_message_text(f"✅ Repositorio `{repo_name}` eliminado.")
        except Exception as e:
            logger.error(f"Error al eliminar: {e}")
            await query.edit_message_text(f"❌ Error al eliminar: {e}")

# ----- FUNCIÓN PRINCIPAL -----
def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
        return

    # 1. Crear la Application (CORRECTO para v20)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # 2. Registrar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_repos))
    application.add_handler(CallbackQueryHandler(button_callback))

    # 3. Iniciar el bot en modo polling
    logger.info("🤖 Bot iniciando...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()    await query.answer()  # Responde a la callback para quitar el "reloj de carga"

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
