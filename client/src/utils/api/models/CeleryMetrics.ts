/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CeleryMetrics = {
    status: CeleryMetrics.status;
    latency_ms?: (number | null);
    active_tasks: number;
    waiting_tasks: number;
    revoked_tasks: number;
    worker_count: number;
    worker_names: Array<string>;
    error?: (string | null);
};
export namespace CeleryMetrics {
    export enum status {
        HEALTHY = 'healthy',
        UNHEALTHY = 'unhealthy',
    }
}

