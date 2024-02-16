# epaper-with-raspberrypi
get weather and chinese poem on raspberrypi's epaper

## 起因
在gpt的帮助下，我完成了对于树莓派的应用，希望更多的人能更快捷的体验到树莓派带来的乐趣，
## 功能说明
功能包括
1. 获取当前天气信息。
2. 获取一句中国古诗词推荐
3. 获取目前树莓派的ip address
4. 把相关信息显示到一个3.52inch的墨水屏上

## 过程
2024/02/15
1. 对于poem进行对象化的修改
2024/02/16
1. 对于可触屏的墨水屏幕进行了解，计划下一步升级交换模式。
2. 解决树莓派启动是运行目录的问题（基于sqlite3的存储方式）


## 心得体会
1. gpts中的python值得尝试，不过gpt-4同样出色。
2. 对于代码的优化无止境，从面向过程进行面向对象的过程中，可以通过分支方式进行同步。
3. 发布时候的目录控制：
    在发布的目录结构中，如果您的项目需要使用 SQLite3 数据库存储数据，可以考虑以下目录结构和部署策略：

项目根目录： 在项目根目录下放置所有的源代码文件以及其他必要的文件，如配置文件、README等。

data 目录： 在项目根目录下创建一个名为 data 的目录，用于存放 SQLite3 数据库文件。您可以将数据库文件放置在此目录中，并在代码中指定相对路径以便访问该数据库文件。

使用相对路径： 在代码中使用相对路径来引用数据库文件，以确保代码在不同环境中的可移植性。您可以使用类似于以下代码来获取数据库文件的路径：

python
Copy code
import os

# 获取当前脚本所在目录的绝对路径
current_directory = os.path.dirname(os.path.abspath(__file__))

# 构建数据库文件的路径
db_file_path = os.path.join(current_directory, 'data', 'your_database.db')
在版本控制中忽略数据库文件： 如果您使用版本控制系统（如 Git），建议将数据库文件添加到 .gitignore 文件中，以防止将其提交到版本库中。这样可以避免数据库文件在团队协作中造成冲突，并保护敏感数据的安全性。

文档和说明： 在 README 文件或项目文档中提供关于如何初始化数据库、数据库结构、访问数据库等方面的说明，以帮助用户正确地使用数据库。

通过以上方法，您可以在发布的目录结构中有效地管理和使用 SQLite3 数据库，并确保代码的可移植性和安全性。




