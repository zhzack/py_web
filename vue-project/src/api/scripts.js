import http from "./http";

export function listScripts() {
    return http.get("/v1/scripts/list");
}

export function runScript(name) {
    return http.post("/v1/scripts/run", { name });
}
