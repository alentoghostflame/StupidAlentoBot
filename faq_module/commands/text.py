# FAQ_CONTROL_MISSING_ARG_1 = "`faq list|add|remove|rm|toggle|role`"
# FAQ_CONTROL_TOO_MANY_ARGS = "Too many arguments, did you wrap your multi-word arguments in quotes?"
#
# FAQ_CONTROL_ROLE_MISSING_ARG_2 = "`faq role add|remove|rm`"
# FAQ_CONTROL_ROLE_MISSING_ARG_3 = "`faq role {} @role`"
#
# FAQ_CONTROL_ADD_KEYWORD_MISSING_ARGS = "`faq add insert_keyword_here \"Insert Phrase Here.\" \"optional_image_url\"`"
# FAQ_CONTROL_ADD_KEYWORD_SUCCESS = "Keyword ``{}`` created."
# FAQ_CONTROL_ADD_KEYWORD_OVERWRITTEN = "Keyword ``{}`` overwritten."
#
# FAQ_CONTROL_REMOVE_KEYWORD_NOT_FOUND = "Keyword ``{}`` not found."
# FAQ_CONTROL_REMOVE_KEYWORD_SUCCESS = "Keyword ``{}`` deleted."
#
# FAQ_CONTROL_TOGGLE_ENABLED = "FAQ enabled."
# FAQ_CONTROL_TOGGLE_DISABLED = "FAQ disabled."
#
# FAQ_CONTROL_ADD_ROLE_SUCCESS = "Role `{}` added to list of FAQ editors."
# FAQ_CONTROL_ADD_ROLE_DUPLICATE = "Role `{}` already in the list of FAQ editors."
#
# FAQ_CONTROL_REMOVE_ROLE_SUCCESS = "Role removed from list of FAQ editors."
# FAQ_CONTROL_REMOVE_ROLE_MISSING = "Role not in list of FAQ editors."


NO_PRIVATE_MESSAGE = "This command can only be used on a server, not in private messages."
USER_MISSING_ADMIN_PERMISSION = "This command requires the Administrator permission, something that you lack."
MISSING_REQUIRED_ARGUMENT = "Invalid usage: `{}`"
FAQ_TOO_MANY_ARGS = "Too many arguments, did you wrap multi-word arguments in quotes?"
FAQ_INVALID_SUBCOMMAND = "Subcommand not found. To see available subcommands, do `faq`"
FAQ_ROLE_INVALID_SUBCOMMAND = "Subcommand not found. To see available subcommands, do `faq role`"
FAQ_KEYWORD_NOT_FOUND = "Keyword `{}` not found."


FAQ_GROUP_DESCRIPTION = "Allows users to get information from keywords wrapped in curly braces. For example, `{policy}`"
FAQ_GROUP_BRIEF = "Allows users to get information from a single keyword."
FAQ_INFO_BRIEF = "Gives info about FAQ keywords, editing roles, and if FAQ is enabled."
FAQ_ADD_BRIEF = "Adds a keyword to show a phrase when wrapped in braces."
FAQ_REMOVE_BRIEF = "Removes a keyword."
FAQ_ENABLE_BRIEF = "Enables the FAQ module, providing information with keywords."
FAQ_DISABLE_BRIEF = "Disables the FAQ module, no longer providing information."
FAQ_ROLE_GROUP_BRIEF = "Controls if users with a specific role can edit keywords and phrases."
FAQ_ROLE_ADD_BRIEF = "Adds a role to be able to add/remove keywords and phrases."
FAQ_ROLE_REMOVE_BRIEF = "Removes a role from being able to add/remove keywords and phrases."

FAQ_HELP_DESCRIPTION = "Allows users to get information with an optional picture by wrapping a keyword in curly " \
                       "braces. Example: `{policy}`"
FAQ_HELP_TOGGLING = f"`faq enable`: {FAQ_ENABLE_BRIEF}\n`faq_disable`: {FAQ_DISABLE_BRIEF}\n Both of these commands " \
                    f"are only available to members with either an editor role or the Discord " \
                    f"\"Administrator\" permission."
FAQ_HELP_INFORMATION = f"`faq info`: {FAQ_INFO_BRIEF}"
FAQ_HELP_PHRASES = f"`faq add keyword phrase`: {FAQ_ADD_BRIEF} Optional `image_url` argument to show an image with " \
                   f"the keyword is triggered.\n`faq remove keyword`: {FAQ_REMOVE_BRIEF} An alternate form of this " \
                   f"command is `faq rm keyword`\n Both of these commands are only available to members with either " \
                   f"an editor role or the Discord \"Administrator\" permission."
FAQ_HELP_ROLES = f"`faq role`: {FAQ_ROLE_GROUP_BRIEF} Perform the command to get more information."

FAQ_ROLE_HELP_DESCRIPTION = f"{FAQ_ROLE_GROUP_BRIEF} The commands in here are only available to members with the " \
                            f"Discord \"Administrator\" permission."
FAQ_ROLE_HELP_USAGE = f"`faq role add @role`: {FAQ_ROLE_ADD_BRIEF}\n`faq role remove @role`: {FAQ_ROLE_REMOVE_BRIEF} " \
                      f"An alternate form of this command is `faq role rm @role`"


FAQ_ADD_OVERWRITTEN = "Keyword `{}` overwritten"
FAQ_ADD_SUCCESS = "Keyword `{}` added."
FAQ_REMOVE_SUCCESS = "Keyword {} removed."
FAQ_ENABLE_SUCCESS = "FAQ module enabled for this server."
FAQ_DISABLE_SUCCESS = "FAQ module disabled for this server."
FAQ_ROLE_ADD_DUPLICATE = "Role {} could already edit the FAQ."
FAQ_ROLE_ADD_SUCCESS = "Role {} can now edit the FAQ."
FAQ_ROLE_REMOVE_NOT_FOUND = "That role already couldn't edit the FAQ."
FAQ_ROLE_REMOVE_SUCCESS = "That role can no longer edit the FAQ."

