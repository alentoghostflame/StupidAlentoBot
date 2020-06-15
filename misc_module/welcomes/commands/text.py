WELCOME_CONTROL_TOO_MANY_ARGS = "Too many arguments, did you forget to wrap multi-line arugments in quotes?\n" \
                                "Tip: You can use a backslash to escape quotes inside quotes `\\\"`"
WELCOME_CONTROL_MISSING_ARG_1 = "`welcome toggle|add|remove|rm|list|set`"
WELCOME_CONTROL_TOGGLE_ON = "Welcomes enabled."
WELCOME_CONTROL_TOGGLE_OFF = "Welcomes disabled."

WELCOME_CONTROL_ADD_MISSING_ARG = "Adds a welcome message for joining users.\n" \
                                  "To have their name appear in the message, put \"{0}\" in the message, without the " \
                                  "quotes. To @mention them, put \"{1}\". Again, without quotes."
WELCOME_CONTROL_ADD_SUCCESS = "Added the following message to list of welcomes:\n```{}```"

WELCOME_CONTROL_REMOVE_MISSING_ARG = "Specify a valid number to remove a welcome message. You can view the welcome " \
                                     "messages by doing the command `welcome list`"
WELCOME_CONTROL_REMOVE_INDEX_OOB = "Index number out of bounds."
WELCOME_CONTROL_REMOVE_SUCCESS = "Successfully removed the welcome message."

WELCOME_CONTROL_SET_INVALID_ARG = "Specify a valid text channel for welcomes to appear in that channel."
WELCOME_CONTROL_SET_SUCCESS = "Welcome channel set to {}"
