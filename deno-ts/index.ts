/**
 * Update the star to {n} stars.
 *
 * Thanks to the Python implementation by @fslongjin:
 *     <https://github.com/fslongjin/This-repo-has-648-stars/blob/851fe4c368b475ab923da72522af147180ddeb03/python/main.py>!
 */

import * as log from "https://deno.land/std@0.148.0/log/mod.ts";

import { Octokit } from "./octokit.ts";

const patToken = Deno.env.get("GITHUB_TOKEN");
const octokit = new Octokit({
  auth: patToken,
});

const repoInfo = {
  owner: "fslongjin",
  repo: "This-repo-has-N-stars",
};

/**
 * The refresh interval in ms.
 */
const refreshInterval = 3000;

/**
 * Get the current stars of this repository.
 */
async function getStars() {
  const response = await octokit.rest.repos.get(repoInfo);

  return response.data.stargazers_count;
}

/**
 * Update the stars of this repository.
 *
 * @param stars The update stars number.
 */
function updateToStars(stars: number) {
  return octokit.rest.repos.update({
    ...repoInfo,
    name: `This-repo-has-${stars}-stars`,
    description: `这个仓库有${stars}个star，不信你试试`,
  });
}

/**
 * Get the scope of this token.
 */
async function getTokenScope() {
  const response = await octokit.request('/');
  return response.headers["x-oauth-scopes"];
}

async function main() {
  let previousStar: number | null = null;

  log.debug(`GitHub Token used: ${patToken?.slice(0, 12)}…`);

  const scope = await getTokenScope();
  log.debug(`Token scope: ${scope}`);

  // FIXME: change to webhook instead of polling for better performance.
  setInterval(async () => {
    const stars = await getStars();
    log.info(`This repo has ${stars} stars currently.`);

    if (previousStar !== stars) {
      const response = await updateToStars(stars);
      if (response.status === 200) {
        log.info(`Update stars to ${stars} success.`);
      } else {
        log.error(`Update stars to ${stars} failed.`);
      }
    } else {
      log.debug("No stars changes. Ignoring");
    }

    log.debug(`Will check again in ${refreshInterval} seconds.`);
    previousStar = stars;
  }, refreshInterval);
}

main();
