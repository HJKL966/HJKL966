#!/usr/bin/env python3
import asyncio
import json
import datetime
import os
import sys

# Ensure the script can find Flask app context and models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from telethon import TelegramClient, errors
from src.main import app, db # Import Flask app and db instance
from src.models.stats import BotStat # Import the BotStat model
from dateutil import parser # For parsing ISO timestamps

# WARNING: Hardcoding credentials is not secure for production.
# Consider using environment variables or a configuration file.
api_id = 27591799
api_hash = "97c5ff5e1210e2599441f4fe5223dcf1"
channel_id = -1002667610742 # The specific channel ID for stats

# Use a unique session name
session_name = "dashboard_reader_session"

async def process_message(message_text):
    """Attempts to parse JSON from message text and save to DB."""
    if not message_text or not message_text.strip().startswith("```json"):
        # print(f"Skipping non-JSON message: {message_text[:50]}...")
        return

    # Extract JSON content (remove ```json and ```)
    json_string = message_text.strip()[7:-3].strip()
    
    try:
        data = json.loads(json_string)
        print(f"Successfully parsed JSON: {data}")

        # Extract data, providing defaults or None if keys are missing
        user_id = data.get("user_id")
        username = data.get("username")
        action = data.get("action")
        timestamp_str = data.get("timestamp")
        error_message = data.get("error")
        raw_update_data = data.get("update") # Keep as string for now
        message_length = data.get("message_length")

        # Ensure required fields are present (adjust as needed)
        if not action or not timestamp_str:
            print(f"Skipping record due to missing action or timestamp: {data}")
            return

        # Parse timestamp string into a timezone-aware datetime object
        try:
            timestamp = parser.isoparse(timestamp_str)
        except ValueError:
            print(f"Skipping record due to invalid timestamp format: {timestamp_str}")
            return

        # Create BotStat object
        new_stat = BotStat(
            # bot_identifier can be added if needed
            user_id=user_id,
            username=username,
            action=action,
            timestamp=timestamp,
            message_length=message_length,
            error_message=error_message,
            raw_update_data=str(raw_update_data), # Store as string
            raw_json=json_string
        )

        # Add to DB session (needs Flask app context)
        db.session.add(new_stat)
        print(f"Added stat to session: Action={action}, User={user_id}")

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e} - Content: {json_string[:100]}...")
    except Exception as e:
        print(f"Error processing data or creating BotStat object: {e}")

async def main():
    print("Attempting to connect to Telegram...")
    client = TelegramClient(session_name, api_id, api_hash)

    try:
        await client.start()
        print("Successfully connected to Telegram!")

        entity = await client.get_entity(channel_id)
        print(f"Successfully found channel: {entity.title}")

        print(f"Fetching recent messages from channel ID {channel_id}...")
        # Fetch messages and process them within the Flask app context
        with app.app_context():
            messages = await client.get_messages(entity, limit=20) # Fetch more messages if needed
            if messages:
                print(f"Processing {len(messages)} messages...")
                for message in messages:
                    await process_message(message.text)
                
                # Commit changes after processing all messages in the batch
                try:
                    db.session.commit()
                    print("Successfully committed stats to database.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing to database: {e}")
            else:
                print("No new messages found to process.")

    except errors.ChannelPrivateError:
         print(f"Error: Cannot access channel {channel_id}. Ensure the user/bot is a member.")
    except ValueError:
         print(f"Error: Channel ID {channel_id} seems invalid or not found.")
    except Exception as e:
        print(f"An error occurred during connection or operation: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()
            print("Disconnected from Telegram.")

if __name__ == "__main__":
    # Run within the Flask app context to access db
    # Example: cd /home/ubuntu/dashboard_project/dashboard && /home/ubuntu/dashboard_project/dashboard/venv/bin/python src/read_stats.py
    asyncio.run(main())

