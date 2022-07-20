use super::config::{OWNER, REPO};
use std::sync::Arc;

use octocrab::{map_github_error, Octocrab, OctocrabBuilder};
use reqwest::Response;
use serde_json::json;

pub fn init() -> anyhow::Result<Arc<Octocrab>> {
    let pat_token = std::env::var("GITHUB_TOKEN")
        .map_err(|_| anyhow::anyhow!("You must specify the GitHub token in envvar GITHUB_TOKEN to change the repo information."))?;

    let builder = OctocrabBuilder::new().personal_token(pat_token);

    Ok(octocrab::initialise(builder)?)
}

/// Get the current stars of this repository.
pub async fn get_stars() -> octocrab::Result<u32> {
    let repo = octocrab::instance().repos(OWNER, REPO).get().await?;

    Ok(repo.stargazers_count.unwrap_or(0))
}

/// Update the stars of this repository.
///
/// Reference: <https://docs.github.com/en/rest/repos/repos#update-a-repository>
pub async fn update_to_stars(stars: u32) -> octocrab::Result<Response> {
    let payload = json!({
        "name": format!("This-repo-has-{stars}-stars"),
        "description": format!("这个仓库有{stars}个star，不信你试试"),
    });

    tracing::debug!("{payload:?}");

    let instance = octocrab::instance();
    let response = instance
        ._patch(
            instance
                .absolute_url(format!("/repos/{OWNER}/{REPO}"))
                .unwrap(),
            Some(&payload),
        )
        .await?;

    map_github_error(response).await
}

/// Get the scope of this token.
#[cfg(debug_assertions)]
pub async fn get_token_scope() -> anyhow::Result<Option<String>> {
    let instance = octocrab::instance();
    let response = instance
        ._get(instance.absolute_url("/").unwrap(), None::<&()>)
        .await?;

    if let Some(token_scope) = response.headers().get("X-OAuth-Scopes") {
        Ok(Some(token_scope.to_str()?.to_string()))
    } else {
        Ok(None)
    }
}
