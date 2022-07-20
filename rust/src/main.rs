mod config;
mod octocrab;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    octocrab::init()?;

    #[cfg(debug_assertions)]
    {
        tracing::debug!("Getting the token scope…");
        tracing::debug!("Token scope: {:?}", octocrab::get_token_scope().await?);
    }

    tracing::debug!("Getting the stars…");
    let stars = octocrab::get_stars().await?;
    tracing::info!("This repo has {stars} stars currently.");

    tracing::debug!("Updating the repo information…");
    octocrab::update_to_stars(stars).await?;
    tracing::info!("Successfully updated the stars of this repo to {stars}.");

    Ok(())
}
