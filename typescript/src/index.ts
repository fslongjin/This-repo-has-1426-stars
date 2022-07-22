import { createServer } from 'http';

import EventSource from 'eventsource';
import { Octokit } from '@octokit/rest';
import { Webhooks, createNodeMiddleware } from '@octokit/webhooks';

/* configs */
const PORT = process.env.PORT || 3000;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const ACTING_URL = process.env.ACTING_URL;
const REPO_URL = process.env.REPO_URL;

if (!GITHUB_TOKEN || !WEBHOOK_SECRET || !REPO_URL || isNaN(+PORT)) {
  throw new Error('Missing required environment variables');
}

const regex = /github\.com\/(?<owner>[^/]+)\/(?<repo>[^/]+)/;
const repoInfo_ = <{ owner?: string; repo?: string }>(
  regex.exec(REPO_URL)?.groups
);
if (!repoInfo_.owner || !repoInfo_.repo) throw new Error('Invalid repo URL');
const repoInfo = <Required<typeof repoInfo_>>repoInfo_; // fix type
/* --- configs-end --- */

const webhooks = new Webhooks({ secret: WEBHOOK_SECRET });
const octokit = new Octokit({ auth: GITHUB_TOKEN });

const editRepo = async (starsCount: number) => {
  await octokit.repos.update({
    ...repoInfo,
    name: `This-repo-has-${starsCount}-stars`,
    description: `这个仓库有${starsCount}个star，不信你试试`,
  });
};

webhooks.on('star', ({ payload: { repository } }) => {
  editRepo(repository.stargazers_count);
});

(async () => {
  const scope = (await octokit.request('/')).headers['x-oauth-scopes'];
  console.info(`Token scope: ${scope}`);

  console.log('init repo stars count...');
  const { data: repository } = await octokit.repos.get({ ...repoInfo });
  await editRepo(repository.stargazers_count);

  createServer(createNodeMiddleware(webhooks))
    .on('error', console.error)
    .on('close', () => console.log('Server closed'))
    .listen(PORT, () => console.log(`Server running on port ${PORT}`));

  if (ACTING_URL) {
    const source = new EventSource(ACTING_URL);

    source.onmessage = (event) => {
      const webhookEvent = JSON.parse(event.data);

      webhooks
        .verifyAndReceive({
          id: webhookEvent['x-request-id'],
          name: webhookEvent['x-github-event'],
          signature: webhookEvent['x-hub-signature'],
          payload: webhookEvent.body,
        })
        .catch(console.error);
    };
  }
})();
