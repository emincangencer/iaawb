# i am afraid arch will break

This project checks for upgradable packages and searches for potential bugs before upgrading.

## Requirements
copy .env.sample > .env

'''
GOOGLE_API_KEY=your_api_key
'''

### System Requirements
- arch
- uv
- pacman-contrib (for checkupdates)

## How to Run
uv run main.py