import { Octokit as Core } from "https://esm.sh/@octokit/core@4.0.4";
import { requestLog } from "https://esm.sh/@octokit/plugin-request-log@1.0.4";
import { paginateRest } from "https://esm.sh/@octokit/plugin-paginate-rest@3.0.0";
import { restEndpointMethods } from "https://esm.sh/@octokit/plugin-rest-endpoint-methods@6.1.2";

export const Octokit = Core.plugin(
  requestLog,
  restEndpointMethods,
  paginateRest,
);
