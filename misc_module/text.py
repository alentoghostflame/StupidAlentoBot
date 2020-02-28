STATUS_MESSAGE_MESSAGE = "Messages Read: {}\nMessages Sent: {}"
STATUS_TOGGLE_MESSAGE = "Callout Delete: {}\nFAQ: {}\nWelcomes: {}"

WELCOME_ADMIN_HELP = "Admin command for controlling the welcome feature for this server. Supports up to 2 arguments, " \
                     "with the 2nd being wrapped in quotes if multi-word. Acceptable 1st arguments are `toggle`, " \
                     "`add`, `remove`, `list`, `set_channel`, and `unset_channel`."
WELCOME_SET_CHANNEL_CURRENT = "Set the welcome channel to this channel."
WELCOME_SET_CHANNEL_OTHER = "Set the welcome channel to the given channel."
WELCOME_UNSET_SUCCESS = "Welcome channel set to be non-existent. It's unselected."
WELCOME_TOGGLE_NO_CHANNEL = "The selected channel to send the welcome messages is non-existent. Fix by using `;set_" \
                            "welcome_channel` in the channel for welcomes to be forwarded to. Not enabling welcomes."
WELCOME_ADD_HELP = "Adds a welcome message. Wrap the message in quotes, and use \"{0}\" without quotes to have the " \
                   "users name be placed there in the message.\n In short, uses Python `.format(member.display_name)`"
WELCOME_ADD_SUCCESS = "Added welcome message."
WELCOME_REMOVE_HELP = "Removes a welcome message of the given index."
WELCOME_REMOVE_SUCCESS = "Successfully removed welcome message."

CALLOUT_DELETE_MISSING_AUDIT_PERMISSION = "I need permission to view the audit log to call out deletes. Disabling " \
                                          "calling out deletes."
CALLOUT_DELETE_ADMIN_HELP = "Admin command for controlling the calling out of deletes. Supports of up to 2 arguments." \
                            " Acceptable first arguments are `toggle`, and that's it."
