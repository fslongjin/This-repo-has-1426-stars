import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse.BodyHandlers;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;

public class Main {

  /** 序列化JSON使用 */
  private static final ObjectMapper MAPPER = new ObjectMapper();
  /** github token */
  private static final String GITHUB_TOKEN = "";
  /** 仓库地址 */
  private static final String REPO_URL =
      "https://api.github.com/repos/fslongjin/This-repo-has-N-stars";

  private static final Pattern PATTERN = Pattern.compile("This-repo-has-(\\d+)?-stars");
  private static final Map<String, String> HEADERS = new HashMap<>();
  private static final HttpClient HTTP_CLIENT = HttpClient.newHttpClient();

  static {
    HEADERS.put("Accept", "application/vnd.github.v3+json");
    HEADERS.put("Authorization", "token " + GITHUB_TOKEN);
  }

  public static void main(String[] args) throws Exception {
    while (true) {
      updateProjectName(getStars(URI.create(REPO_URL)));
      try {
        TimeUnit.SECONDS.sleep(3);
      } catch (InterruptedException ignore) {
      }
    }
  }

  private static void updateProjectName(StarResult starResult)
      throws IOException, InterruptedException {
    // 正则匹配当前仓库的名字来获取star数量
    var matcher = PATTERN.matcher(starResult.repoName());
    if (!matcher.find()) {
      return;
    }
    var currentStars = Integer.parseInt(matcher.group(1));
    // 如果名字中的star数量和实际的star数量不相等则更新
    if (currentStars == starResult.stars()) {
      return;
    }

    var newName = "This-repo-has-%s-stars".formatted(starResult.stars());
    var newData = MAPPER.createObjectNode();
    newData.put("name", newName);
    newData.put("description", "这个仓库有%s个star，不信你试试".formatted(starResult.stars()));
    System.out.printf("Try to update repo, new Name:%s%n", newName);

    var builder =
        HttpRequest.newBuilder()
            .uri(starResult.uri())
            .method("PATCH", BodyPublishers.ofString(MAPPER.writeValueAsString(newData)));
    HEADERS.forEach(builder::header);
    var response = HTTP_CLIENT.send(builder.build(), BodyHandlers.ofString());
    if (response.statusCode() == 200) {
      System.out.printf("Update successfully, new Name:%s%n", newName);
    } else {
      System.out.printf("Update failed, response is :\n %s%n", response.body());
    }
  }

  /**
   * 获取当前仓库的star数量
   *
   * @param uri 仓库地址
   * @return 仓库重定向地址，仓库名称，仓库star数
   */
  private static StarResult getStars(URI uri) throws Exception {
    var builder = HttpRequest.newBuilder().uri(uri).GET();
    HEADERS.forEach(builder::header);
    var response = HTTP_CLIENT.send(builder.build(), BodyHandlers.ofString());
    var objectNode = MAPPER.readTree(response.body());
    if (objectNode.has("full_name")) {
      return new StarResult(
          uri, objectNode.get("full_name").asText(), objectNode.get("watchers").asInt());
    } else {
      // full_name发生变化，重定向到新的地址
      return getStars(URI.create(objectNode.get("url").asText()));
    }
  }

  private record StarResult(URI uri, String repoName, int stars) {}
}
