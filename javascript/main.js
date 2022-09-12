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
    console.log(req.data.name);
};

const checkStar = async (star)=> {
    const rep = await octokit.request('GET /repositories/{repo_id}' , {
        repo_id: process.env.repo_id,
    });
    const repo_name = rep.data.name;
    const data = {
        name: `This-repo-gets-${star}-star`,
        description: `My repo has ${star} stars...(这个仓库现在只有${star}颗星星)`,
    };
    // let regu = /This-Repo-Has-\d-Stars/;
    // if(regu.test(repo_name)) {
    //     console.log("This is right name.");
    // } else {
    //     console.log("This is wrong name.");
    // }
    reNameRepo(data);
};

getStar().then(star=>checkStar(star));