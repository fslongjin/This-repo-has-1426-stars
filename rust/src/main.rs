mod config;
mod octocrab;

use config::REFRESH_INTERVAL;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    octocrab::init()?;

    let mut previous_star = None::<u32>;

    #[cfg(debug_assertions)]
    {
        tracing::debug!("Getting the token scope…");
        tracing::debug!("Token scope: {:?}", octocrab::get_token_scope().await?);
    }

    // FIXME: change to webhook instead of polling for better performance.
    loop {
        tracing::debug!("Getting the stars…");
        let stars = octocrab::get_stars().await?;
        tracing::info!("This repo has {stars} stars currently.");

        if Some(stars) != previous_star {
            tracing::debug!("Updating the repo information…");
            octocrab::update_to_stars(stars).await?;
            tracing::info!("Successfully updated the stars of this repo to {stars}.");
        } else {
            tracing::debug!("Stars didn't change. Ignoring.");
        }

        previous_star = Some(stars);

        tracing::debug!("Wait for {REFRESH_INTERVAL} seconds before next update.");
        tokio::time::sleep(std::time::Duration::from_secs(REFRESH_INTERVAL)).await;
    }
}
