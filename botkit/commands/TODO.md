# Conversation Proxy

## TODO
- [ ] Refactor!!!


# Commands, Actions, QuickActions

## How it's gonna work
Commands from all modules get registered in a central place.
A singleton (compound, all types) internal handler goes through all registered commands and builds a list
 `quick_action_matches: List[CommandDefinition]`.
Then it replies with reply keyboard buttons. `botkit.use_quick_actions()` ??

modulemanager

```
routes.register_command()
```

## TODO
- [ ] add convenient way of constructing CommandDefinition
- [ ] "exclusive" status, where only this single quick action will apply (based on priority over others)
- [ ] debounce the responses (1 second) and allow merges like stickerstorybot (messagemerger)
- [ ] Make it possible to configure the chats in which quick actions trigger:
    - `FindChat(title=r'.*Ideas.*Thoughts$', mine=True)`
    - `FindChat(title=r'.*Todo$', mine=True)`
    - `FindChat(username='@josxabot')`
    - `FindChat(title='sovorel sprachen')`

## Quick Action Registry (Ideas)

### filters.text
(Most common. Needs a good hierarchical menu)
- **Use in inline query** -> "Which bot @?" - @letmebot -> Share button
- **Remind me**
  -> `ChoiceView("Who to remind?", ["Just me", "Someone else", "Me and others"])`
  -> `DateTimePickerView("When?")`
- **Edit** -> `send_as_user(...)` (so that user can edit)
- **Share** -> `ShareView(...)`

### filters.text (multiple)
"Does this message belong to the others?" yes/no
- **Merge** ->
- **Delete** (if forwarded and user admin)
    -> "This will delete messages 1-3, 7, and 8 from {origin_chat_title}" (yes/no)
- **Open in VSCode**

### filters.link
- **Open in browser** -> `ChoiceView(links) if len(links) > 1 else links[0]`
- **Add to Pocket** -> `ChoiceView(links, multiple=True) if len(links) > 1 else links[0]`

### Integrations

- Todoist
    - Add as Task
- Notion
    - Add to project -> `ChoiceView(...)`

### filters.sticker
- Add to pack
- Optimize

### filters.sticker (multiple)
- Merge

### filters.command
- Choose bot

### filters.contains_emoji
- Explain emojis

# Editor

The `EditorView` consists of a message with quick actions above and the content to edit in its own message below:
```
**Actions**
[Share] [Append] [Open in VSCode]
```

## Actions
- Apply a template -> `ChoiceView(...)`
- Share -> `ShareView(...)`
- As draft



# For Nukesor

## Prototype of hierarchical settings module

Click on setting -> opens group of related settings (and back button)
