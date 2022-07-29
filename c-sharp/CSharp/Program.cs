using HtmlAgilityPack;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

// github token
var githubToken = "";

// 仓库地址
var pubRepoUrl = "https://github.com/fslongjin/This-repo-has-4-stars";
var repoUrl = "https://api.github.com/repos/fslongjin/This-repo-has-4-stars";
var repoApiUrl = "https://api.github.com/repos/";

// 构建全局请求
var _client = new HttpClient();
_client.DefaultRequestHeaders.UserAgent.TryParseAdd("request");
_client.DefaultRequestHeaders.Add("Accept", "application/vnd.github.v3+json");
_client.DefaultRequestHeaders.Add("Authorization", $"token {githubToken}");



while (true)
{
    // var repoInfo = GetRepoInfoAsync(repoUrl);
    var repoInfo = GetRepoInfoByHtml(pubRepoUrl);
    if (repoInfo == null) continue;
    await UpdateRepoNameAsync(repoInfo);
    await Task.Delay(3000);
}

/// <summary>
/// 更新Repository信息
/// </summary>
/// <param name="repoUrl">Repository地址</param>
/// <returns></returns>
async Task UpdateRepoNameAsync(RepoInfo repoInfo)
{
    try
    {
        var match = Regex.Match(repoInfo.FullName ?? "", "This-repo-has-(\\d+)?-stars");
        if (!match.Success || match.Groups.Count <= 0)
        {
            Console.WriteLine("正则表达式无法匹配，请确认！");
            return;
        }
        var startStr = match.Groups[1].Value;

        // 如果转化失败，或者和之前的一致就返回
        if (!int.TryParse(startStr, out int preStart) || preStart == repoInfo.Watchers)
        {
            Console.WriteLine("Start没有变更，无需更新");
            return;
        }
        var body = new
        {
            name = $"This-repo-has-{repoInfo.Watchers}-stars",
            description = $"这个仓库有{repoInfo.Watchers}个star，不信你试试",
        };
        var content = new StringContent(JsonSerializer.Serialize(body), Encoding.UTF8);
        var resp = await _client.PatchAsync($"{repoApiUrl}{repoInfo.FullName}", content);
        if (resp.StatusCode != System.Net.HttpStatusCode.OK)
        {
            Console.WriteLine("更新失败");
            return;
        }
        Console.WriteLine("更新成功");
    }
    catch (Exception)
    {
        throw;
    }

}


/// <summary>
/// 获取Repository信息 （存在超频问题）
/// </summary>
/// <param name="repoUrl">Repository地址</param>
/// <returns></returns>
async Task<RepoInfo?> GetRepoInfoAsync(string repoUrl)
{
    try
    {
        var resp = await _client.GetStringAsync(repoUrl);
        var repoInfo = JsonSerializer.Deserialize<RepoInfo>(resp);
        return repoInfo;
    }
    catch (Exception ex)
    {
        Console.WriteLine("获取Repo异常 ex：{0}", ex.Message);
        return null;
    }
}

/// <summary>
/// 获取Repository信息 By Public Url And Html
/// </summary>
/// <param name="repoUrl">Repository地址</param>
/// <returns></returns>
RepoInfo? GetRepoInfoByHtml(string repoUrl)
{
    try
    {
        HtmlWeb web = new HtmlWeb();
        var htmlDoc = web.Load(repoUrl);
        HtmlNode starNaode = htmlDoc.DocumentNode.SelectSingleNode("//*[@id=\"repo-stars-counter-star\"]");
        HtmlNode author = htmlDoc.DocumentNode.SelectSingleNode("//*[@itemprop=\"author\"]/a");
        HtmlNode repoName = htmlDoc.DocumentNode.SelectSingleNode("//*[@itemprop=\"name\"]/a");
        int.TryParse(starNaode.InnerText, out int star);

        return new RepoInfo
        {
            FullName = $"{author.InnerText}/{repoName.InnerText}",
            Watchers = star,
        };
    }
    catch (Exception ex)
    {
        Console.WriteLine("获取Repo异常 ex：{0}", ex.Message);
        return null;
    }
}


class RepoInfo
{
    [JsonPropertyName("full_name")]
    public string? FullName { get; set; }

    [JsonPropertyName("watchers")]
    public int Watchers { get; set; }
}
