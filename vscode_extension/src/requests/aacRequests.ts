/* tslint:disable */
/* eslint-disable */
import { DefaultApi } from  "./generated/aac_rest_api/api"
export * from "./generated/aac_rest_api/model/models"

const port = "8000"
const host = "localhost"
export const aacRestApi = new DefaultApi(`http://${host}:${port}`)