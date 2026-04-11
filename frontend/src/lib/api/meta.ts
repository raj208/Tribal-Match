import { apiGet } from "@/lib/api/client";

export type ApiHealth = {
  status: string;
  app_name: string;
  env: string;
  api_prefix: string;
};

export type ApiModule = {
  name: string;
  base_path: string;
  status: string;
};

export type ApiModulesResponse = {
  modules: ApiModule[];
};

export function getApiHealth() {
  return apiGet<ApiHealth>("/meta/health");
}

export function getApiModules() {
  return apiGet<ApiModulesResponse>("/meta/modules");
}