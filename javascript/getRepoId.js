const { Octokit } =  require('octokit');
require('dotenv').config();

const octokit = new Octokit( {
    auth: process.env.GITHUB_TOKEN,
});

const getId = async () => {
    const repo = await octokit.request('GET /repos/{owner}/{repo_name}', {
        owner:process.env.owner,
        repo_name:process.env.repo_name
    });
    return repo.data.id;
}

getId().then(id=>console.log(id));