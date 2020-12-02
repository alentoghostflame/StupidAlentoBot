# Timekeeper
Helps keep time by displaying it and allowing users to set timers. Initially made to test the built-in timer function in alento_bot.

Has no new dependencies.
## Commands
### Timer
Sets a timer to go off at a custom time with an optional custom message.

Usage: 
* `;timer days:hours:minutes custom_message`
* `;timer 20`
* `;timer 50 It's been 50 minutes.`
* `;timer 3:0 It's been 3 hours.`
* `;timer 2:0:0 It's been 2 days, jeez.`
* `;timer 2:: This also goes off after 2 days.`
* `;timer 7: Goes off after 7 hours, I love shortcuts.`

### Time
Sends the bots local time.

Usage:
* `;time`

### Timeutc
Sends the time in UTC.

Usage:
* `;timeutc`

