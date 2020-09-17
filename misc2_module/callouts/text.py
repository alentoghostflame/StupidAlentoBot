USER_MISSING_PERMISSIONS = "You don't have the permission to run this command."
CALLOUT_COMMAND_NOT_FOUND = "Command not found, do `callout` to list all the commands."
CALLOUT_DELETE_COMMAND_NOT_FOUND = "Command not found, do `callout delete` to list all commands."

CALLOUT_BRIEF = "Controls what users are called out for."
CALLOUT_DELETE_BRIEF = "Controls calling out deletes."
CALLOUT_DELETE_ENABLE_BRIEF = "Enables calling out deletes."
CALLOUT_DELETE_DISABLE_BRIEF = "Disables calling out deletes."

CALLOUT_HELP_DESCRIPTION = "Controls what the bot will call out when the users do a specific action."
CALLOUT_HELP_USAGE = f"`callout delete`: {CALLOUT_DELETE_BRIEF}"


CALLOUT_DELETE_HELP_DESCRIPTION = "Calls out users for deleting their own messages, repeating back what they said " \
                                  "when possible."
CALLOUT_DELETE_HELP_USAGE = f"`callout delete enable`: {CALLOUT_DELETE_ENABLE_BRIEF}\n" \
                            f"`callout delete disable`: {CALLOUT_DELETE_DISABLE_BRIEF}"
CALLOUT_DELETE_PHRASES = {"Hey, I thought I remembered {1} saying \"{0}\"", "Hey {1}, didn't you say something like "
                                                                            "\"{0}\"?",
                          "> {0}\n - {1}"}
CALLOUT_DELETE_ALREADY_ENABLED = "Calling out deletes was already enabled."
CALLOUT_DELETE_ENABLED = "Enabled calling out deletes."
CALLOUT_DELETE_ALREADY_DISABLED = "Calling out deletes was already disabled."
CALLOUT_DELETE_DISABLED = "Disabled calling out deletes."
CALLOUT_DELETE_MISSING_AUDIT_PERMISSION = "I need permission to view the audit log to call out deletes. Disabling " \
                                          "calling out deletes."

