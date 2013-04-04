# Todo

![Todo intro][1]

## Overview

Todo is a simple yet feature packed todo list manager for Alfred.

## Getting started



### Keywords

* `todo` this is the main keyword, and lets you get started
    * `todo <new task>` will add a new task
    * `todo` will display the list of tasks
    * `todo #` will display the list of tags
* `add <new task>` will add a new task
* `done` will show you all items that have been marked as done
* `clear` to remove items


#### Adding new items

* Typing `add a new task` will create a new task titled **a new task**. This will be tagged **#default**
* Typing `todo #work sign off document` will create a task titled **sign off document** and tagged **#work**
* Typing `add !! this is sticky` will create a pinned item titled **this is sticky**, tagged **#default**

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


### Advanced Keywords

Todo is made to work out of the box by default, but in case you need more control the following commands may help:

* `setup {then select a folder in Alfred}`. If you want to change the location of your todo items database file, use this option. Useful if you need it to set it up as a folder within Dropbox to sync your todo items between multiple computers having Todo. 
	* Once you define a setup folder, all your existing todo database file will be moved over to the new location, and you can resume working with Todo. You can use the setup command multiple times.
The todo database file is a simple text based format, you can open it and view it in your favourite text editor. (The format is YAML)
* `reset` As the name suggests, resets your Todo workflow (clears all todo items, resets the location of your todo database file to the default location)
* `export` Will allow you to export your todo list as plain text. If you have specific tags created, you can export them individually. At the moment, the export only copies items to the clipboard
* `import (file mode)` Use this option and specify a text file to import contents from that. Format of the text file can be 1 todo item per line, or the format the export option uses. Import mechanism ignores whitespaces, so you can indent your files as you please. Here is an example.
* `import (from clipboard)` This option will allow you to import the contents of your clipboard, rather than from a file
* `features` keyword will allow you to switch on various features.


#### Features

![Features][3]

Currently, there are three settings. **Quick Create** allows you to create new Todo items (when typing it in using the todo keyword) slightly faster. It prevents Alfred from disappearing and appearing when an item is added.

**Smart Content** - if you would like to add folders, URLs, to Todo, try adding them after Smart Content mode is switched on. It allows the following transformation

![Smart Content Disabled][4]

![Smart Content Enabled][5]

**Smart Content - Page Titles**, when enabled, will pre-fetch the web page title so that you get a better idea what a link will take you to, as in the example above.
 
This allows you to do multiple things, you can now group your favourite links, folders or files by a tag name. Smart Content works best when you have a hot key enabled to add a new Todo item.
 
Remember, smart content items are just simple todo items, so you can pin, tag, delete, mark as done etc as normal. Smart content only kicks in for all new items added, so existing items will remain untouched.


## Syntax Guide

To create or edit todo items, you use the Todo item syntax. A todo item can be simply represented just the task description, or marked up with tags, pin status and a due date. 

A full fedged task description would be like:
> `!!` `#tag` `this is a task` `@mon`

* The `!!` is a shortcut that identifies the todo item should be pinned by deafault.
* `#tag` specifies that the todo item should be tagged with the name `tag`.
* `this is a task` is the text of the todo item
* `@mon` is the due date specifier

Every section other than the task description is optional


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