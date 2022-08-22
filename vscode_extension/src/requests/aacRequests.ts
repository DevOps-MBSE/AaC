/* tslint:disable */
/* eslint-disable */
import { DefaultApi } from  "./generated/aac_rest_api/api"
import * as configuration from "../configuration"
export * from "./generated/aac_rest_api/model/models"

const port = configuration.getConfigurationItem("rest_api.port") ?? "8000"
const host = configuration.getConfigurationItem("rest_api.host") ?? "localhost"
export const aacRestApi = new DefaultApi(`http://${host}:${port}`)