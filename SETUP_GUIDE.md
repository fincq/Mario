# Mario Setup Guide

## Quick Start (Windows)

### Easy Installation
1. Download and extract Mario files
2. **Double-click `install_mario.bat`**
3. Follow the prompts - it will install and run Mario automatically!

### Manual Installation
If the batch file doesn't work:

1. **Check Python Installation**
   ```cmd
   python --version
   ```
   If this fails, install Python from https://python.org

2. **Navigate to Mario Folder**
   - Open the Mario folder in File Explorer
   - Click in the address bar
   - Type `cmd` and press Enter

3. **Install Mario**
   ```cmd
   pip install --editable .
   ```

4. **Run Mario**
   ```cmd
   mario
   ```
   or
   ```cmd
   python -m mario
   ```

## First Time Usage

### 1. Login
- Use your normal Tassomai email and password
- Same credentials you use on the website

### 2. Choose Timing
- **HUMAN-LIKE** (Recommended): Realistic 1.5-4 second delays
- **FAST**: Quick 0.1-0.2 second delays (may look suspicious)
- **CUSTOM**: Set your own timing

### 3. Choose Accuracy
- **75-85%**: Natural looking progression (recommended for most users)
- **85-95%**: High accuracy but still realistic
- **95-100%**: Perfect scores (may look suspicious to teachers)
- **60-75%**: Very natural but slower progress

### 4. Let Mario Run
- Mario runs continuously until you stop it
- Press **Ctrl+C** to stop Mario
- Check your progress on the Tassomai website

## Troubleshooting

### "Authentication Failed"
- Double-check email and password
- Make sure you can log in to Tassomai website normally
- Wait a few minutes (rate limiting)

### "Python not found"
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation
- Restart command prompt after installing

### "pip not recognized"
- Try `python -m pip install --editable .` instead
- Make sure Python was installed with pip

### Mario seems too fast/slow
- Stop Mario (Ctrl+C)
- Run again and choose different timing settings
- Adjust accuracy percentage for your comfort level

## Safety Tips

- Start with lower accuracy (75-80%) to look more natural
- Use HUMAN-LIKE timing for realistic behavior
- Don't run Mario 24/7 - take breaks like a real student would
- Monitor your progress and adjust settings as needed

## Getting Help

- Check the README.md file
- Visit: https://github.com/afonch/Mario
- Make sure your Tassomai account is in good standing