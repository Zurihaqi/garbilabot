import discord
from utils.game_logic import GameLogic
import io
from PIL import Image, ImageDraw, ImageFont
import aiohttp
from pilmoji import Pilmoji

class ProfileCardGenerator:
    """Generate custom profile cards with backgrounds and stats"""
    
    # Class/Rank colors
    CLASS_COLORS = {
        'Novice': (139, 69, 19),
        'Adventurer': (34, 139, 34),
        'Warrior': (65, 105, 225),
        'Knight': (138, 43, 226),
        'Champion': (255, 215, 0),
        'Master': (255, 140, 0),
        'Dragon Slayer': (220, 20, 60),
        'Legendary Hero': (255, 0, 255)
    }
    
    # Rank backgrounds
    RANK_BACKGROUNDS = {
        'Novice': 'https://i.imgur.com/8rKBMN2.png',
        'Adventurer': 'https://i.imgur.com/8rKBMN2.png',
        'Warrior': 'https://i.imgur.com/8rKBMN2.png',
        'Knight': 'https://i.imgur.com/8rKBMN2.png',
        'Champion': 'https://i.imgur.com/8rKBMN2.png',
        'Master': 'https://i.imgur.com/8rKBMN2.png',
        'Dragon Slayer': 'https://i.imgur.com/8rKBMN2.png',
        'Legendary Hero': 'https://i.imgur.com/8rKBMN2.png'
    }
    
    @staticmethod
    async def create_profile_card(user_data, discord_user: discord.User) -> discord.File:
        """Create a custom profile card image"""
        try:
            # Create base image
            width, height = 800, 400
            img = Image.new('RGBA', (width, height), color=(30, 30, 40)) # Changed to RGBA for better handling
            
            bg_url = ProfileCardGenerator.RANK_BACKGROUNDS.get(user_data.cls)
            bg_loaded = False
            
            if bg_url:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(bg_url) as resp:
                            if resp.status == 200:
                                bg_data = await resp.read()
                                bg_img = Image.open(io.BytesIO(bg_data)).convert('RGBA')
                                # Resize background to fit card exactly
                                bg_img = bg_img.resize((width, height))
                                # Paste background
                                img.paste(bg_img, (0, 0))
                                
                                # Add a dark overlay so text remains readable on top of images
                                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100)) # 100 = opacity
                                img = Image.alpha_composite(img, overlay)
                                bg_loaded = True
                except Exception as e:
                    print(f"Failed to load background: {e}")

            # Fallback: If no BG loaded, draw the gradient
            if not bg_loaded:
                draw = ImageDraw.Draw(img)
                for i in range(height):
                    alpha = i / height
                    color = tuple(int(30 + (50 - 30) * alpha) for _ in range(3))
                    draw.rectangle([(0, i), (width, i+1)], fill=color)

            # Re-initialize draw object for shapes (Pilmoji handles text separately)
            draw = ImageDraw.Draw(img)
            
            # Get class color
            class_color = ProfileCardGenerator.CLASS_COLORS.get(user_data.cls, (255, 255, 255))
            
            # Draw accent lines
            draw.rectangle([(0, 0), (width, 5)], fill=class_color)
            draw.rectangle([(0, height-5), (width, height)], fill=class_color)
            
            try:
                avatar_url = discord_user.display_avatar.url
                async with aiohttp.ClientSession() as session:
                    async with session.get(str(avatar_url)) as resp:
                        if resp.status == 200:
                            avatar_data = await resp.read()
                            avatar = Image.open(io.BytesIO(avatar_data)).convert('RGBA') # Convert to RGBA
                            avatar = avatar.resize((120, 120))
                            
                            # Create circular mask
                            mask = Image.new('L', (120, 120), 0)
                            mask_draw = ImageDraw.Draw(mask)
                            mask_draw.ellipse((0, 0, 120, 120), fill=255)
                            
                            # Create border
                            border_size = 130
                            border = Image.new('RGBA', (border_size, border_size), class_color)
                            border_mask = Image.new('L', (border_size, border_size), 0)
                            border_draw = ImageDraw.Draw(border_mask)
                            border_draw.ellipse((0, 0, border_size, border_size), fill=255)
                            
                            # Paste avatar
                            img.paste(border, (30, 50), border_mask)
                            img.paste(avatar, (35, 55), mask)
            except:
                draw.ellipse([(30, 50), (150, 170)], fill=class_color)
                draw.ellipse([(35, 55), (145, 165)], fill=(50, 50, 60))
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                header_font = ImageFont.truetype("arial.ttf", 24)
                text_font = ImageFont.truetype("arial.ttf", 18)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                small_font = ImageFont.load_default()

            with Pilmoji(img) as pilmoji:
                
                # Username
                pilmoji.text((180, 60), str(user_data.username), fill=(255, 255, 255), font=title_font)
                
                # Class Badge
                class_text = f"⚔️ {user_data.cls}"
                # Get text size using standard font method
                left, _top, right, _bottom = draw.textbbox((0, 0), class_text, font=header_font)
                class_width = right - left
                
                # Draw the background rectangle using standard 'draw' (Pilmoji is only for text)
                draw.rounded_rectangle(
                    [(180, 110), (195 + class_width, 145)],
                    radius=10,
                    fill=class_color
                )
                # Draw text with emoji on top
                pilmoji.text((188, 115), class_text, fill=(255, 255, 255), font=header_font)
                
                # Level Badge
                level_text = f"Level {user_data.level}"
                draw.rounded_rectangle(
                    [(205 + class_width, 110), (325 + class_width, 145)],
                    radius=10,
                    fill=(70, 70, 90)
                )
                pilmoji.text((215 + class_width, 115), level_text, fill=(255, 215, 0), font=header_font)
                
                # Stats section
                y_offset = 180
                
                # HP Bar Text
                pilmoji.text((180, y_offset), "❤️ HP", fill=(255, 100, 100), font=text_font)
                
                # HP Bar Graphics (Standard Draw)
                hp_percentage = user_data.hp / user_data.max_hp
                draw.rounded_rectangle([(250, y_offset), (550, y_offset + 25)], radius=5, fill=(60, 60, 70))
                draw.rounded_rectangle(
                    [(250, y_offset), (250 + int(300 * hp_percentage), y_offset + 25)],
                    radius=5,
                    fill=(220, 20, 60)
                )
                pilmoji.text((560, y_offset), f"{user_data.hp}/{user_data.max_hp}", fill=(255, 255, 255), font=text_font)
                
                # XP Bar Text
                y_offset += 40
                next_xp = GameLogic.calculate_level_xp(user_data.level)
                pilmoji.text((180, y_offset), "✨ XP", fill=(100, 149, 237), font=text_font)
                
                # XP Bar Graphics
                xp_percentage = user_data.xp / next_xp if next_xp > 0 else 0
                draw.rounded_rectangle([(250, y_offset), (550, y_offset + 25)], radius=5, fill=(60, 60, 70))
                draw.rounded_rectangle(
                    [(250, y_offset), (250 + int(300 * xp_percentage), y_offset + 25)],
                    radius=5,
                    fill=(100, 149, 237)
                )
                pilmoji.text((560, y_offset), f"{user_data.xp}/{next_xp}", fill=(255, 255, 255), font=text_font)
                
                # Combat stats
                y_offset += 50
                stats_text = [
                    f"⚔️ ATK: {user_data.attack}",
                    f"🛡️ DEF: {user_data.defense}",
                    f"💰 {user_data.balance:,}"
                ]
                
                for i, stat in enumerate(stats_text):
                    x_pos = 180 + (i * 140)
                    draw.rounded_rectangle(
                        [(x_pos, y_offset), (x_pos + 130, y_offset + 35)],
                        radius=8,
                        fill=(70, 70, 90)
                    )
                    pilmoji.text((x_pos + 10, y_offset + 8), stat, fill=(255, 255, 255), font=text_font)
                
                # PvP Record
                y_offset += 50
                win_rate = user_data.win_rate
                record_text = f"⚔️ PvP: {user_data.pvp_wins}W / {user_data.pvp_losses}L ({win_rate:.1f}%)"
                pilmoji.text((180, y_offset), record_text, fill=(255, 215, 0), font=text_font)
                
                # Achievements
                y_offset += 30
                achievements = f"🗺️ {user_data.adventure_count} Adventures   |   🐉 {user_data.boss_kills} Bosses"
                pilmoji.text((180, y_offset), achievements, fill=(150, 150, 150), font=small_font)
            
            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return discord.File(buffer, filename='profile.png')
        except Exception as e:
            print(f"Error creating profile card: {e}")
            import traceback
            traceback.print_exc() # Helps debug errors
            return None