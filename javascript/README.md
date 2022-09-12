# Environment
全局安装node.js
# How to use this script to update name of your repo.
在本地新建一个`.env`配置文件，在配置文件写下下面信息
```
GITHUB_TOKEN=*********
owner=************
repo_name=********
```
GITHUB_TOKEN是你生成的密钥，owner是你的GitHub用户名，repo_name是你新建的自己仓库的名字。

然后在项目终端分别安装相应依赖
```
yarn add octokit -D
yarn add dotenv -D
```

先运行：`node getRepId.js`，获取仓库的id，然后将id信息写入`.env`配置文件
```
GITHUB_TOKEN=*********
owner=************
repo_name=********
repo_id=********
```

然后再运行：`node main.js`，就可以了。