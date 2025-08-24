import json
import discord
import requests
import asyncio
from discord.ext import commands

@nightyScript(
    name="nest.rip file upload v1.1",
    author="raager",
    description="Upload files and images to nest.rip file hosting service. Input api key where it says API KEY HERE within quotation marks on line 31.",
    usage="[p]nestupload <attachment_or_url> or reply to a message with [p]nestupload"
)
def nest_upload_script():
    def get_content_type(filename):
        ext = filename.lower().split('.')[-1]
        if ext in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', '3gp', 'ogv']:
            return f'video/{ext}'
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff']:
            return 'image/jpeg' if ext in ['jpg', 'jpeg'] else f'image/{ext}'
        elif ext in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a', 'opus']:
            return 'audio/mpeg' if ext == 'mp3' else f'audio/{ext}'
        elif ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'zip', 'rar', '7z', 'tar', 'gz', 'json', 'xml', 'csv']:
            return 'application/octet-stream'
        else:
            return 'application/octet-stream'

    @bot.command(name="nestupload", description="Upload files to nest.rip hosting service")
    async def upload_handler(ctx, url: str = None):
        await ctx.message.delete()
        try:
            API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key Account settings -> Security -> API Key 

            file_data = None
            filename = None

            # Handle direct attachment
            if ctx.message.attachments:
                attachment = ctx.message.attachments[0]
                if attachment.size > 100 * 1024 * 1024:
                    msg = await ctx.send("❌ File too large! Max size is 100MB.")
                    await asyncio.sleep(5)
                    await msg.delete()
                    return
                file_data = await attachment.read()
                filename = attachment.filename

            # Handle reply-to-message attachment
            elif ctx.message.reference and ctx.message.reference.resolved:
                replied_message = ctx.message.reference.resolved
                if isinstance(replied_message, discord.Message) and replied_message.attachments:
                    attachment = replied_message.attachments[0]
                    if attachment.size > 100 * 1024 * 1024:
                        msg = await ctx.send("❌ File too large! Max size is 100MB.")
                        await asyncio.sleep(5)
                        await msg.delete()
                        return
                    file_data = await attachment.read()
                    filename = attachment.filename
                else:
                    # If replied message has no attachments, fall back to URL
                    if url:
                        response = requests.get(url)
                        if response.status_code != 200:
                            msg = await ctx.send("❌ Could not download file from URL.")
                            await asyncio.sleep(5)
                            await msg.delete()
                            return
                        content_length = response.headers.get("Content-Length")
                        if content_length and int(content_length) > 100 * 1024 * 1024:
                            msg = await ctx.send("❌ File too large! Max size is 100MB.")
                            await asyncio.sleep(5)
                            await msg.delete()
                            return
                        file_data = response.content
                        filename = url.split("/")[-1] or "uploaded_file"
                    else:
                        msg = await ctx.send("❌ Please attach a file, reply to a message with a file, or provide a URL.")
                        await asyncio.sleep(5)
                        await msg.delete()
                        return

            # Handle URL
            elif url:
                response = requests.get(url)
                if response.status_code != 200:
                    msg = await ctx.send("❌ Could not download file from URL.")
                    await asyncio.sleep(5)
                    await msg.delete()
                    return
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > 100 * 1024 * 1024:
                    msg = await ctx.send("❌ File too large! Max size is 100MB.")
                    await asyncio.sleep(5)
                    await msg.delete()
                    return
                file_data = response.content
                filename = url.split("/")[-1] or "uploaded_file"

            else:
                msg = await ctx.send("❌ Please attach a file, reply to a message with a file, or provide a URL.")
                await asyncio.sleep(5)
                await msg.delete()
                return

            # Get file type
            content_type = get_content_type(filename)

            # Upload using requests with proper multipart formatting
            files = {
                'files': (filename, file_data, content_type)
            }
            headers = {
                'Authorization': API_KEY
            }
            response = requests.post("https://nest.rip/api/files/upload", files=files, headers=headers)

            if response.status_code == 200:
                result = response.json()
                if "fileURL" in result:
                    file_type = content_type.split('/')[0]
                    emoji = {
                        "image": "🖼️",
                        "video": "🎥",
                        "audio": "🎵",
                        "application": "📄",
                    }.get(file_type, "📁")

                    # Fixed: Using proper message formatting instead of embed
                    message_content = (
                        f"**{emoji} Uploaded Successfully to nest.rip!**\n\n"
                        f"**Filename:** `{filename}`\n"
                        f"**Type:** `{content_type}`"
                    )
                    msg = await ctx.send(
                        message_content,
                        allowed_mentions=discord.AllowedMentions.none(),
                        suppress_embeds=True
                    )
                    await asyncio.sleep(5)
                    await msg.delete()

                else:
                    msg = await ctx.send(f"❌ Upload failed: {result.get('message', 'Unknown error')}")
                    await asyncio.sleep(5)
                    await msg.delete()
            else:
                msg = await ctx.send(f"❌ Upload failed. Server returned: {response.status_code}")
                await asyncio.sleep(5)
                await msg.delete()

        except Exception as e:
            msg = await ctx.send(f"❌ Unexpected error:\n`{str(e)}`")
            await asyncio.sleep(5)
            await msg.delete()

nest_upload_script()