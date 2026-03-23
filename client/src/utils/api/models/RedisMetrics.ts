/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type RedisMetrics = {
    status: RedisMetrics.status;
    latency_ms?: (number | null);
    used_memory_human?: (string | null);
    peak_memory_human?: (string | null);
    fragmentation_ratio?: (number | null);
    ops_per_sec?: (number | null);
    hit_rate?: (number | null);
    connected_clients?: (number | null);
    blocked_clients?: (number | null);
    version?: (string | null);
    error?: (string | null);
};
export namespace RedisMetrics {
    export enum status {
        HEALTHY = 'healthy',
        UNHEALTHY = 'unhealthy',
    }
}

