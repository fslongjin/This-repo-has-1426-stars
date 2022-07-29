# 基于 .NET6  开发的 C# 版本

代码中实现了两个版本：

- 使用Github 获取Repository信息，并进行更新；（存在频次限制）

- 使用了HtmlAgilityPack进行Repository信息的爬取，并进行更新；（无法及时更新）



## 使用

请在vs 2022中打开，且确保已安装.NET 6 SDK

1. 代码中修改指定值

```C#
// github token
var githubToken = "";

// repository 地址
var pubRepoUrl = "https://github.com/fslongjin/This-repo-has-4-stars";
var repoUrl = "https://api.github.com/repos/fslongjin/This-repo-has-4-stars";
```

2.  F5