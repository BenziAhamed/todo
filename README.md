# Todo

![Todo intro][1]

## Overview

Todo is a simple yet feature packed todo list manager for Alfred.

![Todo items][6]

## Getting started
### Keywords

* `todo` this is the main keyword, and lets you get started
    * `todo <new task>` will add a new task
    * `todo` will display the list of tasks
    * `todo #` will display the list of tags
    * `todo @` will display all items with a due date
    > **TIP** To see all items due for today, type `todo @today`
* `add <new task>` will add a new task
* `done` will show you all items that have been marked as done
* `clear` to remove items


#### Adding new items

* Typing `add a new task` will create a new task titled **a new task**. This will be tagged **#default**
* Typing `todo #work sign off document` will create a task titled **sign off document** and tagged **#work**
* Typing `add !! this is sticky` will create a pinned item titled **this is sticky**, tagged **#default**
* Typing `todo @today a new task for the day` will create a new item, due for today, titled **a new task for the day**

![Todo add item][2]

When adding items, add and todo keywords are interchangeable, although the key difference is add allows you to add items with the title twice; todo provides a more informative feedback on screen

#### Command modifiers

* Pressing `fn` key when selecting an item will enable edit mode for that item - this works for both todo items and tags
    * In edit mode, use the same syntax that you use to create a new todo - e.g. `#newtag new todo text`. Todo will identify which portion you need to change and update them accordingly
* `Shift` will allow you to mark an item as done. You can view all done items with the done keyword
* `Cmd` will help you delete either a todo item, and all items that match a specific tag
* `Alt` will help you list out all items that match the currently selected items tag
* `Ctrl` will help you pin/unpin a todo item. Pinned items will always be displayed first (they can be deleted as usual)
* `Tab` key against a todo item, you will be shown all todo items with the matching tag
* `Enter` will copy the text content of a todo item to the clipboard

## Lists

![Todo lists][7]

If you want more control over your todo items apart from tagging, pinning and setting due dates for them, you can split up your todo items with lists.

By default, Todo uses a list called `todo`, but you can create new lists using the `list` keyword.

* Typing `list` will display all available lists
* Typing `list <name>` will select a list titled `name` if it exists or allow you to create a new list

At any point in time only one list will be active, and all actions performed by using the `todo`,`add`,`import`,`export` etc keywords will be working against the currently active list.

In list view, `Cmd` + `Enter` will help you to delete a list altogether.

## Advanced Keywords

Todo is made to work out of the box by default, but in case you need more control the following commands may help:

* `setup {then select a folder in Alfred}`. If you want to change the location of your todo items database file, use this option. Useful if you need it to set it up as a folder within Dropbox to sync your todo items between multiple computers having Todo. 
	* Once you define a setup folder, all your existing todo database file will be moved over to the new location, and you can resume working with Todo. You can use the setup command multiple times.
The todo database file is a simple text based format, you can open it and view it in your favourite text editor. (The format is YAML)
* `reset` As the name suggests, resets your Todo workflow (clears all todo items, resets the location of your todo database file to the default location)
* `export` Will allow you to export your todo list as plain text. Two options are available:
	* Export todo list to a .taskpaper file
	* Export todo list in classic plain text/taskpaper format to clipboard 
* `import (file mode)` Use this option and specify a text file to import contents from that. You can import a plain text .txt file with todo items listed one per line, or you can import a .taskpaper file. Some limitations exist for the Taskpaper file import - no support for subprojects, notes, and project names cannot have spaces in them, and are mapped to a Todo tag.
* `import (from clipboard)` This option will allow you to import the contents of your clipboard, rather than from a file
* `features` keyword will allow you to switch on various features.


## Features

![Features][3]

**Quick Create** allows you to create new Todo items (when typing it in using the todo keyword) slightly faster. It prevents Alfred from disappearing and appearing when an item is added.

**Anchored Search** allows you to filter Todo items more quickly. With this option enabled, if you have a task description like `This is a long description`, you can quickly narrow down to that item by typing `tiald`

**Smart Content** - if you would like to add folders, URLs, to Todo, try adding them after Smart Content mode is switched on. It allows the following transformation

![Smart Content Disabled][4]

![Smart Content Enabled][5]

**Smart Content - Page Titles**, when enabled, will pre-fetch the web page title so that you get a better idea what a link will take you to, as in the example above.
 
This allows you to do multiple things, you can now group your favourite links, folders or files by a tag name. Smart Content works best when you have a hot key enabled to add a new Todo item.
 
Remember, smart content items are just simple todo items, so you can pin, tag, delete, mark as done etc as normal. Smart content only kicks in for all new items added, so existing items will remain untouched.

**EggTimer2 in Edit mode** when enabled will allow you to create alarms for todo items in Edit Mode. You must have the [EggTimer2 workflow](http://www.alfredforum.com/topic/275-eggtimer-v2-updated-to-20-final/) installed.


## Syntax Guide

To create or edit todo items, you use the Todo item syntax. A todo item can be simply represented just the task description, or marked up with tags, pin status and a due date. 

A full fedged task description would be like:
> `!!` `#tag` `this is a task` `@mon`

* The `!!` is a shortcut that identifies the todo item should be pinned by deafault.
* `#tag` specifies that the todo item should be tagged with the name `tag`.
* `this is a task` is the text of the todo item
* `@mon` is the due date specifier

Every section other than the task description is optional. All sections can appear anywhere.


### Due dates
The following are supported

* `@today` item is due today
* `@tomorrow` item is due tomorrow
* `@weekend` item is due next Sunday
* `@nextweek` item is due next Monday
* `@mon`,`@tue`,…,`@sun` item is due next specified week day
* `@xd` item is due `x` days from today - `@6d` means item is due 6 days from now
* `@xw` item is due `x` weeks from today
* `@xm` item is due `x` months from today
* `@fuzzy date` item is due on the date specified. `@1 Dec 2013`, `@Jan 2 2013`, `@1-13-2013` et cetera are recognized

#### Clearing due dates

In item edit mode, enter `@!` to clear a set due date.

## Credits

Lots of people have contributed with suggestions and feature ideas. In particular, the following folks from the Alfred Forum:

* [twinpeaks](http://www.alfredforum.com/user/58-twinpeaks/)
* [CarlosNZ](http://www.alfredforum.com/user/104-carlosnz/)
* [xtin](http://www.alfredforum.com/user/2262-xtin/)


[1]: https://dl.dropbox.com/u/2377432/alfredv2/todo/intro.png "About Todo"
[2]: https://dl.dropbox.com/u/2377432/alfredv2/todo/todo_new.png "Add item"
[3]: https://dl.dropbox.com/u/2377432/alfredv2/todo/features.png "Features"
[4]: https://dl.dropbox.com/u/2377432/alfredv2/todo/no_smartcontent.png "Smart Content Disabled"
[5]: https://dl.dropbox.com/u/2377432/alfredv2/todo/smartcontent.png "Smart Content Enabled"
[6]: https://dl.dropbox.com/u/2377432/alfredv2/todo/todo_items.png "Todo items"
[7]: https://dl.dropbox.com/u/2377432/alfredv2/todo/list.png "Todo lists"