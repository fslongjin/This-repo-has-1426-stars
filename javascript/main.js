const { Octokit } =  require('octokit');
require('dotenv').config();

const octokit = new Octokit({
    auth: process.env.GITHUB_TOKEN,
});

const getStar = async () => {
    const rep = await octokit.request('GET /repositories/{repo_id}' , {
        repo_id: process.env.repo_id,
    });
    const stars = rep.data.stargazers_count;
    console.log(`Your repo has ${stars} stars`);
    return rep.data.stargazers_count;
};

const reNameRepo = async (data) => {
    const req = await octokit.request('PATCH /repositories/{repo_id}', {
        repo_id: process.env.repo_id,
        ...data,
    });
};

const checkStar = async (star)=> {
    const rep = await octokit.request('GET /repositories/{repo_id}' , {
        repo_id: process.env.repo_id,
    });
    const repo_name = rep.data.name;
    const data = {
        name: `This-repo-has-${star}-stars`,
    };
    reNameRepo(data);
};

getStar().then(star=>checkStar(star));