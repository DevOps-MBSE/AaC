/* tslint:disable */
/* eslint-disable */
import { Configuration, DefaultApi } from "../requests/generated/aac_rest_api";
import fetch from "node-fetch"
export * from  "../requests/generated/aac_rest_api/models"


const configuration = new Configuration({
  basePath: "http://localhost:8080",
  fetchApi: fetch
});

export const aacRestApi = new DefaultApi(configuration)